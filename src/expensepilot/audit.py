"""Audit logging and human approval tickets."""

from __future__ import annotations

from contextvars import ContextVar
from datetime import datetime
from uuid import uuid4

from psycopg.types.json import Jsonb

from expensepilot.rag import connect

current_thread_id: ContextVar[str] = ContextVar("current_thread_id", default="")


def log_event(
    event_type: str,
    tool_name: str = "",
    payload: dict | None = None,
    output: str = "",
    decision: str = "",
) -> None:
    """Write one audit row; never let audit failure break the agent."""
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                insert into audit_logs
                    (thread_id, event_type, tool_name, input, output, decision)
                values (%s, %s, %s, %s, %s, %s)
                """,
                (
                    current_thread_id.get(),
                    event_type,
                    tool_name,
                    Jsonb(payload or {}),
                    str(output)[:4000],
                    decision,
                ),
            )
            conn.commit()
    except Exception as exc:  # noqa: BLE001 - audit must not break the request
        print(f"[audit] write failed: {exc}")


def create_approval(
    reason: str,
    summary: str = "",
    employee_no: str = "",
    employee_name: str = "",
    amount: float = 0.0,
) -> str:
    """Create a pending approval ticket and log it."""
    ticket_no = f"H{datetime.now():%Y%m%d%H%M%S}{uuid4().hex[:4].upper()}"
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            insert into approvals
                (ticket_no, thread_id, employee_no, employee_name,
                 reason, summary, amount, status)
            values (%s, %s, %s, %s, %s, %s, %s, 'pending')
            """,
            (
                ticket_no,
                current_thread_id.get(),
                employee_no,
                employee_name,
                reason,
                summary,
                amount,
            ),
        )
        conn.commit()

    log_event(
        "human_escalation",
        "escalate_to_human",
        {"reason": reason, "summary": summary, "amount": amount},
        ticket_no,
        "pending_human",
    )
    return ticket_no
