"use client";

import { useState, type FormEvent } from "react";

export type PreferenceValues = {
  location: string;
  cuisine: string;
  budget: "low" | "medium" | "high";
  minRating: number;
  additionalPreferences: string;
};

type PreferencesFormProps = {
  locations: string[];
  cuisines: string[];
  defaultLocation?: string;
  loading?: boolean;
  onSubmit: (values: PreferenceValues) => void;
};

const BUDGET_OPTIONS: { value: PreferenceValues["budget"]; label: string }[] = [
  { value: "low", label: "Low ≤ ₹300 for two" },
  { value: "medium", label: "Medium ₹301–₹600" },
  { value: "high", label: "High > ₹600" },
];

function pickDefaultLocation(locations: string[], preferred?: string): string {
  if (preferred && locations.includes(preferred)) return preferred;
  for (const name of [
    "Indiranagar",
    "Koramangala 5th Block",
    "HSR Layout",
    "Bangalore",
  ]) {
    if (locations.includes(name)) return name;
  }
  return locations[0] ?? "Bangalore";
}

const fieldClass =
  "w-full rounded bg-surface-input border border-outline-strong text-on-surface font-body text-body-md px-gutter-md py-gutter-sm focus:border-primary focus:ring-1 focus:ring-primary transition-colors duration-state-change outline-none";

export function PreferencesForm({
  locations,
  cuisines,
  defaultLocation,
  loading = false,
  onSubmit,
}: PreferencesFormProps) {
  const [location, setLocation] = useState(() =>
    pickDefaultLocation(locations, defaultLocation),
  );
  const [cuisine, setCuisine] = useState(cuisines[0] ?? "Any cuisine");
  const [budget, setBudget] =
    useState<PreferenceValues["budget"]>("medium");
  const [minRating, setMinRating] = useState(4.0);
  const [additionalPreferences, setAdditionalPreferences] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit({
      location,
      cuisine,
      budget,
      minRating,
      additionalPreferences,
    });
  }

  return (
    <section
      aria-labelledby="preferences-heading"
      className="flex flex-col gap-gutter-lg rounded-lg border border-outline-strong bg-surface p-gutter-lg sm:p-gutter-xl"
    >
      <div className="flex flex-wrap items-center justify-between gap-gutter-sm">
        <h2
          id="preferences-heading"
          className="font-headline text-headline-md text-on-surface"
        >
          Search preferences
        </h2>
        <span className="font-label text-label-sm text-on-surface-muted">
          Zomato Bangalore dataset · Groq ranking
        </span>
      </div>

      <form
        className="grid grid-cols-1 items-stretch gap-gutter-lg lg:grid-cols-3"
        onSubmit={handleSubmit}
      >
        <div className="flex flex-col gap-gutter-lg">
          <label className="flex flex-col gap-gutter-xs">
            <span className="font-label text-label-lg text-on-surface">
              Location
            </span>
            <select
              required
              className={fieldClass}
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            >
              {locations.map((loc) => (
                <option key={loc} value={loc}>
                  {loc === "Bangalore"
                    ? "Bangalore (All neighborhoods)"
                    : loc}
                </option>
              ))}
            </select>
            <span className="font-label text-label-sm text-on-surface-muted">
              Required · neighborhood or city-wide
            </span>
          </label>

          <label className="flex flex-col gap-gutter-xs">
            <span className="font-label text-label-lg text-on-surface">
              Cuisine
            </span>
            <select
              className={fieldClass}
              value={cuisine}
              onChange={(e) => setCuisine(e.target.value)}
            >
              {cuisines.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
            <span className="font-label text-label-sm text-on-surface-muted">
              Optional · defaults to Any cuisine
            </span>
          </label>
        </div>

        <div className="flex flex-col gap-gutter-lg">
          <label className="flex flex-col gap-gutter-xs">
            <span className="font-label text-label-lg text-on-surface">
              Budget
            </span>
            <select
              className={fieldClass}
              value={budget}
              onChange={(e) =>
                setBudget(e.target.value as PreferenceValues["budget"])
              }
            >
              {BUDGET_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <span className="font-label text-label-sm text-on-surface-muted">
              Estimated cost for two diners
            </span>
          </label>

          <label className="flex flex-col gap-gutter-sm pt-gutter-xs">
            <div className="flex items-center justify-between">
              <span className="font-label text-label-lg text-on-surface">
                Minimum rating
              </span>
              <span className="rounded-full border border-outline bg-surface-elevated px-gutter-sm py-gutter-xs font-mono text-mono-sm tabular-nums text-secondary">
                {minRating.toFixed(1)}
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={5}
              step={0.1}
              value={minRating}
              onChange={(e) => setMinRating(parseFloat(e.target.value))}
              className="h-2 w-full cursor-pointer appearance-none rounded-full bg-surface-elevated accent-primary"
            />
            <div className="flex items-center justify-between text-on-surface-muted">
              <span className="font-label text-label-sm">0.0</span>
              <span className="font-label text-label-sm">5.0</span>
            </div>
          </label>
        </div>

        <div className="flex flex-col justify-between gap-gutter-md">
          <label className="flex flex-col gap-gutter-xs">
            <div className="flex items-center justify-between">
              <span className="font-label text-label-lg text-on-surface">
                Additional preferences
              </span>
              <span className="font-label text-label-sm text-on-surface-muted">
                Optional
              </span>
            </div>
            <textarea
              rows={3}
              maxLength={500}
              placeholder="family-friendly, quick service, outdoor seating…"
              className={`${fieldClass} resize-none placeholder:text-on-surface-muted`}
              value={additionalPreferences}
              onChange={(e) => setAdditionalPreferences(e.target.value)}
            />
            <span className="font-label text-label-sm text-on-surface-muted">
              Up to 500 characters
            </span>
          </label>

          <button
            type="submit"
            disabled={loading}
            className="inline-flex w-full items-center justify-center rounded bg-primary px-gutter-lg py-gutter-md font-label text-label-lg text-on-primary transition-transform duration-state-change ease-state-change hover:brightness-95 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Finding matches…" : "Get recommendations"}
          </button>
        </div>
      </form>
    </section>
  );
}
