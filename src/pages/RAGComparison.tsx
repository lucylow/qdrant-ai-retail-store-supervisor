import { useState } from "react";
import {
  ArrowRight, ArrowDown, Database, Bot, Brain, Zap,
  CheckCircle2, XCircle, RotateCcw, Layers, BookOpen,
  ShieldCheck, BarChart3, GitBranch,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";

/* ------------------------------------------------------------------ */
/*  Data                                                               */
/* ------------------------------------------------------------------ */

const COMPARISON_ROWS = [
  {
    dimension: "Control Flow",
    traditional: "Linear single-turn: retrieve → generate",
    agentic: "Multi-turn, multi-agent orchestration with async reads/writes",
  },
  {
    dimension: "Responsibility",
    traditional: "One model handles interpretation, reasoning & output",
    agentic: "Decomposed: Shopper = intent, Inventory = feasibility, Pricing = margins",
  },
  {
    dimension: "Memory & Reuse",
    traditional: "Ephemeral retrievals (maybe cached)",
    agentic: "Explicit episodic memory — continuous learning from outcomes",
  },
  {
    dimension: "Failure Recovery",
    traditional: "Single model fallback — harder partial recovery",
    agentic: "Targeted per-agent fallbacks, confidence gating, human-in-the-loop",
  },
  {
    dimension: "Scalability",
    traditional: "Scale at model-serving layer",
    agentic: "Scale by agents + DB partitions, agent concurrency",
  },
  {
    dimension: "Observability",
    traditional: "Single prompt/response log",
    agentic: "Per-agent traces, confidence scores, retrieval audits",
  },
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
  {
    name: "Shopper Agent",
    role: "Intent extraction, dialog safety, user interaction",
    actions: ["Parse structured goal", "Embed & upsert to goals", "Present solutions"],
    color: "bg-primary/15 text-primary border-primary/25",
  },
  {
    name: "Inventory Agent",
    role: "Feasibility, stock/ETA, bundling, pricing",
    actions: ["Poll open goals", "Episodic retrieval", "Product search + filters", "Compose bundles"],
    color: "bg-accent/15 text-accent border-accent/25",
  },
  {
    name: "Pricing Agent",
    role: "Margin analysis, competitive positioning, bundle pricing",
    actions: ["Analyze margins", "Suggest bundle prices", "Competitive position"],
    color: "bg-status-warning/15 text-status-warning border-status-warning/25",
  },
  {
    name: "Merchandising Agent",
    role: "Assortment gaps, cross-sell, display priority",
    actions: ["Recommend cross-sells", "Identify gaps", "Rank display priority"],
    color: "bg-status-info/15 text-status-info border-status-info/25",
  },
];

/* ------------------------------------------------------------------ */
/*  Components                                                         */
/* ------------------------------------------------------------------ */

function FlowDiagram({
  steps,
  label,
}: {
  steps: typeof TRAD_STEPS;
  label: string;
}) {
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
              <div
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg border transition-all duration-300 ${
                  active
                    ? "border-primary bg-primary/10 scale-[1.02] shadow-md"
                    : done
                    ? "border-status-online/30 bg-status-online/5 opacity-70"
                    : "border-border bg-card"
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${active ? "text-primary" : step.color}`} />
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

export default function RAGComparisonPage() {
  return (
    <div className="p-6 space-y-8 animate-fade-in max-w-6xl mx-auto">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium">
          <Brain className="w-3.5 h-3.5" />
          Traditional RAG vs Agentic RAG
        </div>
        <h1 className="text-3xl font-bold tracking-tight">
          RAG Architecture Comparison
        </h1>
        <p className="text-muted-foreground max-w-2xl">
          How a Multi-Agent Store Manager transforms traditional retrieve-and-generate
          into a coordinated, learning system powered by Qdrant's semantic blackboard.
        </p>
      </div>

      {/* Tabbed content */}
      <Tabs defaultValue="comparison" className="space-y-6">
        <TabsList className="bg-muted/50">
          <TabsTrigger value="comparison">Comparison</TabsTrigger>
          <TabsTrigger value="flows">Data Flows</TabsTrigger>
          <TabsTrigger value="agents">Agent Roles</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
        </TabsList>

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
              <div
                key={row.dimension}
                className={`grid grid-cols-[180px_1fr_1fr] text-sm ${
                  i % 2 === 0 ? "bg-card" : "bg-card/50"
                }`}
              >
                <div className="px-4 py-3 font-medium border-r border-border">
                  {row.dimension}
                </div>
                <div className="px-4 py-3 text-muted-foreground border-r border-border">
                  {row.traditional}
                </div>
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
                  <XCircle className="w-4 h-4 text-destructive" />
                  Traditional RAG Flow
                </CardTitle>
              </CardHeader>
              <CardContent>
                <FlowDiagram steps={TRAD_STEPS} label="4-step linear pipeline" />
              </CardContent>
            </Card>

            <Card className="border-status-online/20">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-status-online" />
                  Agentic RAG Flow
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
                    <Badge variant="outline" className={agent.color}>
                      {agent.name}
                    </Badge>
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">{agent.role}</p>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1.5">
                    {agent.actions.map((a) => (
                      <li key={a} className="flex items-center gap-2 text-sm">
                        <ArrowRight className="w-3 h-3 text-primary shrink-0" />
                        {a}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Blackboard diagram */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Database className="w-4 h-4 text-accent" />
                Qdrant Semantic Blackboard
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {["goals", "products", "solutions", "episodes"].map((col) => (
                  <div
                    key={col}
                    className="rounded-lg border border-accent/20 bg-accent/5 p-3 text-center"
                  >
                    <Database className="w-5 h-5 text-accent mx-auto mb-1.5" />
                    <div className="text-sm font-medium capitalize">{col}</div>
                    <div className="text-xs text-muted-foreground mt-0.5">
                      collection
                    </div>
                  </div>
                ))}
              </div>
              <p className="text-xs text-muted-foreground mt-3 text-center">
                Agents read & write to shared Qdrant collections — the semantic blackboard pattern
              </p>
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
              <div
                key={m.label}
                className={`grid grid-cols-[1fr_1fr_1fr] text-sm ${
                  i % 2 === 0 ? "bg-card" : "bg-card/50"
                }`}
              >
                <div className="px-4 py-3 font-medium border-r border-border flex items-center gap-2">
                  <BarChart3 className="w-3.5 h-3.5 text-muted-foreground" />
                  {m.label}
                </div>
                <div className="px-4 py-3 text-muted-foreground border-r border-border">
                  {m.trad}
                </div>
                <div className="px-4 py-3 text-status-online font-medium">{m.agentic}</div>
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
