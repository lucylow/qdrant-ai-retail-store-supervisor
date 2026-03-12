import { AgentAvatar } from "@/components/AgentAvatar";
import {
  Activity, Clock, Zap, GitMerge, Lock, CheckCircle, ArrowRight,
  Brain, Database, ShoppingCart, Package, Eye, MessageSquare,
  RefreshCw, Shield, Server, Layers, TrendingUp, FileText,
  ArrowDown, ArrowUp, Circle, Search, Settings, UserCheck,
  AlertTriangle, ThumbsUp, ThumbsDown, Edit3, RotateCcw
} from "lucide-react";
import { useState, useEffect, useCallback } from "react";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

// ─── Types & Data ────────────────────────────────────────────────────────────

type LogEntry = { id: number; time: string; agent: string; message: string; type: "info" | "success" | "warning" };

const SAMPLE_LOGS: LogEntry[] = [
  { id: 1, time: "14:32:01", agent: "Supervisor", message: "New goal received: '2-person tent Zurich'", type: "info" },
  { id: 2, time: "14:32:01", agent: "Shopper", message: "Parsing goal intent → category: Tents, budget: 200CHF", type: "info" },
  { id: 3, time: "14:32:02", agent: "Inventory", message: "Searching Qdrant episodes collection (similar: 0.92)", type: "info" },
  { id: 4, time: "14:32:02", agent: "Inventory", message: "CACHE HIT! Episode ep_7234 (92% similar, 35ms)", type: "success" },
  { id: 5, time: "14:32:03", agent: "Inventory", message: "Bundle prepared: MSR Hubba Hubba NX2 + Accessories", type: "success" },
  { id: 6, time: "14:32:03", agent: "Supervisor", message: "Goal fulfilled. Writing episode to Qdrant.", type: "success" },
];

// Shopper agent responsibilities
const SHOPPER_CAPABILITIES = [
  { icon: MessageSquare, label: "NLU Parsing", desc: "Parse messy, multi-constraint requests into structured goal objects (category, budget, qty, deadlines, location)" },
  { icon: RefreshCw, label: "Clarification Dialog", desc: "Detect conflicts or incompleteness (budget vs delivery, sizes) and ask targeted follow-ups" },
  { icon: Layers, label: "Goal Normalization", desc: "Map free text to catalog ontology (categories, attributes, facets); handle ambiguous categories" },
  { icon: Brain, label: "Preference Modeling", desc: "Maintain per-user vectors (brands, colors, price bands, risk tolerance) in shopper_memory collection" },
  { icon: Database, label: "Experience Orchestration", desc: "Write goals to Qdrant, poll for solutions, turn bundles into explanations and upsell suggestions" },
  { icon: TrendingUp, label: "Feedback Capture", desc: "Translate accept/reject/modify into labels on solutions to close the learning loop" },
];

// Inventory agent responsibilities
const INVENTORY_CAPABILITIES = [
  { icon: Search, label: "Goal Intake", desc: "Poll Qdrant for goals with status='open' — no direct RPC invocation" },
  { icon: Eye, label: "Constraint Interpretation", desc: "Read structured fields + raw embedding; retrieve episodic memory to bias planning" },
  { icon: Server, label: "Inventory Reasoning", desc: "Query WMS/ERP APIs for stock, price, lead times; enforce hard constraints (stock>0, MOQ, region)" },
  { icon: Package, label: "Bundle Construction", desc: "Build candidate bundles (SKUs + quantities); compute cost, margin, ETA, satisfaction scores" },
  { icon: Brain, label: "Generative Ranking", desc: "LLM ranks bundles by composite objectives (margin, history, ETA, prefs); generates explanations" },
  { icon: Database, label: "Writeback", desc: "Upsert candidates to solutions with goal_id, SKUs, feasibility, confidence; update goal status" },
];

// Qdrant collections schema
const COLLECTIONS = [
  {
    name: "goals", vectors: "utterance embedding + structured JSON vector",
    fields: ["goal_id", "user_id", "channel", "category", "budget_max", "location", "deadline", "status", "solution_ids"],
    statuses: ["open", "inventory_checked", "fulfilled", "failed", "cancelled"],
  },
  {
    name: "solutions", vectors: "solution summary embedding",
    fields: ["solution_id", "goal_id", "products[]", "summary", "eta_days", "total_price", "margin", "feasible", "outcome", "origin_agent"],
    statuses: ["pending", "success", "fail", "partial"],
  },
  {
    name: "goal_solution_links", vectors: "joint goal+solution episode embedding",
    fields: ["goal_id", "solution_id", "user_id", "success", "revenue", "margin_band", "region", "segment", "feedback_tags"],
    statuses: [],
  },
  {
    name: "shopper_memory", vectors: "user preference vector",
    fields: ["user_id", "brand_prefs", "color_prefs", "price_bands", "risk_tolerance", "lifetime_value", "complaint_history"],
    statuses: [],
  },
  {
    name: "inventory_memory", vectors: "SKU/supplier vector",
    fields: ["sku_id", "supplier_id", "backorder_patterns", "quality_issues", "return_reasons", "avg_lead_time"],
    statuses: [],
  },
];

// Lifecycle steps
const SHOPPER_LIFECYCLE = [
  { step: 1, label: "Request Received", desc: "User sends chat or API request", icon: MessageSquare },
  { step: 2, label: "NLU Parse & Clarify", desc: "LLM + tools parse, validate, ask follow-ups until coherent", icon: Brain },
  { step: 3, label: "Embed & Write Goal", desc: "Embed raw text, write to goals with status='open'", icon: Database },
  { step: 4, label: "Poll Solutions", desc: "Subscribe/poll solutions where goal_id matches, outcome='pending'", icon: RefreshCw },
  { step: 5, label: "Rerank & Present", desc: "Rerank by user prefs from shopper_memory, present 1-3 options", icon: TrendingUp },
  { step: 6, label: "Feedback Loop", desc: "Update outcome, status; write episode to goal_solution_links", icon: CheckCircle },
];

