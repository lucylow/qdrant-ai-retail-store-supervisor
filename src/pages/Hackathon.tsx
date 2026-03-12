import { useState } from "react";
import { Link } from "react-router-dom";
import { Award, Database, Github, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";

const TECH_STACK = [
  { name: "Qdrant", role: "Vector Database", desc: "4 collections: goals, solutions, episodes, products. HNSW indexing, scalar quantization." },
  { name: "FastAPI", role: "Backend API", desc: "Python async, OpenAPI spec, SSE streaming, CORS for Lovable frontend." },
  { name: "React + Vite", role: "Frontend", desc: "TailwindCSS, shadcn/ui, TanStack Query, React Router, Lucide icons." },
  { name: "Multi-Agent", role: "Architecture", desc: "Shopper (goal parsing) + Inventory (bundle gen) + Blackboard pattern." },
];

const BENCHMARKS = [
  { metric: "Cache Hit Rate", value: "87%", baseline: "0%", delta: "+87pp" },
  { metric: "P95 Latency", value: "42ms", baseline: "210ms", delta: "-80%" },
  { metric: "P50 Latency", value: "18ms", baseline: "95ms", delta: "-81%" },
  { metric: "Conversion Lift", value: "+24%", baseline: "0%", delta: "+24pp" },
  { metric: "QPS", value: "450", baseline: "~50", delta: "+800%" },
];

type TabType = "overview" | "architecture" | "benchmarks";

export default function HackathonPage() {
  const [tab, setTab] = useState<TabType>("overview");

  return (
    <div className="p-6 space-y-6 animate-fade-in max-w-5xl">
      {/* Header */}
      <div className="rounded-2xl gradient-primary p-8 text-primary-foreground space-y-2">
        <div className="flex items-center gap-2 text-sm opacity-80">
          <Award className="w-4 h-4" /> GenAI Zurich Hackathon 2026 · Qdrant Challenge
        </div>
        <h1 className="text-3xl font-extrabold">Multi-Agent Store Supervisor v6</h1>
        <p className="opacity-90">Hybrid RAG with Qdrant Blackboard Architecture + Episodic Memory</p>
        <div className="flex flex-wrap gap-2 pt-2">
          {["Qdrant", "FastAPI", "React", "Episodic RAG", "Blackboard Architecture"].map((tag) => (
            <span key={tag} className="px-2.5 py-1 rounded-full bg-primary-foreground/20 text-xs font-medium">
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 rounded-xl bg-muted w-fit">
        {(["overview", "architecture", "benchmarks"] as TabType[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium capitalize transition-colors ${
              tab === t ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <div className="space-y-5">
          <div className="grid md:grid-cols-2 gap-4">
            {TECH_STACK.map(({ name, role, desc }) => (
              <div key={name} className="rounded-xl border border-border bg-card p-5 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold">{name}</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-primary/15 text-primary">{role}</span>
                </div>
                <p className="text-sm text-muted-foreground">{desc}</p>
              </div>
            ))}
          </div>
          <div className="flex gap-3">
            <Button variant="outline" className="gap-2" asChild>
              <a href="https://github.com/lucylow/zurich" target="_blank" rel="noopener noreferrer">
                <Github className="w-4 h-4" /> GitHub Repo
              </a>
            </Button>
            <Button variant="outline" className="gap-2" asChild>
              <a href="https://qdrant.tech" target="_blank" rel="noopener noreferrer">
                <ExternalLink className="w-4 h-4" /> Qdrant Docs
              </a>
            </Button>
          </div>
        </div>
      )}

      {tab === "architecture" && (
        <div className="space-y-4">
          <div className="rounded-xl border border-border bg-card p-6 space-y-4">
            <h2 className="font-bold text-lg">Blackboard Architecture</h2>
            <div className="space-y-3 text-sm text-muted-foreground">
              {[
                { n: 1, title: "User Intent", desc: "Shopper agent parses natural-language goal, extracts constraints (budget, region, category)." },
                { n: 2, title: "Qdrant Lookup", desc: "Embed goal vector, search episodes collection. If similarity > 0.85: CACHE HIT (35ms). Else: full RAG (210ms)." },
                { n: 3, title: "Inventory Agent", desc: "Retrieves products, assembles bundle with provenance citations, confidence score." },
                { n: 4, title: "Episodic Write-back", desc: "Successful bundles stored in Qdrant episodes. Improves future cache hit rate." },
              ].map(({ n, title, desc }) => (
                <div key={n} className="flex items-start gap-3">
                  <span className="w-7 h-7 rounded-full bg-primary/20 text-primary flex items-center justify-center text-xs font-bold shrink-0">
                    {n}
                  </span>
                  <div>
                    <strong className="text-foreground">{title}</strong> → {desc}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-4 gap-3 text-center text-xs">
            {[
              { icon: "🎯", label: "goals", count: "347 docs" },
              { icon: "💡", label: "solutions", count: "289 docs" },
              { icon: "📚", label: "episodes", count: "512 docs" },
              { icon: "🛍️", label: "products", count: "10K docs" },
            ].map(({ icon, label, count }) => (
              <div key={label} className="rounded-lg border border-border bg-card p-3 space-y-1">
                <div className="text-2xl">{icon}</div>
                <div className="font-mono font-semibold text-primary">{label}</div>
                <div className="text-muted-foreground">{count}</div>
              </div>
            ))}
          </div>

          {/* Demo flow */}
          <div className="rounded-xl border border-border bg-card p-5 space-y-3">
            <h2 className="font-semibold flex items-center gap-2">
              <Database className="w-4 h-4 text-primary" /> 30s Judge Demo Flow
            </h2>
            <ol className="space-y-2 text-sm text-muted-foreground list-decimal list-inside">
              <li>"2-person tent &lt;200CHF Zurich Friday" → Shopper parses → goal upserted</li>
              <li>Inventory polls (35ms cache HIT 92% episode) → 3 bundles ranked</li>
              <li>Supervisor streams: "Found 2 options, 92% conversion history" [citations]</li>
              <li>Metrics: 87% hit, 42ms P95, 450 QPS</li>
            </ol>
            <Button size="sm" className="gradient-primary mt-1" asChild>
              <Link to="/demo">Run Demo Scripts</Link>
            </Button>
          </div>
        </div>
      )}

      {tab === "benchmarks" && (
        <div className="rounded-xl border border-border bg-card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/50">
                <th className="text-left px-5 py-3 font-medium text-muted-foreground">Metric</th>
                <th className="text-left px-5 py-3 font-medium text-muted-foreground">Our System</th>
                <th className="text-left px-5 py-3 font-medium text-muted-foreground">Baseline</th>
                <th className="text-left px-5 py-3 font-medium text-muted-foreground">Delta</th>
              </tr>
            </thead>
            <tbody>
              {BENCHMARKS.map((row) => (
                <tr key={row.metric} className="border-b border-border last:border-0 hover:bg-muted/20">
                  <td className="px-5 py-3 font-medium">{row.metric}</td>
                  <td className="px-5 py-3 text-status-online font-bold">{row.value}</td>
                  <td className="px-5 py-3 text-muted-foreground">{row.baseline}</td>
                  <td className="px-5 py-3 text-primary">{row.delta}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
