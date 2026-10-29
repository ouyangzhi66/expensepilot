from decimal import Decimal

from expensepilot.tools import budget


class FakeCursor:
    def __init__(self) -> None:
        self._rows: list[tuple] = []

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *args) -> bool:
        return False

    def execute(self, sql: str, params: tuple | None = None) -> None:
        if "from employees" in sql:
            self._rows = [("E001", "张三", "研发部")]
        elif "from budgets" in sql:
            self._rows = [(Decimal("8000"), Decimal("900"))]
        else:
            self._rows = []

    def fetchall(self) -> list[tuple]:
        return self._rows

    def fetchone(self) -> tuple | None:
        return self._rows[0] if self._rows else None


class FakeConnection:
    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *args) -> bool:
        return False

    def cursor(self) -> FakeCursor:
        return FakeCursor()


def test_budget_check_reports_remaining(monkeypatch) -> None:
    monkeypatch.setattr(budget, "connect", lambda: FakeConnection())
    output = budget.budget_check.invoke(
        {"employee": "张三", "period": "2026-10", "category": "hotel", "amount": 800}
    )

    assert "研发部" in output
    assert "7100.00" in output
    assert "超预算：否" in output
