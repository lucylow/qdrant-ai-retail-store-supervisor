import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Database, Zap, ArrowRight, Bot, BookOpen, ShoppingBag, BarChart3, Award,
  Sparkles, Brain, ShieldCheck, MessageSquare, Search, Camera, Image, Package,
  Cpu, Network, TrendingUp, Eye, Layers, Target, Clock, CreditCard, Globe,
  CheckCircle, MapPin, Calendar, Shield,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

// ── Features ────────────────────────────────────────────────────────────────
const FEATURES = [
  { icon: Bot, title: "Multi-Agent System", desc: "Shopper + Inventory agents with blackboard architecture and episodic RAG memory." },
  { icon: Database, title: "Qdrant Vector Memory", desc: "Goals, solutions, episodes, products stored as vectors. 87% cache hit rate." },
  { icon: BookOpen, title: "Episodic Learning", desc: "Agents learn from past interactions. P95 latency 42ms, +24% conversion." },
  { icon: ShoppingBag, title: "Smart Bundles", desc: "Context-aware product recommendations with provenance citations." },
  { icon: BarChart3, title: "Real-time Metrics", desc: "Live dashboard with QPS, cache hit, P95 latency tracking." },
  { icon: Award, title: "Hackathon Ready", desc: "GenAI Zurich 2026 – Qdrant Challenge demo in under 5 minutes." },
];

const DEMO_QUERIES = [
  "2-person tent under 200CHF Zurich Friday",
  "waterproof hiking boots size 42 lightweight",
  "Bio-Milch morgen 10h TWINT",
];

// ── 5 Qdrant Collections ────────────────────────────────────────────────────
const QDRANT_COLLECTIONS = [
  { name: "swiss_products", dim: 384, model: "BGE-M3", payload: "sku, name_de/fr/it, category, stock, price_chf, holiday_multiplier", filter: 'category=="dairy" & stock<10', color: "border-primary/30 bg-primary/5" },
  { name: "holiday_episodes", dim: 384, model: "BGE-M3", payload: "date, multiplier, category, canton", filter: "multiplier>2.0", color: "border-accent/30 bg-accent/5" },
  { name: "pickup_windows", dim: 128, model: "Linear", payload: "window_start, tenant, capacity", filter: "capacity>0 & tenant", color: "border-status-info/30 bg-status-info/5" },
  { name: "twint_payments", dim: 256, model: "MiniLM", payload: "payment_id, phone_hash, amount_chf, status", filter: 'status=="captured"', color: "border-status-warning/30 bg-status-warning/5" },
  { name: "customer_conversations", dim: 384, model: "BGE-M3", payload: "customer_id, tenant, intent", filter: 'intent=="pickup_scheduling"', color: "border-status-online/30 bg-status-online/5" },
];

// ── 4 Agents ─────────────────────────────────────────────────────────────────
const AGENTS = [
  {
    name: "Holiday Inventory Supervisor",
    icon: Calendar,
    desc: "Christmas 4× dairy, Fondue 1.5× cheese, safety stock with cantonal awareness.",
    example: '"Bio-Milch für Weihnachten morgen" → demand_multiplier: 4.0, safety_stock: 120',
    qdrant: "Queries holiday_episodes with filter multiplier>2.0",
    color: "border-primary/30",
  },
  {
    name: "TWINT Checkout Agent",
    icon: CreditCard,
    desc: "QR code generation, PostFinance fallback, Apple Pay. 52% Swiss market share.",
    example: "POST /checkout/twint → QR code → webhook → inventory auto-decrement",
    qdrant: "Stores payment episodes for fraud detection",
    color: "border-accent/30",
  },
  {
    name: "Swiss Scheduling Agent",
    icon: Clock,
    desc: '"morgen 10h47 Zürich HB" → 08:00-12:00 window. 24h format, ±15min tolerance.',
    example: "parse('morgen 10h') → {window: '08:00-12:00', punctuality: 0.95}",
    qdrant: "Searches pickup_windows with capacity>0 filter",
    color: "border-status-info/30",
  },
  {
    name: "RAG Orchestrator",
    icon: Network,
    desc: "Unifies all agents: semantic search → holiday multiplier → pickup → TWINT checkout.",
    example: '"Bio-Milch morgen 10h TWINT" → CHF 4.95, pickup morgen 08:00-12:00',
    qdrant: "Multi-collection search with LangChain tools",
    color: "border-status-online/30",
  },
];

