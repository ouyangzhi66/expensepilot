"""invoice_check: detect duplicate invoice numbers and amount mismatches."""

from __future__ import annotations

from langchain_core.tools import tool

from expensepilot.rag import connect


@tool
def invoice_check(
    invoice_no: str = "",
    invoice_amount: float = 0,
    claimed_amount: float = 0,
) -> str:
    """校验发票号是否重复、票面金额与申报金额是否一致。

    invoice_no: 发票号；invoice_amount: 票面金额；claimed_amount: 申报金额。
    用户提到发票号、或票面金额和申报金额不一致时调用。
    """
    invoice_no = invoice_no.strip()

    if invoice_no:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                "select id, amount, status from reimbursements "
                "where invoice_no = %s limit 1",
                (invoice_no,),
            )
            row = cur.fetchone()
        if row:
            return (
                f"发现重复发票：{invoice_no} 已在报销单 #{row[0]} 使用"
                f"（金额 {row[1]:.2f}，状态 {row[2]}）。按 POL-009 需转人工核查。"
            )

    if (
        invoice_amount > 0
        and claimed_amount > 0
        and abs(invoice_amount - claimed_amount) > 0.01
    ):
        return (
            f"票面金额 {invoice_amount:.2f} 与申报金额 {claimed_amount:.2f} 不一致，"
            "按 POL-004 需转人工核实。"
        )

    if invoice_no or invoice_amount:
        return "发票校验通过：未发现重复，票面金额与申报金额一致。"

    return "未提供发票号或金额，无法校验。"
