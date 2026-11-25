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
    <aside className="w-full lg:col-span-4">
      <article className="flex flex-col gap-gutter-sm rounded-md border border-outline bg-surface p-gutter-md">
        <header className="flex items-center justify-between border-b border-outline pb-gutter-xs">
          <h2 className="font-label text-label-lg text-on-surface">
            Catalog &amp; LLM
          </h2>
          <div className="flex items-center gap-gutter-xs">
            <span
              role="status"
              aria-label={groqConnected ? "Connected" : "Fallback mode"}
              className={`inline-block h-2 w-2 rounded-full ${
                groqConnected ? "bg-success" : "bg-secondary"
              }`}
            />
            <span
              className={`font-label text-label-sm ${
                groqConnected ? "text-success" : "text-secondary"
              }`}
            >
              {groqConnected ? "Connected" : "Fallback mode"}
            </span>
          </div>
        </header>
        <div className="flex flex-col gap-gutter-xs">
          <div className="flex items-center justify-between">
            <span className="font-label text-label-sm text-on-surface-muted">
              Catalog size
            </span>
            <span className="font-mono text-mono-sm tabular-nums text-on-surface">
              {catalogSize.toLocaleString()} places
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="font-label text-label-sm text-on-surface-muted">
              Locations · Cuisines
            </span>
            <span className="font-mono text-mono-sm tabular-nums text-on-surface">
              {locationCount} · {cuisineCount}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="font-label text-label-sm text-on-surface-muted">
              LLM model
            </span>
            <span className="font-mono text-mono-sm text-on-surface">
              {llmModel}
            </span>
          </div>
        </div>
      </article>
    </aside>
  );
}
