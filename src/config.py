"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# Always allowed for local Next.js (`npm run dev`).
_DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)


def _parse_cors_origins(raw: str | None) -> tuple[str, ...]:
    """Merge defaults with comma-separated CORS_ORIGINS (no trailing slashes)."""
    origins: list[str] = list(_DEFAULT_CORS_ORIGINS)
    if raw:
        for part in raw.split(","):
            origin = part.strip().rstrip("/")
            if origin and origin not in origins:
                origins.append(origin)
    return tuple(origins)


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for LLM, filtering, and CORS."""

    llm_api_key: str
    llm_model: str
    llm_base_url: str
    llm_temperature: float
    llm_max_recommendations: int
    candidate_limit: int
    cors_origins: tuple[str, ...]
    cors_origin_regex: str | None


def get_settings() -> Settings:
    """Load settings from `.env` / process environment."""
    regex = os.getenv("CORS_ORIGIN_REGEX", "").strip() or None
    return Settings(
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_model=os.getenv("LLM_MODEL", "openai/gpt-oss-20b"),
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
        llm_max_recommendations=int(os.getenv("LLM_MAX_RECOMMENDATIONS", "5")),
        candidate_limit=int(os.getenv("CANDIDATE_LIMIT", "20")),
        cors_origins=_parse_cors_origins(os.getenv("CORS_ORIGINS")),
        cors_origin_regex=regex,
    )
