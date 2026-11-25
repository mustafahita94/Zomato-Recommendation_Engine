"use client";

import { useCallback, useEffect, useState } from "react";
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

const ANY_CUISINE = "Any cuisine";

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
      <div className="mx-auto flex min-h-screen max-w-content flex-col gap-section px-gutter-md py-gutter-xl sm:px-page-margin sm:py-section">
        <AppHeader
          title="Discover places worth the trip"
          subtitle="Loading Bangalore catalog…"
        />
        <p className="font-body text-body-md text-on-surface-muted">
          Connecting to the recommendation API…
        </p>
      </div>
    );
  }

  if (metaError || !meta) {
    return (
      <div className="mx-auto flex min-h-screen max-w-content flex-col gap-section px-gutter-md py-gutter-xl sm:px-page-margin sm:py-section">
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
          className="inline-flex w-fit items-center justify-center rounded border border-error/50 px-gutter-md py-gutter-sm font-label text-label-lg text-error transition-colors duration-state-change hover:bg-error-container"
        >
          Retry load
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-content flex-col gap-section px-gutter-md py-gutter-xl sm:px-page-margin sm:py-section">
      <header className="grid grid-cols-1 items-start gap-gutter-xl lg:grid-cols-12">
        <AppHeader
          title="Discover places worth the trip"
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
          message="Recommendations will use rating-based ranking. Add LLM_API_KEY to the Python .env for AI ranking and explanations."
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
  );
}
