type SummaryBannerProps = {
  summary: string;
};

export function SummaryBanner({ summary }: SummaryBannerProps) {
  return (
    <div
      role="region"
      aria-label="AI summary banner"
      className="flex items-start gap-gutter-md rounded-md border border-outline-strong bg-surface-elevated p-gutter-md"
    >
      <span
        className="material-symbols-outlined mt-0.5 shrink-0 text-headline-md text-primary"
        aria-hidden
      >
        auto_awesome
      </span>
      <div className="flex flex-col gap-gutter-xs">
        <h3 className="font-title text-title-md text-on-surface">AI overview</h3>
        <p className="text-pretty font-body text-body-md text-on-surface-muted">
          {summary}
        </p>
      </div>
    </div>
  );
}
