type FallbackBannerProps = {
  title?: string;
  message: string;
};

export function FallbackBanner({
  title = "Fallback mode active — rating-based picks shown",
  message,
}: FallbackBannerProps) {
  return (
    <div
      role="region"
      aria-label="Fallback mode notice"
      className="flex items-start gap-gutter-md rounded-md border border-secondary/35 bg-secondary-container/50 p-gutter-md"
    >
      <span
        className="material-symbols-outlined mt-0.5 shrink-0 text-headline-md text-secondary"
        aria-hidden
      >
        info
      </span>
      <div className="flex flex-col gap-gutter-xs">
        <h3 className="font-title text-title-md text-secondary">{title}</h3>
        <p className="text-pretty font-body text-body-md text-on-surface-muted">
          {message}
        </p>
      </div>
    </div>
  );
}
