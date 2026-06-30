"""PSPS scoring: weighted sum of yes/no answers, normalised to 0-100."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Item:
    id: str
    question: str
    weight: int
    threat_refs: list[str]
    recommendation: str
    cost_eur: int
    effort_hours: int


@dataclass
class Answer:
    item_id: str
    yes: bool


def psps(items: list[Item], answers: dict[str, bool]) -> float:
    total = sum(i.weight for i in items)
    if total == 0:
        return 0.0
    got = sum(i.weight for i in items if answers.get(i.id, False))
    return round(100 * got / total, 1)


def gaps(items: list[Item], answers: dict[str, bool]) -> list[Item]:
    """Items answered 'no', sorted by weight desc — priority order."""
    missing = [i for i in items if not answers.get(i.id, False)]
    return sorted(missing, key=lambda i: i.weight, reverse=True)
