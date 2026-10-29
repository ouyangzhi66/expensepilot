"""Interactive multi-turn chat with ExpensePilot."""

import json
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from langchain_core.messages import AIMessage, HumanMessage

from expensepilot.graph import build_graph


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": f"chat-{uuid4().hex[:8]}"}}
    print("ExpensePilot · 输入 exit 退出\n")

    first_turn = True
    while True:
        try:
            question = input("你：").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() in {"exit", "quit", "q"}:
            break
        if not question:
            continue

        payload: dict = {"messages": [HumanMessage(content=question)]}
        if first_turn:
            payload["citations"] = []
            payload["slots"] = {}
            first_turn = False

        result = graph.invoke(payload, config)

        last_ai = None
        for message in reversed(result["messages"]):
            if (
                isinstance(message, AIMessage)
                and message.content
                and not message.tool_calls
            ):
                last_ai = message
                break

        print(f"\n助手：{last_ai.content if last_ai else '(没有回答)'}")
        print(f"槽位：{json.dumps(result.get('slots', {}), ensure_ascii=False)}")
        if result.get("citations"):
            print(f"引用：{result['citations']}")
        print()


if __name__ == "__main__":
    main()
