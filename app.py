"""ExpensePilot Streamlit UI: chat + slots + tool trace + voucher draft."""

import json
import sys
from pathlib import Path
from uuid import uuid4

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from expensepilot.graph import build_graph
from expensepilot.slots import REQUIRED_SLOTS, missing_slots

st.set_page_config(
    page_title="ExpensePilot · 财务报销 Agent",
    page_icon="🧾",
    layout="wide",
)

SLOT_LABELS = {
    "employee": "报销人",
    "trip_city": "出差城市",
    "start_date": "开始日期",
    "end_date": "结束日期",
    "category": "费用类型",
    "amount": "金额",
}

CATEGORY_LABELS = {
    "transport": "交通",
    "hotel": "住宿",
    "meal": "餐费",
    "other": "其他",
}

EXAMPLES = [
    ("帮我报销", "帮我报销"),
    ("上海住宿 800 能报吗", "上海住宿800能报吗"),
    ("李四再报 5000 住宿", "李四再报5000住宿呢"),
]


@st.cache_resource
def get_graph():
    return build_graph()


def new_session() -> None:
    st.session_state.thread_id = f"web-{uuid4().hex[:8]}"
    st.session_state.history = []
    st.session_state.slots = {}
    st.session_state.citations = []
    st.session_state.voucher = None
    st.session_state.last_tools = []
    st.session_state.escalation = None
    st.session_state.turn = 0
    st.session_state.seen = 0


for key, value in {
    "history": [],
    "slots": {},
    "citations": [],
    "voucher": None,
    "last_tools": [],
    "escalation": None,
    "turn": 0,
    "seen": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value
if "thread_id" not in st.session_state:
    new_session()


def slot_display(key: str):
    value = st.session_state.slots.get(key)
    if value in (None, ""):
        return "—"
    if key == "category":
        return CATEGORY_LABELS.get(value, value)
    if key == "amount":
        return f"{float(value):.2f} 元"
    return value


def process(prompt: str) -> None:
    st.session_state.history.append(("user", prompt))
    payload: dict = {"messages": [HumanMessage(content=prompt)]}
    if st.session_state.turn == 0:
        payload["slots"] = {}
        payload["citations"] = []

    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    try:
        with st.spinner("Agent 正在查制度 / 预算 / 生成凭证..."):
            result = get_graph().invoke(payload, config)
    except Exception as exc:  # noqa: BLE001 - show the error in the UI
        st.session_state.history.pop()
        st.error(f"调用失败：{exc}")
        return

    st.session_state.turn += 1
    st.session_state.slots = result.get("slots", {})
    st.session_state.citations = result.get("citations", [])

    new_messages = result["messages"][st.session_state.seen :]
    st.session_state.seen = len(result["messages"])

    calls = []
    results = []
    for message in new_messages:
        if isinstance(message, AIMessage):
            for call in message.tool_calls:
                calls.append({"tool": call["name"], "args": call["args"]})
            if message.content and not message.tool_calls:
                st.session_state.history.append(("assistant", message.content))
        elif isinstance(message, ToolMessage):
            results.append(message.content)
            if "已转人工，工单" in message.content:
                st.session_state.escalation = message.content
            try:
                data = json.loads(message.content)
            except (json.JSONDecodeError, TypeError):
                continue
            if isinstance(data, dict) and "voucher_no" in data:
                st.session_state.voucher = data

    st.session_state.last_tools = []
    for index, call in enumerate(calls):
        raw = results[index] if index < len(results) else ""
        st.session_state.last_tools.append(
            {
                "tool": call,
                "result": raw[:600] + ("..." if len(raw) > 600 else ""),
            }
        )

    st.rerun()


with st.sidebar:
    st.title("🧾 ExpensePilot")
    st.caption("财务报销 Agent · 先查制度与预算，再生成凭证草稿")

    if st.button("重新开始", use_container_width=True):
        new_session()
        st.rerun()

    st.divider()
    st.subheader("槽位")
    for slot_key in REQUIRED_SLOTS:
        st.markdown(f"**{SLOT_LABELS[slot_key]}**：{slot_display(slot_key)}")

    missing = missing_slots(st.session_state.slots)
    if missing:
        st.warning("还缺：" + "、".join(SLOT_LABELS[key] for key in missing))
    else:
        st.success("槽位已齐")

    st.divider()
    st.subheader("引用")
    st.write("、".join(st.session_state.citations) or "—")

    with st.expander("本轮工具调用", expanded=False):
        st.json(st.session_state.last_tools or [])

    with st.expander("凭证草稿", expanded=False):
        if st.session_state.voucher:
            st.json(st.session_state.voucher)
        else:
            st.caption("还没有生成")

    with st.expander("待人工", expanded=False):
        if st.session_state.escalation:
            st.warning(st.session_state.escalation)
        else:
            st.caption("没有待人工工单")

    st.divider()
    st.subheader("示例")
    for label, text in EXAMPLES:
        if st.button(label, use_container_width=True):
            st.session_state.pending = text
            st.rerun()

st.title("财务报销 Agent")
st.caption("信息不全时我会先追问；槽位齐了再查制度、预算并生成凭证草稿。")

try:
    graph = get_graph()
except Exception as exc:  # noqa: BLE001 - configuration error is shown in the UI
    st.error(f"Agent 初始化失败：{exc}")
    st.stop()

for role, content in st.session_state.history:
    with st.chat_message(role, avatar="🧑‍💼" if role == "user" else "🧾"):
        st.markdown(content)

prompt = st.chat_input("例如：帮我报销 / 上海住宿800能报吗")
if st.session_state.get("pending"):
    prompt = st.session_state.pop("pending")

if prompt:
    process(prompt)
