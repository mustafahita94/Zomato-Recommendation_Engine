"""Build grounded LLM prompts from preferences + candidate shortlist."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config import get_settings
from src.models.schemas import RestaurantRecord, UserPreferences

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"
SYSTEM_TEMPLATE_PATH = PROMPTS_DIR / "recommend_system.txt"
USER_TEMPLATE_PATH = PROMPTS_DIR / "recommend_user.txt"

# Cap metadata strings in the prompt to control tokens.
_MAX_META_CHARS = 120


@dataclass(frozen=True)
class PromptBundle:
    """Messages ready for an OpenAI-compatible chat completion call."""

    system: str
    user: str
    max_recommendations: int
    candidate_count: int

    def as_messages(self) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": self.system},
            {"role": "user", "content": self.user},
        ]


def _load_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    return path.read_text(encoding="utf-8")


def _truncate(value: Any, max_chars: int = _MAX_META_CHARS) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).split())
    if not text:
        return None
    if len(text) > max_chars:
        return text[: max_chars - 1].rstrip() + "…"
    return text


def candidate_to_prompt_dict(record: RestaurantRecord) -> dict[str, Any]:
    """Serialize a restaurant with only ranking-relevant fields."""
    payload: dict[str, Any] = {
        "id": record.id,
        "name": record.name,
        "location": record.location,
        "city": record.city,
        "cuisines": list(record.cuisines),
        "cost_for_two": record.cost_for_two,
        "budget_band": record.budget_band.value,
        "rating": record.rating,
        "votes": record.votes,
    }
    meta = record.metadata or {}
    for key in ("rest_type", "dish_liked", "listed_in_type", "online_order", "book_table"):
        truncated = _truncate(meta.get(key))
        if truncated:
            payload[key] = truncated
    return payload


def _render(template: str, **replacements: str) -> str:
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def build_recommendation_prompt(
    preferences: UserPreferences,
    candidates: list[RestaurantRecord],
    *,
    max_recommendations: int | None = None,
) -> PromptBundle:
    """
    Build system + user messages for ranking/explaining filtered candidates.

    Preferences free-text is included only in the user message (never in system).
    Candidate payload is JSON-serialized to avoid quote/special-char breakage.
    """
    if not candidates:
        raise ValueError("Cannot build a recommendation prompt with an empty candidate list.")

    settings = get_settings()
    limit = max_recommendations if max_recommendations is not None else settings.llm_max_recommendations
    limit = max(1, min(int(limit), len(candidates)))

    system_template = _load_template(SYSTEM_TEMPLATE_PATH)
    user_template = _load_template(USER_TEMPLATE_PATH)

    preferences_json = json.dumps(preferences.to_dict(), ensure_ascii=False, indent=2)
    candidates_json = json.dumps(
        [candidate_to_prompt_dict(c) for c in candidates],
        ensure_ascii=False,
        indent=2,
    )

    system = _render(system_template, max_recommendations=str(limit))
    user = _render(
        user_template,
        preferences_json=preferences_json,
        candidates_json=candidates_json,
    )

    return PromptBundle(
        system=system,
        user=user,
        max_recommendations=limit,
        candidate_count=len(candidates),
    )
