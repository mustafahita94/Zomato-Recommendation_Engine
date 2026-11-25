type AppHeaderProps = {
  kicker?: string;
  title: string;
  subtitle: string;
};

export function AppHeader({
  kicker = "AI restaurant recommender",
  title,
  subtitle,
}: AppHeaderProps) {
  return (
    <div className="flex flex-col gap-gutter-md lg:col-span-8">
      <div className="flex items-center gap-gutter-sm">
        <span className="font-display text-title-md tracking-tight text-on-surface">
          Discover
        </span>
        <span className="text-outline-strong" aria-hidden="true">
          /
        </span>
        <span className="font-label text-label-sm uppercase tracking-wider text-primary">
          {kicker}
        </span>
      </div>
      <h1 className="font-display text-display-lg-mobile text-balance text-on-surface lg:text-display-lg">
        {title}
      </h1>
      <p className="max-w-prose text-pretty font-body text-body-lg text-on-surface-muted">
        {subtitle}
      </p>
    </div>
  );
}
