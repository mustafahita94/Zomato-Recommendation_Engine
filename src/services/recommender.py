"""LLM recommendation engine (Groq) with deterministic fallback."""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from openai import OpenAI

from src.config import get_settings
from src.models.schemas import (
    MAX_EXPLANATION_CHARS,
    FilterResult,
    RecommendationItem,
    RecommendationMeta,
    RecommendationResponse,
    RestaurantRecord,
    UserPreferences,
)
from src.services.prompt_builder import PromptBundle, build_recommendation_prompt

logger = logging.getLogger(__name__)

STRICT_RETRY_SUFFIX = (
    "\n\nIMPORTANT: Your previous response was invalid. "
    "Reply with ONLY a single JSON object matching the required schema. "
    "No markdown, no prose outside JSON."
)


def format_estimated_cost(cost_for_two: int) -> str:
    return f"₹{cost_for_two:,} for two"


def _cuisine_display(record: RestaurantRecord) -> str:
    return ", ".join(record.cuisines) if record.cuisines else "Various"


def _normalize_name(name: str) -> str:
    return " ".join(name.casefold().split())


def _truncate_explanation(text: str | None, preferences: UserPreferences, record: RestaurantRecord) -> str:
    if text:
        cleaned = " ".join(str(text).split())
        if cleaned:
            if len(cleaned) > MAX_EXPLANATION_CHARS:
                return cleaned[: MAX_EXPLANATION_CHARS - 1].rstrip() + "…"
            return cleaned
    return _generic_explanation(preferences, record)


def _generic_explanation(preferences: UserPreferences, record: RestaurantRecord) -> str:
    parts = [
        f"Strong match in {record.location}",
        f"rated {record.rating:.1f}",
        f"in the {preferences.budget.value} budget band",
    ]
    if preferences.cuisine:
        parts.append(f"with {preferences.cuisine} options")
    if preferences.additional_preferences:
        parts.append(f"aligned with: {preferences.additional_preferences}")
    return "; ".join(parts) + "."


def _build_candidate_index(
    candidates: list[RestaurantRecord],
) -> dict[str, RestaurantRecord]:
    """Map normalized name → first matching record (stable)."""
    index: dict[str, RestaurantRecord] = {}
    for record in candidates:
        key = _normalize_name(record.name)
        if key not in index:
            index[key] = record
    return index


def _extract_json_object(raw: str) -> dict[str, Any]:
    """Parse JSON from a model response, tolerating optional markdown fences."""
    text = raw.strip()
    if not text:
        raise ValueError("Empty LLM response.")

    # Strip ```json ... ``` fences if present
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, flags=re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        # Fallback: take the outermost {...} span
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("LLM response did not contain a JSON object.")
        payload = json.loads(text[start : end + 1])

    if not isinstance(payload, dict):
        raise ValueError("LLM JSON root must be an object.")
    return payload


def _item_from_store(
    rank: int,
    record: RestaurantRecord,
    explanation: str | None,
    preferences: UserPreferences,
) -> RecommendationItem:
    return RecommendationItem(
        rank=rank,
        name=record.name,
        cuisine=_cuisine_display(record),
        rating=record.rating,
        estimated_cost=format_estimated_cost(record.cost_for_two),
        explanation=_truncate_explanation(explanation, preferences, record),
        restaurant_id=record.id,
        location=record.location,
    )


def ground_llm_payload(
    payload: dict[str, Any],
    candidates: list[RestaurantRecord],
    preferences: UserPreferences,
    *,
    max_recommendations: int,
) -> tuple[str | None, list[RecommendationItem], int]:
    """
    Validate LLM names against candidates and overlay store facts.

    Returns (summary, items, rejected_count).
    """
    index = _build_candidate_index(candidates)
    raw_recs = payload.get("recommendations")
    if not isinstance(raw_recs, list):
        raise ValueError("LLM JSON missing recommendations array.")

    summary = payload.get("summary")
    summary_text = " ".join(str(summary).split()) if summary else None
    if summary_text == "":
        summary_text = None

    items: list[RecommendationItem] = []
    seen_ids: set[str] = set()
    rejected = 0

    for entry in raw_recs:
        if len(items) >= max_recommendations:
            break
        if not isinstance(entry, dict):
            rejected += 1
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            rejected += 1
            continue
        record = index.get(_normalize_name(name))
        if record is None:
            logger.info("Rejected invented/unknown restaurant name from LLM: %r", name)
            rejected += 1
            continue
        if record.id in seen_ids:
            rejected += 1
            continue
        seen_ids.add(record.id)
        items.append(
            _item_from_store(
                rank=len(items) + 1,
                record=record,
                explanation=entry.get("explanation") if isinstance(entry.get("explanation"), str) else None,
                preferences=preferences,
            )
        )

    return summary_text, items, rejected


