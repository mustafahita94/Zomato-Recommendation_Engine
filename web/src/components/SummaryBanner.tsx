type SummaryBannerProps = {
  summary: string;
};

export function SummaryBanner({ summary }: SummaryBannerProps) {
  return (
    <div
      role="region"
      aria-label="AI summary banner"
      className="flex items-start gap-gutter-md rounded-md border border-primary/25 bg-primary-container/50 p-gutter-md shadow-glow"
    >
      <span
        className="mt-0.5 inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-gradient-to-br from-primary to-secondary font-mono text-mono-sm text-on-primary"
        aria-hidden
      >
        AI
      </span>
      <div className="flex flex-col gap-gutter-xs">
        <h3 className="font-title text-title-md text-on-primary-container">
          AI overview
        </h3>
        <p className="text-pretty font-body text-body-md text-on-surface-muted">
          {summary}
        </p>
      </div>
    </div>
  );
}
