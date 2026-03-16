import { useState, useEffect } from "react";
import { MOCK_SCALE_METRICS } from "@/lib/api";
import { MetricCard } from "@/components/MetricCard";
import { Database, Zap, Layers, RefreshCw, CheckCircle, Server, GitBranch } from "lucide-react";
import { cn } from "@/lib/utils";

const LAYERS = [
  {
    id: 1, label: "Query Preprocessing", latency: "12ms", color: "text-status-info",
    bg: "bg-status-info/10 border-status-info/20",
    steps: [
      "Swiss German normalization (Zelt→tent, Franken→CHF)",
      "Intent classification (shop / query / voice)",
      "Query rewriting: 'under 200' → budget_max=200",
      "Multi-modal fusion (text+image query vector)",
    ],
  },
  {
    id: 2, label: "3-Tier Semantic Cache", latency: "4–35ms", color: "text-status-online",
    bg: "bg-status-online/10 border-status-online/20",
    steps: [
      "Redis exact match (4ms, TTL 5min, 62% hit)",
      "Qdrant query cache (28ms, 85% similarity, 19% hit)",
      "Qdrant goal cache (35ms, session patterns, 6% hit)",
      "Combined hit rate: 87%",
    ],
  },
  {
    id: 3, label: "Hybrid Retrieval", latency: "92ms", color: "text-primary",
    bg: "bg-primary/10 border-primary/20",
    steps: [
      "Qdrant text vector (all-mpnet, 384-dim, HNSW M=64)",
      "Qdrant image vector (CLIP ViT-B/32, 512-dim)",
      "Neo4j KG (category→brand→price_band)",
      "Cross-encoder reranker (ms-marco-MiniLM, NDCG+23%)",
      "Reciprocal Rank Fusion (RRF)",
    ],
  },
  {
    id: 4, label: "Context Engineering", latency: "187ms", color: "text-accent",
    bg: "bg-accent/10 border-accent/20",
    steps: [
      "Dynamic chunking (512→2048 tokens, semantic boundaries)",
      "Multi-pass RAG (coarse→fine→hypothesis)",
      "Provenance assembly ([1][2] confidence 0.92)",
      "Guardrails (temporal freshness, stock filter)",
    ],
  },
  {
    id: 5, label: "Agentic Execution", latency: "async", color: "text-status-warning",
    bg: "bg-status-warning/10 border-status-warning/20",
    steps: [
      "ShopperAgent: parse→upsert goal (atomic CAS)",
      "InventoryAgent: poll→solve→bundle (episodic)",
      "SupervisorAgent: rank→explain→stream SSE",
      "16 concurrent agents/store (semaphore pool)",
    ],
  },
  {
    id: 6, label: "Observability", latency: "real-time", color: "text-status-error",
    bg: "bg-status-error/10 border-status-error/20",
    steps: [
      "Prometheus: QPS, P95/P99.9, cache hit, grounding %",
      "Grafana: agent health, retrieval ablation dashboards",
      "Jaeger: end-to-end latency breakdown traces",
      "Slack alerts: >500ms P99.9, <85% cache hit",
    ],
  },
];

const SWISS_EXAMPLES = [
  { raw: "Zelt 2 Personen unter 200 Franken", canonical: "tent 2 person under 200 CHF", intent: "shop" },
  { raw: "Schlafsack für Freitag Zürich", canonical: "sleeping bag for Friday Zurich", intent: "shop" },
  { raw: "Wanderschuhe wasserdicht", canonical: "hiking boots waterproof", intent: "query" },
];

const QDRANT_COLLECTIONS = [
  { name: "products", dims: 384, distance: "COSINE", vectors: "10M", hnsw_m: 64, quant: "INT8" },
  { name: "episodes", dims: 768, distance: "DOT", vectors: "512K", hnsw_m: 32, quant: "INT8" },
  { name: "goals", dims: 384, distance: "COSINE", vectors: "347K", hnsw_m: 16, quant: "INT8" },
  { name: "solutions", dims: 512, distance: "COSINE", vectors: "289K", hnsw_m: 16, quant: "INT8" },
  { name: "querycache", dims: 384, distance: "COSINE", vectors: "50K", hnsw_m: 64, quant: "INT8" },
  { name: "goalcache", dims: 384, distance: "COSINE", vectors: "80K", hnsw_m: 64, quant: "INT8" },
];

