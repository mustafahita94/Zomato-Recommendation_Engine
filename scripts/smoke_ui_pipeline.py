"""Smoke-test the same pipeline the FastAPI /recommend endpoint calls."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.load_dataset import load_processed
from src.models.schemas import validate_preferences
from src.services.filter import filter_candidates
from src.services.recommender import recommend_from_filter


def main() -> None:
    catalog = load_processed()
    prefs = validate_preferences(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        additional_preferences="family-friendly",
    )
    filtered = filter_candidates(prefs, catalog=catalog)
    response = recommend_from_filter(prefs, filtered, max_recommendations=3)
    print(
        f"empty={response.is_empty} n={len(response.recommendations)} "
        f"fallback={response.meta.used_fallback} latency={response.meta.latency_ms}"
    )
    for item in response.recommendations:
        print(f"{item.rank}. {item.name} | {item.cuisine} | {item.rating} | {item.estimated_cost}")
        print(f"   {item.explanation}")


if __name__ == "__main__":
    main()
