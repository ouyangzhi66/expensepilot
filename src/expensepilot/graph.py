"""LangGraph wiring: agent ↔ policy_search / budget_check tools."""

from __future__ import annotations

import re

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from expensepilot.config import MODEL_NAME, OPENAI_API_KEY, OPENAI_BASE_URL
from expensepilot.state import AgentState
from expensepilot.tools import budget_check, policy_search

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
"""

TOOLS = {"policy_search": policy_search, "budget_check": budget_check}


def build_graph():
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-xxx":
        raise RuntimeError("OPENAI_API_KEY is not set; edit .env first.")

    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        temperature=0,
    )
    llm_with_tools = llm.bind_tools([policy_search, budget_check])

    def agent_node(state: AgentState) -> dict:
        response = llm_with_tools.invoke(
            [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        )
        update: dict = {"messages": [response]}

        # 最终回答落定后，只把回答里真正引用的条款记进 citations。
        if isinstance(response, AIMessage) and not response.tool_calls:
            content = response.content if isinstance(response.content, str) else ""
            cited = list(dict.fromkeys(re.findall(r"POL-\d{3}", content)))
            update["citations"] = cited
        return update

    def tool_node(state: AgentState) -> dict:
        last = state["messages"][-1]
        outputs = []
        for call in last.tool_calls:
            result = TOOLS[call["name"]].invoke(call["args"])
            outputs.append(ToolMessage(content=result, tool_call_id=call["id"]))
        return {"messages": outputs}

    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            return "tools"
        return END

    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    builder.add_edge("tools", "agent")
    return builder.compile()
