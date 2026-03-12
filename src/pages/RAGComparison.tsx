import { useState, useCallback } from "react";
import {
  ArrowRight, ArrowDown, Database, Bot, Brain, Zap,
  CheckCircle2, XCircle, RotateCcw, Layers, BookOpen,
  ShieldCheck, BarChart3, GitBranch, MessageSquare,
  Search, Package, Server, Activity, Eye, RefreshCw,
  Shield, TrendingUp, Clock, User, ImageIcon, Upload,
  Camera, ScanEye, Palette, Sparkles,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

/* ------------------------------------------------------------------ */
/*  Data                                                               */
/* ------------------------------------------------------------------ */

const COMPARISON_ROWS = [
  { dimension: "Control Flow", traditional: "Linear single-turn: retrieve → generate", agentic: "Multi-turn, multi-agent orchestration with async reads/writes" },
  { dimension: "Responsibility", traditional: "One model handles interpretation, reasoning & output", agentic: "Decomposed: Shopper = intent, Inventory = feasibility, Pricing = margins" },
  { dimension: "Memory & Reuse", traditional: "Ephemeral retrievals (maybe cached)", agentic: "Explicit episodic memory — continuous learning from outcomes" },
  { dimension: "Failure Recovery", traditional: "Single model fallback — harder partial recovery", agentic: "Targeted per-agent fallbacks, confidence gating, human-in-the-loop" },
  { dimension: "Scalability", traditional: "Scale at model-serving layer", agentic: "Scale by agents + DB partitions, agent concurrency" },
  { dimension: "Observability", traditional: "Single prompt/response log", agentic: "Per-agent traces, confidence scores, retrieval audits" },
];

const TRAD_STEPS = [
  { label: "User Query", icon: Bot, color: "text-primary" },
  { label: "Retrieve Top-K", icon: Database, color: "text-accent" },
  { label: "Compose Prompt", icon: Layers, color: "text-muted-foreground" },
  { label: "Generate Answer", icon: Zap, color: "text-status-online" },
];

const AGENTIC_STEPS = [
  { label: "User Query", icon: Bot, color: "text-primary" },
  { label: "Query Rewrite & Expand", icon: RotateCcw, color: "text-accent" },
  { label: "Primary Retrieval", icon: Database, color: "text-accent" },
  { label: "Episodic Memory Lookup", icon: BookOpen, color: "text-status-warning" },
  { label: "Context Scoring & Selection", icon: Brain, color: "text-primary" },
  { label: "Confidence Gate", icon: ShieldCheck, color: "text-status-error" },
  { label: "Fallback (if needed)", icon: GitBranch, color: "text-muted-foreground" },
  { label: "Multi-Agent Reasoning", icon: Layers, color: "text-accent" },
  { label: "Generate + Trace", icon: Zap, color: "text-status-online" },
];

const METRICS = [
  { label: "Time to First Solution", trad: "~120ms", agentic: "~42ms (cache hit)" },
  { label: "Episode Reuse Rate", trad: "0%", agentic: "67%" },
  { label: "Feasibility Rate", trad: "72%", agentic: "94%" },
  { label: "Conversion Rate", trad: "18%", agentic: "+24% lift" },
  { label: "Confidence Tracking", trad: "None", agentic: "Per-agent scores" },
];

const AGENTS = [
  { name: "Shopper Agent", role: "Intent extraction, dialog safety, user interaction", actions: ["Parse structured goal", "Embed & upsert to goals", "Present solutions"], color: "bg-primary/15 text-primary border-primary/25" },
  { name: "Inventory Agent", role: "Feasibility, stock/ETA, bundling, pricing", actions: ["Poll open goals", "Episodic retrieval", "Product search + filters", "Compose bundles"], color: "bg-accent/15 text-accent border-accent/25" },
  { name: "Pricing Agent", role: "Margin analysis, competitive positioning, bundle pricing", actions: ["Analyze margins", "Suggest bundle prices", "Competitive position"], color: "bg-status-warning/15 text-status-warning border-status-warning/25" },
  { name: "Merchandising Agent", role: "Assortment gaps, cross-sell, display priority", actions: ["Recommend cross-sells", "Identify gaps", "Rank display priority"], color: "bg-status-info/15 text-status-info border-status-info/25" },
];

// Chatbot pipeline data
const CHATBOT_PIPELINE_STEPS = [
  { label: "User Message", desc: "Natural language input via chat interface", icon: MessageSquare, color: "text-primary" },
  { label: "Embedding Model", desc: "Convert query to vector (NVmix-8B / bge-m3)", icon: Brain, color: "text-accent" },
  { label: "Qdrant Retriever", desc: "Multi-collection search: products, episodes, profiles", icon: Database, color: "text-accent" },
  { label: "Context Assembly", desc: "Merge retrieved docs + user profile + memory", icon: Layers, color: "text-status-warning" },
  { label: "Prompt Template", desc: "Inject context into agent-specific prompt", icon: BookOpen, color: "text-primary" },
  { label: "LLM Reasoning", desc: "GPT-4o-mini / Claude 3.5 / Llama 3.3", icon: Zap, color: "text-status-online" },
  { label: "Agent Response", desc: "Structured goal or ranked bundles", icon: CheckCircle2, color: "text-status-online" },
];

const SHOPPER_RAG_SOURCES = [
  { collection: "user_profiles", purpose: "Long-term preferences, brand affinities, price bands", icon: User },
  { collection: "goal_solution_links", purpose: "Past successful goals for bias toward converting patterns", icon: BookOpen },
  { collection: "products", purpose: "Catalog semantic search for category validation", icon: Package },
];

const INVENTORY_RAG_SOURCES = [
  { collection: "goal_solution_links", purpose: "Similar successful episodes (92% conversion patterns)", icon: BookOpen },
  { collection: "products", purpose: "Feasible SKUs matching constraints (stock > 0, region, price)", icon: Package },
  { collection: "procedural_memory", purpose: "Learned routing patterns and bundle heuristics", icon: Brain },
];

const QDRANT_COLLECTIONS = [
  { name: "products", purpose: "Product embeddings (catalog)", icon: Package, color: "text-accent" },
  { name: "user_profiles", purpose: "Long-term user preferences", icon: User, color: "text-primary" },
  { name: "goal_solution_links", purpose: "Episodic memory (experiences)", icon: BookOpen, color: "text-status-warning" },
  { name: "procedural_memory", purpose: "Learned agent patterns", icon: Brain, color: "text-status-info" },
  { name: "goals", purpose: "Active shopping goals", icon: Search, color: "text-primary" },
  { name: "solutions", purpose: "Generated bundles", icon: Package, color: "text-status-online" },
];

const ORCHESTRATION_TASKS = [
  { task: "Understand request", agent: "Shopper Agent", method: "NLU + user_profiles RAG" },
  { task: "Create structured goal", agent: "Shopper Agent", method: "LLM + schema validation" },
  { task: "Generate product bundles", agent: "Inventory Agent", method: "Episodic RAG + product search" },
  { task: "Validate stock/pricing", agent: "MCP Tools", method: "Warehouse API + Pricing Engine" },
  { task: "Rank & explain solutions", agent: "Inventory Agent", method: "LLM ranking + provenance" },
  { task: "Present to user", agent: "Shopper Agent", method: "Solution reranking by prefs" },
];

const MEMORY_TYPES = [
  { type: "Short-term", storage: "Session buffer (Redis)", retention: "1 hour", desc: "Current conversation context — last 5-10 turns", icon: Clock, color: "text-status-warning" },
  { type: "Long-term", storage: "Qdrant user_profiles", retention: "Permanent", desc: "User preferences, lifetime value, risk profile", icon: Database, color: "text-primary" },
  { type: "Episodic", storage: "Qdrant goal_solution_links", retention: "Permanent", desc: "Goal → solution → outcome experiences for learning", icon: BookOpen, color: "text-accent" },
  { type: "Procedural", storage: "Qdrant procedural_memory", retention: "Permanent", desc: "Learned routing patterns and agent coordination rules", icon: Brain, color: "text-status-online" },
];

const CONVERSATION_EXAMPLE = [
  { role: "user" as const, text: "I need a 2 person tent under 200 CHF" },
  { role: "system" as const, text: "Shopper Agent: Structured goal created\n→ category: camping_tent\n→ budget_max: 200 CHF\n→ capacity: 2 persons" },
  { role: "system" as const, text: "Inventory Agent: 3 episodes retrieved (89% similar)\n→ Bundle 1: MSR Hubba NX2 + mat = 180 CHF (92% conf)\n→ Bundle 2: NorthFace Stormbreak = 199 CHF (91% conf)" },
  { role: "assistant" as const, text: "Here are the best options for your camping trip! The MSR Hubba Hubba NX2 bundle at 180 CHF is the top pick — it matched 92% of similar successful requests." },
];

/* ------------------------------------------------------------------ */
/*  Components                                                         */
/* ------------------------------------------------------------------ */

function FlowDiagram({ steps, label }: { steps: typeof TRAD_STEPS; label: string }) {
  const [activeStep, setActiveStep] = useState(-1);

  const animate = () => {
    let i = 0;
    setActiveStep(0);
    const interval = setInterval(() => {
      i++;
      if (i >= steps.length) {
        clearInterval(interval);
        setTimeout(() => setActiveStep(-1), 1200);
      } else {
        setActiveStep(i);
      }
    }, 500);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-sm">{label}</h3>
        <Button size="sm" variant="outline" onClick={animate} className="gap-1.5 text-xs">
          <Zap className="w-3 h-3" /> Animate
        </Button>
      </div>
      <div className="flex flex-col gap-1">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          const active = idx === activeStep;
          const done = activeStep > idx;
          return (
            <div key={step.label}>
              <div className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg border transition-all duration-300",
                active ? "border-primary bg-primary/10 scale-[1.02] shadow-md" :
                done ? "border-status-online/30 bg-status-online/5 opacity-70" :
                "border-border bg-card"
              )}>
                <Icon className={cn("w-4 h-4 shrink-0", active ? "text-primary" : step.color)} />
                <span className="text-sm flex-1">{step.label}</span>
                {done && <CheckCircle2 className="w-3.5 h-3.5 text-status-online" />}
                {active && <span className="w-3.5 h-3.5 border-2 border-primary border-t-transparent rounded-full animate-spin" />}
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

function ChatbotPipelineSection() {
  const [pipelineStep, setPipelineStep] = useState<number | null>(null);
  const [simRunning, setSimRunning] = useState(false);

  const runSim = useCallback(async () => {
    setSimRunning(true);
    setPipelineStep(null);
    for (let i = 0; i < CHATBOT_PIPELINE_STEPS.length; i++) {
      await new Promise(r => setTimeout(r, 500));
      setPipelineStep(i);
    }
    setSimRunning(false);
  }, []);

  return (
    <div className="space-y-6">
      {/* Architecture overview */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Layers className="h-4 w-4 text-primary" />
            RAG Chatbot Architecture — Agentic Pipeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row items-center gap-3">
            {[
              { label: "User", icon: MessageSquare, color: "border-primary/30 bg-primary/5" },
              { label: "RAG Chatbot", icon: Bot, color: "border-accent/30 bg-accent/5" },
              { label: "Shopper Agent", icon: Search, color: "border-primary/30 bg-primary/5" },
              { label: "Inventory Agent", icon: Package, color: "border-status-warning/30 bg-status-warning/5" },
              { label: "MCP Tools", icon: Server, color: "border-status-info/30 bg-status-info/5" },
              { label: "Response", icon: CheckCircle2, color: "border-status-online/30 bg-status-online/5" },
            ].map((node, i, arr) => (
              <div key={node.label} className="flex items-center gap-2">
                <div className={cn("rounded-lg border p-3 text-center min-w-[100px]", node.color)}>
                  <node.icon className="h-5 w-5 mx-auto mb-1 text-foreground" />
                  <div className="text-xs font-semibold">{node.label}</div>
                </div>
                {i < arr.length - 1 && <ArrowRight className="h-4 w-4 text-muted-foreground hidden md:block shrink-0" />}
                {i < arr.length - 1 && <ArrowDown className="h-4 w-4 text-muted-foreground md:hidden shrink-0" />}
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-lg bg-muted/30 border border-border p-3 text-center">
            <p className="text-xs text-muted-foreground italic">
              "Qdrant provides shared memory and retrieval for both agents — the chatbot orchestrates multi-turn agentic RAG."
            </p>
          </div>
        </CardContent>
      </Card>

      {/* LangChain RAG Pipeline simulation */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm flex items-center gap-2">
              <Zap className="h-4 w-4 text-primary" />
              Agentic RAG Pipeline — Step-by-Step
            </CardTitle>
            <Button size="sm" variant="outline" onClick={runSim} disabled={simRunning}>
              {simRunning ? <><Activity className="h-3 w-3 animate-pulse mr-1" /> Running…</> : <><Zap className="h-3 w-3 mr-1" /> Simulate</>}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {CHATBOT_PIPELINE_STEPS.map((step, i) => {
              const active = pipelineStep !== null && pipelineStep >= i;
              const current = pipelineStep === i;
              const Icon = step.icon;
              return (
                <div key={i} className={cn(
                  "rounded-lg border p-3 transition-all duration-300 space-y-1",
                  current ? "border-primary/50 bg-primary/10 scale-[1.02] shadow-md" :
                  active ? "border-status-online/30 bg-status-online/5" :
                  "border-border bg-muted/20"
                )}>
                  <div className="flex items-center gap-2">
                    <Icon className={cn("h-4 w-4", active ? step.color : "text-muted-foreground")} />
                    <span className="text-xs font-semibold">{step.label}</span>
                  </div>
                  <p className="text-[10px] text-muted-foreground leading-tight">{step.desc}</p>
                  {current && <div className="h-1 bg-primary/30 rounded-full overflow-hidden"><div className="h-full bg-primary rounded-full animate-pulse w-2/3" /></div>}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Agent-specific RAG sources */}
      <div className="grid md:grid-cols-2 gap-4">
        <Card className="border-primary/20">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Search className="h-4 w-4 text-primary" />
              Shopper Agent RAG Sources
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {SHOPPER_RAG_SOURCES.map((s, i) => (
              <div key={i} className="rounded-lg border border-border bg-muted/20 p-3 space-y-1">
                <div className="flex items-center gap-2">
                  <s.icon className="h-4 w-4 text-primary" />
                  <Badge variant="outline" className="font-mono text-[10px]">{s.collection}</Badge>
                </div>
                <p className="text-xs text-muted-foreground">{s.purpose}</p>
              </div>
            ))}
            <div className="rounded-lg bg-muted/30 border border-border p-3">
              <p className="text-[10px] text-muted-foreground font-semibold mb-1">Prompt Template:</p>
              <pre className="text-[10px] text-muted-foreground font-mono whitespace-pre-wrap leading-relaxed">{`You are the Shopper Agent.
User request: {user_message}
User profile: {user_profile}
Past successful goals: {episodes}

Extract structured goal JSON:
{ "category", "constraints": { "price_max", "location" } }`}</pre>
            </div>
          </CardContent>
        </Card>

        <Card className="border-accent/20">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Package className="h-4 w-4 text-accent" />
              Inventory Agent RAG Sources
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {INVENTORY_RAG_SOURCES.map((s, i) => (
              <div key={i} className="rounded-lg border border-border bg-muted/20 p-3 space-y-1">
                <div className="flex items-center gap-2">
                  <s.icon className="h-4 w-4 text-accent" />
                  <Badge variant="outline" className="font-mono text-[10px]">{s.collection}</Badge>
                </div>
                <p className="text-xs text-muted-foreground">{s.purpose}</p>
              </div>
            ))}
            <div className="rounded-lg bg-muted/30 border border-border p-3">
              <p className="text-[10px] text-muted-foreground font-semibold mb-1">Prompt Template:</p>
              <pre className="text-[10px] text-muted-foreground font-mono whitespace-pre-wrap leading-relaxed">{`You are the Inventory Agent.
Goal: {structured_goal}
Successful episodes: {episodes}
Available products: {products}
Patterns: {procedural_memory}

Generate top 3 bundles with confidence scores.`}</pre>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Orchestration table */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <GitBranch className="h-4 w-4 text-primary" />
            Multi-Agent Orchestration Layer
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-border overflow-hidden">
            <div className="grid grid-cols-3 bg-muted/30 text-[10px] font-semibold uppercase tracking-wider">
              <div className="px-3 py-2 border-r border-border">Task</div>
              <div className="px-3 py-2 border-r border-border">Agent</div>
              <div className="px-3 py-2">Method</div>
            </div>
            {ORCHESTRATION_TASKS.map((t, i) => (
              <div key={i} className={cn("grid grid-cols-3 text-xs", i % 2 === 0 ? "bg-card" : "bg-card/50")}>
                <div className="px-3 py-2.5 border-r border-border font-medium">{t.task}</div>
                <div className="px-3 py-2.5 border-r border-border text-muted-foreground">{t.agent}</div>
                <div className="px-3 py-2.5 text-muted-foreground">{t.method}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Qdrant collections */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Database className="h-4 w-4 text-accent" />
            Qdrant Collections Used by Chatbot
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {QDRANT_COLLECTIONS.map((c) => (
              <div key={c.name} className="rounded-lg border border-border bg-muted/20 p-3 text-center space-y-1">
                <c.icon className={cn("h-5 w-5 mx-auto", c.color)} />
                <div className="text-xs font-semibold font-mono">{c.name}</div>
                <div className="text-[10px] text-muted-foreground">{c.purpose}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Example conversation */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <MessageSquare className="h-4 w-4 text-primary" />
            Example Conversation Flow
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {CONVERSATION_EXAMPLE.map((msg, i) => (
            <div key={i} className={cn("flex gap-3", msg.role === "user" && "flex-row-reverse")}>
              <div className={cn(
                "max-w-[85%] rounded-xl px-4 py-3 text-sm",
                msg.role === "user" ? "bg-primary/10 border border-primary/20 text-foreground" :
                msg.role === "system" ? "bg-muted/50 border border-border text-muted-foreground font-mono text-xs" :
                "bg-card border border-border text-foreground"
              )}>
                {msg.role === "system" && <Badge variant="outline" className="text-[9px] mb-1.5">Agent Internal</Badge>}
                <pre className="whitespace-pre-wrap leading-relaxed">{msg.text}</pre>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

function MemoryIntegrationSection() {
  const [simStep, setSimStep] = useState<number | null>(null);
  const [simRunning, setSimRunning] = useState(false);

  const MEMORY_FLOW = [
    { label: "User Query", desc: "Input enters short-term buffer", icon: MessageSquare },
    { label: "Short-term Context", desc: "Last 5 turns + current goal appended", icon: Clock },
    { label: "RAG Retrieval", desc: "Query user_profiles + episodes + products", icon: Search },
    { label: "Agent Reasoning", desc: "LLM plans with full memory context", icon: Brain },
    { label: "Solution Generation", desc: "Bundles created with provenance", icon: Package },
    { label: "Episode Stored", desc: "Outcome → goal_solution_links for learning", icon: Database },
  ];

  const runSim = useCallback(async () => {
    setSimRunning(true);
    setSimStep(null);
    for (let i = 0; i < MEMORY_FLOW.length; i++) {
      await new Promise(r => setTimeout(r, 600));
      setSimStep(i);
    }
    setSimRunning(false);
  }, []);

  return (
    <div className="space-y-6">
      {/* 4 memory types */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {MEMORY_TYPES.map((m) => (
          <Card key={m.type} className="border-border">
            <CardContent className="p-4 space-y-2">
              <div className="flex items-center gap-2">
                <m.icon className={cn("h-5 w-5", m.color)} />
                <span className="font-semibold text-sm">{m.type} Memory</span>
                <Badge variant="outline" className="text-[10px] ml-auto">{m.retention}</Badge>
              </div>
              <p className="text-xs text-muted-foreground">{m.desc}</p>
              <div className="text-[10px] text-muted-foreground font-mono bg-muted/30 rounded px-2 py-1">
                Storage: {m.storage}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Memory-enhanced RAG flow */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm flex items-center gap-2">
              <RefreshCw className="h-4 w-4 text-primary" />
              Memory-Enhanced RAG Workflow
            </CardTitle>
            <Button size="sm" variant="outline" onClick={runSim} disabled={simRunning}>
              {simRunning ? <><Activity className="h-3 w-3 animate-pulse mr-1" /> Running…</> : <><Zap className="h-3 w-3 mr-1" /> Simulate</>}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {MEMORY_FLOW.map((step, i) => {
              const active = simStep !== null && simStep >= i;
              const current = simStep === i;
              const Icon = step.icon;
              return (
                <div key={i} className={cn(
                  "rounded-lg border p-3 text-center transition-all duration-300 space-y-1",
                  current ? "border-primary/50 bg-primary/10 scale-[1.03] shadow-md" :
                  active ? "border-status-online/30 bg-status-online/5" :
                  "border-border bg-muted/20"
                )}>
                  <Icon className={cn("h-5 w-5 mx-auto", active ? "text-primary" : "text-muted-foreground")} />
                  <div className="text-xs font-semibold">{step.label}</div>
                  <div className="text-[10px] text-muted-foreground leading-tight">{step.desc}</div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Learning impact */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-status-online" />
            Memory Learning Impact
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border border-border bg-muted/20 p-4 space-y-3">
                <div className="text-xs font-semibold text-muted-foreground">Without Memory</div>
                {[
                  { label: "Goal #1", value: 60 },
                  { label: "Goal #5", value: 60 },
                  { label: "Goal #10", value: 60 },
                ].map(g => (
                  <div key={g.label} className="space-y-1">
                    <div className="flex justify-between text-[10px]">
                      <span>{g.label}</span><span className="text-muted-foreground">{g.value}%</span>
                    </div>
                    <Progress value={g.value} className="h-1.5" />
                  </div>
                ))}
              </div>
              <div className="rounded-lg border border-status-online/20 bg-status-online/5 p-4 space-y-3">
                <div className="text-xs font-semibold text-status-online">With Memory</div>
                {[
                  { label: "Goal #1", value: 60 },
                  { label: "Goal #5", value: 87 },
                  { label: "Goal #10", value: 94 },
                ].map(g => (
                  <div key={g.label} className="space-y-1">
                    <div className="flex justify-between text-[10px]">
                      <span>{g.label}</span><span className="text-status-online font-semibold">{g.value}%</span>
                    </div>
                    <Progress value={g.value} className="h-1.5" />
                  </div>
                ))}
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: "Accuracy", desc: "Real product data from Qdrant", icon: Shield },
                { label: "Personalization", desc: "Uses user profiles + episodes", icon: User },
                { label: "Continuous Learning", desc: "Episodic memory improves future", icon: TrendingUp },
              ].map(b => (
                <div key={b.label} className="rounded-lg border border-border bg-muted/20 p-3 text-center space-y-1">
                  <b.icon className="h-5 w-5 mx-auto text-primary" />
                  <div className="text-xs font-semibold">{b.label}</div>
                  <div className="text-[10px] text-muted-foreground">{b.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Production stack */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Server className="h-4 w-4 text-accent" />
            Production RAG Stack
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center gap-2">
            {[
              { label: "Frontend (Chat UI)", color: "border-primary/30 bg-primary/5" },
              { label: "Chatbot API (FastAPI / Edge Function)", color: "border-accent/30 bg-accent/5" },
              { label: "LangChain Agents (Shopper + Inventory)", color: "border-status-warning/30 bg-status-warning/5" },
              { label: "Qdrant Vector DB (6 Collections)", color: "border-accent/30 bg-accent/5" },
              { label: "MCP Services (Stock + Pricing + Shipping)", color: "border-status-info/30 bg-status-info/5" },
            ].map((layer, i, arr) => (
              <div key={layer.label} className="w-full max-w-md">
                <div className={cn("rounded-lg border p-3 text-center text-xs font-medium", layer.color)}>
                  {layer.label}
                </div>
                {i < arr.length - 1 && <div className="flex justify-center py-1"><ArrowDown className="h-3 w-3 text-muted-foreground/40" /></div>}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function RAGComparisonPage() {
  return (
    <div className="p-6 space-y-8 animate-fade-in max-w-6xl mx-auto">
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium">
          <Brain className="w-3.5 h-3.5" />
          RAG Chatbot + Agentic Architecture
        </div>
        <h1 className="text-3xl font-bold tracking-tight">RAG Architecture</h1>
        <p className="text-muted-foreground max-w-2xl">
          Agentic RAG chatbot powering Shopper + Inventory agents via Qdrant shared memory, LangChain pipelines, and MCP tool verification.
        </p>
      </div>

      <Tabs defaultValue="chatbot" className="space-y-6">
        <TabsList className="bg-muted/50 flex-wrap h-auto gap-1">
          <TabsTrigger value="chatbot">Chatbot Pipeline</TabsTrigger>
          <TabsTrigger value="memory">Memory Integration</TabsTrigger>
          <TabsTrigger value="comparison">Traditional vs Agentic</TabsTrigger>
          <TabsTrigger value="visual">Visual RAG</TabsTrigger>
          <TabsTrigger value="flows">Data Flows</TabsTrigger>
          <TabsTrigger value="agents">Agent Roles</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
        </TabsList>

        {/* --- Chatbot Pipeline --- */}
        <TabsContent value="chatbot" className="space-y-4">
          <ChatbotPipelineSection />
        </TabsContent>

        {/* --- Memory Integration --- */}
        <TabsContent value="memory" className="space-y-4">
          <MemoryIntegrationSection />
        </TabsContent>

        {/* --- Visual RAG --- */}
        <TabsContent value="visual" className="space-y-4">
          <VisualRAGSection />
        </TabsContent>

        {/* --- Comparison Table --- */}
        <TabsContent value="comparison" className="space-y-4">
          <div className="rounded-xl border border-border overflow-hidden">
            <div className="grid grid-cols-[180px_1fr_1fr] bg-muted/30 text-xs font-semibold uppercase tracking-wider">
              <div className="px-4 py-3 border-r border-border">Dimension</div>
              <div className="px-4 py-3 border-r border-border flex items-center gap-1.5">
                <XCircle className="w-3 h-3 text-destructive" /> Traditional RAG
              </div>
              <div className="px-4 py-3 flex items-center gap-1.5">
                <CheckCircle2 className="w-3 h-3 text-status-online" /> Agentic RAG
              </div>
            </div>
            {COMPARISON_ROWS.map((row, i) => (
              <div key={row.dimension} className={cn("grid grid-cols-[180px_1fr_1fr] text-sm", i % 2 === 0 ? "bg-card" : "bg-card/50")}>
                <div className="px-4 py-3 font-medium border-r border-border">{row.dimension}</div>
                <div className="px-4 py-3 text-muted-foreground border-r border-border">{row.traditional}</div>
                <div className="px-4 py-3">{row.agentic}</div>
              </div>
            ))}
          </div>
        </TabsContent>

        {/* --- Data Flows --- */}
        <TabsContent value="flows">
          <div className="grid md:grid-cols-2 gap-6">
            <Card className="border-destructive/20">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <XCircle className="w-4 h-4 text-destructive" /> Traditional RAG Flow
                </CardTitle>
              </CardHeader>
              <CardContent>
                <FlowDiagram steps={TRAD_STEPS} label="4-step linear pipeline" />
              </CardContent>
            </Card>
            <Card className="border-status-online/20">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-status-online" /> Agentic RAG Flow
                </CardTitle>
              </CardHeader>
              <CardContent>
                <FlowDiagram steps={AGENTIC_STEPS} label="9-step agentic pipeline" />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* --- Agent Roles --- */}
        <TabsContent value="agents">
          <div className="grid md:grid-cols-2 gap-4">
            {AGENTS.map((agent) => (
              <Card key={agent.name}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Badge variant="outline" className={agent.color}>{agent.name}</Badge>
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">{agent.role}</p>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1.5">
                    {agent.actions.map((a) => (
                      <li key={a} className="flex items-center gap-2 text-sm">
                        <ArrowRight className="w-3 h-3 text-primary shrink-0" /> {a}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Database className="w-4 h-4 text-accent" /> Qdrant Semantic Blackboard
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {["goals", "products", "solutions", "episodes"].map((col) => (
                  <div key={col} className="rounded-lg border border-accent/20 bg-accent/5 p-3 text-center">
                    <Database className="w-5 h-5 text-accent mx-auto mb-1.5" />
                    <div className="text-sm font-medium capitalize">{col}</div>
                    <div className="text-xs text-muted-foreground mt-0.5">collection</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* --- Metrics --- */}
        <TabsContent value="metrics">
          <div className="rounded-xl border border-border overflow-hidden">
            <div className="grid grid-cols-[1fr_1fr_1fr] bg-muted/30 text-xs font-semibold uppercase tracking-wider">
              <div className="px-4 py-3 border-r border-border">Metric</div>
              <div className="px-4 py-3 border-r border-border">Traditional</div>
              <div className="px-4 py-3">Agentic</div>
            </div>
            {METRICS.map((m, i) => (
              <div key={m.label} className={cn("grid grid-cols-[1fr_1fr_1fr] text-sm", i % 2 === 0 ? "bg-card" : "bg-card/50")}>
                <div className="px-4 py-3 font-medium border-r border-border flex items-center gap-2">
                  <BarChart3 className="w-3.5 h-3.5 text-muted-foreground" /> {m.label}
                </div>
                <div className="px-4 py-3 text-muted-foreground border-r border-border">{m.trad}</div>
                <div className="px-4 py-3 text-status-online font-medium">{m.agentic}</div>
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
