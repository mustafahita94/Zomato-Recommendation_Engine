type ErrorBannerProps = {
  title: string;
  message: string;
};

export function ErrorBanner({ title, message }: ErrorBannerProps) {
  return (
    <div
      role="region"
      aria-label="Error banner"
      className="flex items-start gap-gutter-md rounded-lg border border-error/40 bg-error-container/50 p-gutter-lg backdrop-blur-sm"
    >
      <span
        className="material-symbols-outlined mt-0.5 shrink-0 text-headline-md text-error"
        aria-hidden
      >
        error_outline
      </span>
      <div className="flex flex-col gap-gutter-xs">
        <h3 className="font-title text-title-md text-error">{title}</h3>
        <p className="max-w-prose text-pretty font-body text-body-md text-on-surface-muted">
          {message}
        </p>
      </div>
    </div>
  );
}
