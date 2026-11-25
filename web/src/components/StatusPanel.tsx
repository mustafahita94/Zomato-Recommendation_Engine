type StatusPanelProps = {
  catalogSize: number;
  locationCount: number;
  cuisineCount: number;
  llmModel: string;
  groqConnected: boolean;
};

export function StatusPanel({
  catalogSize,
  locationCount,
  cuisineCount,
  llmModel,
  groqConnected,
}: StatusPanelProps) {
  return (
    <aside className="w-full animate-fade-up stagger-2 lg:col-span-4">
      <article className="glass-panel flex flex-col gap-gutter-md rounded-lg p-gutter-lg">
        <header className="flex items-center justify-between gap-gutter-sm">
          <h2 className="font-label text-label-lg text-on-surface">
            Live catalog
          </h2>
          <span className="chip">
            <span
              role="status"
              aria-label={groqConnected ? "Connected" : "Fallback mode"}
              className={`inline-block h-2 w-2 rounded-full ${
                groqConnected
                  ? "animate-soft-pulse bg-success shadow-[0_0_10px_rgba(74,222,128,0.7)]"
                  : "bg-secondary"
              }`}
            />
            <span
              className={
                groqConnected ? "text-success" : "text-secondary"
              }
            >
              {groqConnected ? "Groq live" : "Fallback"}
            </span>
          </span>
        </header>

        <div className="grid grid-cols-2 gap-gutter-sm">
          <div className="rounded-md border border-white/10 bg-black/30 p-gutter-md">
            <p className="font-label text-label-sm text-on-surface-muted">
              Places
            </p>
            <p className="mt-gutter-xs font-display text-headline-md tabular-nums text-on-surface">
              {catalogSize.toLocaleString()}
            </p>
          </div>
          <div className="rounded-md border border-white/10 bg-black/30 p-gutter-md">
            <p className="font-label text-label-sm text-on-surface-muted">
              Areas
            </p>
            <p className="mt-gutter-xs font-display text-headline-md tabular-nums text-on-surface">
              {locationCount}
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-gutter-xs border-t border-white/10 pt-gutter-md">
          <div className="flex items-center justify-between gap-gutter-sm">
            <span className="font-label text-label-sm text-on-surface-muted">
              Cuisines
            </span>
            <span className="font-mono text-mono-sm tabular-nums text-on-surface">
              {cuisineCount}
            </span>
          </div>
          <div className="flex items-center justify-between gap-gutter-sm">
            <span className="font-label text-label-sm text-on-surface-muted">
              Model
            </span>
            <span className="truncate font-mono text-mono-sm text-accent">
              {llmModel}
            </span>
          </div>
        </div>
      </article>
    </aside>
  );
}
