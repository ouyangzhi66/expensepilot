from expensepilot.tools import policy


def test_policy_search_formats_citations(monkeypatch) -> None:
    def fake_search(query: str, k: int = 3) -> list[tuple]:
        return [("POL-001", "住宿标准", "POL-001-1", "一线城市 500 元/晚。", 0.93)]

    monkeypatch.setattr(policy, "search", fake_search)
    output = policy.policy_search.invoke({"query": "住宿标准是多少"})

    assert "POL-001" in output
    assert "500" in output