// ── Named Vectors ────────────────────────────────────────────────────────────
const NAMED_VECTORS = [
  { name: "text_vector", size: 1536, model: "all-MiniLM-L6-v2", desc: "Title + description embedding" },
  { name: "image_vector", size: 512, model: "CLIP ViT-B/32", desc: "Product photo embedding" },
  { name: "metadata_vector", size: 128, model: "Linear projection", desc: "Category + price band encoding" },
];

// ── Fusion Strategies ────────────────────────────────────────────────────────
const FUSION_STRATEGIES = [
  { name: "Early Fusion", desc: "Concatenate text+image → single 2048-dim", icon: "🔗" },
  { name: "Late Fusion (RRF)", desc: "Parallel searches, combine scores", icon: "⚡" },
  { name: "Cross-Modal", desc: "Text → image-similar products", icon: "🔄" },
];

// ── Visual Demo Products ─────────────────────────────────────────────────────
const VISUAL_RESULTS = [
  { name: "REI Co-op Half Dome 2+", price: 178, match: 92, delivery: "Thu" },
  { name: "Mountain Hardwear Mineral King 2", price: 195, match: 87, delivery: "Fri" },
  { name: "NorthFace Stormbreak 2", price: 199, match: 91, delivery: "2-day" },
];

// ── Live Demo Chat ───────────────────────────────────────────────────────────
function LiveDemoChat() {
  const [step, setStep] = useState(0);
  const steps = [
    { role: "user", text: "Bio-Milch morgen 10h Zürich HB, TWINT bitte" },
    { role: "shopper", text: "📥 Parsing: category=dairy, time=morgen 10h, location=Zürich HB, payment=TWINT" },
    { role: "inventory", text: "📦 Holiday check: Christmas 4× demand → safety_stock=120, current=45 → ⚠️ replenish triggered" },
    { role: "scheduler", text: "🕐 Window: morgen 08:00-12:00 (capacity: 18/25), punctuality: 95%" },
    { role: "twint", text: "💳 TWINT QR generated: CHF 4.95, order_id=ord_abc123, expires 10min" },
    { role: "result", text: "✅ Bio-Milch 1L → CHF 4.95 (holiday +25%), pickup morgen 08:00-12:00 Zürich HB, TWINT QR ready" },
  ];

  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
        <MessageSquare className="w-5 h-5 text-primary" />
        Live 4-Agent Demo
      </h3>
      <div className="space-y-3 min-h-[220px]">
        {steps.slice(0, step + 1).map((s, i) => (
          <div key={i} className={cn(
            "text-sm px-4 py-2.5 rounded-xl max-w-[90%] animate-fade-in",
            s.role === "user" ? "ml-auto bg-primary text-primary-foreground" :
            s.role === "result" ? "bg-status-online/10 border border-status-online/30 text-foreground" :
            "bg-muted text-foreground"
          )}>
            {s.text}
          </div>
        ))}
      </div>
      <div className="flex gap-2 mt-4">
        <Button size="sm" variant="outline" onClick={() => setStep(0)}>Reset</Button>
        <Button size="sm" onClick={() => setStep(Math.min(step + 1, steps.length - 1))} disabled={step >= steps.length - 1}>
          Next Step <ArrowRight className="w-3 h-3 ml-1" />
        </Button>
        <Button size="sm" variant="secondary" onClick={() => setStep(steps.length - 1)}>Run All</Button>
      </div>
    </div>
  );
}

