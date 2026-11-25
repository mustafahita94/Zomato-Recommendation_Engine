"""Dataset ingestion and preprocessing."""

from __future__ import annotations

from typing import Any

__all__ = [
    "load_processed",
    "load_raw_dataset",
    "preprocess",
    "run_ingestion",
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        from src.ingestion import load_dataset as _load_dataset

        return getattr(_load_dataset, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