function AnimatedNumber({ target, suffix = "" }: { target: number; suffix?: string }) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    const step = target / 40;
    let cur = 0;
    const t = setInterval(() => {
      cur = Math.min(cur + step, target);
      setVal(Math.floor(cur));
      if (cur >= target) clearInterval(t);
    }, 30);
    return () => clearInterval(t);
  }, [target]);
  return <>{val.toLocaleString()}{suffix}</>;
}

export default function ScalePage() {
  const [activeLayer, setActiveLayer] = useState<number | null>(null);
  const m = MOCK_SCALE_METRICS;

  return (
    <div className="p-6 space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-xs text-primary font-medium mb-1">
          <Layers className="w-3.5 h-3.5" /> 6-LAYER CONTEXT SYSTEM
        </div>
        <h1 className="text-2xl font-bold">Hyper-Scale RAG Architecture</h1>
        <p className="text-sm text-muted-foreground">10K QPS · P99.9 187ms · 87% cache hit · 92% grounded · 18M vectors</p>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {[
          { label: "Target QPS", value: <AnimatedNumber target={10000} />, sub: "Walmart-scale" },
          { label: "P99.9 Latency", value: "187ms", sub: "Binary quant" },
          { label: "Cache Hit", value: "87%", sub: "3-tier Redis+Qdrant" },
          { label: "Grounding", value: "92%", sub: "Provenance score" },
          { label: "Vectors", value: "18M", sub: "INT8 quantized" },
          { label: "Agents", value: "16", sub: "Semaphore pool" },
        ].map(({ label, value, sub }) => (
          <div key={label} className="rounded-xl border border-border bg-card p-3 text-center">
            <div className="text-xl font-bold text-gradient">{value}</div>
            <div className="text-xs font-medium text-foreground mt-0.5">{label}</div>
            <div className="text-xs text-muted-foreground">{sub}</div>
          </div>
        ))}
      </div>

      {/* 6-Layer pipeline */}
      <div>
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <GitBranch className="w-4 h-4 text-primary" /> 6-Layer Pipeline (click to expand)
        </h2>
        <div className="space-y-2">
          {LAYERS.map((layer) => {
            const open = activeLayer === layer.id;
            return (
              <div key={layer.id} className={cn("rounded-xl border transition-all cursor-pointer", layer.bg)} onClick={() => setActiveLayer(open ? null : layer.id)}>
                <div className="flex items-center gap-3 p-4">
                  <span className={cn("w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold border shrink-0", layer.bg)}>
                    {layer.id}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm">{layer.label}</span>
                      <span className={cn("text-xs font-mono", layer.color)}>{layer.latency}</span>
                    </div>
                  </div>
                  <span className={cn("text-xs transition-transform", open && "rotate-180")}>▼</span>
                </div>
                {open && (
                  <div className="px-4 pb-4 pt-0">
                    <ul className="space-y-1.5">
                      {layer.steps.map((s, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                          <CheckCircle className="w-3.5 h-3.5 text-status-online mt-0.5 shrink-0" />
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Swiss German preprocessing */}
      <div className="rounded-xl border border-border bg-card p-5 space-y-4">
        <h2 className="font-semibold flex items-center gap-2">
          🇨🇭 Swiss German Query Normalization
        </h2>
        <p className="text-sm text-muted-foreground">Layer 1 maps Swiss German dialect to canonical English before embedding.</p>
        <div className="space-y-2">
          {SWISS_EXAMPLES.map((ex) => (
            <div key={ex.raw} className="rounded-lg bg-muted p-3 grid grid-cols-[1fr_auto_1fr] gap-3 items-center text-sm">
              <span className="font-mono text-muted-foreground">"{ex.raw}"</span>
              <span className="text-primary text-center">→</span>
              <div className="flex items-center gap-2">
                <span className="font-mono">"{ex.canonical}"</span>
                <span className="text-xs px-1.5 py-0.5 rounded bg-primary/15 text-primary ml-auto">{ex.intent}</span>
              </div>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-3 gap-2 text-xs text-center">
          {[["Zelt", "tent"], ["Schlafsack", "sleeping bag"], ["Franken", "CHF"], ["unter", "under"], ["Freitag", "Friday"], ["Wanderschuhe", "hiking boots"]].map(([de, en]) => (
            <div key={de} className="rounded bg-muted/60 px-2 py-1.5">
              <span className="text-muted-foreground">{de}</span>
              <span className="text-primary mx-1">→</span>
              <span>{en}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Qdrant collections */}
      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <div className="px-5 py-4 border-b border-border flex items-center gap-2">
          <Database className="w-4 h-4 text-primary" />
          <h2 className="font-semibold">Qdrant Collections (18M vectors, INT8 quantized)</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/50">
                {["Collection", "Dims", "Distance", "Vectors", "HNSW M", "Quant"].map((h) => (
                  <th key={h} className="text-left px-4 py-3 font-medium text-muted-foreground">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {QDRANT_COLLECTIONS.map((c) => (
                <tr key={c.name} className="border-b border-border last:border-0 hover:bg-muted/20">
                  <td className="px-4 py-3 font-mono text-primary font-medium">{c.name}</td>
                  <td className="px-4 py-3 text-muted-foreground">{c.dims}</td>
                  <td className="px-4 py-3 text-muted-foreground">{c.distance}</td>
                  <td className="px-4 py-3 font-medium">{c.vectors}</td>
                  <td className="px-4 py-3 text-status-online">{c.hnsw_m}</td>
                  <td className="px-4 py-3">
                    <span className="text-xs px-2 py-0.5 rounded-full bg-accent/15 text-accent">{c.quant}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Cache tier breakdown */}
      <div className="rounded-xl border border-border bg-card p-5 space-y-4">
        <h2 className="font-semibold flex items-center gap-2">
          <Zap className="w-4 h-4 text-primary" /> 3-Tier Cache Breakdown (87% total hit)
        </h2>
        <div className="space-y-3">
          {m.cache_layers.map((layer) => (
            <div key={layer.name} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="font-medium">{layer.name}</span>
                <div className="flex items-center gap-3 text-muted-foreground">
                  <span className="text-status-online font-medium">{(layer.hit_rate * 100).toFixed(0)}% hit</span>
                  <span>{layer.latency_ms}ms</span>
                </div>
              </div>
              <div className="h-2 rounded-full bg-muted overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-primary to-accent transition-all" style={{ width: `${layer.hit_rate * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
        <div className="pt-2 border-t border-border flex items-center justify-between text-sm">
          <span className="font-semibold">Combined hit rate</span>
          <span className="text-xl font-bold text-gradient">87%</span>
        </div>
      </div>

      {/* Infrastructure */}
      <div className="rounded-xl border border-border bg-card p-5 space-y-3">
        <h2 className="font-semibold flex items-center gap-2">
          <Server className="w-4 h-4 text-primary" /> Docker Cluster (Production)
        </h2>
        <div className="grid sm:grid-cols-3 gap-3 text-sm">
          {[
            { name: "Qdrant", replicas: 3, image: "qdrant/qdrant:v1.10.1", port: "6333" },
            { name: "FastAPI backend", replicas: 16, image: "backend:latest", port: "8000" },
            { name: "Redis cluster", replicas: 1, image: "redis:7.2-stack", port: "6379" },
          ].map((svc) => (
            <div key={svc.name} className="rounded-lg bg-muted p-3 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-medium">{svc.name}</span>
                <span className="text-xs px-1.5 py-0.5 rounded-full bg-status-online/15 text-status-online">x{svc.replicas}</span>
              </div>
              <div className="font-mono text-xs text-muted-foreground">{svc.image}</div>
              <div className="text-xs text-muted-foreground">:{svc.port}</div>
            </div>
          ))}
        </div>
        <div className="rounded-lg bg-background/60 p-3 font-mono text-xs text-muted-foreground border border-border">
          <span className="text-status-online">$</span> docker-compose -f docker-compose.scale.yml up
          <br />
          <span className="text-muted-foreground/50"># → 10K QPS retail RAG in 90s. Production Day 1.</span>
        </div>
      </div>
    </div>
  );
}
