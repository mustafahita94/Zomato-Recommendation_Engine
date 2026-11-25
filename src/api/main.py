"""FastAPI app: preferences → filter → Groq recommendations."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.config import get_settings
from src.ingestion.load_dataset import (
    DEFAULT_PROCESSED_CSV,
    DEFAULT_PROCESSED_PARQUET,
    load_processed,
)
from src.models.schemas import PreferenceValidationError, validate_preferences
from src.services.filter import filter_candidates
from src.services.recommender import recommend_from_filter

ANY_CUISINE = "Any cuisine"

# In-memory catalog cache (loaded once at startup).
_catalog: pd.DataFrame | None = None
_locations: list[str] = []
_cuisines: list[str] = []


def _api_key_configured(api_key: str) -> bool:
    return bool(api_key) and not api_key.startswith("your_")


def _short_model_name(model: str) -> str:
    return model.split("/")[-1] if model else "—"


def _build_locations(catalog: pd.DataFrame) -> list[str]:
    neighborhoods = sorted(
        {
            str(value).strip()
            for value in catalog["location"].dropna().tolist()
            if str(value).strip()
        },
        key=lambda value: value.casefold(),
    )
    ordered: list[str] = ["Bangalore"]
    ordered.extend(loc for loc in neighborhoods if loc.casefold() != "bangalore")
    return ordered


def _build_cuisines(catalog: pd.DataFrame) -> list[str]:
    cuisines: set[str] = set()
    for raw in catalog["cuisines"].dropna().astype(str):
        for part in raw.split("|"):
            token = part.strip()
            if token:
                cuisines.add(token)
    return [ANY_CUISINE] + sorted(cuisines, key=lambda value: value.casefold())


def _load_catalog() -> pd.DataFrame:
    if not DEFAULT_PROCESSED_PARQUET.exists() and not DEFAULT_PROCESSED_CSV.exists():
        raise FileNotFoundError(
            "Processed restaurant catalog not found. "
            "Run `python -m src.ingestion.load_dataset` first."
        )
    return load_processed()


def _ensure_catalog() -> pd.DataFrame:
    """Return cached catalog, loading it on first use if needed."""
    global _catalog, _locations, _cuisines
    if _catalog is None:
        _catalog = _load_catalog()
        _locations = _build_locations(_catalog)
        _cuisines = _build_cuisines(_catalog)
    return _catalog


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        _ensure_catalog()
    except FileNotFoundError:
        # Allow API to start; /meta and /recommend return 503 until data exists.
        pass
    yield


app = FastAPI(
    title="Discover — Restaurant Recommendations",
    version="1.0.0",
    lifespan=lifespan,
)

_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(_settings.cors_origins),
    allow_origin_regex=_settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    location: str
    budget: str = "medium"
    cuisine: str | None = None
    min_rating: float = Field(default=4.0, ge=0.0, le=5.0)
    additional_preferences: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/meta")
def meta() -> dict[str, Any]:
    try:
        catalog = _ensure_catalog()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    settings = get_settings()
    return {
        "catalog_size": int(len(catalog)),
        "locations": _locations,
        "cuisines": _cuisines,
        "location_count": len(_locations),
        "cuisine_count": max(0, len(_cuisines) - 1),
        "llm_model": _short_model_name(settings.llm_model),
        "groq_connected": _api_key_configured(settings.llm_api_key),
    }


@app.post("/recommend")
def recommend(body: RecommendRequest) -> dict[str, Any]:
    try:
        catalog = _ensure_catalog()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    cuisine = body.cuisine
    if cuisine is not None and cuisine.strip().casefold() in {
        "",
        ANY_CUISINE.casefold(),
        "any",
    }:
        cuisine = None

    try:
        preferences = validate_preferences(
            location=body.location,
            budget=body.budget,
            cuisine=cuisine,
            min_rating=body.min_rating,
            additional_preferences=body.additional_preferences,
        )
    except PreferenceValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    filtered = filter_candidates(preferences, catalog=catalog)
    response = recommend_from_filter(preferences, filtered)
    return response.to_dict()
