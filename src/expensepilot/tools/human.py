"""escalate_to_human: hand a case to a human and create a ticket."""

from __future__ import annotations

from langchain_core.tools import tool

from expensepilot.audit import create_approval
from expensepilot.rag import connect


@tool
def escalate_to_human(
    reason: str,
    summary: str = "",
    employee: str = "",
    amount: float = 0,
) -> str:
    """把无法自动处理或需要审批的报销转给人工，并生成工单。

    以下情况必须调用：
    - 预算超支
    - 代他人报销、越权
    - 制度之间冲突，或信息不足无法判断
    - 用户明确要求人工

    reason: 转人工原因；summary: 一句话摘要；employee: 员工姓名或工号；amount: 涉及金额。
    """
    employee_no = ""
    employee_name = employee.strip()
    if employee.strip():
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                "select employee_no, name from employees "
                "where employee_no = %s or name = %s limit 1",
                (employee.strip(), employee.strip()),
            )
            row = cur.fetchone()
        if row:
            employee_no, employee_name = row

    ticket_no = create_approval(
        reason=reason.strip() or "需要人工确认",
        summary=summary.strip(),
        employee_no=employee_no,
        employee_name=employee_name,
        amount=amount,
    )

    return (
        f"已转人工，工单 {ticket_no}。原因：{reason}。"
        f"金额：{amount:.2f} 元。请等待财务/部门负责人处理，不要重复提交。"
    )
