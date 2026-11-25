"use client";

import { useCallback, useEffect, useState, type ReactNode } from "react";
import { fetchMeta, postRecommend } from "@/lib/api";
import type { CatalogMeta, RecommendationResponse } from "@/lib/types";
import { AppHeader } from "./AppHeader";
import { ErrorBanner } from "./ErrorBanner";
import { FallbackBanner } from "./FallbackBanner";
import {
  PreferencesForm,
  type PreferenceValues,
} from "./PreferencesForm";
import { RecommendationList } from "./RecommendationList";
import { StatusPanel } from "./StatusPanel";
import { TopNav } from "./TopNav";

const ANY_CUISINE = "Any cuisine";

function PageShell({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto flex min-h-screen max-w-content flex-col px-gutter-md pb-section pt-gutter-md sm:px-page-margin sm:pt-gutter-lg">
      {children}
    </div>
  );
}

export function DiscoverPage() {
  const [meta, setMeta] = useState<CatalogMeta | null>(null);
  const [metaError, setMetaError] = useState<string | null>(null);
  const [loadingMeta, setLoadingMeta] = useState(true);

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [response, setResponse] = useState<RecommendationResponse | null>(
    null,
  );
  const [lastLocation, setLastLocation] = useState("Bangalore");
  const [formKey, setFormKey] = useState(0);

  const loadMeta = useCallback(async () => {
    setLoadingMeta(true);
    setMetaError(null);
    try {
      const data = await fetchMeta();
      setMeta(data);
    } catch (err) {
      setMeta(null);
      setMetaError(
        err instanceof Error
          ? err.message
          : "Unable to load the restaurant catalog.",
      );
    } finally {
      setLoadingMeta(false);
    }
  }, []);

  useEffect(() => {
    void loadMeta();
  }, [loadMeta]);

  async function handleSubmit(values: PreferenceValues) {
    setSubmitting(true);
    setSubmitError(null);
    setLastLocation(values.location);
    try {
      const cuisine =
        !values.cuisine || values.cuisine === ANY_CUISINE
          ? null
          : values.cuisine;
      const result = await postRecommend({
        location: values.location,
        budget: values.budget,
        cuisine,
        min_rating: values.minRating,
        additional_preferences: values.additionalPreferences.trim() || null,
      });
      setResponse(result);
    } catch (err) {
      setResponse(null);
      setSubmitError(
        err instanceof Error
          ? err.message
          : "Something went wrong while generating recommendations.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  function handleReset() {
    setResponse(null);
    setSubmitError(null);
    setFormKey((key) => key + 1);
  }

  if (loadingMeta) {
    return (
      <PageShell>
        <TopNav />
        <div className="flex flex-col gap-section">
          <AppHeader
            title="Places worth the trip"
            subtitle="Loading Bangalore catalog…"
          />
          <div className="glass-panel h-28 animate-pulse rounded-lg" />
          <p className="font-mono text-mono-sm text-on-surface-muted">
            Connecting to the recommendation API…
          </p>
        </div>
      </PageShell>
    );
  }

  if (metaError || !meta) {
    return (
      <PageShell>
        <TopNav groqConnected={false} />
        <div className="flex flex-col gap-section">
          <AppHeader
            kicker="Setup needed"
            title="Restaurant catalog missing"
            subtitle="Graceful recovery when the API or processed dataset is unavailable."
          />
          <ErrorBanner
            title="Restaurant catalog missing or failed to load"
            message={
              metaError ||
              "Unable to read the Bangalore Zomato catalog. Ensure the API is running and the processed dataset exists, then refresh."
            }
          />
          <button
            type="button"
            onClick={() => void loadMeta()}
            className="btn-ghost w-fit border-error/50 text-error hover:border-error hover:bg-error-container"
          >
            Retry load
          </button>
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <TopNav groqConnected={meta.groq_connected} />
      <div className="flex flex-col gap-section">
        <header className="grid grid-cols-1 items-start gap-gutter-xl lg:grid-cols-12">
          <AppHeader
            title="Places worth the trip"
            subtitle="Set your Bangalore neighborhood, budget, and cuisine to get five ranked restaurant picks with concise AI explanations."
          />
          <StatusPanel
            catalogSize={meta.catalog_size}
            locationCount={meta.location_count}
            cuisineCount={meta.cuisine_count}
            llmModel={meta.llm_model}
            groqConnected={meta.groq_connected}
          />
        </header>

        {!meta.groq_connected ? (
          <FallbackBanner
            title="Fallback mode — Groq API key not set"
            message="Recommendations will use rating-based ranking. Add LLM_API_KEY on Railway for AI ranking and explanations."
          />
        ) : null}

        <PreferencesForm
          key={formKey}
          locations={meta.locations}
          cuisines={meta.cuisines}
          loading={submitting}
          onSubmit={handleSubmit}
        />

        {submitError ? (
          <ErrorBanner
            title="Something went wrong while generating recommendations"
            message={submitError}
          />
        ) : null}

        {response ? (
          <RecommendationList
            response={response}
            location={lastLocation}
            onReset={handleReset}
          />
        ) : null}
      </div>
    </PageShell>
  );
}
