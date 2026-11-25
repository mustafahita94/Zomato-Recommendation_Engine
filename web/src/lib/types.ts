export type CatalogMeta = {
  catalog_size: number;
  locations: string[];
  cuisines: string[];
  location_count: number;
  cuisine_count: number;
  llm_model: string;
  groq_connected: boolean;
};

export type RecommendationItem = {
  rank: number;
  name: string;
  cuisine: string;
  rating: number;
  estimated_cost: string;
  explanation: string;
  restaurant_id?: string | null;
  location?: string | null;
};

export type RecommendationMeta = {
  candidates_considered: number;
  filters_applied: string[];
  used_fallback: boolean;
  parse_success: boolean;
  latency_ms: number | null;
  model: string | null;
  message: string | null;
};

export type RecommendationResponse = {
  summary: string | null;
  recommendations: RecommendationItem[];
  meta: RecommendationMeta;
  empty_message: string | null;
  is_empty: boolean;
};

export type RecommendRequest = {
  location: string;
  budget: "low" | "medium" | "high";
  cuisine: string | null;
  min_rating: number;
  additional_preferences: string | null;
};
