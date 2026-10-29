"""Ask the ExpensePilot agent one question."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from expensepilot.graph import build_graph

if __name__ == "__main__":
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        question = input("问题：").strip()

    graph = build_graph()
    result = graph.invoke(
        {
            "messages": [HumanMessage(content=question)],
            "citations": [],
            "slots": {},
        }
    )

    print(f"\n问题：{question}\n")
    for message in result["messages"]:
        if isinstance(message, AIMessage):
            for call in message.tool_calls:
                print(f"[tool_call] {call['name']} {call['args']}")
            if message.content:
                print(f"[assistant] {message.content}")
        elif isinstance(message, ToolMessage):
            preview = message.content[:300].replace("\n", " ")
            print(f"[tool_result] {preview}...")

    print(f"\ncitations: {result.get('citations', [])}")
