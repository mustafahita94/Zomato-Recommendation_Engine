"""Domain schemas for preferences, restaurants, and filter results."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class BudgetBand(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PreferenceValidationError(ValueError):
    """Raised when user preferences fail validation."""


MAX_ADDITIONAL_PREFERENCES_CHARS = 500


@dataclass(frozen=True)
class UserPreferences:
    """Validated user search preferences."""

    location: str
    budget: BudgetBand
    cuisine: str | None
    min_rating: float
    additional_preferences: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "location": self.location,
            "budget": self.budget.value,
            "cuisine": self.cuisine,
            "min_rating": self.min_rating,
            "additional_preferences": self.additional_preferences,
        }


@dataclass(frozen=True)
class RestaurantRecord:
    """One restaurant from the processed catalog."""

    id: str
    name: str
    location: str
    city: str
    cuisines: list[str]
    cost_for_two: int
    budget_band: BudgetBand
    rating: float
    votes: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["budget_band"] = self.budget_band.value
        return payload

    @classmethod
    def from_row(cls, row: dict[str, Any] | Any) -> RestaurantRecord:
        """Build a record from a pandas Series or mapping."""
        data = row.to_dict() if hasattr(row, "to_dict") else dict(row)
        raw_cuisines = data.get("cuisines", [])
        if isinstance(raw_cuisines, str):
            cuisines = [part.strip() for part in raw_cuisines.split("|") if part.strip()]
        elif isinstance(raw_cuisines, list):
            cuisines = [str(part).strip() for part in raw_cuisines if str(part).strip()]
        else:
            cuisines = []

        metadata = {
            key: data.get(key)
            for key in ("rest_type", "online_order", "book_table", "dish_liked", "listed_in_type")
            if data.get(key) not in (None, "")
        }

        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            location=str(data["location"]),
            city=str(data.get("city", "")),
            cuisines=cuisines,
            cost_for_two=int(data["cost_for_two"]),
            budget_band=BudgetBand(str(data["budget_band"]).strip().lower()),
            rating=float(data["rating"]),
            votes=int(data.get("votes") or 0),
            metadata=metadata,
        )


@dataclass(frozen=True)
class FilterResult:
    """Deterministic shortlist plus diagnostics for empty/error UX."""

    candidates: list[RestaurantRecord]
    total_matched: int
    filters_applied: list[str]
    stage_counts: dict[str, int]
    empty_message: str | None = None

    @property
    def is_empty(self) -> bool:
        return len(self.candidates) == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidates": [c.to_dict() for c in self.candidates],
            "total_matched": self.total_matched,
            "filters_applied": list(self.filters_applied),
            "stage_counts": dict(self.stage_counts),
            "empty_message": self.empty_message,
            "is_empty": self.is_empty,
        }


MAX_EXPLANATION_CHARS = 400


@dataclass(frozen=True)
class RecommendationItem:
    """One ranked restaurant ready for UI display."""

    rank: int
    name: str
    cuisine: str
    rating: float
    estimated_cost: str
    explanation: str
    restaurant_id: str | None = None
    location: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "name": self.name,
            "cuisine": self.cuisine,
            "rating": self.rating,
            "estimated_cost": self.estimated_cost,
            "explanation": self.explanation,
            "restaurant_id": self.restaurant_id,
            "location": self.location,
        }


@dataclass(frozen=True)
class RecommendationMeta:
    """Diagnostics attached to a recommendation response."""

    candidates_considered: int
    filters_applied: list[str]
    used_fallback: bool = False
    parse_success: bool = True
    latency_ms: float | None = None
    model: str | None = None
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidates_considered": self.candidates_considered,
            "filters_applied": list(self.filters_applied),
            "used_fallback": self.used_fallback,
            "parse_success": self.parse_success,
            "latency_ms": self.latency_ms,
            "model": self.model,
            "message": self.message,
        }


@dataclass(frozen=True)
class RecommendationResponse:
    """Final ranked recommendations for the UI / API."""

    summary: str | None
    recommendations: list[RecommendationItem]
    meta: RecommendationMeta
    empty_message: str | None = None

    @property
    def is_empty(self) -> bool:
        return len(self.recommendations) == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "recommendations": [item.to_dict() for item in self.recommendations],
            "meta": self.meta.to_dict(),
            "empty_message": self.empty_message,
            "is_empty": self.is_empty,
        }


def _normalize_optional_text(value: Any, *, field_name: str, max_chars: int | None = None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise PreferenceValidationError(f"{field_name} must be a string.")
    text = " ".join(value.strip().split())
    if not text:
        return None
    if max_chars is not None and len(text) > max_chars:
        text = text[:max_chars].rstrip()
    return text


def validate_preferences(
    *,
    location: Any,
    budget: Any = BudgetBand.MEDIUM,
    cuisine: Any = None,
    min_rating: Any = 0.0,
    additional_preferences: Any = None,
) -> UserPreferences:
    """
    Validate and normalize raw preference inputs.

    Rules:
    - location is required (non-empty after trim)
    - budget must be low | medium | high (default: medium if omitted via caller)
    - cuisine empty → None (any cuisine)
    - min_rating must be numeric; clamped to [0, 5]
    - additional_preferences truncated; not used as a hard filter
    """
    if location is None or (isinstance(location, str) and not location.strip()):
        raise PreferenceValidationError("Location is required.")
    if not isinstance(location, str):
        raise PreferenceValidationError("Location must be a string.")

    location_norm = " ".join(location.strip().split())
    # Title-ish normalize while preserving known all-caps tokens like BTM/HSR
    location_norm = " ".join(
        part if part.isupper() and len(part) <= 4 else part.capitalize()
        for part in location_norm.split()
    )
    # Canonical city alias
    if location_norm.casefold() in {"bengaluru", "bangalore"}:
        location_norm = "Bangalore"

    if budget is None or (isinstance(budget, str) and not budget.strip()):
        raise PreferenceValidationError("Budget is required (low, medium, or high).")
    try:
        budget_norm = BudgetBand(str(budget).strip().lower())
    except ValueError as exc:
        raise PreferenceValidationError("Budget must be one of: low, medium, high.") from exc

    cuisine_norm = _normalize_optional_text(cuisine, field_name="cuisine")
    if cuisine_norm is not None:
        cuisine_norm = " ".join(
            part if part.isupper() else part.capitalize() for part in cuisine_norm.split()
        )

    if min_rating is None or (isinstance(min_rating, str) and not str(min_rating).strip()):
        raise PreferenceValidationError("Minimum rating is required and must be a number.")
    try:
        rating_value = float(min_rating)
    except (TypeError, ValueError) as exc:
        raise PreferenceValidationError("Minimum rating must be a number.") from exc
    if rating_value != rating_value:  # NaN
        raise PreferenceValidationError("Minimum rating must be a number.")
    rating_clamped = max(0.0, min(5.0, rating_value))

    extras = _normalize_optional_text(
        additional_preferences,
        field_name="additional_preferences",
        max_chars=MAX_ADDITIONAL_PREFERENCES_CHARS,
    )

    return UserPreferences(
        location=location_norm,
        budget=budget_norm,
        cuisine=cuisine_norm,
        min_rating=rating_clamped,
        additional_preferences=extras,
    )
