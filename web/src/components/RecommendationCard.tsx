import type { RecommendationItem } from "@/lib/types";

type RecommendationCardProps = {
  item: RecommendationItem;
  mutedExplain?: boolean;
  index?: number;
};

export function RecommendationCard({
  item,
  mutedExplain = false,
  index = 0,
}: RecommendationCardProps) {
  const locationBit = item.location ? ` · ${item.location}` : "";
  const rating =
    item.rating != null && !Number.isNaN(item.rating)
      ? item.rating.toFixed(1)
      : "N/A";
  const stagger = `stagger-${Math.min(index + 1, 5)}`;

  return (
    <article
      className={`glass-panel flex animate-fade-up ${stagger} flex-col gap-gutter-md rounded-lg p-gutter-lg transition-all duration-surface-enter ease-surface-enter hover:-translate-y-1 hover:border-primary/40 hover:shadow-glow`}
    >
      <header className="flex items-start justify-between gap-gutter-md">
        <div className="flex min-w-0 items-start gap-gutter-md">
          <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-gradient-to-br from-primary to-secondary font-mono text-mono-sm tabular-nums text-on-primary shadow-glow">
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
        <span className="inline-flex shrink-0 items-center gap-gutter-xs rounded-full border border-secondary/30 bg-secondary-container/70 px-gutter-sm py-gutter-xs font-mono text-mono-sm tabular-nums text-secondary">
          <span
            className="material-symbols-outlined filled text-label-sm"
            aria-hidden
          >
            star
          </span>
          <span>{rating}</span>
        </span>
      </header>
      <div className="h-px w-full bg-gradient-to-r from-transparent via-white/15 to-transparent" />
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
