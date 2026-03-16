import { useQuery } from "@tanstack/react-query";
import { api, MOCK_METRICS, MOCK_SCALE_METRICS } from "@/lib/api";
import { MetricCard } from "@/components/MetricCard";
import { Database, Clock, Zap, TrendingUp, BarChart3, Target } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis,
} from "recharts";

const LATENCY_DATA = [
  { label: "P50", value: 18, target: 20 },
  { label: "P75", value: 28, target: 35 },
  { label: "P90", value: 38, target: 50 },
  { label: "P95", value: 42, target: 60 },
  { label: "P99", value: 89, target: 120 },
  { label: "P99.9", value: 187, target: 250 },
];

const CACHE_TIMELINE = [
  { time: "00:00", hit: 82, miss: 18 },
  { time: "04:00", hit: 85, miss: 15 },
  { time: "08:00", hit: 87, miss: 13 },
  { time: "12:00", hit: 91, miss: 9 },
  { time: "16:00", hit: 89, miss: 11 },
  { time: "20:00", hit: 87, miss: 13 },
];

const ABLATION = [
  { name: "Full Stack (v6)", cacheHit: 87, latency: 42, grounding: 92, conversion: 124 },
  { name: "Full RAG (no cache)", cacheHit: 0, latency: 210, grounding: 88, conversion: 108 },
  { name: "BM25 only", cacheHit: 0, latency: 95, grounding: 61, conversion: 100 },
  { name: "Random baseline", cacheHit: 0, latency: 20, grounding: 0, conversion: 72 },
];

const RADAR_DATA = [
  { metric: "Cache Hit", value: 87, full: 100 },
  { metric: "Grounding", value: 92, full: 100 },
  { metric: "Conversion", value: 124, full: 150 },
  { metric: "QPS (norm)", value: 45, full: 100 },
  { metric: "Latency (inv)", value: 79, full: 100 },
];

const TOOLTIP_STYLE = {
  backgroundColor: "hsl(var(--card))",
  border: "1px solid hsl(var(--border))",
  borderRadius: "8px",
  color: "hsl(var(--foreground))",
  fontSize: "12px",
};

export default function MetricsPage() {
  const { data: metrics = MOCK_METRICS } = useQuery({
    queryKey: ["metrics"],
    queryFn: api.metrics,
    retry: 0,
    staleTime: 30_000,
    placeholderData: MOCK_METRICS,
  });
  const m = MOCK_SCALE_METRICS;

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">Performance Metrics</h1>
        <p className="text-sm text-muted-foreground">Qdrant Agentic RAG · 10K QPS target · P99.9 187ms</p>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="Cache Hit Rate" value={`${(metrics.cache_hit * 100).toFixed(0)}%`} icon={<Database className="w-4 h-4" />} trend={3} highlight description="3-tier Redis+Qdrant" />
        <MetricCard label="P95 Latency" value={metrics.p95_latency_ms} unit="ms" icon={<Clock className="w-4 h-4" />} trend={-8} description="P99.9: 187ms" />
        <MetricCard label="Grounding Score" value={`${((metrics.grounding_score ?? 0.92) * 100).toFixed(0)}%`} icon={<Target className="w-4 h-4" />} trend={4} description="Provenance-verified" />
        <MetricCard label="Conversion Lift" value="+24%" icon={<TrendingUp className="w-4 h-4" />} description="vs keyword baseline" />
      </div>

      {/* Scale targets */}
      <div className="rounded-xl border border-primary/20 bg-primary/5 p-5 space-y-3">
        <h2 className="font-semibold text-sm text-primary">Scale Targets (Production v6)</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
          {[
            { label: "Target QPS", current: "450", target: "10K", pct: 4.5 },
            { label: "P99.9", current: "187ms", target: "250ms ✓", pct: 100 },
            { label: "Cache Hit", current: "87%", target: "90%", pct: 97 },
            { label: "Vectors", current: "18M", target: "18M ✓", pct: 100 },
          ].map(({ label, current, target, pct }) => (
            <div key={label} className="space-y-1">
              <div className="text-xs text-muted-foreground">{label}</div>
              <div className="font-bold text-gradient">{current}</div>
              <div className="text-xs text-muted-foreground">target: {target}</div>
              <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${Math.min(pct, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Charts row 1 */}
      <div className="grid lg:grid-cols-2 gap-5">
        <div className="rounded-xl border border-border bg-card p-5 space-y-4">
          <h2 className="font-semibold text-sm flex items-center gap-2">
            <Clock className="w-4 h-4 text-primary" /> Latency Percentiles (ms) · actual vs target
          </h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={LATENCY_DATA} barCategoryGap="30%">
              <XAxis dataKey="label" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
              <Bar dataKey="value" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} name="Actual" />
              <Bar dataKey="target" fill="hsl(var(--border))" radius={[4, 4, 0, 0]} name="Target" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-xl border border-border bg-card p-5 space-y-4">
          <h2 className="font-semibold text-sm flex items-center gap-2">
            <Database className="w-4 h-4 text-primary" /> Cache Hit vs Miss Over Time (%)
          </h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={CACHE_TIMELINE}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="time" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
              <Line type="monotone" dataKey="hit" stroke="hsl(var(--status-online))" strokeWidth={2} dot={false} name="Hit %" />
              <Line type="monotone" dataKey="miss" stroke="hsl(var(--status-error))" strokeWidth={2} dot={false} name="Miss %" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts row 2 */}
      <div className="grid lg:grid-cols-2 gap-5">
        {/* Radar */}
        <div className="rounded-xl border border-border bg-card p-5 space-y-3">
          <h2 className="font-semibold text-sm flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-primary" /> System Capability Radar
          </h2>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={RADAR_DATA}>
              <PolarGrid stroke="hsl(var(--border))" />
              <PolarAngleAxis dataKey="metric" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} />
              <PolarRadiusAxis tick={false} axisLine={false} />
              <Radar dataKey="value" stroke="hsl(var(--primary))" fill="hsl(var(--primary))" fillOpacity={0.2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Cache tiers */}
        <div className="rounded-xl border border-border bg-card p-5 space-y-3">
          <h2 className="font-semibold text-sm flex items-center gap-2">
            <Zap className="w-4 h-4 text-primary" /> Cache Tier Performance
          </h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={m.cache_layers.map(l => ({ name: l.name.split(" ")[0], hitRate: Math.round(l.hit_rate * 100), latency: l.latency_ms }))} layout="vertical">
              <XAxis type="number" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis dataKey="name" type="category" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} axisLine={false} tickLine={false} width={48} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
              <Bar dataKey="hitRate" fill="hsl(var(--status-online))" radius={[0, 4, 4, 0]} name="Hit %" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Ablation table */}
      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <div className="px-5 py-4 border-b border-border">
          <h2 className="font-semibold text-sm flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-primary" /> Ablation Study
          </h2>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              {["System", "Cache Hit", "P95 Latency", "Grounding", "Conv. Index"].map((h) => (
                <th key={h} className="text-left px-5 py-3 font-medium text-muted-foreground">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ABLATION.map((row, i) => (
              <tr key={row.name} className={`border-b border-border last:border-0 ${i === 0 ? "bg-primary/5" : ""}`}>
                <td className={`px-5 py-3 font-medium ${i === 0 ? "text-primary" : ""}`}>{row.name} {i === 0 && "⭐"}</td>
                <td className="px-5 py-3 text-status-online">{row.cacheHit}%</td>
                <td className="px-5 py-3">{row.latency}ms</td>
                <td className="px-5 py-3">{row.grounding}%</td>
                <td className="px-5 py-3">{row.conversion}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
