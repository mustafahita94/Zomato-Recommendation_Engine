"""Sanity checks for the Phase 1 processed restaurant catalog."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.load_dataset import (  # noqa: E402
    DEFAULT_PROCESSED_CSV,
    DEFAULT_PROCESSED_PARQUET,
    load_processed,
    run_ingestion,
)

REQUIRED_COLUMNS = [
    "id",
    "name",
    "location",
    "city",
    "cuisines",
    "cost_for_two",
    "budget_band",
    "rating",
]


def print_distributions(frame: pd.DataFrame) -> None:
    print("\n=== Distributions ===")
    print("\nCity counts:")
    print(frame["city"].value_counts().to_string())
    print("\nTop 15 locations (neighborhoods):")
    print(frame["location"].value_counts().head(15).to_string())
    print("\nBudget band:")
    print(frame["budget_band"].value_counts().to_string())
    print("\nRating describe:")
    print(frame["rating"].describe().to_string())
    print("\nTop 15 cuisine tokens:")
    cuisine_tokens = (
        frame["cuisines"]
        .dropna()
        .str.split("|")
        .explode()
        .str.strip()
        .value_counts()
        .head(15)
    )
    print(cuisine_tokens.to_string())


def verify_exit_criteria(frame: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in frame.columns]
    if missing:
        raise AssertionError(f"Missing required columns: {missing}")

    assert pd.api.types.is_numeric_dtype(frame["cost_for_two"]), "cost_for_two must be numeric"
    assert pd.api.types.is_float_dtype(frame["rating"]) or pd.api.types.is_numeric_dtype(
        frame["rating"]
    ), "rating must be numeric"
    assert set(frame["budget_band"].unique()) <= {"low", "medium", "high"}
    assert frame["rating"].between(0, 5).all(), "ratings must be in 0–5"
    assert len(frame) > 0, "processed catalog is empty"

    bangalore = frame[frame["city"].str.casefold() == "bangalore"]
    assert len(bangalore) > 0, "Expected non-empty Bangalore rows"

    # Quick reload timing / integrity
    reloaded = load_processed()
    assert len(reloaded) == len(frame)

    print("\n=== Exit criteria ===")
    print(f"Required fields present: {REQUIRED_COLUMNS}")
    print(f"cost_for_two dtype: {frame['cost_for_two'].dtype}")
    print(f"rating dtype: {frame['rating'].dtype}")
    print(f"budget bands: {sorted(frame['budget_band'].unique())}")
    print(f"Bangalore rows: {len(bangalore)}")
    print("All exit criteria passed.")


def main() -> None:
    if not DEFAULT_PROCESSED_CSV.exists() and not DEFAULT_PROCESSED_PARQUET.exists():
        print("Processed catalog missing — running ingestion first...")
        processed, stats, csv_path, parquet_path = run_ingestion()
        print(f"Ingestion complete: {stats}")
        print(f"Wrote {csv_path} and {parquet_path}")
    else:
        processed = load_processed()
        print(f"Loaded processed catalog: {len(processed)} rows")

    print(f"\nRows in catalog: {len(processed)}")
    print_distributions(processed)
    verify_exit_criteria(processed)


if __name__ == "__main__":
    main()
