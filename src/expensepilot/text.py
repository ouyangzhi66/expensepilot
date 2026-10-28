"""Clause-level splitting for policy documents."""

from __future__ import annotations

import re

_SENTENCE_RE = re.compile(r"(?<=[。；！？])")


def split_clauses(text: str, max_chars: int = 180) -> list[str]:
    """Split policy text into clause-sized chunks, keeping sentence boundaries."""
    text = text.strip()
    if not text:
        return []

    sentences = [part.strip() for part in _SENTENCE_RE.split(text) if part.strip()]
    chunks: list[str] = []
    buffer = ""
    for sentence in sentences:
        if buffer and len(buffer) + len(sentence) > max_chars:
            chunks.append(buffer)
            buffer = sentence
        else:
            buffer += sentence
    if buffer:
        chunks.append(buffer)
    return chunks