export default function LandingPage() {
  const [activeAgent, setActiveAgent] = useState(0);
  const [visualStep, setVisualStep] = useState(0);

  return (
    <div className="min-h-screen flex flex-col">
      {/* ══════════════════════════════════════════════════════════════════════
          HERO
      ══════════════════════════════════════════════════════════════════════ */}
      <section className="relative flex-1 flex flex-col items-center justify-center px-6 py-24 text-center overflow-hidden">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-primary/5 blur-[120px]" />
          <div className="absolute top-1/3 right-1/4 w-[300px] h-[300px] rounded-full bg-accent/5 blur-[80px]" />
        </div>
        <div className="relative z-10 max-w-4xl mx-auto space-y-6 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium">
            <Award className="w-3.5 h-3.5" />
            GenAI Zurich Hackathon 2026 · Qdrant Challenge
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight">
            <span className="text-foreground">Multi-Agent</span><br />
            <span className="text-gradient">Store Supervisor</span>
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Production-grade Swiss retail platform with 4 Qdrant-powered agents,
            TWINT payments, holiday forecasting, and multimodal search.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <Button size="lg" className="gradient-primary text-primary-foreground font-semibold shadow-lg hover:opacity-90 gap-2" asChild>
              <Link to="/chat">Try Demo <ArrowRight className="w-4 h-4" /></Link>
            </Button>
            <Button size="lg" variant="outline" className="gap-2" asChild>
              <Link to="/dashboard"><BarChart3 className="w-4 h-4" /> Dashboard</Link>
            </Button>
          </div>
          <div className="flex flex-wrap justify-center gap-2 pt-4">
            {DEMO_QUERIES.map((q) => (
              <Link key={q} to={`/chat?q=${encodeURIComponent(q)}`}>
                <span className="text-xs px-3 py-1.5 rounded-full bg-muted border border-border text-muted-foreground hover:text-foreground hover:border-primary/30 transition-colors cursor-pointer">
                  "{q}"
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════════════
          PRODUCTION METRICS
      ══════════════════════════════════════════════════════════════════════ */}
      <section className="border-t border-border bg-card/50 py-10 px-6">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-6 gap-6 text-center">
          {[
            { label: "Qdrant QPS", value: "500+" },
            { label: "P95 Latency", value: "42ms" },
            { label: "TWINT Share", value: "52%" },
            { label: "Stockout ↓", value: "67%" },
            { label: "Punctuality", value: "95%" },
            { label: "Collections", value: "5" },
          ].map(({ label, value }) => (
            <div key={label}>
              <div className="text-3xl font-bold text-gradient">{value}</div>
              <div className="text-sm text-muted-foreground mt-1">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════════════
          5 QDRANT COLLECTIONS
      ══════════════════════════════════════════════════════════════════════ */}
      <section className="py-20 px-6 bg-background">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-4">
              <Database className="w-3.5 h-3.5" /> Core Infrastructure
            </div>
            <h2 className="text-3xl font-bold">5 Qdrant Collections</h2>
            <p className="text-muted-foreground mt-2">Swiss retail vectors with payload indexing and sub-50ms filtering.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {QDRANT_COLLECTIONS.map((c) => (
              <div key={c.name} className={cn("rounded-xl border p-5", c.color)}>
                <div className="flex items-center gap-2 mb-3">
                  <Database className="w-4 h-4 text-primary" />
                  <code className="font-mono text-sm font-semibold">{c.name}</code>
                </div>
                <div className="space-y-1.5 text-xs text-muted-foreground">
                  <div><span className="text-foreground font-medium">Dim:</span> {c.dim}d · {c.model}</div>
                  <div><span className="text-foreground font-medium">Payload:</span> {c.payload}</div>
                  <div><span className="text-foreground font-medium">Filter:</span> <code className="bg-background px-1 rounded">{c.filter}</code></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════════════
          4 SPECIALIZED AGENTS
      ══════════════════════════════════════════════════════════════════════ */}
      <section className="py-20 px-6 bg-muted/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-4">
              <Bot className="w-3.5 h-3.5" /> Agent Architecture
            </div>
            <h2 className="text-3xl font-bold">4 Specialized Agents</h2>
            <p className="text-muted-foreground mt-2">Each agent reads/writes Qdrant collections via the blackboard pattern.</p>
          </div>
          <div className="grid lg:grid-cols-2 gap-6">
            {AGENTS.map((agent, i) => (
              <button
                key={agent.name}
                onClick={() => setActiveAgent(i)}
                className={cn(
                  "rounded-xl border p-6 text-left transition-all",
                  activeAgent === i ? "border-primary bg-primary/5 shadow-md" : "border-border bg-card hover:border-primary/30"
                )}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <agent.icon className="w-5 h-5 text-primary" />
                  </div>
                  <h3 className="font-semibold">{agent.name}</h3>
                </div>
                <p className="text-sm text-muted-foreground mb-3">{agent.desc}</p>
                <div className="space-y-2 text-xs">
                  <div className="p-2 rounded-lg bg-muted/50 font-mono">{agent.example}</div>
                  <div className="flex items-center gap-1.5 text-muted-foreground">
                    <Database className="w-3 h-3" /> {agent.qdrant}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════════════
          LIVE 4-AGENT DEMO
      ══════════════════════════════════════════════════════════════════════ */}
      <section className="py-20 px-6 bg-background">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold">🤖 Live Multi-Agent Demo</h2>
            <p className="text-muted-foreground mt-2">Watch 4 agents coordinate through Qdrant blackboard memory.</p>
          </div>
          <LiveDemoChat />
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════════════
          MULTIMODAL SEARCH: TEXT + IMAGES + INVENTORY
      ══════════════════════════════════════════════════════════════════════ */}
      <section className="py-20 px-6 bg-muted/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent/10 border border-accent/20 text-accent text-sm font-medium mb-4">
              <Camera className="w-3.5 h-3.5" /> Advanced Search
            </div>
            <h2 className="text-3xl font-bold">🖼️ Multimodal Hybrid Search</h2>
            <p className="text-muted-foreground mt-2 max-w-2xl mx-auto">
              Qdrant named vectors fuse text goals, product images, and inventory metadata.
              "Show me something like this tent" → 92% visual match in 8ms.
            </p>
          </div>

          {/* Named Vectors */}
          <div className="rounded-xl border border-border bg-card p-6 mb-8">
            <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
              <Database className="w-5 h-5 text-primary" /> Named Vectors Architecture
            </h3>
            <div className="grid md:grid-cols-3 gap-4">
              {NAMED_VECTORS.map((v) => (
                <div key={v.name} className="rounded-lg border border-border bg-muted/30 p-4">
                  <code className="text-primary font-mono text-sm">{v.name}</code>
                  <p className="text-xs text-muted-foreground mt-1">{v.size}d · {v.model}</p>
                  <p className="text-xs text-muted-foreground">{v.desc}</p>
                </div>
              ))}
            </div>
            <div className="mt-4 rounded-lg bg-muted/50 p-4 font-mono text-xs text-muted-foreground overflow-x-auto">
              <span className="text-primary">POST</span> /collections/products/points/search<br />
              {`{ "vector": {"name": "image_vector", "vector": [0.1, ...]},`}<br />
              {`  "filter": {"must": [{"key": "stock_status", "match": {"value": "in_stock"}}]},`}<br />
              {`  "limit": 5, "with_payload": true }`}
            </div>
          </div>

          {/* Fusion Strategies */}
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            {FUSION_STRATEGIES.map((f) => (
              <div key={f.name} className="rounded-xl border border-border bg-card p-5">
                <div className="text-2xl mb-2">{f.icon}</div>
                <h4 className="font-semibold text-sm">{f.name}</h4>
                <p className="text-xs text-muted-foreground mt-1">{f.desc}</p>
              </div>
            ))}
          </div>

          {/* Visual Demo Flow */}
          <div className="rounded-xl border border-border bg-card p-6 mb-8">
            <h3 className="font-semibold text-lg mb-4">📱 Visual-First Recommendation Demo</h3>
            <div className="grid md:grid-cols-3 gap-4">
              <button onClick={() => setVisualStep(0)} className={cn("rounded-lg border p-5 text-center transition-all", visualStep === 0 ? "border-primary bg-primary/5" : "border-border")}>
                <div className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary inline-block mb-3">Step 1</div>
                <Camera className="w-10 h-10 mx-auto text-muted-foreground/50 mb-2" />
                <p className="text-sm">Upload tent photo</p>
              </button>
              <button onClick={() => setVisualStep(1)} className={cn("rounded-lg border p-5 text-center transition-all", visualStep === 1 ? "border-primary bg-primary/5" : "border-border")}>
                <div className="text-xs px-2 py-0.5 rounded-full bg-accent/10 text-accent inline-block mb-3">Step 2</div>
                <Cpu className="w-10 h-10 mx-auto text-muted-foreground/50 mb-2" />
                <p className="text-sm">CLIP embed + filter</p>
                <p className="text-xs text-muted-foreground mt-1">price&lt;200 CHF, in_stock, CH</p>
              </button>
              <button onClick={() => setVisualStep(2)} className={cn("rounded-lg border p-5 text-center transition-all", visualStep === 2 ? "border-primary bg-primary/5" : "border-border")}>
                <div className="text-xs px-2 py-0.5 rounded-full bg-status-online/10 text-status-online inline-block mb-3">Step 3</div>
                <Package className="w-10 h-10 mx-auto text-muted-foreground/50 mb-2" />
                <p className="text-sm">Ranked results</p>
              </button>
            </div>
            {visualStep === 2 && (
              <div className="mt-4 space-y-2 animate-fade-in">
                {VISUAL_RESULTS.map((r) => (
                  <div key={r.name} className="flex items-center justify-between p-3 rounded-lg bg-muted/50 border border-border">
                    <div>
                      <span className="font-medium text-sm">🏕️ {r.name}</span>
                      <span className="text-xs text-muted-foreground ml-2">({r.match}% visual match)</span>
                    </div>
                    <div className="text-right">
                      <span className="font-semibold text-sm">{r.price} CHF</span>
                      <span className="text-xs text-muted-foreground ml-2">{r.delivery}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Impact Stats */}
          <div className="grid grid-cols-3 gap-4">
            <div className="rounded-xl border border-primary/20 bg-primary/5 p-5 text-center">
              <div className="text-2xl font-bold text-primary">+59%</div>
              <p className="text-xs text-muted-foreground mt-1">Visual vs text-only conversion</p>
            </div>
            <div className="rounded-xl border border-accent/20 bg-accent/5 p-5 text-center">
              <div className="text-2xl font-bold text-accent">8ms</div>
              <p className="text-xs text-muted-foreground mt-1">P95 multi-vector search</p>
            </div>
            <div className="rounded-xl border border-status-online/20 bg-status-online/5 p-5 text-center">
              <div className="text-2xl font-bold text-status-online">96%</div>
              <p className="text-xs text-muted-foreground mt-1">Constraint compliance</p>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════════════
          GENERATIVE AI SECTION
      ══════════════════════════════════════════════════════════════════════ */}
      <section className="py-20 px-6 bg-background">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-4">
              <Sparkles className="w-3.5 h-3.5" /> Generative AI
            </div>
            <h2 className="text-3xl font-bold">🎯 Appropriate & Effective Use of GenAI</h2>
            <p className="text-muted-foreground mt-2 max-w-2xl mx-auto">
              LLMs handle language understanding, explanation, and planning. Core business logic stays deterministic.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Shopper Agent */}
            <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <MessageSquare className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-semibold text-lg">Shopper Agent: NLU</h3>
              </div>
              <ul className="space-y-3 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span><strong className="text-foreground">Intent extraction:</strong> "Bio-Milch morgen 10h Zürich HB" → {'{category, time, location, payment}'} structured goal for Qdrant.</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span><strong className="text-foreground">Conflict resolution:</strong> Budget too low for delivery deadline? LLM asks targeted follow-ups instead of failing.</span>
                </li>
              </ul>
            </div>

            {/* Inventory Agent */}
            <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Brain className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-semibold text-lg">Inventory Agent: Explanation</h3>
              </div>
              <ul className="space-y-3 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span><strong className="text-foreground">Trade-off synthesis:</strong> Calls real APIs for stock/prices, then LLM explains: "Option A is 15 CHF cheaper but arrives 2 days later."</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span><strong className="text-foreground">Episodic grounding:</strong> Retrieves similar past goal–solution pairs from Qdrant before planning—no hallucinated strategies.</span>
                </li>
              </ul>
            </div>
          </div>

          {/* RAG Interaction */}
          <div className="rounded-xl border border-primary/20 bg-gradient-to-r from-primary/5 to-muted p-6 mb-8">
            <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
              <Database className="w-5 h-5 text-primary" />
              GenAI ↔ Qdrant: Retrieval-Augmented Reasoning
            </h3>
            <div className="grid sm:grid-cols-2 gap-6 text-sm">
              <div>
                <h4 className="font-medium text-foreground mb-2">📥 Outputs → Memory</h4>
                <p className="text-muted-foreground">Goals, solutions, outcomes embedded in Qdrant. Each episode pairs goal + solution + outcome for long-term searchable memory.</p>
              </div>
              <div>
                <h4 className="font-medium text-foreground mb-2">🔍 Memory → Prompts</h4>
                <p className="text-muted-foreground">Before proposing bundles, agents retrieve similar successful episodes and inject them into LLM context. Grounded in what historically worked.</p>
              </div>
            </div>
          </div>

          {/* Guardrails */}
          <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-6">
            <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-destructive" />
              Guardrails: Deterministic Business Logic
            </h3>
            <div className="flex flex-wrap gap-2">
              {["Stock availability", "Exact prices", "TWINT payments", "Pickup capacity", "Holiday multipliers", "Qdrant status updates"].map((item) => (
                <span key={item} className="text-xs px-3 py-1.5 rounded-full bg-background border border-border text-foreground">
                  ✓ {item}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════════════
          DATASETS
      ══════════════════════════════════════════════════════════════════════ */}
      <section className="py-16 px-6 bg-muted/30">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-8">📊 Production Datasets</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="rounded-xl border border-border bg-primary/5 p-6 text-center">
              <h3 className="text-xl font-bold mb-4">OTTO Kaggle</h3>
              <div className="grid grid-cols-2 gap-3 text-sm mb-4">
                <div><strong>14M</strong> sessions</div>
                <div><strong>21M</strong> events</div>
                <div><strong>1.9M</strong> products</div>
                <div><strong>8ms</strong> P95</div>
              </div>
            </div>
            <div className="rounded-xl border border-border bg-accent/5 p-6 text-center">
              <h3 className="text-xl font-bold mb-4">RetailRocket</h3>
              <div className="grid grid-cols-2 gap-3 text-sm mb-4">
                <div><strong>2.7M</strong> events</div>
                <div><strong>1.4M</strong> items</div>
                <div><strong>417K</strong> visitors</div>
                <div><strong>8.2%</strong> conversion</div>
              </div>
            </div>
            <div className="rounded-xl border border-border bg-status-warning/5 p-6 text-center">
              <h3 className="text-xl font-bold mb-4">Qdrant Discovery</h3>
              <div className="grid grid-cols-2 gap-3 text-sm mb-4">
                <div><strong>92%</strong> precision</div>
                <div><strong>4</strong> contexts</div>
                <div><strong>18ms</strong> P95</div>
                <div><strong>59%</strong> lift</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════════════
          ARCHITECTURE HIGHLIGHTS
      ══════════════════════════════════════════════════════════════════════ */}
      <section className="py-20 px-6 bg-background">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Architecture Highlights</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map(({ icon: Icon, title, desc }) => (
              <div key={title} className="rounded-xl border border-border bg-card p-5 hover:border-primary/30 transition-colors group">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-3 group-hover:bg-primary/20 transition-colors">
                  <Icon className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-semibold mb-1.5">{title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════════════
          CTA
      ══════════════════════════════════════════════════════════════════════ */}
      <section className="py-16 px-6 border-t border-border text-center">
        <div className="max-w-xl mx-auto space-y-4">
          <h2 className="text-2xl font-bold">Ready to demo?</h2>
          <p className="text-muted-foreground">Swiss retail platform with TWINT, holiday forecasting, and multimodal search.</p>
          <div className="flex justify-center gap-3">
            <Button className="gradient-primary gap-2" asChild>
              <Link to="/chat">Start Chat <Zap className="w-4 h-4" /></Link>
            </Button>
            <Button variant="outline" className="gap-2" asChild>
              <Link to="/dashboard"><BarChart3 className="w-4 h-4" /> Dashboard</Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}
