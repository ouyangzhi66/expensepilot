from expensepilot.tools import human


class FakeCursor:
    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *args) -> bool:
        return False

    def execute(self, sql: str, params: tuple | None = None) -> None:
        pass

    def fetchone(self) -> tuple:
        return ("E001", "张三")


class FakeConnection:
    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *args) -> bool:
        return False

    def cursor(self) -> FakeCursor:
        return FakeCursor()


def test_escalate_creates_ticket(monkeypatch) -> None:
    monkeypatch.setattr(human, "connect", lambda: FakeConnection())
    monkeypatch.setattr(human, "create_approval", lambda **kwargs: "HTEST-001")

    output = human.escalate_to_human.invoke(
        {"reason": "代他人报销", "employee": "张三", "amount": 800}
    )

    assert "HTEST-001" in output
    assert "800.00" in output
    assert "代他人报销" in output
