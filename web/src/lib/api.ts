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

// Visual fashion search (Fashion-MNIST + CLIP)
export type VisualSearchMatch = {
  id: string;
  category: string;
  price?: number;
  stock_status?: string;
  similarity: number;
  style?: string;
  color?: string;
};

export type VisualSearchResponse = {
  visual_matches: number;
  top_matches: VisualSearchMatch[];
  avg_similarity: number;
  error?: string;
  demo_stats?: string;
  p95_latency?: string;
  accuracy?: string;
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
  { id: "p1", sku: "TENT-001", name: "MSR Hubba Hubba NX 2", description: "2-person backpacking tent, 1.72kg, freestanding", price: 189, category: "Tents", stock: 47, stock_status: "in_stock", shipping_zone: "CH", brand: "MSR", rating: 4.7, reviews_count: 1284, shipping_days: 2 },
  { id: "p2", sku: "TENT-002", name: "Big Agnes Copper Spur HV UL2", description: "Ultralight 2-person tent, 1.13kg, 3-season", price: 249, category: "Tents", stock: 12, stock_status: "in_stock", shipping_zone: "CH", brand: "Big Agnes", rating: 4.8, reviews_count: 892, shipping_days: 2 },
  { id: "p3", sku: "FOOT-001", name: "Salomon X Ultra 4 GTX", description: "Men's hiking shoes, Gore-Tex waterproof", price: 179, category: "Footwear", stock: 34, stock_status: "in_stock", shipping_zone: "CH", brand: "Salomon", rating: 4.6, reviews_count: 2341, shipping_days: 1 },
  { id: "p4", sku: "COOK-001", name: "MSR PocketRocket 2", description: "Ultralight backpacking stove, 73g", price: 49, category: "Cooking", stock: 89, stock_status: "in_stock", shipping_zone: "EU", brand: "MSR", rating: 4.9, reviews_count: 3102, shipping_days: 3 },
  { id: "p5", sku: "SLEEP-001", name: "Sea to Summit Spark SP1", description: "Sleeping bag, comfort -3°C, 850+ down", price: 239, category: "Sleeping", stock: 5, stock_status: "low_stock", shipping_zone: "CH", brand: "Sea to Summit", rating: 4.5, reviews_count: 567, shipping_days: 2 },
  { id: "p6", sku: "POLE-001", name: "Black Diamond Distance FLZ", description: "Carbon trekking poles, 3-section, pair", price: 169, category: "Poles", stock: 0, stock_status: "out_of_stock", shipping_zone: "CH", brand: "Black Diamond", rating: 4.4, reviews_count: 891, shipping_days: 5 },
  { id: "p7", sku: "TENT-003", name: "REI Co-op Kingdom 2", description: "2-person camping tent, spacious, easy setup", price: 198, category: "Tents", stock: 23, stock_status: "in_stock", shipping_zone: "CH", brand: "REI", rating: 4.6, reviews_count: 1567, shipping_days: 2 },
  { id: "p8", sku: "CLOTH-001", name: "Patagonia Nano Puff", description: "Insulated jacket, PrimaLoft, packable", price: 229, category: "Clothing", stock: 67, stock_status: "in_stock", shipping_zone: "EU", brand: "Patagonia", rating: 4.8, reviews_count: 4521, shipping_days: 3 },
  { id: "p9", sku: "SLEEP-002", name: "Marmot Trestles Elite 15", description: "Sleeping bag, comfort -9°C, synthetic", price: 159, category: "Sleeping", stock: 8, stock_status: "low_stock", shipping_zone: "CH", brand: "Marmot", rating: 4.3, reviews_count: 723, shipping_days: 2 },
  { id: "p10", sku: "FOOT-002", name: "La Sportiva TX4", description: "Approach shoes, Vibram sole, leather", price: 165, category: "Footwear", stock: 41, stock_status: "in_stock", shipping_zone: "CH", brand: "La Sportiva", rating: 4.7, reviews_count: 1102, shipping_days: 1 },
  { id: "p11", sku: "COOK-002", name: "Jetboil Flash", description: "Integrated cooking system, 1L, rapid boil", price: 119, category: "Cooking", stock: 56, stock_status: "in_stock", shipping_zone: "CH", brand: "Jetboil", rating: 4.6, reviews_count: 2890, shipping_days: 2 },
  { id: "p12", sku: "TENT-004", name: "Marmot Tungsten 2P", description: "2-person tent, DAC press-fit poles, waterproof", price: 219, category: "Tents", stock: 3, stock_status: "low_stock", shipping_zone: "EU", brand: "Marmot", rating: 4.2, reviews_count: 445, shipping_days: 4 },
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

  visualSearch: async (
    image: File,
    filters?: { stock_status?: string; price_max?: number; category?: string }
  ): Promise<VisualSearchResponse> => {
    const form = new FormData();
    form.append("image", image);
    if (filters && Object.keys(filters).length > 0) {
      form.append("filters", JSON.stringify(filters));
    }
    const res = await fetch(`${BASE_URL}/api/visual-search`, {
      method: "POST",
      body: form,
      signal: AbortSignal.timeout(30_000),
    });
    if (!res.ok) throw new Error(`${res.status}`);
    return res.json() as Promise<VisualSearchResponse>;
  },
};
