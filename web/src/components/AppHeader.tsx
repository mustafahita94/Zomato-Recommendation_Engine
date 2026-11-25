type AppHeaderProps = {
  kicker?: string;
  title: string;
  subtitle: string;
};

export function AppHeader({
  kicker = "Bangalore dining intelligence",
  title,
  subtitle,
}: AppHeaderProps) {
  return (
    <div className="flex animate-fade-up flex-col gap-gutter-lg lg:col-span-8">
      <div className="flex flex-wrap items-center gap-gutter-sm">
        <span className="relative inline-flex h-9 w-9 items-center justify-center" aria-hidden>
          <span className="absolute left-0 top-0 h-5 w-5 rounded-[5px] bg-primary shadow-glow" />
          <span className="absolute bottom-0 right-0 h-5 w-5 rounded-[5px] bg-secondary opacity-90" />
        </span>
        <span className="font-display text-headline-md tracking-tight text-gradient-brand">
          Discover
        </span>
        <span className="chip uppercase tracking-[0.14em] text-accent">
          {kicker}
        </span>
      </div>
      <h1 className="max-w-[18ch] font-display text-display-lg-mobile text-balance text-on-surface lg:text-display-lg">
        {title}
      </h1>
      <p className="max-w-prose text-pretty font-body text-body-lg text-on-surface-muted">
        {subtitle}
      </p>
    </div>
  );
}
