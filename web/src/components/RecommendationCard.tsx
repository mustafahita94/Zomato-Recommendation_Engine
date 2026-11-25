import type { RecommendationItem } from "@/lib/types";

type RecommendationCardProps = {
  item: RecommendationItem;
  mutedExplain?: boolean;
};

export function RecommendationCard({
  item,
  mutedExplain = false,
}: RecommendationCardProps) {
  const locationBit = item.location ? ` · ${item.location}` : "";
  const rating =
    item.rating != null && !Number.isNaN(item.rating)
      ? item.rating.toFixed(1)
      : "N/A";

  return (
    <article className="flex flex-col gap-gutter-md rounded-lg border border-outline-strong bg-surface p-gutter-lg transition-transform duration-surface-enter ease-surface-enter hover:-translate-y-px hover:border-primary/40">
      <header className="flex items-start justify-between gap-gutter-md">
        <div className="flex min-w-0 items-start gap-gutter-md">
          <span className="inline-flex shrink-0 items-center justify-center rounded-full border border-primary/40 bg-primary-container px-gutter-sm py-gutter-xs font-mono text-mono-sm tabular-nums text-on-primary-container">
            #{item.rank}
          </span>
          <div className="flex min-w-0 flex-col gap-gutter-xs">
            <h3 className="font-headline text-headline-md text-on-surface">
              {item.name}
            </h3>
            <p className="font-body text-body-md text-on-surface-muted">
              {item.cuisine}
              {locationBit} · {item.estimated_cost}
            </p>
          </div>
        </div>
        <span className="inline-flex shrink-0 items-center gap-gutter-xs rounded-full border border-secondary/30 bg-secondary-container px-gutter-sm py-gutter-xs font-mono text-mono-sm tabular-nums text-secondary">
          <span
            className="material-symbols-outlined filled text-label-sm"
            aria-hidden
          >
            star
          </span>
          <span>{rating}</span>
        </span>
      </header>
      <hr className="border-outline" />
      <p
        className={`text-pretty font-body text-body-lg ${
          mutedExplain ? "text-on-surface-muted" : "text-on-surface"
        }`}
      >
        {item.explanation}
      </p>
    </article>
  );
}
