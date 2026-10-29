from expensepilot.slots import (
    REQUIRED_SLOTS,
    build_question,
    merge_slots,
    missing_slots,
    parse_slot_json,
    parse_turn_json,
)


def test_missing_slots_all() -> None:
    assert missing_slots({}) == list(REQUIRED_SLOTS)


def test_missing_slots_complete() -> None:
    slots = {
        "employee": "张三",
        "trip_city": "上海",
        "start_date": "2026-10-12",
        "end_date": "2026-10-13",
        "category": "hotel",
        "amount": 800,
    }
    assert missing_slots(slots) == []


def test_merge_slots_ignores_empty() -> None:
    merged = merge_slots({"employee": "张三"}, {"employee": "  ", "trip_city": "上海"})
    assert merged == {"employee": "张三", "trip_city": "上海"}


def test_parse_slot_json_aliases() -> None:
    data = parse_slot_json(
        '{"employee":"张三","trip_city":"上海","category":"住宿","amount":"800元"}'
    )
    assert data["category"] == "hotel"
    assert data["amount"] == 800.0
    assert data["trip_city"] == "上海"


def test_question_lists_missing_items() -> None:
    question = build_question(["trip_city", "amount"])
    assert "城市" in question
    assert "金额" in question


def test_parse_turn_intent_and_slots() -> None:
    intent, slots = parse_turn_json(
        '{"intent":"policy","slots":{"trip_city":"上海"}}'
    )
    assert intent == "policy"
    assert slots == {"trip_city": "上海"}
