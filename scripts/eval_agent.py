"""Run the 15-case end-to-end evaluation for D09."""

import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from langchain_core.messages import AIMessage, HumanMessage

from expensepilot.graph import build_graph

ROOT = Path(__file__).resolve().parents[1]

with (ROOT / "eval" / "cases.csv").open(encoding="utf-8") as handle:
    cases = list(csv.DictReader(handle))

graph = build_graph()
rows = []
for case in cases:
    started = time.time()
    result = graph.invoke(
        {
            "messages": [HumanMessage(content=case["input"])],
            "citations": [],
            "slots": {},
            "intent": "",
        },
        {"configurable": {"thread_id": f"eval-{case['id']}"}},
    )
    elapsed = time.time() - started

    actual_tools = []
    final_answer = ""
    for message in result["messages"]:
        if isinstance(message, AIMessage):
            for call in message.tool_calls:
                actual_tools.append(call["name"])
            if message.content and not message.tool_calls:
                final_answer = message.content

    expected_tools = {
        item.strip() for item in case["expected_tools"].split(",") if item.strip()
    }
    actual_set = set(actual_tools)
    if expected_tools:
        tools_ok = expected_tools.issubset(actual_set)
    else:
        tools_ok = not actual_set

    must = [item.strip() for item in case["must_contain"].split("|") if item.strip()]
    missing = [keyword for keyword in must if keyword not in final_answer]
    content_ok = not missing

    forbidden = [
        item.strip() for item in case["must_not_contain"].split("|") if item.strip()
    ]
    forbidden_hit = [keyword for keyword in forbidden if keyword in final_answer]
    forbidden_ok = not forbidden_hit

    expected_policy = case["expected_policy"].strip()
    citations = result.get("citations", [])
    citation_ok = (
        not expected_policy
        or expected_policy in citations
        or expected_policy in final_answer
    )

    passed = tools_ok and content_ok and forbidden_ok and citation_ok
    rows.append(
        {
            "id": case["id"],
            "type": case["type"],
            "pass": passed,
            "tools_ok": tools_ok,
            "content_ok": content_ok,
            "citation_ok": citation_ok,
            "tools": ",".join(actual_tools),
            "missing": ",".join(missing),
            "forbidden": ",".join(forbidden_hit),
            "seconds": round(elapsed, 2),
            "answer": final_answer.replace("\n", " ")[:300],
        }
    )

    status = "PASS" if passed else "FAIL"
    print(f"{status} {case['id']} {case['type']} tools={actual_tools}")
    if not passed:
        print(f"     missing={missing} forbidden={forbidden_hit} citations={citations}")

total = len(rows)
passed_count = sum(row["pass"] for row in rows)
tools_count = sum(row["tools_ok"] for row in rows)
content_count = sum(row["content_ok"] for row in rows)
citation_count = sum(row["citation_ok"] for row in rows)

print()
print(f"pass       {passed_count}/{total}")
print(f"tools      {tools_count}/{total}")
print(f"content    {content_count}/{total}")
print(f"citations  {citation_count}/{total}")

result_path = ROOT / "eval" / "results_d09.csv"
with result_path.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
print(f"saved {result_path}")
