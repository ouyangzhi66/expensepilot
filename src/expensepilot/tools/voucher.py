"""voucher_create: build and validate a reimbursement voucher draft."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from uuid import uuid4

from jsonschema import ValidationError, validate
from langchain_core.tools import tool

from expensepilot.config import PROJECT_ROOT
from expensepilot.rag import connect

SCHEMA_PATH = PROJECT_ROOT / "schemas" / "voucher.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

CATEGORY_LABELS = {
    "transport": "交通费",
    "hotel": "住宿费",
    "meal": "餐费",
    "other": "其他费用",
}

ACCOUNT_SUBJECTS = {
    "transport": "管理费用-差旅费-交通费",
    "hotel": "管理费用-差旅费-住宿费",
    "meal": "管理费用-业务招待费",
    "other": "管理费用-其他",
}


def _parse_date(value: str, field: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} 格式应为 YYYY-MM-DD") from exc


@tool
def voucher_create(
    employee: str,
    category: str,
    amount: float,
    trip_city: str = "",
    start_date: str = "",
    end_date: str = "",
    invoice_no: str = "",
    citations: list[str] | None = None,
    tax_rate: float = 0.06,
) -> str:
    """生成一张报销凭证草稿，并校验 8 个必填字段。

    employee: 员工姓名或工号（如“张三”/“E001”）。
    category: 费用类型 transport / hotel / meal / other。
    amount: 含税金额。
    trip_city: 出差城市。
    start_date / end_date: 行程日期，格式 YYYY-MM-DD。
    invoice_no: 发票号，没有可留空。
    citations: 已引用的制度条款号列表，例如 ["POL-001"]，至少 1 条。
    tax_rate: 税率，默认 6%。

    返回：校验通过的凭证 JSON 字符串；校验失败时返回错误说明。
    """
    if category not in CATEGORY_LABELS:
        return f"费用类型 {category} 不支持，请用 transport/hotel/meal/other。"
    if amount <= 0:
        return "金额必须大于 0。"
    if not 0 <= tax_rate <= 0.2:
        return "税率应在 0 到 0.2 之间。"

    clean_citations = []
    for citation in citations or []:
        if re.fullmatch(r"POL-\d{3}", citation) and citation not in clean_citations:
            clean_citations.append(citation)
    if not clean_citations:
        return "缺少条款引用：请先查制度，并把 POL-xxx 传给 citations。"

    try:
        start = _parse_date(start_date, "start_date")
        end = _parse_date(end_date, "end_date")
        if start and end and end < start:
            return "end_date 不能早于 start_date。"
    except ValueError as exc:
        return str(exc)

    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "select employee_no, name, department from employees "
            "where employee_no = %s or name = %s limit 2",
            (employee.strip(), employee.strip()),
        )
        rows = cur.fetchall()

    if not rows:
        return f"没有找到员工：{employee}"
    if len(rows) > 1:
        candidates = "、".join(f"{row[1]}({row[0]})" for row in rows)
        return f"找到多个员工：{candidates}，请提供工号。"

    employee_no, employee_name, department = rows[0]
    period = start.strftime("%Y-%m") if start else date.today().strftime("%Y-%m")
    city = trip_city.strip()
    summary = f"{period} {city} {CATEGORY_LABELS[category]}报销".replace("  ", " ").strip()

    tax_amount = round(amount - amount / (1 + tax_rate), 2)
    voucher = {
        "voucher_no": f"V{datetime.now():%Y%m%d%H%M%S}{uuid4().hex[:4].upper()}",
        "employee_no": employee_no,
        "employee_name": employee_name,
        "department": department,
        "category": category,
        "amount": round(amount, 2),
        "tax_amount": tax_amount,
        "summary": summary,
        "account_subject": ACCOUNT_SUBJECTS[category],
        "citations": clean_citations,
        "trip_city": city,
        "start_date": start.isoformat() if start else None,
        "end_date": end.isoformat() if end else None,
        "invoice_no": invoice_no.strip() or None,
        "status": "draft",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    try:
        validate(instance=voucher, schema=SCHEMA)
    except ValidationError as exc:
        return f"凭证校验失败：{exc.message}"

    return json.dumps(voucher, ensure_ascii=False, indent=2)
