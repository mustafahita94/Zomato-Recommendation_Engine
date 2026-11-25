import type { RecommendationResponse } from "@/lib/types";
import { EmptyState } from "./EmptyState";
import { FallbackBanner } from "./FallbackBanner";
import { RecommendationCard } from "./RecommendationCard";
import { SummaryBanner } from "./SummaryBanner";

type RecommendationListProps = {
  response: RecommendationResponse;
  location: string;
  onReset?: () => void;
};

export function RecommendationList({
  response,
  location,
  onReset,
}: RecommendationListProps) {
  const count = response.recommendations.length;
  const heading =
    count > 0 && location
      ? `Top ${count} picks in ${location}`
      : "Recommendations";
  const sortLabel = response.meta.used_fallback
    ? "Sorted by rating"
    : "Sorted by AI match";

  const latency =
    response.meta.latency_ms != null
      ? `${Math.round(response.meta.latency_ms)}ms`
      : "n/a";
  const filters =
    response.meta.filters_applied.length > 0
      ? response.meta.filters_applied.join(" · ")
      : "none";
  const fallbackBit = response.meta.used_fallback ? " · fallback" : "";

  return (
    <main aria-labelledby="results-heading" className="flex flex-col gap-gutter-lg">
      <div className="flex flex-wrap items-baseline justify-between gap-gutter-sm">
        <h2
          id="results-heading"
          className="font-headline text-headline-lg text-on-surface"
        >
          {heading}
        </h2>
        <span className="font-mono text-mono-sm tabular-nums text-on-surface-muted">
          {sortLabel}
        </span>
      </div>

      {response.is_empty || count === 0 ? (
        <EmptyState message={response.empty_message} onReset={onReset} />
      ) : (
        <>
          {response.meta.used_fallback ? (
            <FallbackBanner
              message={
                response.meta.message ||
                "Groq LLM ranking is temporarily unavailable. Showing top Zomato-rated matches."
              }
            />
          ) : null}

          {response.summary ? (
            <SummaryBanner summary={response.summary} />
          ) : null}

          <div className="flex flex-col gap-gutter-md">
            {response.recommendations.map((item) => (
              <RecommendationCard
                key={`${item.rank}-${item.restaurant_id ?? item.name}`}
                item={item}
                mutedExplain={response.meta.used_fallback}
              />
            ))}
          </div>

          <footer className="flex flex-wrap items-center justify-between gap-gutter-sm border-t border-outline pt-gutter-sm">
            <p className="font-mono text-mono-sm tabular-nums text-on-surface-muted">
              {response.meta.candidates_considered} candidates considered ·{" "}
              {filters} · {latency}
              {fallbackBit}
            </p>
            <span className="font-label text-label-sm text-on-surface-muted">
              Discover · Bangalore
            </span>
          </footer>
        </>
      )}
    </main>
  );
}
