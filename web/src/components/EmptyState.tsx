type EmptyStateProps = {
  message?: string | null;
  onReset?: () => void;
};

export function EmptyState({ message, onReset }: EmptyStateProps) {
  return (
    <article className="glass-panel flex flex-col items-center gap-gutter-md rounded-lg border-dashed p-gutter-xl text-center">
      <span
        className="material-symbols-outlined text-headline-lg text-on-surface-muted"
        aria-hidden
      >
        search_off
      </span>
      <header className="flex flex-col gap-gutter-xs">
        <h3 className="font-headline text-headline-md text-on-surface">
          No matching restaurants found
        </h3>
        <p className="max-w-prose text-pretty font-body text-body-md text-on-surface-muted">
          {message ||
            "Try relaxing your cuisine to Any cuisine, raising your budget tier, lowering the minimum rating, or switching Location to Bangalore."}
        </p>
      </header>
      {onReset ? (
        <button type="button" onClick={onReset} className="btn-ghost">
          Reset filters
        </button>
      ) : null}
    </article>
  );
}
