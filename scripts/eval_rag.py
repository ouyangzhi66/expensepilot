"""Evaluate policy retrieval hit rate against eval/rag_queries.csv."""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from expensepilot.rag import search

ROOT = Path(__file__).resolve().parents[1]

with (ROOT / "eval" / "rag_queries.csv").open(encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

top1 = 0
top3 = 0
for row in rows:
    results = search(row["query"], k=3)
    policy_nos = [result[0] for result in results]
    expected = row["expected_policy"]
    hit1 = bool(policy_nos) and policy_nos[0] == expected
    hit3 = expected in policy_nos
    top1 += int(hit1)
    top3 += int(hit3)
    status = "TOP1" if hit1 else ("TOP3" if hit3 else "MISS")
    print(f"{status:4} {row['query']} -> {policy_nos} (expected {expected})")

total = len(rows)
print(f"top1 {top1}/{total}, top3 {top3}/{total}")
