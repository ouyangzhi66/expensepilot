import json

from expensepilot.tools import voucher


class FakeCursor:
    def __init__(self) -> None:
        self._rows: list[tuple] = []

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *args) -> bool:
        return False

    def execute(self, sql: str, params: tuple | None = None) -> None:
        self._rows = [("E001", "张三", "研发部")]

    def fetchall(self) -> list[tuple]:
        return self._rows


class FakeConnection:
    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *args) -> bool:
        return False

    def cursor(self) -> FakeCursor:
        return FakeCursor()


def test_voucher_create_returns_valid_draft(monkeypatch) -> None:
    monkeypatch.setattr(voucher, "connect", lambda: FakeConnection())
    output = voucher.voucher_create.invoke(
        {
            "employee": "张三",
            "category": "hotel",
            "amount": 800,
            "trip_city": "上海",
            "start_date": "2026-10-12",
            "end_date": "2026-10-13",
            "invoice_no": "INV-20261012-01",
            "citations": ["POL-001"],
        }
    )

    data = json.loads(output)
    assert data["employee_name"] == "张三"
    assert data["department"] == "研发部"
    assert data["amount"] == 800
    assert data["tax_amount"] == 45.28
    assert data["citations"] == ["POL-001"]
    assert data["status"] == "draft"


def test_voucher_create_requires_citation(monkeypatch) -> None:
    monkeypatch.setattr(voucher, "connect", lambda: FakeConnection())
    output = voucher.voucher_create.invoke(
        {"employee": "张三", "category": "hotel", "amount": 800, "citations": []}
    )

    assert "缺少条款引用" in output
