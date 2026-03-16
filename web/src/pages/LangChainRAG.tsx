import { useState, useCallback } from "react";
import {
  ArrowDown, ArrowRight, Database, Bot, Brain, Zap, Layers,
  CheckCircle2, XCircle, RotateCcw, BookOpen, GitBranch,
  Play, Search, FileText, Cpu, Network, Filter, Sparkles,
  ShoppingCart, Package, MessageSquare, Shield, AlertTriangle,
  TrendingUp, Clock, Eye, Server, RefreshCw,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

/* ------------------------------------------------------------------ */
/*  Data                                                               */
/* ------------------------------------------------------------------ */

const RAG_MODES = [
  {
    id: "naive",
    label: "Naive RAG",
    tagline: "Linear retrieve → generate",
    color: "text-muted-foreground",
    badge: "bg-muted text-muted-foreground",
    steps: [
      { label: "User Query", icon: Bot },
      { label: "Retrieve Top-K from Qdrant", icon: Database },
      { label: "Compose Prompt", icon: FileText },
      { label: "Generate Answer", icon: Zap },
    ],
    pros: ["Simple to implement", "Low latency", "Predictable"],
    cons: ["No error recovery", "No learning", "Single-pass only"],
    latency: "~120ms",
    accuracy: "72%",
  },
  {
    id: "agentic",
    label: "Agentic RAG",
    tagline: "LLM agent with Shopper + Inventory tools",
    color: "text-primary",
    badge: "bg-primary/15 text-primary",
    steps: [
      { label: "User Query", icon: Bot },
      { label: "Shopper: Parse Goal", icon: Search },
      { label: "Retrieve (MMR) from Qdrant", icon: Database },
      { label: "Inventory: Solve Bundle", icon: Layers },
      { label: "Confidence Gate", icon: Filter },
      { label: "Re-retrieve if low confidence", icon: RotateCcw },
      { label: "Generate + Trace", icon: Zap },
    ],
    pros: ["Multi-agent coordination", "Confidence gating", "Episodic learning"],
    cons: ["More complex", "Higher latency on miss", "More moving parts"],
    latency: "~42ms (cache) / 2.4s",
    accuracy: "94%",
  },
  {
    id: "hybrid",
    label: "Hybrid RAG",
    tagline: "Query rewriting + retrieval validation",
    color: "text-accent",
    badge: "bg-accent/15 text-accent",
    steps: [
      { label: "User Query", icon: Bot },
      { label: "Rewrite / Expand Query", icon: RotateCcw },
      { label: "Retrieve from Qdrant", icon: Database },
      { label: "Validate Relevance (score > 0.65)", icon: Filter },
      { label: "Generate with validated docs", icon: Zap },
    ],
    pros: ["Better retrieval quality", "Filters noise", "Balanced complexity"],
    cons: ["Added latency from rewriting", "May over-filter"],
    latency: "~85ms",
    accuracy: "88%",
  },
  {
    id: "graph",
    label: "GraphRAG",
    tagline: "Knowledge graph + vector retrieval",
    color: "text-status-warning",
    badge: "bg-status-warning/15 text-status-warning",
    steps: [
      { label: "User Query", icon: Bot },
      { label: "Vector Retrieval", icon: Database },
      { label: "Extract Entities", icon: Brain },
      { label: "Knowledge Graph Traversal", icon: Network },
      { label: "Merge Vector + Graph Docs", icon: GitBranch },
      { label: "Generate with enriched context", icon: Zap },
    ],
    pros: ["Captures relationships", "Richer context", "Better for complex queries"],
    cons: ["Requires graph infrastructure", "Highest complexity", "Graph maintenance"],
    latency: "~150ms",
    accuracy: "91%",
  },
];

const LANGCHAIN_COMPONENTS = [
  { name: "Document Loaders", desc: "PDFs, CSVs, webpages → raw text", icon: FileText, color: "text-primary" },
  { name: "Text Splitters", desc: "Chunk documents for granular search", icon: Layers, color: "text-accent" },
  { name: "Embeddings", desc: "all-MiniLM-L6-v2 → 384-dim vectors", icon: Cpu, color: "text-status-warning" },
  { name: "Vector Store", desc: "Qdrant — cosine similarity search", icon: Database, color: "text-status-info" },
  { name: "Retriever", desc: "MMR / similarity search with filters", icon: Search, color: "text-primary" },
  { name: "Agent Tools", desc: "Shopper + Inventory as callable tools", icon: Bot, color: "text-accent" },
];

const TOOL_DEFINITIONS = [
  {
    name: "ShopperParseAndWrite",
    description: "Parses shopper text into a structured goal and writes it to the goals collection.",
    input: "user_message: str",
    output: "Parsed goal dict → upserted to Qdrant",
    color: "border-primary/25 bg-primary/5",
  },
  {
    name: "InventorySolve",
    description: "Retrieve products matching a goal and propose a bundle solution.",
    input: "goal_text: str",
    output: "Bundle candidates → upserted to solutions",
    color: "border-accent/25 bg-accent/5",
  },
];

// Collection schemas with payload examples
const COLLECTION_SCHEMAS = [
  {
    name: "goals",
    desc: "One point per goal/session",
    vectors: "Embedding of raw utterance; optionally second vector for structured goal JSON",
    payloadIndexes: ["region", "status", "user_id", "created_at"],
    example: {
      id: 5001,
      user_id: "user_123",
      status: "open",
      region: "EU",
      goal_text: "Need a blue t-shirt for a birthday, budget ~25, deliver in 5 days",
      constraints: { budget: 25, delivery_days: 5, color: "blue" },
      created_at: "2026-03-11T12:00:00Z",
    },
  },
  {
    name: "products",
    desc: "One or many points per SKU / description chunk",
    vectors: "Embedding of name + description chunk",
    payloadIndexes: ["sku", "stock", "region", "category", "price"],
    example: {
      id: 1001,
      sku: "TSHIRT-BLUE-M",
      name: "Blue T-Shirt (M)",
      category: "apparel",
      stock: 12,
      region: "EU",
      price: 19.99,
      attrs: { material: "cotton", color: "blue" },
      chunk_index: 0,
    },
  },
  {
    name: "solutions",
    desc: "Candidate bundles produced by Inventory agent",
    vectors: "Embedding of solution summary (bundle + rationale)",
    payloadIndexes: ["goal_id", "status", "score_summary"],
    example: {
      id: 11001,
      goal_id: 5001,
      candidates: [
        { product_id: 1001, sku: "TSHIRT-BLUE-M", score: 0.92 },
        { product_id: 1005, sku: "GIFT-WRAP-STD", score: 0.74 },
      ],
      status: "candidate",
      score_summary: 0.83,
      created_at: "2026-03-11T12:00:10Z",
    },
  },
  {
    name: "goal_solution_links",
    desc: "Episodic memory — stores outcome + short rationale",
    vectors: "Joint embedding of goal_text + solution_summary",
    payloadIndexes: ["outcome", "score", "goal_id"],
    example: {
      id: 90001,
      goal_id: 5001,
      solution_id: 11001,
      outcome: "purchased",
      score: 0.83,
      notes: "Delivered on time; user rated 5/5",
      created_at: "2026-03-25T08:00:00Z",
    },
  },
];

// Global RAG rules
const RAG_RULES = [
  { icon: Cpu, title: "Embedding Model", desc: "Single model across all collections (e.g., 384-dim all-mpnet-base-v2). Keep vector dim consistent." },
  { icon: Layers, title: "Chunking", desc: "200–400 tokens with 20–50 token overlap. Store chunk metadata (source, sku, doc_id, chunk_index)." },
  { icon: Search, title: "Search Config", desc: "Default top_k=8 for products, top_k=4 for episodic. Use MMR for diverse candidates." },
  { icon: Filter, title: "Payload Indexes", desc: "Index region, stock, status, user_id, created_at, sku. Boolean/range filters for stock and price." },
  { icon: Shield, title: "Score Thresholds", desc: "Require similarity >0.75 cosine for episodic reuse. Below = no reliable precedent." },
  { icon: FileText, title: "Prompt Budget", desc: "Limit retrieved context to 2–4k tokens. Prefer condensed summaries when tight." },
];

// Fallback rules
const FALLBACK_RULES = [
  { condition: "No in-stock products (strict filters)", actions: ["Relax region constraint (offer longer ETA)", "Relax budget ±20%", "Ask Shopper to confirm relaxation with user"] },
  { condition: "Low episodic similarity (< 0.75)", actions: ["Do NOT reuse episodes", "Create novel candidate bundles from scratch"] },
  { condition: "Low confidence (score_summary < 0.5)", actions: ["Shopper asks clarifying question", "Mark solution status = 'needs_human'"] },
  { condition: "Stale product data (> 24h TTL)", actions: ["Reject stale product points", "Reconcile with live inventory system before use"] },
];

// Telemetry fields
const TELEMETRY_FIELDS = [
  { field: "time_to_first_solution", desc: "goal.created_at → first solution upserted", type: "float (ms)" },
  { field: "feasibility", desc: "Did the item actually ship?", type: "boolean" },
  { field: "conversion", desc: "Was the solution purchased?", type: "boolean" },
  { field: "episode_reuse", desc: "Was solution derived from a previous episode?", type: "boolean" },
  { field: "user_rating", desc: "Post-delivery rating", type: "float (1-5)" },
  { field: "return_rate", desc: "Was the item returned?", type: "boolean" },
];

// Few-shot episodes
const SEED_EPISODES = [
  { id: 90001, goal: "Need blue casual t-shirt under 30, EU delivery in 4 days", skus: ["TSHIRT-BLUE-M", "GIFT-WRAP-STD"], outcome: "purchased", score: 0.9, notes: "Delivered on time; 5-star rating" },
  { id: 90002, goal: "Looking for lightweight running shoes, budget 100, US, 7 days", skus: ["RUN-SHOE-ULTRA", "SOCKS-COOL"], outcome: "purchased", score: 0.85, notes: "Customer returned due to size" },
  { id: 90003, goal: "Gift: leather wallet, budget 50-80, deliver EU", skus: ["WALLET-LEATHER-MID"], outcome: "purchased", score: 0.95, notes: "High satisfaction" },
  { id: 90004, goal: "Need eco-friendly water bottle, budget 25, deliver within 3 days", skus: ["BOTTLE-INSUL-750"], outcome: "rejected", score: 0.4, notes: "Out of stock at time of ordering" },
];

// Demo flow steps
const DEMO_FLOW = [
  { step: 1, agent: "Shopper", action: "Parse user text → write goal to Qdrant", detail: 'Embeds "Need a blue t-shirt..." → goals collection, status=open' },
  { step: 2, agent: "Inventory", action: "Poll goals → retrieve episodes + products", detail: "Searches goal_solution_links (top 4) + products (top 12, stock>0, region=EU)" },
  { step: 3, agent: "Inventory", action: "Compose 3 bundles, compute scores", detail: "avg(product_similarity × availability_factor) → score_summary" },
  { step: 4, agent: "Inventory", action: "Upsert solutions + tentative episode", detail: "solutions + goal_solution_links with outcome='candidate'" },
  { step: 5, agent: "Shopper", action: "Fetch solutions, present options", detail: "Rerank by user prefs, present 1-3 options with rationale" },
  { step: 6, agent: "Shopper", action: "Capture feedback → write final episode", detail: "Update goal_solution_links with outcome='purchased' + notes" },
];

/* ------------------------------------------------------------------ */
/*  Flow Diagram                                                       */
/* ------------------------------------------------------------------ */

function PipelineFlow({ steps, modeColor }: { steps: typeof RAG_MODES[0]["steps"]; modeColor: string }) {
  const [activeStep, setActiveStep] = useState(-1);

  const animate = () => {
    let i = 0;
    setActiveStep(0);
    const interval = setInterval(() => {
      i++;
      if (i >= steps.length) {
        clearInterval(interval);
        setTimeout(() => setActiveStep(-1), 1000);
      } else {
        setActiveStep(i);
      }
    }, 450);
  };

  return (
    <div className="space-y-3">
      <Button size="sm" variant="outline" onClick={animate} className="gap-1.5 text-xs">
        <Play className="w-3 h-3" /> Animate
      </Button>
      <div className="flex flex-col gap-1">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          const active = idx === activeStep;
          const done = activeStep > idx;
          return (
            <div key={step.label}>
              <div
                className={`flex items-center gap-3 px-3 py-2 rounded-lg border transition-all duration-300 ${
                  active
                    ? "border-primary bg-primary/10 scale-[1.02] shadow-md"
                    : done
                    ? "border-status-online/30 bg-status-online/5 opacity-70"
                    : "border-border bg-card"
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${active ? "text-primary" : modeColor}`} />
                <span className="text-sm flex-1">{step.label}</span>
                {done && <CheckCircle2 className="w-3.5 h-3.5 text-status-online" />}
                {active && (
                  <span className="w-3.5 h-3.5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                )}
              </div>
              {idx < steps.length - 1 && (
                <div className="flex justify-center py-0.5">
                  <ArrowDown className="w-3 h-3 text-muted-foreground/40" />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function LangChainRAGPage() {
  const [selectedMode, setSelectedMode] = useState("agentic");
  const [demoStep, setDemoStep] = useState<number | null>(null);
  const activeMode = RAG_MODES.find((m) => m.id === selectedMode)!;

  const runDemo = useCallback(async () => {
    setDemoStep(null);
    for (let i = 0; i < DEMO_FLOW.length; i++) {
      await new Promise((r) => setTimeout(r, 700));
      setDemoStep(i);
    }
  }, []);

  return (
    <div className="p-4 md:p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium">
          <Sparkles className="w-3.5 h-3.5" />
          LangChain + Qdrant · RAG Context
        </div>
        <h1 className="text-2xl font-bold tracking-tight">RAG Context Architecture</h1>
        <p className="text-sm text-muted-foreground max-w-2xl">
          Complete RAG context spec for Shopper + Inventory agents — collection schemas, prompt templates,
          episodic memory, fallback rules, and end-to-end demo flow.
        </p>
      </div>

      <Tabs defaultValue="architectures" className="space-y-4">
        <TabsList className="flex-wrap h-auto gap-1">
          <TabsTrigger value="architectures">Architectures</TabsTrigger>
          <TabsTrigger value="collections">Collections</TabsTrigger>
          <TabsTrigger value="prompts">Prompt Templates</TabsTrigger>
          <TabsTrigger value="episodic">Episodic Memory</TabsTrigger>
          <TabsTrigger value="fallbacks">Fallbacks</TabsTrigger>
          <TabsTrigger value="demo">E2E Demo</TabsTrigger>
          <TabsTrigger value="components">LangChain Stack</TabsTrigger>
          <TabsTrigger value="tools">Agent Tools</TabsTrigger>
        </TabsList>

        {/* ─── Architectures ─── */}
        <TabsContent value="architectures" className="space-y-6">
          {/* Global RAG rules */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Shield className="h-4 w-4 text-primary" />
                Global RAG Rules (Both Agents)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {RAG_RULES.map((rule) => (
                  <div key={rule.title} className="flex items-start gap-2 p-2 rounded-lg bg-muted/30 border border-border text-xs">
                    <rule.icon className="h-3.5 w-3.5 text-primary shrink-0 mt-0.5" />
                    <div>
                      <span className="font-medium">{rule.title}:</span>{" "}
                      <span className="text-muted-foreground">{rule.desc}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Mode selector */}
          <div className="flex flex-wrap gap-2">
            {RAG_MODES.map((mode) => (
              <button
                key={mode.id}
                onClick={() => setSelectedMode(mode.id)}
                className={`px-4 py-2 rounded-lg border text-sm font-medium transition-all ${
                  selectedMode === mode.id
                    ? `${mode.badge} border-current`
                    : "border-border text-muted-foreground hover:text-foreground hover:border-border"
                }`}
              >
                {mode.label}
              </button>
            ))}
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  <Badge className={activeMode.badge}>{activeMode.label}</Badge>
                  <span className="text-muted-foreground text-sm font-normal">{activeMode.tagline}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <PipelineFlow steps={activeMode.steps} modeColor={activeMode.color} />
              </CardContent>
            </Card>

            <div className="space-y-4">
              <Card>
                <CardContent className="pt-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-lg bg-muted/50 p-3 text-center">
                      <div className="text-lg font-bold font-mono text-primary">{activeMode.latency}</div>
                      <div className="text-xs text-muted-foreground">Latency</div>
                    </div>
                    <div className="rounded-lg bg-muted/50 p-3 text-center">
                      <div className="text-lg font-bold font-mono text-status-online">{activeMode.accuracy}</div>
                      <div className="text-xs text-muted-foreground">Accuracy</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-status-online" /> Strengths
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1">
                    {activeMode.pros.map((p) => (
                      <li key={p} className="flex items-center gap-2 text-sm">
                        <ArrowRight className="w-3 h-3 text-status-online shrink-0" /> {p}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-1.5">
                    <XCircle className="w-3.5 h-3.5 text-destructive" /> Tradeoffs
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1">
                    {activeMode.cons.map((c) => (
                      <li key={c} className="flex items-center gap-2 text-sm text-muted-foreground">
                        <ArrowRight className="w-3 h-3 text-destructive shrink-0" /> {c}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Comparison */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Architecture Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {RAG_MODES.map((mode) => {
                  const accuracy = parseInt(mode.accuracy);
                  return (
                    <div key={mode.id} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className={`font-medium ${mode.color}`}>{mode.label}</span>
                        <span className="text-muted-foreground">{mode.accuracy} accuracy · {mode.latency}</span>
                      </div>
                      <Progress value={accuracy} className="h-2" />
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── Collections ─── */}
        <TabsContent value="collections" className="space-y-4">
          {COLLECTION_SCHEMAS.map((col) => (
            <Card key={col.name} className="border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Database className="h-4 w-4 text-accent" />
                  <code className="font-mono text-primary">{col.name}</code>
                  <span className="text-muted-foreground font-normal text-xs">— {col.desc}</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-xs text-muted-foreground">
                  <span className="font-medium">Vectors:</span> {col.vectors}
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs text-muted-foreground font-medium">Payload indexes:</span>
                  {col.payloadIndexes.map((idx) => (
                    <Badge key={idx} variant="outline" className="text-[10px] font-mono">{idx}</Badge>
                  ))}
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1 font-medium">Example payload:</p>
                  <pre className="bg-muted/50 p-3 rounded-lg text-[11px] font-mono overflow-x-auto leading-relaxed">
                    {JSON.stringify(col.example, null, 2)}
                  </pre>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* ─── Prompt Templates ─── */}
        <TabsContent value="prompts" className="space-y-4">
          {/* Shopper prompt */}
          <Card className="border-primary/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <ShoppingCart className="h-4 w-4 text-primary" />
                Shopper — Parse & Compose Prompts
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-xs text-muted-foreground mb-2 font-medium">Parse prompt (user text → structured goal):</p>
                <pre className="bg-muted/50 p-3 rounded-lg text-[11px] font-mono overflow-x-auto leading-relaxed">
{`SYSTEM: You are Shopper. Convert USER_TEXT into a structured JSON goal.
Return ONLY valid JSON on one line (no commentary).
Fields: goal_text, budget (number|null), delivery_days (int|null),
region (string|null), preferences (object), user_id (string).

If ambiguous, output JSON with "clarify": true and "clarification"
containing a one-sentence question.

USER_TEXT: {user_text}
USER_ID: {user_id}

EXAMPLE:
Input: "Need a blue t-shirt under $30, ships to EU in 5 days."
Output: {"goal_text":"Need a blue t-shirt for birthday",
  "budget":30,"delivery_days":5,"region":"EU",
  "preferences":{"color":"blue"},"user_id":"user_123"}
Rationale: Parsed explicit budget, color, and delivery deadline.`}
                </pre>
              </div>

              <div>
                <p className="text-xs text-muted-foreground mb-2 font-medium">Composition prompt (showing options):</p>
                <pre className="bg-muted/50 p-3 rounded-lg text-[11px] font-mono overflow-x-auto leading-relaxed">
{`SYSTEM: Present solutions to the user clearly.

INPUT:
- GOAL: {goal_json}
- SOLUTIONS: [{solution_1}, {solution_2}, {solution_3}]
- EPISODIC PRECEDENT: {similar_past_outcome}

TASK: Render 3 user-friendly options with:
- Bullet list of items (name, price)
- Total cost
- Delivery estimate
- One-line justification
- Confidence indicator`}
                </pre>
              </div>

              <div className="rounded-lg bg-muted/30 border border-border p-3">
                <p className="text-xs text-muted-foreground">
                  <strong>Retrieval strategy:</strong> Fetch solutions where goal_id matches (top 3 by score_summary). 
                  If no solutions, fall back to episodic retrieval (goal_solution_links, top_k=4, threshold 0.75) 
                  + product similarity search (top_k=6, filter stock{">"} 0 and region).
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Inventory prompt */}
          <Card className="border-accent/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Package className="h-4 w-4 text-accent" />
                Inventory — Planning Prompt
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <pre className="bg-muted/50 p-3 rounded-lg text-[11px] font-mono overflow-x-auto leading-relaxed">
{`SYSTEM: You are Inventory. Input: structured goal, episodic
precedent summaries, and candidate product snippets.

Build up to 3 ranked solution bundles. Output valid JSON array:
[{"bundle_id": 1, "skus": [...], "total_price": 29.99,
  "feasible": true, "score": 0.8, "rationale": "..." }, ...]

RULES:
- Filter out any product with stock == 0.
- Prefer precedents if similarity > threshold.
- Score range: 0.0 - 1.0.

INPUT_GOAL: {goal_json}
EPISODIC_PRECEDENTS: [ {precedent_summary}, ... ]
CANDIDATE_PRODUCTS: [ {sku, name, stock, price, attrs}, ... ]

TASK:
1) Filter by hard constraints: stock>0, same region.
2) Compose up to 3 bundles (single or multi-SKU).
   Prefer past successful precedents as templates.
3) Rank by feasibility × expected conversion.
4) Output JSON array of bundles.`}
              </pre>

              <div className="rounded-lg bg-muted/30 border border-border p-3">
                <p className="text-xs text-muted-foreground">
                  <strong>Retrieval strategy:</strong> Embed goal_text → search goal_solution_links (top_k=4, outcome=purchased, threshold 0.72) 
                  + search products (top_k=12, filter stock{">"} 0 & region & price within budget).
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── Episodic Memory ─── */}
        <TabsContent value="episodic" className="space-y-4">
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Brain className="h-4 w-4 text-primary" />
                Episodic Embedding Strategy
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-xs text-muted-foreground">
                Create a short summary string for each solved episode and embed that string into goal_solution_links. 
                This keeps episodic points compact and retrievable by similarity to new goals.
              </p>
              <pre className="bg-muted/50 p-3 rounded-lg text-[11px] font-mono overflow-x-auto">
{`# Episode summary format (embed this string):
f"goal:{short_goal} | sol:{top_skus} | outcome:{outcome} | score:{score}"

# Example:
"goal:blue t-shirt under 30, EU | sol:TSHIRT-BLUE-M,GIFT-WRAP-STD | outcome:purchased | score:0.9"`}
              </pre>
            </CardContent>
          </Card>

          {/* Seed episodes */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Database className="h-4 w-4 text-accent" />
                Few-Shot Episodic Seeds ({SEED_EPISODES.length} episodes)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {SEED_EPISODES.map((ep) => (
                  <div key={ep.id} className={`rounded-lg border p-3 text-xs ${
                    ep.outcome === "purchased" ? "border-status-online/30 bg-status-online/5" : "border-destructive/30 bg-destructive/5"
                  }`}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono text-muted-foreground">#{ep.id}</span>
                      <div className="flex items-center gap-2">
                        <Badge variant={ep.outcome === "purchased" ? "default" : "destructive"} className="text-[10px]">
                          {ep.outcome}
                        </Badge>
                        <span className="font-mono font-bold">{ep.score}</span>
                      </div>
                    </div>
                    <p className="text-foreground mb-1">{ep.goal}</p>
                    <div className="flex items-center gap-1 flex-wrap mb-1">
                      {ep.skus.map((s) => (
                        <Badge key={s} variant="outline" className="text-[10px] font-mono">{s}</Badge>
                      ))}
                    </div>
                    <p className="text-muted-foreground italic">{ep.notes}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Seeding code */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Seeding Code (paste & run once)</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted/50 p-3 rounded-lg text-[11px] font-mono overflow-x-auto leading-relaxed">
{`from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from langchain.embeddings import SentenceTransformerEmbeddings

client = QdrantClient(url="http://localhost:6333")
emb = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")

episodes = [
  {"id": 90001, "goal": "blue t-shirt under 30, EU",
   "skus": ["TSHIRT-BLUE-M", "GIFT-WRAP-STD"],
   "outcome": "purchased", "score": 0.9},
  # ... more episodes
]

points = []
for ep in episodes:
    summary = f"goal:{ep['goal']} | sol:{','.join(ep['skus'])}"
              f" | outcome:{ep['outcome']} | score:{ep['score']}"
    vec = emb.embed_query(summary)
    points.append(PointStruct(id=ep["id"], vector=vec, payload=ep))

client.upsert(collection_name="goal_solution_links", points=points)`}
              </pre>
            </CardContent>
          </Card>

          {/* Telemetry */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <TrendingUp className="h-4 w-4" /> Evaluation & Telemetry Fields
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Field</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Type</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {TELEMETRY_FIELDS.map((t) => (
                    <TableRow key={t.field}>
                      <TableCell className="font-mono text-xs text-primary">{t.field}</TableCell>
                      <TableCell className="text-xs text-muted-foreground">{t.desc}</TableCell>
                      <TableCell><Badge variant="outline" className="text-[10px]">{t.type}</Badge></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <p className="text-[11px] text-muted-foreground mt-2 italic">
                Attach these as extra payload fields in goal_solution_links for offline evaluation and re-weighting of episodic retrieval.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── Fallbacks ─── */}
        <TabsContent value="fallbacks" className="space-y-4">
          {FALLBACK_RULES.map((rule, i) => (
            <Card key={i} className="border-border">
              <CardContent className="p-4 space-y-2">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-status-warning shrink-0" />
                  <h3 className="font-medium text-sm">{rule.condition}</h3>
                </div>
                <ul className="space-y-1 pl-6">
                  {rule.actions.map((a, j) => (
                    <li key={j} className="flex items-start gap-2 text-xs text-muted-foreground">
                      <ArrowRight className="h-3 w-3 text-primary shrink-0 mt-0.5" />
                      {a}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}

          {/* Implementation tips */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Implementation Tips & Gotchas</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1.5 text-xs text-muted-foreground">
                {[
                  "Use payload filters for hard constraints (stock, region, price) and vectors for relevance — mixing both gives robust results",
                  "Normalize numeric constraints (budget, delivery_days) so filters work reliably",
                  "Keep episodic docs short (1–2 sentences) to reduce noise and ensure similarity aligns with goal phrasing",
                  "Store exact prompt + retrieved chunk IDs used to generate each solution for reproducible audits",
                  "Route solutions with score_summary < 0.4 to ops for manual review (human in the loop)",
                  "Use as_retriever(search_type='mmr') to avoid near-duplicate chunks",
                  "Cheap models for parsing, expensive models for planning/ranking",
                  "Keep product stock fresh — vector similarity won't catch staleness",
                ].map((tip) => (
                  <li key={tip} className="flex items-start gap-2">
                    <CheckCircle2 className="w-3 h-3 text-status-online shrink-0 mt-0.5" />
                    {tip}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── E2E Demo ─── */}
        <TabsContent value="demo" className="space-y-4">
          <Card className="border-border">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Play className="h-4 w-4 text-primary" />
                  End-to-End Demo: Shopper → Inventory Flow
                </CardTitle>
                <Button size="sm" variant="outline" onClick={runDemo}>
                  <Zap className="h-3 w-3 mr-1" /> Run Demo
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {DEMO_FLOW.map((step, i) => {
                  const done = demoStep !== null && demoStep >= i;
                  const active = demoStep === i;
                  const isShopper = step.agent === "Shopper";
                  return (
                    <div key={i} className={`rounded-lg border p-3 transition-all duration-300 ${
                      active ? (isShopper ? "border-primary bg-primary/10 scale-[1.01]" : "border-accent bg-accent/10 scale-[1.01]") :
                      done ? "border-status-online/30 bg-status-online/5" : "border-border"
                    }`}>
                      <div className="flex items-center gap-2 mb-1">
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${
                          done ? "bg-status-online/20 text-status-online" : "bg-muted text-muted-foreground"
                        }`}>{step.step}</div>
                        <Badge variant="outline" className={`text-[10px] ${isShopper ? "text-primary border-primary/30" : "text-accent border-accent/30"}`}>
                          {step.agent}
                        </Badge>
                        <span className="text-xs font-medium">{step.action}</span>
                        {done && <CheckCircle2 className="h-3 w-3 text-status-online ml-auto" />}
                        {active && <span className="w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin ml-auto" />}
                      </div>
                      <p className="text-[11px] text-muted-foreground pl-8">{step.detail}</p>
                    </div>
                  );
                })}
              </div>
              {demoStep === DEMO_FLOW.length - 1 && (
                <div className="mt-4 rounded-lg border border-status-online/30 bg-status-online/5 p-3 text-center animate-fade-in">
                  <p className="text-sm font-medium text-status-online">✓ Full cycle complete — episode stored for future reuse</p>
                  <p className="text-xs text-muted-foreground mt-1">Next similar goal will benefit from this episode (episodic RAG)</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Demo code */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Demo Script (paste-ready Python)</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted/50 p-3 rounded-lg text-[11px] font-mono overflow-x-auto leading-relaxed">
{`# demo_end2end.py
from langchain_agents import shopper_parse_and_write, inventory_solve_and_write

# 1) Shopper receives user text
user_text = "Need a blue t-shirt for a birthday, under $30, deliver in 5 days to EU"
goal = shopper_parse_and_write(user_text, user_id="demo_user_1")
print("Shopper wrote goal:", goal)

# 2) Inventory solves (reads goal, writes solutions)
solution = inventory_solve_and_write(goal)
print("Inventory wrote solution:", solution)

# 3) Shopper presents solutions to user
sol_hits = client.search(
    collection_name="solutions",
    query_vector=emb.embed_query(goal["goal_text"]),
    limit=3, with_payload=True
)
for h in sol_hits:
    print("Option:", h.payload.get("bundles"))

# 4) User selects → write final episode
client.upsert("goal_solution_links", points=[
    PointStruct(id=uuid4(), vector=emb.embed_query(episode_summary),
    payload={"goal_id": goal["id"], "outcome": "purchased",
             "score": 0.83, "notes": "Delivered on time"})
])`}
              </pre>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── LangChain Stack ─── */}
        <TabsContent value="components" className="space-y-4">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {LANGCHAIN_COMPONENTS.map((comp) => {
              const Icon = comp.icon;
              return (
                <Card key={comp.name} className="hover:border-primary/30 transition-colors">
                  <CardContent className="pt-4 space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center">
                        <Icon className={`w-4 h-4 ${comp.color}`} />
                      </div>
                      <h3 className="font-semibold text-sm">{comp.name}</h3>
                    </div>
                    <p className="text-sm text-muted-foreground">{comp.desc}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">LangChain → Qdrant Pipeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap items-center gap-2 text-sm">
                {["Document Loaders", "Text Splitters", "Embeddings", "QdrantVectorStore", "Retriever", "Agent"].map(
                  (step, i) => (
                    <div key={step} className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">{step}</Badge>
                      {i < 5 && <ArrowRight className="w-3 h-3 text-muted-foreground" />}
                    </div>
                  )
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Quick Start</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-xs bg-muted/50 rounded-lg p-4 overflow-x-auto font-mono text-muted-foreground leading-relaxed">
{`from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

client = QdrantClient(url="localhost:6333")
vectorstore = QdrantVectorStore(
    client=client,
    collection_name="products",
    embedding=OpenAIEmbeddings()
)

# MMR retriever for diverse candidates
retriever = vectorstore.as_retriever(
    search_type="mmr", search_kwargs={"k": 5}
)

docs = retriever.get_relevant_documents("2-person tent under 200CHF")`}
              </pre>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── Agent Tools ─── */}
        <TabsContent value="tools" className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            {TOOL_DEFINITIONS.map((tool) => (
              <Card key={tool.name} className={`border ${tool.color}`}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Bot className="w-4 h-4" />
                    {tool.name}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-muted-foreground">{tool.description}</p>
                  <div className="space-y-1.5 text-xs">
                    <div className="flex gap-2">
                      <span className="text-muted-foreground w-12 shrink-0">Input:</span>
                      <code className="font-mono bg-muted/50 px-1.5 py-0.5 rounded">{tool.input}</code>
                    </div>
                    <div className="flex gap-2">
                      <span className="text-muted-foreground w-12 shrink-0">Output:</span>
                      <span>{tool.output}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Brain className="w-4 h-4 text-primary" />
                Coordinator Agent Decision Flow
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                {[
                  { condition: "User intent unclear", action: "→ Call Shopper to parse & clarify" },
                  { condition: "Goal parsed, need products", action: "→ Call Inventory to search & bundle" },
                  { condition: "Low confidence (<70%)", action: "→ Re-retrieve with expanded query" },
                  { condition: "Bundle ready", action: "→ Present to user, capture outcome" },
                  { condition: "Outcome received", action: "→ Write episodic memory for future reuse" },
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-3 px-3 py-2 rounded-lg bg-card border border-border">
                    <Badge variant="outline" className="text-xs shrink-0 mt-0.5">{i + 1}</Badge>
                    <div>
                      <span className="font-medium">{item.condition}</span>
                      <span className="text-muted-foreground"> {item.action}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── Indexing Pipeline ─── */}
        <TabsContent value="indexing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Indexing Pipeline (Data Ingestion)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {[
                  { step: "1. Load Documents", desc: "PDFs, CSVs, product catalogs → raw text via LangChain loaders", icon: FileText },
                  { step: "2. Split Text", desc: "RecursiveCharacterTextSplitter(chunk_size=500, overlap=50)", icon: Layers },
                  { step: "3. Embed Chunks", desc: "all-MiniLM-L6-v2 → 384-dim vectors (or OpenAI 1536-dim)", icon: Cpu },
                  { step: "4. Store in Qdrant", desc: "QdrantVectorStore.from_documents() with payload indexes", icon: Database },
                  { step: "5. Create Retriever", desc: "vectorstore.as_retriever(search_type='mmr', k=5)", icon: Search },
                ].map((item, i) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.step}>
                      <div className="flex items-start gap-3 px-4 py-3 rounded-lg border border-border bg-card">
                        <Icon className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                        <div>
                          <div className="font-medium text-sm">{item.step}</div>
                          <div className="text-xs text-muted-foreground">{item.desc}</div>
                        </div>
                      </div>
                      {i < 4 && (
                        <div className="flex justify-center py-0.5">
                          <ArrowDown className="w-3 h-3 text-muted-foreground/40" />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Database className="w-4 h-4 text-accent" />
                Qdrant Collections
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {["goals", "products", "solutions", "goal_solution_links", "shopper_memory"].map((col) => (
                  <div key={col} className="rounded-lg border border-accent/20 bg-accent/5 p-3 text-center">
                    <Database className="w-4 h-4 text-accent mx-auto mb-1" />
                    <div className="text-xs font-medium font-mono">{col}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
