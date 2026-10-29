"""LangGraph wiring: slot filling → agent ↔ tools."""

from __future__ import annotations

import json
import re
from datetime import date

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from expensepilot.audit import current_thread_id, log_event
from expensepilot.config import MODEL_NAME, OPENAI_API_KEY, OPENAI_BASE_URL
from expensepilot.slots import build_question, merge_slots, missing_slots, parse_slot_json
from expensepilot.state import AgentState
from expensepilot.tools import (
    budget_check,
    escalate_to_human,
    policy_search,
    voucher_create,
)

SYSTEM_PROMPT = """你是 ExpensePilot，一个财务报销助手。

规则：
1. 只要问题涉及报销标准、发票、额度、审批、时限，必须先调用 policy_search，不要凭记忆回答。
2. 回答必须引用条款号（如 POL-001），并说明关键数字。
3. 制度里没有的，明确说“制度里没有相关规定”，不要编。
4. 与报销无关的问题，说明你只处理报销和制度问题。
5. 不要替用户做最终审批；不确定时建议转人工。
6. 问题涉及部门/个人预算、剩余额度、会不会超预算时，必须调用 budget_check；
   同时涉及制度上限时，policy_search 和 budget_check 都要调用。
7. 预算数字以 budget_check 返回为准，不要自己算；制度上限和预算余额要分开说。
8. 用户要求生成凭证/报销单/凭证草稿时，先完成 policy_search 和 budget_check，再调用 voucher_create；
   把已引用的 POL 编号传给 citations，至少 1 条。
9. 凭证生成后，说明这是草稿，8 个必填字段要完整，需人工确认。
10. 下方会给出“当前槽位”。槽位已齐时不要重复追问，直接按槽位调用工具。
11. 出现以下情况必须调用 escalate_to_human：预算超支、代报/越权、制度冲突、
    信息不足无法判断、用户明确要求人工。不要自行批准。
12. 转人工后说明工单号和原因，不要重复提交。
13. 工具调用会自动写审计日志，不要声称自己写了日志。
14. 用户说“替/代/帮别人报销”时，不要先追问关系，直接调用 escalate_to_human，
    reason 写“代他人报销”，并带上 employee 和 amount。
"""

TOOLS = {
    "policy_search": policy_search,
    "budget_check": budget_check,
    "voucher_create": voucher_create,
    "escalate_to_human": escalate_to_human,
}


def _slot_prompt(current: dict, transcript: str) -> str:
    return f"""你是报销槽位抽取器。今天是 {date.today().isoformat()}。

从对话中抽取报销信息，只输出一个 JSON 对象，不要 markdown，不要解释。

字段：
- employee: 报销人姓名或工号
- trip_city: 出差城市
- start_date: 开始日期，YYYY-MM-DD
- end_date: 结束日期，YYYY-MM-DD
- category: 只能是 transport / hotel / meal / other
- amount: 数字，单位元
- invoice_no: 发票号

没有出现或不确定的字段填 null。用户说“住宿”就填 hotel，“交通/高铁/打车”填 transport，“餐费/招待”填 meal。
已知槽位：{json.dumps(current, ensure_ascii=False)}
对话：
{transcript}
"""


def build_graph():
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-xxx":
        raise RuntimeError("OPENAI_API_KEY is not set; edit .env first.")

    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        temperature=0,
    )
    slot_llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        temperature=0,
        max_tokens=300,
    )
    llm_with_tools = llm.bind_tools(
        [policy_search, budget_check, voucher_create, escalate_to_human]
    )

    def extract_node(state: AgentState) -> dict:
        messages = state["messages"]
        transcript = []
        for message in messages[-8:]:
            if isinstance(message, HumanMessage):
                role = "用户"
            elif isinstance(message, AIMessage):
                role = "助手"
            else:
                continue
            content = message.content if isinstance(message.content, str) else ""
            if content:
                transcript.append(f"{role}：{content}")

        prompt = _slot_prompt(dict(state.get("slots", {})), "\n".join(transcript))
        response = slot_llm.invoke([SystemMessage(content=prompt)])
        content = response.content if isinstance(response.content, str) else ""
        update = parse_slot_json(content)
        return {"slots": merge_slots(dict(state.get("slots", {})), update)}

    def ask_node(state: AgentState) -> dict:
        missing = missing_slots(dict(state.get("slots", {})))
        return {"messages": [AIMessage(content=build_question(missing))]}

    def route_after_extract(state: AgentState) -> str:
        return "ask" if missing_slots(dict(state.get("slots", {}))) else "agent"

    def agent_node(state: AgentState) -> dict:
        slots_text = json.dumps(state.get("slots", {}), ensure_ascii=False)
        response = llm_with_tools.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                SystemMessage(content=f"当前槽位：{slots_text}"),
                *state["messages"],
            ]
        )
        update: dict = {"messages": [response]}

        if isinstance(response, AIMessage) and not response.tool_calls:
            content = response.content if isinstance(response.content, str) else ""
            cited = list(dict.fromkeys(re.findall(r"POL-\d{3}", content)))
            update["citations"] = cited
        return update

    def tool_node(state: AgentState, config: RunnableConfig) -> dict:
        last = state["messages"][-1]
        thread_id = config.get("configurable", {}).get("thread_id", "")
        token = current_thread_id.set(thread_id)
        outputs = []
        try:
            for call in last.tool_calls:
                result = TOOLS[call["name"]].invoke(call["args"])
                decision = (
                    "pending_human"
                    if call["name"] == "escalate_to_human"
                    else "allowed"
                )
                log_event("tool_call", call["name"], call["args"], result, decision)
                outputs.append(ToolMessage(content=result, tool_call_id=call["id"]))
        finally:
            current_thread_id.reset(token)
        return {"messages": outputs}

    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            return "tools"
        return END

    builder = StateGraph(AgentState)
    builder.add_node("extract", extract_node)
    builder.add_node("ask", ask_node)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "extract")
    builder.add_conditional_edges(
        "extract", route_after_extract, {"ask": "ask", "agent": "agent"}
    )
    builder.add_edge("ask", END)
    builder.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    builder.add_edge("tools", "agent")

    return builder.compile(checkpointer=MemorySaver())
