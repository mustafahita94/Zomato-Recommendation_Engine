type TopNavProps = {
  groqConnected?: boolean | null;
};

export function TopNav({ groqConnected = null }: TopNavProps) {
  return (
    <nav
      aria-label="Primary"
      className="glass-nav sticky top-gutter-md z-20 mx-auto mb-gutter-xl flex w-full max-w-content items-center justify-between gap-gutter-md rounded-lg px-gutter-md py-gutter-sm sm:px-gutter-lg"
    >
      <div className="flex items-center gap-gutter-sm">
        <span className="relative inline-flex h-7 w-7" aria-hidden>
          <span className="absolute left-0 top-0 h-4 w-4 rounded-[4px] bg-primary" />
          <span className="absolute bottom-0 right-0 h-4 w-4 rounded-[4px] bg-secondary" />
        </span>
        <span className="font-display text-title-md text-on-surface">
          Discover
        </span>
        <span className="hidden font-body text-body-md text-on-surface-muted sm:inline">
          / Bangalore
        </span>
      </div>

      <div className="flex items-center gap-gutter-sm">
        {groqConnected != null ? (
          <span className="chip">
            <span
              className={`inline-block h-1.5 w-1.5 rounded-full ${
                groqConnected
                  ? "animate-soft-pulse bg-success"
                  : "bg-secondary"
              }`}
              aria-hidden
            />
            {groqConnected ? "Groq live" : "Fallback"}
          </span>
        ) : null}
        <span className="chip hidden sm:inline-flex">AI picks</span>
      </div>
    </nav>
  );
}
