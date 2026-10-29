"""Slot definitions and helpers for multi-turn reimbursement collection."""

from __future__ import annotations

import json
import re
from typing import Literal

from pydantic import BaseModel, ValidationError

REQUIRED_SLOTS = (
    "employee",
    "trip_city",
    "start_date",
    "end_date",
    "category",
    "amount",
)

INTENTS = {"reimburse", "policy", "budget", "other"}

SLOT_QUESTIONS = {
    "employee": "报销人是谁？（姓名或工号，例如“张三”/“E001”）",
    "trip_city": "出差城市是哪里？",
    "start_date": "行程开始日期是哪天？（YYYY-MM-DD）",
    "end_date": "行程结束日期是哪天？（YYYY-MM-DD）",
    "category": "费用类型是什么？（交通/住宿/餐费/其他）",
    "amount": "金额是多少元？",
}

CATEGORY_ALIASES = {
    "住宿": "hotel",
    "酒店": "hotel",
    "住宿费": "hotel",
    "交通": "transport",
    "打车": "transport",
    "高铁": "transport",
    "机票": "transport",
    "餐费": "meal",
    "餐饮": "meal",
    "吃饭": "meal",
    "招待": "meal",
    "其他": "other",
}


class SlotUpdate(BaseModel):
    employee: str | None = None
    trip_city: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    category: Literal["transport", "hotel", "meal", "other"] | None = None
    amount: float | None = None
    invoice_no: str | None = None


def missing_slots(slots: dict) -> list[str]:
    """Return required slot names that are empty, in the order we ask for them."""
    missing = []
    for key in REQUIRED_SLOTS:
        value = slots.get(key)
        if value is None:
            missing.append(key)
        elif isinstance(value, str) and not value.strip():
            missing.append(key)
        elif key == "amount" and not value:
            missing.append(key)
    return missing


def merge_slots(current: dict, update: dict) -> dict:
    """Merge non-empty new slot values into the current slots."""
    merged = dict(current)
    for key, value in update.items():
        if value is None:
            continue
        if isinstance(value, str):
            value = value.strip()
            if not value:
                continue
        merged[key] = value
    return merged


def build_question(missing: list[str]) -> str:
    lines = [f"{index}. {SLOT_QUESTIONS[key]}" for index, key in enumerate(missing, 1)]
    return (
        "还差这几项信息：\n"
        + "\n".join(lines)
        + "\n\n可以一次发我，例如：张三，上海，2026-10-12 到 2026-10-13，住宿 800。"
    )


def _load_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return {}

    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _normalize_slots(data: dict) -> dict:
    data = dict(data)

    category = data.get("category")
    if isinstance(category, str):
        data["category"] = CATEGORY_ALIASES.get(category.strip(), category.strip())

    amount = data.get("amount")
    if isinstance(amount, str):
        cleaned = re.sub(r"[^\d.]", "", amount)
        data["amount"] = float(cleaned) if cleaned else None

    try:
        return SlotUpdate.model_validate(data).model_dump(exclude_none=True)
    except ValidationError:
        return {}


def parse_slot_json(text: str) -> dict:
    """Parse the slot extractor's JSON, tolerating code fences and nested slots."""
    data = _load_json(text)
    if isinstance(data.get("slots"), dict):
        data = data["slots"]
    return _normalize_slots(data)


def parse_turn_json(text: str) -> tuple[str, dict]:
    """Parse intent + slots from one extractor response."""
    data = _load_json(text)
    intent = str(data.get("intent", "reimburse")).strip()
    if intent not in INTENTS:
        intent = "reimburse"

    slots = data.get("slots")
    if not isinstance(slots, dict):
        slots = {key: value for key, value in data.items() if key != "intent"}

    return intent, _normalize_slots(slots)
