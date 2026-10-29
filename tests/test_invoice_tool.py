from expensepilot.tools import invoice


class FakeCursor:
    def __init__(self, row) -> None:
        self._row = row

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *args) -> bool:
        return False

    def execute(self, sql: str, params: tuple | None = None) -> None:
        pass

    def fetchone(self):
        return self._row


class FakeConnection:
    def __init__(self, row) -> None:
        self._row = row

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *args) -> bool:
        return False

    def cursor(self) -> FakeCursor:
        return FakeCursor(self._row)


def test_duplicate_invoice_is_reported(monkeypatch) -> None:
    monkeypatch.setattr(invoice, "connect", lambda: FakeConnection((12, 700, "pending")))
    output = invoice.invoice_check.invoke({"invoice_no": "INV-1"})

    assert "重复发票" in output
    assert "POL-009" in output


def test_amount_mismatch_is_reported(monkeypatch) -> None:
    monkeypatch.setattr(invoice, "connect", lambda: FakeConnection(None))
    output = invoice.invoice_check.invoke(
        {"invoice_amount": 600, "claimed_amount": 800}
    )

    assert "不一致" in output
    assert "POL-004" in output
