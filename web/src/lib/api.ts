import type {
  CatalogMeta,
  RecommendRequest,
  RecommendationResponse,
} from "./types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

async function parseError(res: Response): Promise<string> {
  try {
    const data = (await res.json()) as { detail?: string | unknown };
    if (typeof data.detail === "string") return data.detail;
    return JSON.stringify(data.detail ?? data);
  } catch {
    return res.statusText || `Request failed (${res.status})`;
  }
}

export async function fetchMeta(): Promise<CatalogMeta> {
  const res = await fetch(`${API_URL}/meta`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(await parseError(res));
  }
  return res.json() as Promise<CatalogMeta>;
}

export async function postRecommend(
  body: RecommendRequest,
): Promise<RecommendationResponse> {
  const res = await fetch(`${API_URL}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(await parseError(res));
  }
  return res.json() as Promise<RecommendationResponse>;
}

export { API_URL };
