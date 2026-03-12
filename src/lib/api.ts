// API client for Multi-Agent Store Supervisor backend (FastAPI @ localhost:8000)
// Falls back to mock data when backend is offline — no console errors, no spam retries.

const BASE_URL = (import.meta.env.VITE_API_URL as string) || "http://localhost:8000";
export { BASE_URL };

// ─── Types ───────────────────────────────────────────────────────────────────

export type HealthResponse = { status: string; qdrant?: boolean; ok?: boolean };

export type MetricsResponse = {
  cache_hit: number;
  p95_latency_ms: number;
  p99_latency_ms?: number;
  qps?: number;
  total_goals?: number;
  total_solutions?: number;
  grounding_score?: number;
  active_agents?: number;
};

export type QueryResponse = {
  query: string;
  rag_answer: { answer: string; provenance?: ProvItem[] } | string;
  products_count?: number;
  episodes?: unknown[];
};

export type ProvItem = {
  id?: string | number;
  text?: string;
  source?: string;
  score?: number;
};

export type Goal = {
  id: string;
  text: string;
  status: "open" | "pending" | "fulfilled" | "failed";
  region?: string;
  created_at?: string;
  constraints?: Record<string, unknown>;
};

export type Solution = {
  id: string;
  goal_id: string;
  products: Product[];
  total_price?: number;
  currency?: string;
  eta?: string;
  confidence?: number;
  provenance?: ProvItem[];
};

export type Product = {
  id?: string;
  sku?: string;
  name?: string;
  title?: string;
  description?: string;
  price?: number;
  image_url?: string;
  category?: string;
  score?: number;
  stock?: number;
  stock_status?: "in_stock" | "low_stock" | "out_of_stock";
  shipping_zone?: "CH" | "EU" | "WORLD";
  brand?: string;
  rating?: number;
  reviews_count?: number;
  shipping_days?: number;
  updated_at?: string;
};

export type Episode = {
  id: string;
  goal_text?: string;
  bundle?: Product[];
  success_rate?: number;
  timestamp?: string;
  region?: string;
};

export type CacheLayer = "redis" | "qdrant_query" | "qdrant_goal" | "miss";

export type ScaleMetrics = {
  qps_target: number;
  qps_current: number;
  p99_9_latency_ms: number;
  cache_layers: { name: string; hit_rate: number; latency_ms: number }[];
  grounding_score: number;
  vector_count: number;
  active_agents: number;
};

// ─── Mock Data ────────────────────────────────────────────────────────────────

export const MOCK_METRICS: MetricsResponse = {
  cache_hit: 0.87,
  p95_latency_ms: 42,
  p99_latency_ms: 98,
  qps: 450,
  total_goals: 347,
  total_solutions: 289,
  grounding_score: 0.92,
  active_agents: 16,
};

export const MOCK_SCALE_METRICS: ScaleMetrics = {
  qps_target: 10000,
  qps_current: 450,
  p99_9_latency_ms: 187,
  grounding_score: 0.92,
  vector_count: 18_000_000,
  active_agents: 16,
  cache_layers: [
    { name: "Redis exact", hit_rate: 0.62, latency_ms: 4 },
    { name: "Qdrant query cache", hit_rate: 0.19, latency_ms: 28 },
    { name: "Qdrant goal cache", hit_rate: 0.06, latency_ms: 35 },
  ],
};

export const MOCK_GOALS: Goal[] = [
  { id: "g1", text: "2-person tent under 200CHF Zurich Friday", status: "fulfilled", region: "Zurich" },
  { id: "g2", text: "hiking boots waterproof size 42", status: "pending", region: "Zurich" },
  { id: "g3", text: "camping stove lightweight backpacking", status: "open", region: "Geneva" },
  { id: "g4", text: "sleeping bag -5°C winter Switzerland", status: "open", region: "Zurich" },
  { id: "g5", text: "trekking poles carbon fiber", status: "failed", region: "Basel" },
];

export const MOCK_EPISODES: Episode[] = [
  { id: "ep1", goal_text: "2-person tent Zurich weekend", success_rate: 0.92, region: "Zurich", timestamp: "2026-03-10T14:22:00Z" },
  { id: "ep2", goal_text: "hiking gear complete set", success_rate: 0.78, region: "Geneva", timestamp: "2026-03-09T10:11:00Z" },
  { id: "ep3", goal_text: "winter sleeping bag budget", success_rate: 0.85, region: "Zurich", timestamp: "2026-03-08T09:45:00Z" },
];