def fallback_recommendations(
    preferences: UserPreferences,
    candidates: list[RestaurantRecord],
    *,
    max_recommendations: int | None = None,
    filters_applied: list[str] | None = None,
    latency_ms: float | None = None,
    message: str | None = None,
    model: str | None = None,
    parse_success: bool = False,
) -> RecommendationResponse:
    """Deterministic top-N by rating when LLM is unavailable or unusable."""
    settings = get_settings()
    limit = max_recommendations if max_recommendations is not None else settings.llm_max_recommendations
    limit = max(1, int(limit))
    top = candidates[:limit]

    items = [
        _item_from_store(
            rank=i + 1,
            record=record,
            explanation=None,
            preferences=preferences,
        )
        for i, record in enumerate(top)
    ]

    summary = (
        f"Showing top {len(items)} restaurants by rating for {preferences.location} "
        f"({preferences.budget.value} budget)."
        if items
        else None
    )

    return RecommendationResponse(
        summary=summary,
        recommendations=items,
        meta=RecommendationMeta(
            candidates_considered=len(candidates),
            filters_applied=list(filters_applied or []),
            used_fallback=True,
            parse_success=parse_success,
            latency_ms=latency_ms,
            model=model,
            message=message or "Used rating-based fallback ranking.",
        ),
    )


def _call_groq(messages: list[dict[str, str]], *, temperature: float | None = None) -> str:
    settings = get_settings()
    if not settings.llm_api_key or settings.llm_api_key.startswith("your_"):
        raise RuntimeError(
            "LLM_API_KEY is missing. Set your Groq API key in .env "
            "(https://console.groq.com/keys)."
        )

    client = OpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )
    temp = settings.llm_temperature if temperature is None else temperature
    create_kwargs: dict[str, Any] = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": temp,
        "response_format": {"type": "json_object"},
    }
    try:
        response = client.chat.completions.create(**create_kwargs)
    except Exception as exc:  # noqa: BLE001
        # Some Groq models reject response_format; retry once without it.
        if "response_format" in str(exc).casefold() or "json_object" in str(exc).casefold():
            logger.info("Groq rejected response_format; retrying without it")
            create_kwargs.pop("response_format", None)
            response = client.chat.completions.create(**create_kwargs)
        else:
            raise
    content = response.choices[0].message.content
    if not content:
        raise ValueError("LLM returned empty content.")
    return content


