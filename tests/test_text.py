from expensepilot.text import split_clauses


def test_short_text_stays_one_chunk() -> None:
    assert split_clauses("住宿上限 500 元/晚。") == ["住宿上限 500 元/晚。"]


def test_long_text_splits_on_sentence_boundaries() -> None:
    text = "第一句。" * 60
    chunks = split_clauses(text, max_chars=50)
    assert len(chunks) > 1
    assert all(len(chunk) <= 50 for chunk in chunks)
    assert "".join(chunks) == text


def test_empty_text_returns_empty_list() -> None:
    assert split_clauses("   ") == []
