"""Embed all policy clauses into pgvector."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from expensepilot.rag import ingest

if __name__ == "__main__":
    policies, chunks = ingest()
    print(f"ingested {chunks} chunks from {policies} policies")
