"""Unit-style checks for preference validation and candidate filtering."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.load_dataset import load_processed
from src.models.schemas import PreferenceValidationError, validate_preferences
from src.services.filter import filter_candidates, filter_from_raw


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_validation() -> None:
    prefs = validate_preferences(
        location="  bangalore ",
        budget="MEDIUM",
        cuisine="north indian",
        min_rating=4.2,
        additional_preferences="family-friendly",
    )
    _assert(prefs.location == "Bangalore", "location alias/case normalize failed")
    _assert(prefs.budget.value == "medium", "budget normalize failed")
    _assert(prefs.cuisine is not None and "North" in prefs.cuisine, "cuisine normalize failed")
    _assert(prefs.min_rating == 4.2, "min_rating parse failed")

    clamped = validate_preferences(location="HSR", budget="low", min_rating=9)
    _assert(clamped.min_rating == 5.0, "min_rating should clamp to 5")

    empty_cuisine = validate_preferences(location="HSR", budget="low", cuisine="  ")
    _assert(empty_cuisine.cuisine is None, "blank cuisine should become None")

    try:
        validate_preferences(location="   ", budget="low")
        raise AssertionError("empty location should raise")
    except PreferenceValidationError:
        pass

    try:
        validate_preferences(location="HSR", budget="luxury")
        raise AssertionError("invalid budget should raise")
    except PreferenceValidationError:
        pass

    try:
        validate_preferences(location="HSR", budget="low", min_rating="abc")
        raise AssertionError("non-numeric rating should raise")
    except PreferenceValidationError:
        pass

    print("validation checks passed")


def test_happy_path(catalog) -> None:
    result = filter_from_raw(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        additional_preferences="family-friendly, quick service",
        catalog=catalog,
        limit=20,
    )
    _assert(not result.is_empty, "expected Italian medium Bangalore matches")
    _assert(len(result.candidates) <= 20, "shortlist must be capped at 20")
    _assert(result.total_matched >= len(result.candidates), "total_matched should be >= returned")
    _assert(result.empty_message is None, "happy path should not set empty_message")
    # additional_preferences must not act as a hard filter
    _assert("additional_preferences" not in result.filters_applied, "free text must not be a hard filter")

    ratings = [c.rating for c in result.candidates]
    _assert(ratings == sorted(ratings, reverse=True), "candidates must be sorted by rating desc")
    _assert(all(c.budget_band.value == "medium" for c in result.candidates), "budget filter failed")
    _assert(all(c.rating >= 4.0 for c in result.candidates), "rating filter failed")
    _assert(
        all(any("italian" in tok.casefold() for tok in c.cuisines) for c in result.candidates),
        "cuisine token filter failed",
    )

    print(
        f"happy path: returned={len(result.candidates)} "
        f"matched={result.total_matched} stages={result.stage_counts}"
    )
    print("sample shortlist:")
    for candidate in result.candidates[:5]:
        print(
            f"  {candidate.rating:.1f} | {candidate.name} | "
            f"{', '.join(candidate.cuisines[:3])} | ₹{candidate.cost_for_two}"
        )


def test_no_matches(catalog) -> None:
    result = filter_from_raw(
        location="Atlantis",
        budget="high",
        cuisine="Martian",
        min_rating=4.5,
        catalog=catalog,
        limit=20,
    )
    _assert(result.is_empty, "Atlantis should yield empty shortlist")
    _assert(result.empty_message is not None and "Atlantis" in result.empty_message, "empty message missing")
    _assert(result.stage_counts.get("location", -1) == 0, "location stage should be zero")
    print(f"no matches: message={result.empty_message}")


def test_overly_strict(catalog) -> None:
    result = filter_from_raw(
        location="Bangalore",
        budget="low",
        cuisine="Italian",
        min_rating=4.9,
        catalog=catalog,
        limit=20,
    )
    # May be empty or tiny; must be detectable either way
    if result.is_empty:
        _assert(result.empty_message is not None, "strict empty needs message")
        print(f"overly strict: empty → {result.empty_message}")
    else:
        _assert(len(result.candidates) <= 20, "still capped")
        print(f"overly strict: matched={result.total_matched}")


def test_partial_and_cap(catalog) -> None:
    # Broad query that would match many rows without truncation
    result = filter_from_raw(
        location="Bangalore",
        budget="medium",
        cuisine=None,
        min_rating=0,
        catalog=catalog,
        limit=15,
    )
    _assert(result.total_matched > 15, "expected large match set before cap")
    _assert(len(result.candidates) == 15, "must truncate to limit")
    print(f"partial/cap: matched={result.total_matched} returned={len(result.candidates)}")

    # Neighborhood-only match
    hsr = filter_from_raw(location="HSR", budget="medium", min_rating=3.5, catalog=catalog, limit=10)
    _assert(not hsr.is_empty, "HSR should have matches")
    _assert(all("hsr" in c.location.casefold() for c in hsr.candidates), "HSR location match failed")
    print(f"neighborhood HSR: returned={len(hsr.candidates)}")


def test_stable_shortlist(catalog) -> None:
    prefs = validate_preferences(location="Indiranagar", budget="high", cuisine="North Indian", min_rating=4.0)
    first = filter_candidates(prefs, catalog=catalog, limit=10)
    second = filter_candidates(prefs, catalog=catalog, limit=10)
    ids_first = [c.id for c in first.candidates]
    ids_second = [c.id for c in second.candidates]
    _assert(ids_first == ids_second, "shortlist must be stable across runs")
    print(f"stable shortlist: {len(ids_first)} ids identical across runs")


def main() -> None:
    catalog = load_processed()
    print(f"catalog rows: {len(catalog)}")
    test_validation()
    test_happy_path(catalog)
    test_no_matches(catalog)
    test_overly_strict(catalog)
    test_partial_and_cap(catalog)
    test_stable_shortlist(catalog)
    print("\nAll Phase 2 filter checks passed.")


if __name__ == "__main__":
    main()
