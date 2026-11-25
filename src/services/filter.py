"""Deterministic candidate filter: preferences → shortlist."""

from __future__ import annotations

import re
from typing import Iterable

import pandas as pd

from src.config import get_settings
from src.ingestion.load_dataset import CITY_ALIASES, load_processed
from src.models.schemas import FilterResult, RestaurantRecord, UserPreferences

DEFAULT_CANDIDATE_LIMIT = 20


def _normalize_key(value: str) -> str:
    return " ".join(value.casefold().split())


def _location_aliases(location: str) -> set[str]:
    key = _normalize_key(location)
    aliases = {key}
    if key in CITY_ALIASES:
        aliases.add(_normalize_key(CITY_ALIASES[key]))
    for alias, canonical in CITY_ALIASES.items():
        if _normalize_key(canonical) == key:
            aliases.add(alias)
    return aliases


def _location_match_mask(frame: pd.DataFrame, location: str) -> pd.Series:
    """
    Match city or neighborhood.

    Rules (case-insensitive):
    1. Exact match on city or location
    2. Alias match (Bangalore ↔ Bengaluru) on city
    3. Contains match either way (e.g. "Koramangala" vs "Koramangala 5th Block")
    """
    aliases = _location_aliases(location)
    city_key = frame["city"].fillna("").map(_normalize_key)
    loc_key = frame["location"].fillna("").map(_normalize_key)

    exact = city_key.isin(aliases) | loc_key.isin(aliases)

    # Contains: user query in field, or field in user query (for short aliases like HSR)
    contains = pd.Series(False, index=frame.index)
    for alias in aliases:
        if not alias:
            continue
        contains = contains | city_key.str.contains(re.escape(alias), regex=True, na=False)
        contains = contains | loc_key.str.contains(re.escape(alias), regex=True, na=False)
        contains = contains | loc_key.map(lambda value, a=alias: bool(value) and a.find(value) >= 0 and len(value) >= 3)

    return exact | contains


def _cuisine_tokens(value: str) -> list[str]:
    return [tok for tok in re.split(r"[,|/]+", value) if tok.strip()]


def _cuisine_match_mask(frame: pd.DataFrame, cuisine: str) -> pd.Series:
    """
    Token match against pipe-separated cuisines (case-insensitive).

    A restaurant matches if any of its cuisine tokens equals the preference
    or contains the preference as a whole-token/phrase (e.g. "Indian" in
    "North Indian"). Preference free-text is NOT applied here.
    """
    wanted = {_normalize_key(tok) for tok in _cuisine_tokens(cuisine)}
    wanted.discard("")
    if not wanted:
        return pd.Series(True, index=frame.index)

    def row_matches(raw: object) -> bool:
        if raw is None or (isinstance(raw, float) and pd.isna(raw)):
            return False
        tokens = [_normalize_key(tok) for tok in str(raw).split("|") if tok.strip()]
        for token in tokens:
            for needle in wanted:
                if token == needle or needle in token or token in needle:
                    return True
        return False

    return frame["cuisines"].map(row_matches)


def _empty_message(stage_counts: dict[str, int], preferences: UserPreferences) -> str:
    """Build a user-facing hint when the shortlist is empty."""
    if stage_counts.get("location", 0) == 0:
        return (
            f"No restaurants found for location '{preferences.location}'. "
            "Try a Bangalore neighborhood (e.g. Indiranagar, HSR) or 'Bangalore'."
        )
    if preferences.cuisine and stage_counts.get("cuisine", 0) == 0:
        return (
            f"No '{preferences.cuisine}' matches in '{preferences.location}'. "
            "Try clearing cuisine or picking a broader style."
        )
    if stage_counts.get("budget", 0) == 0:
        return (
            f"No restaurants in the '{preferences.budget.value}' budget band "
            f"for your other filters. Try an adjacent budget."
        )
    if stage_counts.get("rating", 0) == 0:
        return (
            f"No restaurants rated {preferences.min_rating}+ with your filters. "
            "Try lowering the minimum rating."
        )
    return "No restaurants matched your filters. Try relaxing cuisine, budget, or rating."


def filter_candidates(
    preferences: UserPreferences,
    catalog: pd.DataFrame | None = None,
    *,
    limit: int | None = None,
) -> FilterResult:
    """
    Apply the deterministic filter pipeline and return a capped shortlist.

    Pipeline order:
    1. location
    2. cuisine (skipped when cuisine is None)
    3. budget band
    4. rating >= min_rating
    5. sort rating desc, votes desc, name asc
    6. truncate to top N
    """
    frame = load_processed() if catalog is None else catalog.copy()
    if limit is None:
        limit = get_settings().candidate_limit or DEFAULT_CANDIDATE_LIMIT
    limit = max(1, int(limit))

    filters_applied: list[str] = []
    stage_counts: dict[str, int] = {"catalog": len(frame)}

    # 1. Location
    filtered = frame.loc[_location_match_mask(frame, preferences.location)].copy()
    filters_applied.append("location")
    stage_counts["location"] = len(filtered)

    # 2. Cuisine (optional)
    if preferences.cuisine:
        filtered = filtered.loc[_cuisine_match_mask(filtered, preferences.cuisine)].copy()
        filters_applied.append("cuisine")
        stage_counts["cuisine"] = len(filtered)
    else:
        stage_counts["cuisine"] = len(filtered)

    # 3. Budget band
    budget_value = preferences.budget.value
    filtered = filtered.loc[filtered["budget_band"].astype(str).str.lower() == budget_value].copy()
    filters_applied.append("budget")
    stage_counts["budget"] = len(filtered)

    # 4. Min rating
    filtered = filtered.loc[filtered["rating"] >= preferences.min_rating].copy()
    filters_applied.append("min_rating")
    stage_counts["rating"] = len(filtered)

    total_matched = len(filtered)

    if total_matched == 0:
        return FilterResult(
            candidates=[],
            total_matched=0,
            filters_applied=filters_applied,
            stage_counts=stage_counts,
            empty_message=_empty_message(stage_counts, preferences),
        )

    # 5. Sort (stable secondary keys for ties)
    filtered = filtered.sort_values(
        by=["rating", "votes", "name"],
        ascending=[False, False, True],
        kind="mergesort",
    )

    # 6. Truncate
    shortlist = filtered.head(limit)
    candidates = [RestaurantRecord.from_row(row) for _, row in shortlist.iterrows()]

    return FilterResult(
        candidates=candidates,
        total_matched=total_matched,
        filters_applied=filters_applied,
        stage_counts=stage_counts,
        empty_message=None,
    )


def filter_from_raw(
    *,
    location: str,
    budget: str = "medium",
    cuisine: str | None = None,
    min_rating: float = 0.0,
    additional_preferences: str | None = None,
    catalog: pd.DataFrame | None = None,
    limit: int | None = None,
) -> FilterResult:
    """Validate raw inputs then filter. Convenience for scripts/UI."""
    from src.models.schemas import validate_preferences

    preferences = validate_preferences(
        location=location,
        budget=budget,
        cuisine=cuisine,
        min_rating=min_rating,
        additional_preferences=additional_preferences,
    )
    return filter_candidates(preferences, catalog=catalog, limit=limit)


def records_as_dicts(records: Iterable[RestaurantRecord]) -> list[dict]:
    return [record.to_dict() for record in records]