const INVENTORY_LIFECYCLE = [
  { step: 1, label: "Scroll Open Goals", desc: "Job loop scrolls goals with status='open' and recent created_at", icon: Search },
  { step: 2, label: "Fetch & Embed", desc: "Get goal payload + embeddings from Qdrant", icon: Database },
  { step: 3, label: "Episodic Retrieval", desc: "Query goal_solution_links for success=true, high similarity episodes", icon: Brain },
  { step: 4, label: "Inventory API Queries", desc: "Hit WMS/ERP with category, price, region filters + business rules", icon: Server },
  { step: 5, label: "Bundle & Rank", desc: "Filter infeasible, build bundles, attach episode priors; LLM ranks top N", icon: Package },
  { step: 6, label: "Write Solutions", desc: "Write solutions, update goals.status to 'inventory_checked'", icon: CheckCircle },
];

// Guardrails
const GUARDRAILS = [
  { title: "Deterministic vs Generative Split", desc: "All stock, price, tax, shipping from APIs/databases — never from LLM hallucination. LLMs restricted to understanding, planning, ranking, explanation.", icon: Shield },
  { title: "Schema-First Design", desc: "Structured goal fields validated and sanitized (types, ranges, enums) before hitting inventory. Validation fails → shopper re-asks, never guesses.", icon: FileText },
  { title: "Tooling / MCP Layer", desc: "Shopper tools: catalog search, attribute schema, user-profile API. Inventory tools: warehouse stock, pricing engine, shipping estimator, reservations.", icon: Settings },
  { title: "Agentic RAG Pattern", desc: "Before generating bundles, inventory agent retrieves similar successful episodes and injects into planning prompt — retrieval-augmented reasoning, not document RAG.", icon: Brain },
];

// Metrics
const AGENT_METRICS = [
  { metric: "Time to First Solution", formula: "mean(solution.created_at − goal.created_at)", target: "<5s", current: "2.8s" },
  { metric: "Goal Resolution Rate", formula: "% goals with solution within 30s", target: ">92%", current: "94%" },
  { metric: "Solution Acceptance Rate", formula: "% solutions user accepts", target: ">75%", current: "78%" },
  { metric: "Coordination Lag", formula: "mean(inventory_poll_interval)", target: "<2s", current: "1.7s" },
  { metric: "Feasibility@3", formula: "% top-3 bundles with full stock + delivery", target: ">85%", current: "87%" },
  { metric: "Historical Match Rate", formula: "% solutions using learned episodes", target: ">80%", current: "82%" },
  { metric: "Episode Growth", formula: "goal_solution_links count over time", target: "growing", current: "127" },
  { metric: "Conversion Lift", formula: "lift for goals with episodic matches vs without", target: ">20%", current: "+31%" },
];

// Pipeline steps for simulation
const PIPELINE_STEPS = [
  { label: "ShopperAgent", icon: "🛒", desc: "Parse utterance → upsert goal (atomic CAS)", latency: "18ms", color: "border-primary/40 bg-primary/5 text-primary" },
  { label: "InventoryAgent", icon: "📦", desc: "Search episodes → retrieve products → RRF bundle", latency: "42ms", color: "border-accent/40 bg-accent/5 text-accent" },
  { label: "SupervisorAgent", icon: "🎯", desc: "Rank bundles → assemble provenance → SSE stream", latency: "12ms", color: "border-status-online/40 bg-status-online/5 text-status-online" },
];

// ─── Component ───────────────────────────────────────────────────────────────

