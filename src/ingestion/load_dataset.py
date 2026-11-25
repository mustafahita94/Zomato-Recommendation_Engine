"""
Load and preprocess the Hugging Face Zomato restaurant dataset.

Column meanings (processed catalog)
-----------------------------------
id              Stable row id (name + location + cost hash).
name            Restaurant name.
location        Neighborhood / locality (e.g. Banashankari, HSR).
city            City name (this dataset is Bangalore; Bengaluru normalized).
cuisines        Pipe-separated cuisine tokens (e.g. "North Indian|Chinese").
cost_for_two    Approximate cost for two people (INR, numeric).
budget_band     low | medium | high from cost_for_two thresholds.
rating          Float rating on a 0–5 scale (parsed from rate like "4.1/5").
votes           Number of rating votes.
rest_type       Restaurant type (e.g. Casual Dining, Cafe).
online_order    Yes/No whether online ordering is available.
book_table      Yes/No whether table booking is available.
dish_liked      Popular dishes (optional free text).
listed_in_type  Zomato listing category (e.g. Buffet, Delivery).

Budget band thresholds (INR for two)
------------------------------------
low     cost_for_two <= 300
medium  300 < cost_for_two <= 600
high    cost_for_two > 600
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

import pandas as pd
from datasets import load_dataset

DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"
DEFAULT_CITY = "Bangalore"

# Source → processed field map (required for schema validation)
REQUIRED_SOURCE_COLUMNS = [
    "name",
    "location",
    "cuisines",
    "approx_cost(for two people)",
    "rate",
    "votes",
]

CITY_ALIASES = {
    "bengaluru": "Bangalore",
    "bangalore": "Bangalore",
}

BUDGET_LOW_MAX = 300
BUDGET_MEDIUM_MAX = 600

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROCESSED_CSV = PROJECT_ROOT / "data" / "processed" / "restaurants.csv"
DEFAULT_PROCESSED_PARQUET = PROJECT_ROOT / "data" / "processed" / "restaurants.parquet"


def load_raw_dataset(split: str = "train") -> pd.DataFrame:
    """Download/load the Hugging Face dataset into a DataFrame."""
    dataset = load_dataset(DATASET_ID, split=split)
    frame = dataset.to_pandas()
    missing = [col for col in REQUIRED_SOURCE_COLUMNS if col not in frame.columns]
    if missing:
        raise ValueError(
            f"Dataset schema mismatch for {DATASET_ID}. Missing columns: {missing}. "
            f"Found: {list(frame.columns)}"
        )
    return frame


def normalize_text(value: Any) -> str | None:
    """Trim whitespace; return None for empty / nullish values."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None
    return text


def normalize_location(value: Any) -> str | None:
    """Trim and title-case a locality / city string."""
    text = normalize_text(value)
    if text is None:
        return None
    return " ".join(part.capitalize() if not part.isupper() else part for part in text.split())


def normalize_city(address: Any, fallback: str = DEFAULT_CITY) -> str:
    """
    Resolve city for a row.

    This HF dump is Bangalore-centric (~96% of addresses mention Bangalore/Bengaluru).
    """
    text = normalize_text(address)
    if text:
        lowered = text.lower()
        for alias, canonical in CITY_ALIASES.items():
            if alias in lowered:
                return canonical
    return fallback


def parse_rating(value: Any) -> float | None:
    """Parse ratings like '4.1/5' or '4.1 /5'; drop NEW / - / blanks."""
    text = normalize_text(value)
    if text is None:
        return None
    cleaned = text.replace(" ", "")
    if cleaned.upper() in {"NEW", "-", "N/A"}:
        return None
    match = re.match(r"^(\d+(?:\.\d+)?)(?:/5)?$", cleaned)
    if not match:
        return None
    rating = float(match.group(1))
    if rating < 0 or rating > 5:
        return None
    return rating


def parse_cost(value: Any) -> float | None:
    """Parse cost strings such as '800' or '1,200' into a float."""
    text = normalize_text(value)
    if text is None:
        return None
    digits = re.sub(r"[^\d.]", "", text.replace(",", ""))
    if not digits:
        return None
    try:
        cost = float(digits)
    except ValueError:
        return None
    if cost <= 0 or cost > 100_000:
        return None
    return cost


def assign_budget_band(cost: float) -> str:
    """Map numeric cost_for_two to low / medium / high."""
    if cost <= BUDGET_LOW_MAX:
        return "low"
    if cost <= BUDGET_MEDIUM_MAX:
        return "medium"
    return "high"


def normalize_cuisines(value: Any) -> list[str]:
    """Split multi-cuisine strings into trimmed, de-duplicated tokens."""
    text = normalize_text(value)
    if text is None:
        return []
    tokens: list[str] = []
    seen: set[str] = set()
    for part in text.split(","):
        token = normalize_text(part)
        if token is None:
            continue
        # Preserve common cuisine casing (North Indian, BBQ, etc.)
        normalized = " ".join(token.split())
        key = normalized.casefold()
        if key in seen:
            continue
        seen.add(key)
        tokens.append(normalized)
    return tokens


