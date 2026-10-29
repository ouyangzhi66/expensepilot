"""budget_check: query department budget and test a proposed amount."""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal

from langchain_core.tools import tool

from expensepilot.rag import connect

VALID_CATEGORIES = {"transport", "hotel", "meal", "other"}


@tool
def budget_check(
    employee: str = "",
    department: str = "",
    period: str = "",
    category: str = "hotel",
    amount: float = 0,
) -> str:
    """查询部门月度预算，并判断一笔拟报销是否超预算。

    employee: 员工姓名或工号（如“张三”/“E001”）；只知道部门时留空。
    department: 部门名称（如“研发部”）；employee 为空时使用。
    period: 月份，格式 YYYY-MM；留空取当前月。
    category: 费用类型 transport / hotel / meal / other。
    amount: 拟报销金额；只查余额时传 0。
    """
    if category not in VALID_CATEGORIES:
        return f"费用类型 {category} 不支持，请用 transport/hotel/meal/other。"
    if amount < 0:
        return "拟报销金额不能为负数。"
    if not period:
        period = date.today().strftime("%Y-%m")
    if not re.fullmatch(r"\d{4}-\d{2}", period):
        return "月份格式应为 YYYY-MM，例如 2026-10。"

    with connect() as conn, conn.cursor() as cur:
        dept = department.strip()
        person = ""

        if employee.strip():
            name = employee.strip()
            cur.execute(
                "select employee_no, name, department from employees "
                "where employee_no = %s or name = %s limit 2",
                (name, name),
            )
            rows = cur.fetchall()
            if not rows:
                # 允许模型把部门名误填进 employee
                cur.execute(
                    "select 1 from budgets where department = %s limit 1", (name,)
                )
                if cur.fetchone():
                    dept = name
                else:
                    return f"没有找到员工或部门：{name}"
            elif len(rows) > 1:
                candidates = "、".join(f"{row[1]}({row[0]})" for row in rows)
                return f"找到多个员工：{candidates}，请提供工号。"
            else:
                employee_no, employee_name, employee_dept = rows[0]
                person = f"{employee_name}（{employee_no}，{employee_dept}）"
                dept = employee_dept

        if not dept:
            return "请提供员工姓名/工号，或部门名称。"

        cur.execute(
            "select amount_limit, amount_used from budgets "
            "where department = %s and period = %s and category = %s",
            (dept, period, category),
        )
        budget = cur.fetchone()

    if not budget:
        return f"{dept} 在 {period} 没有 {category} 预算记录。"

    limit, used = budget
    remaining = limit - used
    lines = []
    if person:
        lines.append(f"员工：{person}")
    lines.append(f"部门：{dept}")
    lines.append(f"期间：{period}，类型：{category}")
    lines.append(f"额度：{limit:.2f}，已用：{used:.2f}，剩余：{remaining:.2f}")

    if amount > 0:
        proposed = Decimal(str(amount))
        over = proposed - remaining
        if over > 0:
            lines.append(f"拟报销：{proposed:.2f}；超预算：是，超出 {over:.2f}。")
        else:
            lines.append(
                f"拟报销：{proposed:.2f}；超预算：否，剩余 {remaining - proposed:.2f}。"
            )
    else:
        lines.append("拟报销：未提供（只查余额）。")

    return "\n".join(lines)