export const MOCK_PRODUCTS: Product[] = [
  { id: "p1", name: "MSR Hubba Hubba NX 2", description: "2-person backpacking tent, 1.72kg", price: 189, category: "Tents" },
  { id: "p2", name: "Big Agnes Copper Spur HV UL2", description: "Ultralight 2-person tent", price: 249, category: "Tents" },
  { id: "p3", name: "Salomon X Ultra 4 GTX", description: "Men's hiking shoes, Gore-Tex", price: 179, category: "Footwear" },
  { id: "p4", name: "MSR PocketRocket 2", description: "Ultralight backpacking stove", price: 49, category: "Cooking" },
  { id: "p5", name: "Sea to Summit Spark SP1", description: "Sleeping bag, comfort -3°C", price: 239, category: "Sleeping" },
  { id: "p6", name: "Black Diamond Distance FLZ", description: "Carbon trekking poles, pair", price: 169, category: "Poles" },
];

// ─── Backend health singleton (prevents hammering dead endpoint) ──────────────

let _backendOnline: boolean | null = null;
let _lastCheck = 0;
const HEALTH_TTL = 30_000; // only recheck every 30s

export async function checkBackendOnline(): Promise<boolean> {
  const now = Date.now();
  if (_backendOnline !== null && now - _lastCheck < HEALTH_TTL) return _backendOnline;
  try {
    const res = await fetch(`${BASE_URL}/health`, {
      signal: AbortSignal.timeout(3000),
    });
    _backendOnline = res.ok;
  } catch {
    _backendOnline = false;
  }
  _lastCheck = now;
  return _backendOnline;
}

// ─── Core fetcher (no retry noise in console) ─────────────────────────────────

async function fetchJSON<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...opts,
    signal: AbortSignal.timeout(5000),
    headers: { "Content-Type": "application/json", ...(opts?.headers ?? {}) },
  });
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json() as Promise<T>;
}

// ─── API (each call falls back if backend is offline) ────────────────────────

export const api = {
  health: () => fetchJSON<HealthResponse>("/health"),

  metrics: async (): Promise<MetricsResponse> => {
    const online = await checkBackendOnline();
    if (!online) return MOCK_METRICS;
    return fetchJSON<MetricsResponse>("/metrics").catch(() => MOCK_METRICS);
  },

  query: (q: string, collection = "demo_retail") =>
    fetchJSON<QueryResponse>(`/query?q=${encodeURIComponent(q)}&collection=${collection}`),

  createGoal: (text: string, region = "Zurich") =>
    fetchJSON<Goal>("/goals", { method: "POST", body: JSON.stringify({ text, region }) }),

  getGoals: async (): Promise<Goal[]> => {
    const online = await checkBackendOnline();
    if (!online) return MOCK_GOALS;
    return fetchJSON<Goal[]>("/goals").catch(() => MOCK_GOALS);
  },

  getSolution: (goalId: string) => fetchJSON<Solution>(`/solutions/${goalId}`),

  getEpisodes: async (): Promise<Episode[]> => {
    const online = await checkBackendOnline();
    if (!online) return MOCK_EPISODES;
    return fetchJSON<Episode[]>("/episodes").catch(() => MOCK_EPISODES);
  },

  getProducts: async (q?: string): Promise<Product[]> => {
    const online = await checkBackendOnline();
    if (!online) return MOCK_PRODUCTS;
    return fetchJSON<Product[]>(`/products${q ? `?q=${encodeURIComponent(q)}` : ""}`).catch(() => MOCK_PRODUCTS);
  },

  streamChat: (message: string, onChunk: (text: string) => void, onDone: () => void) => {
    const url = `${BASE_URL}/stream_query?q=${encodeURIComponent(message)}`;
    const es = new EventSource(url);
    const timeout = setTimeout(() => { onDone(); es.close(); }, 8000);
    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.token) onChunk(data.token);
        if (data.done) { clearTimeout(timeout); onDone(); es.close(); }
      } catch {
        onChunk(e.data);
      }
    };
    es.onerror = () => { clearTimeout(timeout); onDone(); es.close(); };
    return () => { clearTimeout(timeout); es.close(); };
  },
};
