"""Apply a .sql file statement by statement."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from expensepilot.rag import connect

if __name__ == "__main__":
    sql_path = Path(sys.argv[1])
    sql = sql_path.read_text(encoding="utf-8")
    statements = [part.strip() for part in sql.split(";") if part.strip()]

    with connect() as conn, conn.cursor() as cur:
        for statement in statements:
            cur.execute(statement)
        conn.commit()

    print(f"applied {len(statements)} statements from {sql_path}")
