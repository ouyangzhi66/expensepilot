"""Agent state shared by LangGraph nodes."""

from __future__ import annotations

from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    citations: list[str]
    slots: dict[str, Any]
    intent: str
