"""打印最近的转人工工单与审计记录，核对「人在回路」是否留痕。

用法：
    python scripts/audit_report.py            # 最近 5 条
    python scripts/audit_report.py 10         # 最近 10 条
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import psycopg

from expensepilot.config import DATABASE_URL


def main(limit: int = 5) -> None:
    if not DATABASE_URL:
        raise SystemExit("DATABASE_URL 未配置，先在 .env 或环境变量里填上")

    with psycopg.connect(DATABASE_URL) as conn, conn.cursor() as cur:
        cur.execute(
            """
            select ticket_no, employee_name, reason, amount, status, created_at
            from approvals
            order by id desc
            limit %s
            """,
            (limit,),
        )
        approvals = cur.fetchall()

        cur.execute(
            """
            select tool_name, decision, count(*) as n
            from audit_logs
            group by tool_name, decision
            order by n desc
            """
        )
        stats = cur.fetchall()

        cur.execute(
            """
            select thread_id, tool_name, decision, created_at
            from audit_logs
            order by id desc
            limit %s
            """,
            (limit,),
        )
        recent = cur.fetchall()

    print(f"== 最近 {len(approvals)} 条转人工工单 ==")
    for ticket_no, name, reason, amount, status, created_at in approvals:
        print(
            f"{ticket_no} | {name or '-'} | {reason} | "
            f"{amount if amount is not None else '-'} | {status} | {created_at:%Y-%m-%d %H:%M:%S}"
        )

    print("\n== 审计日志按工具/决策聚合 ==")
    for tool_name, decision, count in stats:
        print(f"{tool_name or '-'} | {decision or '-'} | {count}")

    print(f"\n== 最近 {len(recent)} 条审计记录 ==")
    for thread_id, tool_name, decision, created_at in recent:
        print(
            f"{created_at:%Y-%m-%d %H:%M:%S} | {thread_id or '-'} | "
            f"{tool_name or '-'} | {decision or '-'}"
        )


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
