"""Search policy clauses from the command line."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from expensepilot.rag import search

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("-k", type=int, default=3)
    args = parser.parse_args()

    for policy_no, title, clause_no, content, score in search(args.query, args.k):
        print(f"[{score:.3f}] {policy_no} {clause_no} {title}")
        print(f"  {content}")