export default function AgentsPage() {
  const [logs, setLogs] = useState<LogEntry[]>(SAMPLE_LOGS);
  const [live, setLive] = useState(false);
  const [activeStep, setActiveStep] = useState<number | null>(null);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [shopperStep, setShopperStep] = useState<number | null>(null);
  const [inventoryStep, setInventoryStep] = useState<number | null>(null);

  useEffect(() => {
    if (!live) return;
    const interval = setInterval(() => {
      const msgs = [
        { agent: "Shopper", message: `Polling for new goals… (${Math.floor(Math.random() * 5)} pending)`, type: "info" as const },
        { agent: "Inventory", message: `Qdrant search latency: ${Math.floor(25 + Math.random() * 40)}ms`, type: "info" as const },
        { agent: "Supervisor", message: `Cache hit rate: ${(80 + Math.random() * 10).toFixed(1)}%`, type: "success" as const },
        { agent: "Inventory", message: `Episode retrieved ep_${Math.floor(Math.random() * 9999)} (${(88 + Math.random() * 5).toFixed(0)}% similar)`, type: "success" as const },
        { agent: "Shopper", message: `Swiss-DE normalized: "Zelt" → "tent", "Franken" → "CHF"`, type: "info" as const },
        { agent: "Inventory", message: `Bundle feasibility check: 3/3 items in stock ✓`, type: "success" as const },
        { agent: "Shopper", message: `Preference vector updated for user_7832 (brand affinity: +0.12)`, type: "info" as const },
      ];
      const pick = msgs[Math.floor(Math.random() * msgs.length)];
      setLogs(prev => [{ ...pick, id: Date.now(), time: new Date().toLocaleTimeString() }, ...prev.slice(0, 49)]);
    }, 2000);
    return () => clearInterval(interval);
  }, [live]);

  const runPipeline = useCallback(async () => {
    setPipelineRunning(true);
    setActiveStep(null);
    for (let i = 0; i < PIPELINE_STEPS.length; i++) {
      await new Promise((r) => setTimeout(r, 600));
      setActiveStep(i);
    }
    setPipelineRunning(false);
  }, []);

  const runLifecycle = useCallback(async (agent: "shopper" | "inventory") => {
    const setter = agent === "shopper" ? setShopperStep : setInventoryStep;
    const steps = agent === "shopper" ? SHOPPER_LIFECYCLE : INVENTORY_LIFECYCLE;
    setter(null);
    for (let i = 0; i < steps.length; i++) {
      await new Promise((r) => setTimeout(r, 500));
      setter(i);
    }
  }, []);

  const LOG_COLORS = { info: "text-muted-foreground", success: "text-status-online", warning: "text-status-warning" };

  return (
    <div className="p-4 md:p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Brain className="h-6 w-6 text-primary" />
          AI Agent Architecture
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Blackboard pattern: Shopper + Inventory agents coordinate via Qdrant shared semantic memory — no direct agent-to-agent calls
        </p>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="flex-wrap h-auto gap-1">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="shopper">Shopper Agent</TabsTrigger>
          <TabsTrigger value="inventory">Inventory Agent</TabsTrigger>
          <TabsTrigger value="memory">Shared Memory</TabsTrigger>
          <TabsTrigger value="guardrails">Guardrails</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
          <TabsTrigger value="live">Live Monitor</TabsTrigger>
          <TabsTrigger value="hitl">Human-in-the-Loop</TabsTrigger>
        </TabsList>

        {/* ─── Overview ─── */}
        <TabsContent value="overview" className="space-y-6">
          {/* Blackboard architecture diagram */}
          <Card className="border-border overflow-hidden">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <GitMerge className="h-4 w-4 text-primary" />
                Blackboard / Agentic-RAG Architecture
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col md:flex-row items-center gap-4">
                {/* Shopper */}
                <div className="flex-1 rounded-xl border border-primary/30 bg-primary/5 p-4 space-y-2 text-center">
                  <AgentAvatar type="shopper" online size="lg" />
                  <h3 className="font-bold text-sm">Shopper Agent</h3>
                  <p className="text-xs text-muted-foreground">Customer-facing: NLU, goal extraction, preference modeling, feedback capture</p>
                  <div className="flex flex-wrap gap-1 justify-center mt-2">
                    {["NLU", "Clarify", "Normalize", "Prefs", "Feedback"].map(t => (
                      <Badge key={t} variant="outline" className="text-[10px]">{t}</Badge>
                    ))}
                  </div>
                </div>

                {/* Arrows to Qdrant */}
                <div className="flex flex-col items-center gap-1">
                  <ArrowRight className="h-5 w-5 text-primary hidden md:block" />
                  <ArrowDown className="h-5 w-5 text-primary md:hidden" />
                  <span className="text-[10px] text-muted-foreground">writes goals</span>
                </div>

                {/* Qdrant (center) */}
                <div className="flex-1 rounded-xl border-2 border-accent/50 bg-accent/5 p-4 space-y-2 text-center">
                  <Database className="h-8 w-8 mx-auto text-accent" />
                  <h3 className="font-bold text-sm">Qdrant Shared Memory</h3>
                  <p className="text-xs text-muted-foreground">Blackboard: goals, solutions, episodes, shopper_memory, inventory_memory</p>
                  <div className="flex flex-wrap gap-1 justify-center mt-2">
                    {COLLECTIONS.map(c => (
                      <Badge key={c.name} variant="secondary" className="text-[10px] font-mono">{c.name}</Badge>
                    ))}
                  </div>
                </div>

                {/* Arrows from Qdrant */}
                <div className="flex flex-col items-center gap-1">
                  <ArrowRight className="h-5 w-5 text-accent hidden md:block" />
                  <ArrowDown className="h-5 w-5 text-accent md:hidden" />
                  <span className="text-[10px] text-muted-foreground">polls goals</span>
                </div>

                {/* Inventory */}
                <div className="flex-1 rounded-xl border border-accent/30 bg-accent/5 p-4 space-y-2 text-center">
                  <AgentAvatar type="inventory" online size="lg" />
                  <h3 className="font-bold text-sm">Inventory Agent</h3>
                  <p className="text-xs text-muted-foreground">Back-office: goal intake, constraint reasoning, bundle construction, learning</p>
                  <div className="flex flex-wrap gap-1 justify-center mt-2">
                    {["Poll", "Episodes", "WMS/ERP", "Bundle", "Rank"].map(t => (
                      <Badge key={t} variant="outline" className="text-[10px]">{t}</Badge>
                    ))}
                  </div>
                </div>
              </div>

              {/* Key principle */}
              <div className="mt-6 rounded-lg bg-muted/30 border border-border p-3 text-center">
                <p className="text-xs text-muted-foreground italic">
                  "Both agents coordinate <strong>only</strong> via Qdrant collections — no direct LLM-to-LLM calls. This is the blackboard pattern."
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Pipeline simulator */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Zap className="h-4 w-4 text-primary" />
                  Pipeline Simulation
                </CardTitle>
                <Button size="sm" variant="outline" onClick={runPipeline} disabled={pipelineRunning}>
                  {pipelineRunning ? <><Activity className="h-3 w-3 animate-pulse mr-1" /> Running…</> : <><Zap className="h-3 w-3 mr-1" /> Simulate</>}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                {PIPELINE_STEPS.map((step, i) => {
                  const done = activeStep !== null && activeStep >= i;
                  const active = activeStep === i;
                  return (
                    <div key={i} className="flex sm:flex-col items-center gap-2 flex-1">
                      <div className={cn(
                        "w-full rounded-lg border p-3 text-center space-y-1 transition-all duration-300",
                        active ? cn(step.color, "scale-[1.03] shadow-lg") :
                        done ? "border-status-online/30 bg-status-online/5" : "border-border bg-muted/20"
                      )}>
                        <div className="text-2xl">{step.icon}</div>
                        <div className={cn("text-xs font-semibold", done ? "text-foreground" : "text-muted-foreground")}>{step.label}</div>
                        <div className="text-[10px] text-muted-foreground leading-tight">{step.desc}</div>
                        <div className={cn("text-xs font-mono font-bold mt-1", done ? "text-status-online" : "text-muted-foreground")}>
                          {done ? step.latency : "—"}
                        </div>
                        {done && <CheckCircle className="w-3.5 h-3.5 text-status-online mx-auto" />}
                      </div>
                      {i < PIPELINE_STEPS.length - 1 && (
                        <div className={cn("hidden sm:block text-xl transition-colors", done ? "text-primary" : "text-muted-foreground/30")}>→</div>
                      )}
                    </div>
                  );
                })}
              </div>
              {activeStep === PIPELINE_STEPS.length - 1 && (
                <div className="mt-4 rounded-lg border border-status-online/30 bg-status-online/5 p-3 flex items-center justify-between animate-fade-in">
                  <div className="text-sm font-medium text-status-online">✓ Goal fulfilled — bundle streamed via SSE</div>
                  <div className="text-xs text-muted-foreground font-mono">total: 72ms · cache: HIT · confidence: 0.92</div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Side-by-side agent cards */}
          <div className="grid md:grid-cols-2 gap-4">
            <Card className="border-primary/20">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <ShoppingCart className="h-4 w-4 text-primary" />
                  Shopper Agent — Customer-Facing
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {SHOPPER_CAPABILITIES.map((cap, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs">
                    <cap.icon className="h-3.5 w-3.5 text-primary shrink-0 mt-0.5" />
                    <div>
                      <span className="font-medium">{cap.label}:</span>{" "}
                      <span className="text-muted-foreground">{cap.desc}</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="border-accent/20">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Package className="h-4 w-4 text-accent" />
                  Inventory Agent — Back-Office
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {INVENTORY_CAPABILITIES.map((cap, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs">
                    <cap.icon className="h-3.5 w-3.5 text-accent shrink-0 mt-0.5" />
                    <div>
                      <span className="font-medium">{cap.label}:</span>{" "}
                      <span className="text-muted-foreground">{cap.desc}</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* ─── Shopper Agent Detail ─── */}
        <TabsContent value="shopper" className="space-y-4">
          <Card className="border-primary/20">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm flex items-center gap-2">
                  <ShoppingCart className="h-4 w-4 text-primary" />
                  Shopper Agent Lifecycle
                </CardTitle>
                <Button size="sm" variant="outline" onClick={() => runLifecycle("shopper")}>
                  <Zap className="h-3 w-3 mr-1" /> Simulate
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {SHOPPER_LIFECYCLE.map((s, i) => {
                  const done = shopperStep !== null && shopperStep >= i;
                  const active = shopperStep === i;
                  return (
                    <div key={i} className={cn(
                      "rounded-lg border p-3 space-y-1 transition-all duration-300",
                      active ? "border-primary bg-primary/10 scale-[1.02]" :
                      done ? "border-status-online/30 bg-status-online/5" : "border-border"
                    )}>
                      <div className="flex items-center gap-2">
                        <div className={cn(
                          "w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold",
                          done ? "bg-status-online/20 text-status-online" : "bg-muted text-muted-foreground"
                        )}>{s.step}</div>
                        <s.icon className={cn("h-4 w-4", done ? "text-primary" : "text-muted-foreground")} />
                        <span className="text-xs font-semibold">{s.label}</span>
                      </div>
                      <p className="text-[11px] text-muted-foreground pl-8">{s.desc}</p>
                      {done && <CheckCircle className="h-3 w-3 text-status-online ml-8" />}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Tools */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Shopper Agent Tools</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid sm:grid-cols-2 gap-2">
                {[
                  { tool: "catalog_search", desc: "Search product catalog by attributes" },
                  { tool: "attribute_schema", desc: "Introspect catalog ontology for normalization" },
                  { tool: "user_profile_api", desc: "Fetch user prefs, history, LTV from shopper_memory" },
                  { tool: "qdrant_write_goal", desc: "Embed and upsert goal to goals collection" },
                  { tool: "qdrant_poll_solutions", desc: "Poll solutions by goal_id + outcome filter" },
                  { tool: "qdrant_write_episode", desc: "Write feedback episode to goal_solution_links" },
                ].map(t => (
                  <div key={t.tool} className="flex items-center gap-2 text-xs p-2 rounded-lg bg-muted/30 border border-border">
                    <code className="text-primary font-mono text-[10px]">{t.tool}</code>
                    <span className="text-muted-foreground">— {t.desc}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── Inventory Agent Detail ─── */}
        <TabsContent value="inventory" className="space-y-4">
          <Card className="border-accent/20">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Package className="h-4 w-4 text-accent" />
                  Inventory Agent Lifecycle
                </CardTitle>
                <Button size="sm" variant="outline" onClick={() => runLifecycle("inventory")}>
                  <Zap className="h-3 w-3 mr-1" /> Simulate
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {INVENTORY_LIFECYCLE.map((s, i) => {
                  const done = inventoryStep !== null && inventoryStep >= i;
                  const active = inventoryStep === i;
                  return (
                    <div key={i} className={cn(
                      "rounded-lg border p-3 space-y-1 transition-all duration-300",
                      active ? "border-accent bg-accent/10 scale-[1.02]" :
                      done ? "border-status-online/30 bg-status-online/5" : "border-border"
                    )}>
                      <div className="flex items-center gap-2">
                        <div className={cn(
                          "w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold",
                          done ? "bg-status-online/20 text-status-online" : "bg-muted text-muted-foreground"
                        )}>{s.step}</div>
                        <s.icon className={cn("h-4 w-4", done ? "text-accent" : "text-muted-foreground")} />
                        <span className="text-xs font-semibold">{s.label}</span>
                      </div>
                      <p className="text-[11px] text-muted-foreground pl-8">{s.desc}</p>
                      {done && <CheckCircle className="h-3 w-3 text-status-online ml-8" />}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Agentic RAG example */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Brain className="h-4 w-4" /> Agentic RAG — Episode-Augmented Planning
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted/50 p-4 rounded-lg text-xs font-mono overflow-x-auto leading-relaxed">
{`# Before generating a bundle, retrieve similar successful episodes
episodes = qdrant.search(
    collection="goal_solution_links",
    query_vector=embed(current_goal),
    filter={"success": True},
    limit=3
)

# Inject into planning prompt
prompt = f"""
Current goal: {goal.text}
Budget: {goal.budget_max} | Region: {goal.location} | Deadline: {goal.deadline}

Here are 3 successful past solutions for similar goals:
{format_episodes(episodes)}

Propose a new bundle or explain why past solutions don't fit.
Rank by: margin × feasibility × preference_score
"""
bundle = llm.generate(prompt, tools=[inventory_api, pricing_engine])`}
              </pre>
            </CardContent>
          </Card>

          {/* Tools */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Inventory Agent Tools</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid sm:grid-cols-2 gap-2">
                {[
                  { tool: "warehouse_stock_api", desc: "Query WMS for real-time stock levels by SKU + region" },
                  { tool: "pricing_engine", desc: "Get current pricing, promotions, margin calculations" },
                  { tool: "shipping_estimator", desc: "Estimate delivery times and costs by carrier + region" },
                  { tool: "reservation_api", desc: "Place soft reservations on items during bundle construction" },
                  { tool: "qdrant_search_episodes", desc: "Retrieve successful episodes for agentic RAG planning" },
                  { tool: "qdrant_write_solution", desc: "Upsert candidate bundles with feasibility + confidence" },
                ].map(t => (
                  <div key={t.tool} className="flex items-center gap-2 text-xs p-2 rounded-lg bg-muted/30 border border-border">
                    <code className="text-accent font-mono text-[10px]">{t.tool}</code>
                    <span className="text-muted-foreground">— {t.desc}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── Shared Memory ─── */}
        <TabsContent value="memory" className="space-y-4">
          {COLLECTIONS.map(col => (
            <Card key={col.name} className="border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Database className="h-4 w-4 text-accent" />
                  <code className="font-mono text-primary">{col.name}</code>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="text-xs text-muted-foreground">
                  <span className="font-medium">Vectors:</span> {col.vectors}
                </div>
                <div className="flex flex-wrap gap-1">
                  {col.fields.map(f => (
                    <Badge key={f} variant="outline" className="text-[10px] font-mono">{f}</Badge>
                  ))}
                </div>
                {col.statuses.length > 0 && (
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] text-muted-foreground">Statuses:</span>
                    {col.statuses.map(s => (
                      <Badge key={s} variant="secondary" className="text-[10px]">{s}</Badge>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* ─── Guardrails ─── */}
        <TabsContent value="guardrails" className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            {GUARDRAILS.map((g, i) => (
              <Card key={i} className="border-border">
                <CardContent className="p-4 space-y-2">
                  <div className="flex items-center gap-2">
                    <g.icon className="h-5 w-5 text-primary" />
                    <h3 className="font-bold text-sm">{g.title}</h3>
                  </div>
                  <p className="text-xs text-muted-foreground">{g.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* ─── Metrics ─── */}
        <TabsContent value="metrics">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <TrendingUp className="h-4 w-4" /> Agent Performance & Learning Metrics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Metric</TableHead>
                    <TableHead>Formula</TableHead>
                    <TableHead>Target</TableHead>
                    <TableHead>Current</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {AGENT_METRICS.map(m => (
                    <TableRow key={m.metric}>
                      <TableCell className="font-medium text-sm">{m.metric}</TableCell>
                      <TableCell className="text-xs text-muted-foreground font-mono">{m.formula}</TableCell>
                      <TableCell><Badge variant="outline" className="text-[10px]">{m.target}</Badge></TableCell>
                      <TableCell className="font-bold text-status-online">{m.current}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Example story */}
          <Card className="mt-4 border-border bg-muted/20">
            <CardContent className="p-4">
              <p className="text-xs text-muted-foreground italic">
                <strong>Example:</strong> For "2-person tent under 200, Zurich by Friday" — first time uses rules only. 
                Later, when a similar goal appears, inventory agent finds a converting episode with a specific bundle + shipping choice, 
                biases to that pattern, and acceptance/margin metrics improve. This is how the system gets smarter.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── Live Monitor ─── */}
        <TabsContent value="live" className="space-y-4">
          {/* Agent status cards */}
          <div className="grid sm:grid-cols-3 gap-3">
            {[
              { type: "supervisor" as const, label: "Supervisor", latency: "12ms", goals: 347, online: true },
              { type: "shopper" as const, label: "Shopper", latency: "18ms", goals: 289, online: true },
              { type: "inventory" as const, label: "Inventory", latency: "42ms", goals: 289, online: true },
            ].map(a => (
              <Card key={a.type} className="border-border">
                <CardContent className="p-3 flex items-center gap-3">
                  <AgentAvatar type={a.type} online={a.online} size="md" />
                  <div className="flex-1">
                    <div className="font-semibold text-sm">{a.label}</div>
                    <div className="flex gap-3 text-xs text-muted-foreground mt-0.5">
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{a.latency}</span>
                      <span className="flex items-center gap-1"><Zap className="w-3 h-3" />{a.goals} goals</span>
                    </div>
                  </div>
                  <Badge variant="outline" className="text-[10px] text-status-online border-status-online/30">Running</Badge>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Semaphore */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Lock className="h-4 w-4 text-primary" />
                Semaphore Pool — 16 Concurrent Slots
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-8 gap-1.5">
                {Array.from({ length: 16 }).map((_, i) => {
                  const agent = i < 2 ? "S" : i < 3 ? "s" : i < 6 ? "I" : null;
                  return (
                    <div key={i} className={cn(
                      "h-8 rounded-md border text-xs flex items-center justify-center font-medium",
                      agent === "S" ? "bg-primary/20 border-primary/40 text-primary" :
                      agent === "s" ? "bg-accent/20 border-accent/40 text-accent" :
                      agent === "I" ? "bg-status-info/20 border-status-info/40 text-status-info" :
                      "bg-muted/40 border-border text-muted-foreground/40"
                    )}>{agent || "·"}</div>
                  );
                })}
              </div>
              <div className="flex gap-3 text-xs text-muted-foreground mt-2">
                <span className="text-primary">S=Supervisor</span>
                <span className="text-accent">s=Shopper</span>
                <span className="text-status-info">I=Inventory</span>
                <span className="ml-auto">6/16 active</span>
              </div>
            </CardContent>
          </Card>

          {/* Live logs */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Activity className="h-4 w-4 text-primary" /> Execution Logs
                </CardTitle>
                <Button
                  size="sm"
                  variant={live ? "default" : "outline"}
                  onClick={() => setLive(!live)}
                >
                  {live ? "● Live" : "○ Start Live"}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="font-mono text-xs space-y-1 max-h-64 overflow-y-auto bg-muted/20 rounded-lg p-3">
                {logs.map((log) => (
                  <div key={log.id} className={cn("flex gap-3", LOG_COLORS[log.type])}>
                    <span className="opacity-50 shrink-0">{log.time}</span>
                    <span className="text-primary shrink-0">[{log.agent}]</span>
                    <span>{log.message}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── Human-in-the-Loop ─── */}
        <TabsContent value="hitl" className="space-y-6">
          <HITLSection />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ─── HITL Data ────────────────────────────────────────────────────────────────

const HITL_TRIGGERS = [
  { trigger: "Low Confidence Bundle", desc: "Inventory Agent proposes bundles with <80% confidence score", icon: AlertTriangle, threshold: "<0.80", frequency: "~12% of goals" },
  { trigger: "Ambiguous Goal", desc: "Shopper Agent detects conflicting constraints (e.g., budget vs. delivery speed)", icon: MessageSquare, threshold: "conflict_score > 0.6", frequency: "~8% of goals" },
  { trigger: "High-Margin Order", desc: "Orders above margin threshold requiring pricing approval from merchant", icon: TrendingUp, threshold: "margin > 40%", frequency: "~5% of goals" },
  { trigger: "No Episodic Match", desc: "No similar successful episodes found in goal_solution_links collection", icon: Brain, threshold: "similarity < 0.5", frequency: "~15% of goals" },
  { trigger: "Stock Conflict", desc: "Reservation race condition or partial stock availability across warehouses", icon: Package, threshold: "stock_risk > 0.7", frequency: "~3% of goals" },
  { trigger: "New Category", desc: "Goal maps to a category with fewer than 5 historical episodes", icon: Database, threshold: "episode_count < 5", frequency: "~6% of goals" },
];

type ReviewItem = {
  id: string;
  goalText: string;
  userId: string;
  region: string;
  trigger: string;
  confidence: number;
  proposals: { sku: string; name: string; price: number; match: number }[];
  status: "pending" | "approved" | "rejected" | "edited";
  timestamp: string;
  agentNotes: string;
};

const MOCK_REVIEW_QUEUE: ReviewItem[] = [
  {
    id: "goal-8821", goalText: "2-person tent under 200CHF, Zurich by Friday", userId: "user_7832",
    region: "Zurich", trigger: "Low Confidence", confidence: 0.67,
    proposals: [
      { sku: "TENT-MSR-NX2", name: "MSR Hubba Hubba NX2", price: 178, match: 92 },
      { sku: "TENT-NF-STORM", name: "NorthFace Stormbreak 2", price: 199, match: 91 },
      { sku: "TENT-BIG-COP", name: "Big Agnes Copper Spur", price: 195, match: 85 },
    ],
    status: "pending", timestamp: "14:32:01",
    agentNotes: "Bundle confidence below threshold (0.67 < 0.80). Two products near budget ceiling. No strong episodic match for Zurich + Friday deadline combo.",
  },
  {
    id: "goal-8834", goalText: "Premium sleeping bag for -20°C Alpine expedition", userId: "user_2190",
    region: "Bern", trigger: "High Margin", confidence: 0.89,
    proposals: [
      { sku: "BAG-WM-KODIAK", name: "Western Mountaineering Kodiak", price: 589, match: 96 },
      { sku: "BAG-FF-SNOW", name: "Feathered Friends Snowbunting", price: 549, match: 94 },
    ],
    status: "pending", timestamp: "14:28:45",
    agentNotes: "High-margin order (52% margin). Confidence is good but requires merchant pricing approval per policy.",
  },
  {
    id: "goal-8847", goalText: "Camping stove that works above 3000m, budget flexible", userId: "user_4401",
    region: "Geneva", trigger: "No Episodes", confidence: 0.52,
    proposals: [
      { sku: "STOVE-MSR-WLI", name: "MSR WhisperLite International", price: 129, match: 78 },
      { sku: "STOVE-JB-FLASH", name: "Jetboil Flash", price: 109, match: 71 },
    ],
    status: "pending", timestamp: "14:25:12",
    agentNotes: "No successful episodes found for high-altitude stove queries. Category has only 2 historical episodes. Agent cannot rank with confidence.",
  },
];

const HITL_FLOW_STEPS = [
  { step: 1, label: "Agent Detects Trigger", desc: "Inventory or Shopper agent identifies a condition requiring human review", icon: AlertTriangle, color: "text-status-warning" },
  { step: 2, label: "Status → pending_human_review", desc: "Goal status updated in Qdrant goals collection via set_payload", icon: Database, color: "text-accent" },
  { step: 3, label: "Dashboard Polls Queue", desc: "Merchant dashboard scrolls goals with status='pending_human_review'", icon: Search, color: "text-primary" },
  { step: 4, label: "Merchant Reviews", desc: "Human approves, rejects, or edits proposed bundles with optional feedback", icon: UserCheck, color: "text-status-info" },
  { step: 5, label: "Outcome Stored", desc: "Decision + feedback written to goal_solution_links as episodic memory", icon: Brain, color: "text-status-online" },
  { step: 6, label: "Agent Learns", desc: "Future similar goals use this episode — HITL decisions improve agent confidence over time", icon: TrendingUp, color: "text-primary" },
];

const HITL_METRICS = [
  { metric: "Review Queue Depth", value: "3", target: "<10", status: "good" },
  { metric: "Avg Review Time", value: "45s", target: "<120s", status: "good" },
  { metric: "Approval Rate", value: "72%", target: ">60%", status: "good" },
  { metric: "Edit Rate", value: "18%", target: "<25%", status: "good" },
  { metric: "Rejection Rate", value: "10%", target: "<15%", status: "good" },
  { metric: "Learning Impact", value: "+23%", target: ">15%", status: "good" },
  { metric: "Auto-Resolve After HITL", value: "89%", target: ">80%", status: "good" },
  { metric: "Escalation Rate", value: "8.2%", target: "<12%", status: "good" },
];

// ─── HITL Component ──────────────────────────────────────────────────────────

function HITLSection() {
  const [reviewQueue, setReviewQueue] = useState<ReviewItem[]>(MOCK_REVIEW_QUEUE);
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(null);
  const [feedback, setFeedback] = useState("");
  const [flowStep, setFlowStep] = useState<number | null>(null);
  const [simRunning, setSimRunning] = useState(false);

  const handleAction = (id: string, action: "approved" | "rejected" | "edited") => {
    setReviewQueue(prev => prev.map(item =>
      item.id === id ? { ...item, status: action } : item
    ));
    setSelectedItem(null);
    setFeedback("");
  };

  const runFlowSim = useCallback(async () => {
    setSimRunning(true);
    setFlowStep(null);
    for (let i = 0; i < HITL_FLOW_STEPS.length; i++) {
      await new Promise(r => setTimeout(r, 700));
      setFlowStep(i);
    }
    setSimRunning(false);
  }, []);

  const pendingCount = reviewQueue.filter(r => r.status === "pending").length;
  const resolvedCount = reviewQueue.filter(r => r.status !== "pending").length;

  return (
    <div className="space-y-6">
      {/* Header stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Card className="border-border">
          <CardContent className="p-4 text-center">
            <UserCheck className="h-5 w-5 mx-auto text-primary mb-1" />
            <div className="text-2xl font-bold">{pendingCount}</div>
            <div className="text-xs text-muted-foreground">Pending Review</div>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="p-4 text-center">
            <CheckCircle className="h-5 w-5 mx-auto text-status-online mb-1" />
            <div className="text-2xl font-bold">{resolvedCount}</div>
            <div className="text-xs text-muted-foreground">Resolved</div>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="p-4 text-center">
            <Clock className="h-5 w-5 mx-auto text-status-warning mb-1" />
            <div className="text-2xl font-bold">45s</div>
            <div className="text-xs text-muted-foreground">Avg Review Time</div>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="p-4 text-center">
            <TrendingUp className="h-5 w-5 mx-auto text-accent mb-1" />
            <div className="text-2xl font-bold">+23%</div>
            <div className="text-xs text-muted-foreground">Learning Impact</div>
          </CardContent>
        </Card>
      </div>

      {/* HITL Flow Diagram */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm flex items-center gap-2">
              <RotateCcw className="h-4 w-4 text-primary" />
              HITL Workflow — Agent → Human → Learning Loop
            </CardTitle>
            <Button size="sm" variant="outline" onClick={runFlowSim} disabled={simRunning}>
              {simRunning ? <><Activity className="h-3 w-3 animate-pulse mr-1" /> Simulating…</> : <><Zap className="h-3 w-3 mr-1" /> Simulate Flow</>}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {HITL_FLOW_STEPS.map((step, i) => {
              const active = flowStep !== null && flowStep >= i;
              const current = flowStep === i;
              const Icon = step.icon;
              return (
                <div key={i} className={cn(
                  "rounded-lg border p-3 text-center transition-all duration-300 space-y-1",
                  current ? "border-primary/50 bg-primary/10 scale-[1.03] shadow-md" :
                  active ? "border-status-online/30 bg-status-online/5" :
                  "border-border bg-muted/20"
                )}>
                  <div className="text-xs text-muted-foreground font-mono">Step {step.step}</div>
                  <Icon className={cn("h-5 w-5 mx-auto", active ? step.color : "text-muted-foreground")} />
                  <div className="text-xs font-semibold">{step.label}</div>
                  <div className="text-[10px] text-muted-foreground leading-tight">{step.desc}</div>
                </div>
              );
            })}
          </div>
          <div className="mt-4 rounded-lg bg-muted/30 border border-border p-3 text-center">
            <p className="text-xs text-muted-foreground italic">
              "Every human decision becomes episodic memory — agents learn from merchant expertise and reduce escalation rate over time."
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Trigger conditions */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-status-warning" />
            HITL Trigger Conditions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {HITL_TRIGGERS.map((t, i) => {
              const Icon = t.icon;
              return (
                <div key={i} className="rounded-lg border border-border bg-muted/20 p-3 space-y-2">
                  <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4 text-status-warning shrink-0" />
                    <span className="text-sm font-semibold">{t.trigger}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">{t.desc}</p>
                  <div className="flex items-center justify-between text-[10px]">
                    <Badge variant="outline" className="font-mono text-[10px]">{t.threshold}</Badge>
                    <span className="text-muted-foreground">{t.frequency}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Review Queue */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Eye className="h-4 w-4 text-primary" />
            Merchant Review Queue
            <Badge variant="secondary" className="text-[10px] ml-2">{pendingCount} pending</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {reviewQueue.map((item) => (
            <div key={item.id} className={cn(
              "rounded-lg border p-4 transition-all",
              item.status === "approved" ? "border-status-online/30 bg-status-online/5" :
              item.status === "rejected" ? "border-status-error/30 bg-status-error/5" :
              item.status === "edited" ? "border-status-info/30 bg-status-info/5" :
              "border-border bg-muted/10 hover:border-primary/30"
            )}>
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="outline" className="text-[10px] font-mono">{item.id}</Badge>
                    <Badge variant="secondary" className="text-[10px]">{item.trigger}</Badge>
                    <Badge variant="outline" className="text-[10px]">
                      {item.region}
                    </Badge>
                    <span className="text-[10px] text-muted-foreground">{item.timestamp}</span>
                  </div>
                  <p className="text-sm font-medium">{item.goalText}</p>
                  <p className="text-xs text-muted-foreground">User: {item.userId}</p>

                  {/* Agent notes */}
                  <div className="rounded-md bg-muted/30 border border-border p-2">
                    <p className="text-[10px] text-muted-foreground font-semibold mb-1">Agent Notes:</p>
                    <p className="text-xs text-muted-foreground">{item.agentNotes}</p>
                  </div>

                  {/* Proposals */}
                  <div className="space-y-1.5">
                    <p className="text-[10px] text-muted-foreground font-semibold">Proposed Solutions:</p>
                    {item.proposals.map((p, pi) => (
                      <div key={pi} className="flex items-center justify-between rounded-md border border-border bg-background p-2">
                        <div className="flex items-center gap-2">
                          <Package className="h-3 w-3 text-muted-foreground" />
                          <span className="text-xs font-medium">{p.name}</span>
                          <Badge variant="outline" className="text-[10px] font-mono">{p.sku}</Badge>
                        </div>
                        <div className="flex items-center gap-3 text-xs">
                          <span className="font-mono">{p.price} CHF</span>
                          <span className={cn("font-semibold", p.match >= 90 ? "text-status-online" : p.match >= 80 ? "text-status-warning" : "text-status-error")}>
                            {p.match}% match
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Confidence bar */}
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-[10px]">
                      <span className="text-muted-foreground">Confidence</span>
                      <span className={cn("font-mono font-semibold",
                        item.confidence >= 0.8 ? "text-status-online" :
                        item.confidence >= 0.6 ? "text-status-warning" : "text-status-error"
                      )}>
                        {(item.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <Progress value={item.confidence * 100} className="h-1.5" />
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-1.5 shrink-0">
                  {item.status === "pending" ? (
                    <>
                      <Button size="sm" variant="outline" className="text-xs border-status-online/30 text-status-online hover:bg-status-online/10" onClick={() => handleAction(item.id, "approved")}>
                        <ThumbsUp className="h-3 w-3 mr-1" /> Approve
                      </Button>
                      <Button size="sm" variant="outline" className="text-xs border-status-error/30 text-status-error hover:bg-status-error/10" onClick={() => handleAction(item.id, "rejected")}>
                        <ThumbsDown className="h-3 w-3 mr-1" /> Reject
                      </Button>
                      <Button size="sm" variant="outline" className="text-xs" onClick={() => setSelectedItem(item)}>
                        <Edit3 className="h-3 w-3 mr-1" /> Edit
                      </Button>
                    </>
                  ) : (
                    <Badge className={cn("text-xs",
                      item.status === "approved" ? "bg-status-online/20 text-status-online border-status-online/30" :
                      item.status === "rejected" ? "bg-status-error/20 text-status-error border-status-error/30" :
                      "bg-status-info/20 text-status-info border-status-info/30"
                    )}>
                      {item.status === "approved" ? <ThumbsUp className="h-3 w-3 mr-1" /> :
                       item.status === "rejected" ? <ThumbsDown className="h-3 w-3 mr-1" /> :
                       <Edit3 className="h-3 w-3 mr-1" />}
                      {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                    </Badge>
                  )}
                </div>
              </div>

              {/* Edit feedback area */}
              {selectedItem?.id === item.id && (
                <div className="mt-3 pt-3 border-t border-border space-y-2">
                  <textarea
                    className="w-full bg-muted border border-border rounded-lg px-3 py-2 text-sm outline-none focus:border-primary/50 resize-none"
                    rows={2}
                    placeholder="Merchant feedback (e.g., 'Customer prefers lighter weight')"
                    value={feedback}
                    onChange={e => setFeedback(e.target.value)}
                  />
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => handleAction(item.id, "edited")} className="text-xs">
                      <CheckCircle className="h-3 w-3 mr-1" /> Submit Edit
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => { setSelectedItem(null); setFeedback(""); }} className="text-xs">
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Metrics */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Activity className="h-4 w-4 text-primary" />
            HITL Performance Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {HITL_METRICS.map((m, i) => (
              <div key={i} className="rounded-lg border border-border bg-muted/20 p-3 text-center space-y-1">
                <div className="text-lg font-bold">{m.value}</div>
                <div className="text-xs font-medium">{m.metric}</div>
                <div className="text-[10px] text-muted-foreground">Target: {m.target}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Qdrant Status Transitions */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Database className="h-4 w-4 text-accent" />
            Qdrant Status Transitions (HITL Path)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center justify-center gap-2 text-xs">
            {[
              { label: "open", color: "bg-status-info/20 text-status-info border-status-info/30" },
              { label: "→", color: "" },
              { label: "pending_inventory", color: "bg-status-warning/20 text-status-warning border-status-warning/30" },
              { label: "→", color: "" },
              { label: "pending_human_review", color: "bg-primary/20 text-primary border-primary/30" },
              { label: "→", color: "" },
              { label: "solved / failed", color: "bg-status-online/20 text-status-online border-status-online/30" },
            ].map((s, i) => s.label === "→" ? (
              <ArrowRight key={i} className="h-4 w-4 text-muted-foreground" />
            ) : (
              <Badge key={i} variant="outline" className={cn("font-mono", s.color)}>{s.label}</Badge>
            ))}
          </div>
          <div className="mt-4 rounded-lg bg-muted/20 border border-border p-3">
            <pre className="text-[11px] text-muted-foreground font-mono whitespace-pre-wrap leading-relaxed">{`# Qdrant HITL status flow
qdrant.set_payload(
  collection="goals",
  points=[goal_id],
  payload={"status": "pending_human_review", "proposed_solutions": [...]}
)

# Merchant dashboard polls
goals = qdrant.scroll(
  collection="goals",
  filter=Filter(must=[FieldCondition(key="status", match=MatchValue(value="pending_human_review"))]),
  limit=10
)

# After merchant decision → episode logged
qdrant.upsert("goal_solution_links", episode_with_human_feedback)`}</pre>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