def make_id(name: str, location: str, cost: float) -> str:
    """Build a short stable id from identifying fields."""
    payload = f"{name.casefold()}|{location.casefold()}|{int(cost)}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]


def preprocess(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Clean and normalize the raw dataset into the processed restaurant catalog.

    Returns (processed_frame, stats).
    """
    before = len(raw)
    work = pd.DataFrame(
        {
            "name": raw["name"].map(normalize_text),
            "location": raw["location"].map(normalize_location),
            "city": raw["address"].map(normalize_city) if "address" in raw.columns else DEFAULT_CITY,
            "cuisines_list": raw["cuisines"].map(normalize_cuisines),
            "cost_for_two": raw["approx_cost(for two people)"].map(parse_cost),
            "rating": raw["rate"].map(parse_rating),
            "votes": pd.to_numeric(raw["votes"], errors="coerce").fillna(0).astype(int),
            "rest_type": raw["rest_type"].map(normalize_text) if "rest_type" in raw.columns else None,
            "online_order": raw["online_order"].map(normalize_text) if "online_order" in raw.columns else None,
            "book_table": raw["book_table"].map(normalize_text) if "book_table" in raw.columns else None,
            "dish_liked": raw["dish_liked"].map(normalize_text) if "dish_liked" in raw.columns else None,
            "listed_in_type": (
                raw["listed_in(type)"].map(normalize_text) if "listed_in(type)" in raw.columns else None
            ),
        }
    )

    # Drop rows missing critical fields
    work = work.dropna(subset=["name", "location", "cost_for_two", "rating"])
    work = work[work["cuisines_list"].map(bool)]

    work["budget_band"] = work["cost_for_two"].map(assign_budget_band)
    work["cuisines"] = work["cuisines_list"].map(lambda items: "|".join(items))
    work["id"] = [
        make_id(name, location, cost)
        for name, location, cost in zip(work["name"], work["location"], work["cost_for_two"], strict=True)
    ]

    # Deduplicate identical name + location, keep highest votes then rating
    work = work.sort_values(["votes", "rating"], ascending=[False, False])
    work = work.drop_duplicates(subset=["name", "location"], keep="first")

    columns = [
        "id",
        "name",
        "location",
        "city",
        "cuisines",
        "cost_for_two",
        "budget_band",
        "rating",
        "votes",
        "rest_type",
        "online_order",
        "book_table",
        "dish_liked",
        "listed_in_type",
    ]
    processed = work[columns].reset_index(drop=True)
    processed["cost_for_two"] = processed["cost_for_two"].astype(int)
    processed["rating"] = processed["rating"].astype(float)

    stats = {
        "rows_before": before,
        "rows_after": len(processed),
        "rows_dropped": before - len(processed),
    }
    return processed, stats


def save_processed(
    frame: pd.DataFrame,
    csv_path: Path = DEFAULT_PROCESSED_CSV,
    parquet_path: Path = DEFAULT_PROCESSED_PARQUET,
) -> tuple[Path, Path]:
    """Persist the processed catalog as CSV and Parquet."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(csv_path, index=False)
    frame.to_parquet(parquet_path, index=False)
    return csv_path, parquet_path


def load_processed(path: Path | None = None) -> pd.DataFrame:
    """
    Read the processed restaurant catalog.

    Prefers Parquet when available; falls back to CSV.
    """
    parquet_path = Path(path) if path else DEFAULT_PROCESSED_PARQUET
    csv_path = DEFAULT_PROCESSED_CSV if path is None else Path(path)

    if path is None:
        if parquet_path.exists():
            return pd.read_parquet(parquet_path)
        if csv_path.exists():
            return pd.read_csv(csv_path)
        raise FileNotFoundError(
            f"Processed catalog not found. Expected {parquet_path} or {csv_path}. "
            "Run: python -m src.ingestion.load_dataset"
        )

    suffix = Path(path).suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def run_ingestion() -> tuple[pd.DataFrame, dict[str, int], Path, Path]:
    """Full pipeline: load → preprocess → save."""
    raw = load_raw_dataset()
    processed, stats = preprocess(raw)
    csv_path, parquet_path = save_processed(processed)
    return processed, stats, csv_path, parquet_path


def main() -> None:
    processed, stats, csv_path, parquet_path = run_ingestion()
    print(f"Rows before: {stats['rows_before']}")
    print(f"Rows after:  {stats['rows_after']}")
    print(f"Rows dropped:{stats['rows_dropped']}")
    print(f"Wrote {csv_path}")
    print(f"Wrote {parquet_path}")
    print("Budget band counts:")
    print(processed["budget_band"].value_counts().to_string())
    print("Top locations:")
    print(processed["location"].value_counts().head(10).to_string())


if __name__ == "__main__":
    main()
