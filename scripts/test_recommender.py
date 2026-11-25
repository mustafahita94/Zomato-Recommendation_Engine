"""Phase 3 checks: prompt builder, grounding, fallback, optional live Groq call."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import get_settings
from src.ingestion.load_dataset import load_processed
from src.models.schemas import validate_preferences
from src.services.filter import filter_candidates
from src.services.prompt_builder import build_recommendation_prompt
from src.services.recommender import (
    fallback_recommendations,
    ground_llm_payload,
    recommend,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_prompt_builder(preferences, candidates) -> None:
    prompt = build_recommendation_prompt(preferences, candidates, max_recommendations=5)
    _assert("candidate" in prompt.system.casefold() or "ONLY" in prompt.system, "system prompt weak")
    _assert(preferences.location in prompt.user, "preferences missing from user prompt")
    _assert(candidates[0].name in prompt.user, "candidate name missing from prompt")
    # Must be valid JSON embed (special chars handled)
    _assert('"recommendations"' in prompt.system or "recommendations" in prompt.system.casefold(), "schema missing")
    messages = prompt.as_messages()
    _assert(messages[0]["role"] == "system" and messages[1]["role"] == "user", "message roles wrong")
    # Free-text must not leak into system role
    if preferences.additional_preferences:
        _assert(
            preferences.additional_preferences not in prompt.system,
            "free-text must stay out of system prompt",
        )
        _assert(preferences.additional_preferences in prompt.user, "free-text should be in user prompt")
    print(f"prompt builder: candidates={prompt.candidate_count} max_recs={prompt.max_recommendations}")


def test_grounding_rejects_invented(preferences, candidates) -> None:
    payload = {
        "summary": "A mixed shortlist.",
        "recommendations": [
            {"rank": 1, "name": candidates[0].name, "explanation": "Fits budget and cuisine."},
            {"rank": 2, "name": "Totally Fake Bistro XYZ", "explanation": "Invented place."},
            {"rank": 3, "name": candidates[0].name, "explanation": "Duplicate should drop."},
        ],
    }
    summary, items, rejected = ground_llm_payload(
        payload,
        candidates,
        preferences,
        max_recommendations=5,
    )
    _assert(summary is not None, "summary should pass through")
    _assert(len(items) == 1, "only one grounded unique name expected")
    _assert(items[0].name == candidates[0].name, "name should match store")
    _assert(items[0].rating == candidates[0].rating, "rating must come from store")
    _assert(rejected >= 2, "invented + duplicate should be rejected")
    _assert("₹" in items[0].estimated_cost, "cost display should use rupee format")
    print(f"grounding: kept={len(items)} rejected={rejected}")


def test_fallback_without_llm(preferences, candidates) -> None:
    response = fallback_recommendations(
        preferences,
        candidates,
        max_recommendations=3,
        filters_applied=["location", "cuisine", "budget", "min_rating"],
        message="test fallback",
    )
    _assert(response.meta.used_fallback is True, "fallback flag missing")
    _assert(len(response.recommendations) == min(3, len(candidates)), "fallback length wrong")
    _assert(response.recommendations[0].rank == 1, "ranks should start at 1")
    _assert(all(r.explanation for r in response.recommendations), "explanations required")
    # Ratings should be non-increasing (candidates already sorted)
    ratings = [r.rating for r in response.recommendations]
    _assert(ratings == sorted(ratings, reverse=True), "fallback should preserve rating order")
    print(f"fallback: n={len(response.recommendations)} summary={response.summary}")


def test_recommend_forces_fallback(preferences, candidates) -> None:
    response = recommend(preferences, candidates, max_recommendations=3, use_llm=False)
    _assert(response.meta.used_fallback is True, "use_llm=False should fallback")
    _assert(not response.is_empty, "expected non-empty fallback")
    print(f"recommend(use_llm=False): n={len(response.recommendations)}")


def test_empty_candidates(preferences) -> None:
    response = recommend(preferences, [], use_llm=False)
    _assert(response.is_empty, "empty candidates → empty response")
    _assert(response.empty_message is not None, "empty_message required")
    print(f"empty: message={response.empty_message}")


def test_live_groq(preferences, candidates) -> None:
    settings = get_settings()
    if not settings.llm_api_key or settings.llm_api_key.startswith("your_"):
        print("live Groq: SKIPPED (set LLM_API_KEY in .env to exercise the real call)")
        return

    response = recommend(preferences, candidates, max_recommendations=3, use_llm=True)
    _assert(not response.is_empty, "live Groq should return recommendations or fallback items")
    candidate_names = {_normalize(c.name) for c in candidates}
    for item in response.recommendations:
        _assert(_normalize(item.name) in candidate_names, f"ungrounded name slipped through: {item.name}")
        _assert(item.explanation, "explanation required")

    print(
        json.dumps(
            {
                "used_fallback": response.meta.used_fallback,
                "parse_success": response.meta.parse_success,
                "latency_ms": response.meta.latency_ms,
                "model": response.meta.model,
                "summary": response.summary,
                "recommendations": [r.to_dict() for r in response.recommendations],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if response.meta.used_fallback:
        print("live Groq: call fell back (check key/model/network); fallback path still OK")
    else:
        print("live Groq: ranked recommendations OK")


def _normalize(name: str) -> str:
    return " ".join(name.casefold().split())


def main() -> None:
    catalog = load_processed()
    preferences = validate_preferences(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        additional_preferences="family-friendly, quick service",
    )
    filtered = filter_candidates(preferences, catalog=catalog, limit=15)
    _assert(not filtered.is_empty, "need a non-empty shortlist for Phase 3 tests")
    candidates = filtered.candidates
    print(
        f"shortlist: returned={len(candidates)} matched={filtered.total_matched} "
        f"stages={filtered.stage_counts}"
    )

    test_prompt_builder(preferences, candidates)
    test_grounding_rejects_invented(preferences, candidates)
    test_fallback_without_llm(preferences, candidates)
    test_recommend_forces_fallback(preferences, candidates)
    test_empty_candidates(preferences)
    test_live_groq(preferences, candidates)

    settings = get_settings()
    print(
        f"\nconfig: model={settings.llm_model} base_url={settings.llm_base_url} "
        f"key_set={bool(settings.llm_api_key and not settings.llm_api_key.startswith('your_'))}"
    )
    print("All Phase 3 recommender checks passed.")


if __name__ == "__main__":
    main()