def _recommend_via_llm(
    preferences: UserPreferences,
    candidates: list[RestaurantRecord],
    *,
    prompt: PromptBundle,
    filters_applied: list[str],
) -> RecommendationResponse:
    settings = get_settings()
    started = time.perf_counter()
    messages = prompt.as_messages()
    raw: str | None = None
    last_error: Exception | None = None

    for attempt in range(2):
        try:
            attempt_messages = messages
            if attempt == 1:
                attempt_messages = [
                    messages[0],
                    {"role": "user", "content": messages[1]["content"] + STRICT_RETRY_SUFFIX},
                ]
            raw = _call_groq(attempt_messages)
            payload = _extract_json_object(raw)
            summary, items, rejected = ground_llm_payload(
                payload,
                candidates,
                preferences,
                max_recommendations=prompt.max_recommendations,
            )
            latency_ms = (time.perf_counter() - started) * 1000

            if not items:
                logger.warning(
                    "LLM parse yielded zero grounded items (rejected=%s); falling back",
                    rejected,
                )
                return fallback_recommendations(
                    preferences,
                    candidates,
                    max_recommendations=prompt.max_recommendations,
                    filters_applied=filters_applied,
                    latency_ms=latency_ms,
                    message="LLM returned no restaurants matching the candidate list; used fallback.",
                    model=settings.llm_model,
                    parse_success=False,
                )

            # Top up with rating-based picks if the model returned a partial valid list
            if len(items) < min(prompt.max_recommendations, len(candidates)):
                used_ids = {item.restaurant_id for item in items if item.restaurant_id}
                for record in candidates:
                    if len(items) >= prompt.max_recommendations:
                        break
                    if record.id in used_ids:
                        continue
                    items.append(
                        _item_from_store(
                            rank=len(items) + 1,
                            record=record,
                            explanation=None,
                            preferences=preferences,
                        )
                    )

            logger.info(
                "LLM recommend ok: candidates=%s returned=%s rejected=%s latency_ms=%.1f model=%s",
                len(candidates),
                len(items),
                rejected,
                latency_ms,
                settings.llm_model,
            )
            return RecommendationResponse(
                summary=summary,
                recommendations=items,
                meta=RecommendationMeta(
                    candidates_considered=len(candidates),
                    filters_applied=list(filters_applied),
                    used_fallback=False,
                    parse_success=True,
                    latency_ms=latency_ms,
                    model=settings.llm_model,
                    message=None,
                ),
            )
        except Exception as exc:  # noqa: BLE001 — convert any provider/parse failure to fallback
            last_error = exc
            logger.warning("LLM attempt %s failed: %s", attempt + 1, exc)

    latency_ms = (time.perf_counter() - started) * 1000
    logger.error(
        "LLM recommend failed after retries: candidates=%s latency_ms=%.1f error=%s",
        len(candidates),
        latency_ms,
        last_error,
    )
    return fallback_recommendations(
        preferences,
        candidates,
        max_recommendations=prompt.max_recommendations,
        filters_applied=filters_applied,
        latency_ms=latency_ms,
        message=f"LLM unavailable ({last_error}); showing rating-based picks.",
        model=settings.llm_model,
        parse_success=False,
    )


def recommend(
    preferences: UserPreferences,
    candidates: list[RestaurantRecord] | FilterResult,
    *,
    max_recommendations: int | None = None,
    use_llm: bool = True,
) -> RecommendationResponse:
    """
    Rank and explain candidates via Groq; fall back to rating sort on failure.

    Accepts either a candidate list or a FilterResult. Empty shortlists return
    an empty RecommendationResponse with the filter empty_message when available.
    """
    filters_applied: list[str] = []
    empty_message: str | None = None

    if isinstance(candidates, FilterResult):
        filters_applied = list(candidates.filters_applied)
        empty_message = candidates.empty_message
        candidate_list = list(candidates.candidates)
    else:
        candidate_list = list(candidates)

    if not candidate_list:
        return RecommendationResponse(
            summary=None,
            recommendations=[],
            meta=RecommendationMeta(
                candidates_considered=0,
                filters_applied=filters_applied,
                used_fallback=False,
                parse_success=True,
                message="No candidates to recommend.",
            ),
            empty_message=empty_message or "No restaurants matched your filters.",
        )

    settings = get_settings()
    prompt = build_recommendation_prompt(
        preferences,
        candidate_list,
        max_recommendations=max_recommendations,
    )

    if not use_llm:
        return fallback_recommendations(
            preferences,
            candidate_list,
            max_recommendations=prompt.max_recommendations,
            filters_applied=filters_applied,
            message="LLM disabled; showing rating-based picks.",
            model=settings.llm_model,
            parse_success=True,
        )

    return _recommend_via_llm(
        preferences,
        candidate_list,
        prompt=prompt,
        filters_applied=filters_applied,
    )


def recommend_from_filter(
    preferences: UserPreferences,
    filter_result: FilterResult,
    *,
    max_recommendations: int | None = None,
    use_llm: bool = True,
) -> RecommendationResponse:
    """Convenience wrapper around recommend() for FilterResult inputs."""
    return recommend(
        preferences,
        filter_result,
        max_recommendations=max_recommendations,
        use_llm=use_llm,
    )
