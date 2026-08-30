export type StorySummary = {
  slug: string;
  section: "news" | "articles";
  headline: string;
  dek: string;
  dateline: string;
  source_name: string;
  source_url: string;
  author: string | null;
  published_at: string | null;
  word_count: number;
  tags: string[];
  hero_image_url: string | null;
  generation_method: string;
};

export type StoryDetail = StorySummary & {
  lead: string;
  sections: { heading: string; body: string }[];
  key_facts: string[];
  entities: string[];
  body_markdown: string;
  canonical_url: string;
  language: string;
};

export type Page<T> = {
  items: T[];
  next_cursor: string | null;
  has_more: boolean;
  count: number | null;
};

export type ModelSummary = {
  slug: string;
  name: string;
  provider: string;
  family: string;
  release_date: string | null;
  modality: string;
  context_window_tokens: number | null;
  open_weights: boolean;
  reasoning: boolean;
  multimodal: boolean;
  input_price_per_million_usd: number | null;
  output_price_per_million_usd: number | null;
  license_name: string;
  availability: string;
};

export type ModelDetail = ModelSummary & {
  id: string;
  max_output_tokens: number | null;
  parameters: string | null;
  fine_tune_available: boolean;
  knowledge_cutoff: string | null;
  architecture: string;
  deployment_options: string[];
  typical_use_cases: string[];
  strengths: string[];
  limitations: string[];
  safety_notes: string;
  documentation_url: string;
  benchmarks: Record<string, string | number | null>;
  pricing_notes: string;
};

export type Comparison = {
  models: ModelDetail[];
  rows: {
    key: string;
    label: string;
    description: string;
    values: string[];
    differs: boolean;
  }[];
  summary: {
    model_count: number;
    open_weights_count: number;
    reasoning_count: number;
    multimodal_count: number;
    cheapest_input: string | null;
    largest_context: string | null;
  };
};

function apiBaseUrl() {
  if (typeof window === "undefined") {
    return (
      process.env.INTERNAL_API_URL ??
      process.env.NEXT_PUBLIC_API_URL ??
      "http://localhost:8000/api/v1"
    );
  }
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
}

async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`API request failed (${response.status})`);
  }
  return (await response.json()) as T;
}

export function listNews(limit = 12) {
  return apiGet<Page<StorySummary>>(`/news?limit=${limit}`);
}

export function getNews(slug: string) {
  return apiGet<StoryDetail>(`/news/${slug}`);
}

export function listArticles(limit = 12) {
  return apiGet<Page<StorySummary>>(`/articles?limit=${limit}`);
}

export function getArticle(slug: string) {
  return apiGet<StoryDetail>(`/articles/${slug}`);
}

export function listModels() {
  return apiGet<ModelSummary[]>("/models");
}

export function getModel(slug: string) {
  return apiGet<ModelDetail>(`/models/${slug}`);
}

export function compareModels(slugs: string[]) {
  const query = slugs.map((slug) => `slugs=${encodeURIComponent(slug)}`).join("&");
  return apiGet<Comparison>(`/models/compare?${query}`);
}

export function formatDate(value: string | null) {
  if (!value) {
    return "Undated";
  }
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
