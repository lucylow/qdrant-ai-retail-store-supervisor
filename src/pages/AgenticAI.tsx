import { useState, useCallback } from "react";
import {
  ArrowRight, ArrowDown, Database, Bot, Brain, Zap,
  CheckCircle2, XCircle, Layers, Network, TrendingUp,
  Users, Cpu, BarChart3, Sparkles, Quote, Clock,
  HardDrive, BookOpen, Cog, Shield, Activity, Play, RotateCcw,
  Target, MessageSquare,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";

/* ------------------------------------------------------------------ */
/*  Data                                                               */
/* ------------------------------------------------------------------ */

const SINGLE_AGENT_LIMITS = [
  "One model handles everything: NLU, reasoning, execution",
  "No specialization — same LLM does shopping AND inventory",
  "Memory is just conversation history, not shared context",
  "Scaling means retraining or bigger models",
  "No error isolation — one failure crashes the whole pipeline",
];

const MULTI_AGENT_FEATURES = [
  { bold: "Shopper Agent:", text: "Human-facing reasoning + goal extraction" },
  { bold: "↓ Qdrant shared memory ↓", text: "" },
  { bold: "Inventory Agent:", text: "Domain expertise + execution" },
  { bold: "↓ Qdrant learning memory ↓", text: "" },
  { bold: "System:", text: "Emergent intelligence > individual agents" },
];

const PILLARS = [
  {
    icon: Brain,
    title: "Specialization",
    description: "Each agent focuses on what it does best: Shopper on language understanding, Inventory on logistics and product matching.",
    color: "text-primary",
  },
  {
    icon: Network,
    title: "Coordination",
    description: "Shared memory in Qdrant replaces brittle RPC chains. Agents work asynchronously via the semantic blackboard.",
    color: "text-accent",
  },
  {
    icon: TrendingUp,
    title: "Emergent Intelligence",
    description: "The system outperforms any single agent by combining complementary skills and learning from collective experience.",
    color: "text-chart-4",
  },
];

const AGENTIC_CHECKLIST = [
  { label: "Autonomous reasoning", desc: "Each agent reasons independently without central control" },
  { label: "Tool use", desc: "Agents call tools (Qdrant search, LLM, inventory API) dynamically" },
  { label: "Shared memory", desc: "Goals, solutions, episodes stored as vectors in Qdrant" },
  { label: "Episodic learning", desc: "Successful transactions become reusable knowledge" },
  { label: "Graceful degradation", desc: "If one agent fails, others continue with fallback logic" },
  { label: "Asynchronous coordination", desc: "No blocking RPC — agents poll and act on state changes" },
];

const FLOW_STEPS = [
  { label: "User: \"Blue t-shirt under $30, EU, 5 days\"", type: "user" as const },
  { label: "Shopper Agent extracts structured goal", type: "shopper" as const },
  { label: "→ Upserts goal to Qdrant (status: open)", type: "qdrant" as const },
  { label: "Inventory Agent polls open goals", type: "inventory" as const },
  { label: "→ Searches episodic memory for precedents", type: "qdrant" as const },
  { label: "→ Vector search products (stock>0, region=EU)", type: "qdrant" as const },
  { label: "→ Composes candidate bundles", type: "inventory" as const },
  { label: "→ Upserts solution to Qdrant", type: "qdrant" as const },
  { label: "Shopper fetches solution, presents to user", type: "shopper" as const },
  { label: "User selects → outcome written to episodes", type: "qdrant" as const },
  { label: "System learns: successful bundle ranked higher", type: "system" as const },
];

const TYPE_COLORS: Record<string, string> = {
  user: "border-muted-foreground/30 bg-muted/30",
  shopper: "border-primary/30 bg-primary/5",
  inventory: "border-accent/30 bg-accent/5",
  qdrant: "border-chart-2/30 bg-chart-2/5",
  system: "border-chart-2/30 bg-chart-2/5",
};

const TYPE_ICONS: Record<string, typeof Bot> = {
  user: Users,
  shopper: Bot,
  inventory: Cpu,
  qdrant: Database,
  system: Sparkles,
};

/* ------------------------------------------------------------------ */
/*  Animated Flow                                                      */
/* ------------------------------------------------------------------ */

function AgentFlow() {
  const [activeStep, setActiveStep] = useState(-1);

  const animate = () => {
    let i = 0;
    setActiveStep(0);
    const interval = setInterval(() => {
      i++;
      if (i >= FLOW_STEPS.length) {
        clearInterval(interval);
        setTimeout(() => setActiveStep(-1), 1500);
      } else {
        setActiveStep(i);
      }
    }, 600);
  };

  return (
    <div className="space-y-3">
      <Button size="sm" variant="outline" onClick={animate} className="gap-1.5 text-xs">
        <Zap className="w-3 h-3" /> Run Transaction
      </Button>
      <div className="flex flex-col gap-1">
        {FLOW_STEPS.map((step, idx) => {
          const Icon = TYPE_ICONS[step.type];
          const active = idx === activeStep;
          const done = activeStep > idx;
          return (
            <div key={idx}>
              <div
                className={`flex items-center gap-3 px-3 py-2 rounded-lg border transition-all duration-300 ${
                  active
                    ? "border-primary bg-primary/10 scale-[1.02] shadow-md"
                    : done
                    ? "border-chart-2/30 bg-chart-2/5 opacity-60"
                    : TYPE_COLORS[step.type]
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${active ? "text-primary" : "text-muted-foreground"}`} />
                <span className="text-sm flex-1">{step.label}</span>
                {done && <CheckCircle2 className="w-3.5 h-3.5 text-chart-2" />}
                {active && (
                  <span className="w-3.5 h-3.5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                )}
              </div>
              {idx < FLOW_STEPS.length - 1 && (
                <div className="flex justify-center py-0.5">
                  <ArrowDown className="w-3 h-3 text-muted-foreground/30" />
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
/*  Memory Architecture Section                                        */
/* ------------------------------------------------------------------ */

function MemoryArchitectureSection() {
  const memoryTypes = [
    {
      type: "Short-term (Working)",
      icon: Clock,
      color: "bg-chart-4/20 text-chart-4",
      storage: "In-memory / Redis",
      retention: "1 hour",
      pruning: "Sliding window",
      update: "Every turn",
      collection: "Session buffer",
      desc: "Current conversation (last 5–10 turns), immediate task context, pending solutions not yet accepted/rejected.",
      agentUse: {
        shopper: "Last 3 user messages + responses, current goal being discussed",
        inventory: "Current batch of open goals being processed",
      },
      example: `Session user123:
[
  {"role":"user","content":"2-person tent under 200CHF"},
  {"role":"assistant","content":"Found 3 options..."},
  {"role":"user","content":"Option 2 looks good"}
]
Max: 4k tokens (~10 turns) | Eviction: oldest first`,
    },
    {
      type: "Long-term (Persistent)",
      icon: HardDrive,
      color: "bg-primary/20 text-primary",
      storage: "Qdrant user_profiles",
      retention: "Permanent",
      pruning: "Manual",
      update: "Session end",
      collection: "user_profiles",
      desc: "User preferences, lifetime value, risk profile, brand affinities, complaint history across all sessions.",
      agentUse: {
        shopper: "Inject user profile into goal extraction prompt to bias toward preferences",
        inventory: "Weight bundles by user's brand/price preferences",
      },
      example: `{
  "userId": "user123",
  "preferences": {
    "brands": ["MSR", "Big Agnes"],
    "priceSensitivity": "medium",
    "deliveryTolerance": "2-3 days",
    "riskProfile": "conservative"
  },
  "lifetimeValue": 1250,
  "complaints": ["late_delivery: 2026-02-15"]
}`,
    },
    {
      type: "Episodic (Experience)",
      icon: BookOpen,
      color: "bg-accent/20 text-accent",
      storage: "Qdrant goal_solution_links",
      retention: "Permanent",
      pruning: "Success-weighted",
      update: "Every outcome",
      collection: "goal_solution_links",
      desc: "Specific goal → solution → outcome episodes. The core learning memory — 'what worked before?' for case-based reasoning.",
      agentUse: {
        shopper: "RAG: similar successful goals → bias structured extraction toward converting patterns",
        inventory: "RAG: 3 similar successful episodes → rank new bundles by proven success",
      },
      example: `{
  "episodeId": "ep-789",
  "goalId": "goal-123",
  "solutionId": "sol-456",
  "success": true,
  "revenue": 180,
  "feedbackTags": ["good_value","fast_delivery"],
  "summary": "2-person tent Zurich → Tent XYZ bundle worked",
  "vector": embed(goal_text + solution_summary)
}`,
    },
    {
      type: "Procedural (Routines)",
      icon: Cog,
      color: "bg-chart-2/20 text-chart-2",
      storage: "Qdrant procedural_memory",
      retention: "Permanent",
      pruning: "Success-only",
      update: "Post-episode",
      collection: "procedural_memory",
      desc: "Learned routing patterns, agent coordination heuristics. Which agent combinations + bundle patterns convert best for each category/region.",
      agentUse: {
        shopper: "Skip clarification for well-known patterns (92%+ success rate)",
        inventory: "Use optimal bundle templates instead of generating from scratch",
      },
      example: `{
  "patternId": "camping-zurich-fast",
  "trigger": {
    "category": "camping",
    "location": "Zurich",
    "deadline": "<3 days"
  },
  "successRate": 0.92,
  "recommendedAgents": ["inventory","logistics"],
  "optimalBundles": ["tent+mat","sleeping_bag_single"]
}`,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Architecture diagram */}
      <Card className="border-border bg-card">
        <CardContent className="pt-5">
          <div className="grid grid-cols-3 gap-3 text-center mb-4">
            <div className="rounded-lg border border-chart-4/30 bg-chart-4/5 p-3">
              <Clock className="h-5 w-5 text-chart-4 mx-auto mb-1" />
              <p className="text-xs font-medium text-foreground">Short-term</p>
              <p className="text-[10px] text-muted-foreground">Session context</p>
            </div>
            <div className="rounded-lg border border-primary/30 bg-primary/5 p-3">
              <HardDrive className="h-5 w-5 text-primary mx-auto mb-1" />
              <p className="text-xs font-medium text-foreground">Long-term</p>
              <p className="text-[10px] text-muted-foreground">User profiles</p>
            </div>
            <div className="rounded-lg border border-accent/30 bg-accent/5 p-3">
              <Database className="h-5 w-5 text-accent mx-auto mb-1" />
              <p className="text-xs font-medium text-foreground">Agentic RAG</p>
              <p className="text-[10px] text-muted-foreground">Qdrant Memory</p>
            </div>
          </div>
          <div className="flex justify-center gap-6 text-[10px] text-muted-foreground">
            <ArrowDown className="h-4 w-4" />
            <ArrowDown className="h-4 w-4" />
            <ArrowDown className="h-4 w-4" />
          </div>
          <div className="grid grid-cols-4 gap-2 mt-2 text-center">
            {memoryTypes.map((m) => (
              <div key={m.type} className={`rounded p-2 border ${m.color.replace("text-", "border-").replace("/20", "/30")} ${m.color.split(" ")[0]}`}>
                <m.icon className={`h-3.5 w-3.5 mx-auto mb-0.5 ${m.color.split(" ")[1]}`} />
                <p className="text-[10px] font-medium text-foreground">{m.type.split(" (")[0]}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Memory type cards */}
      <div className="space-y-4">
        {memoryTypes.map((m) => (
          <Card key={m.type} className="border-border bg-card">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm flex items-center gap-2">
                  <m.icon className={`h-4 w-4 ${m.color.split(" ")[1]}`} />
                  {m.type}
                </CardTitle>
                <Badge className={m.color + " text-[10px]"}>{m.collection}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-xs text-muted-foreground">{m.desc}</p>

              {/* Management policies row */}
              <div className="grid grid-cols-4 gap-2 text-[11px]">
                <div><span className="text-muted-foreground block">Storage</span><span className="font-mono">{m.storage.split(" ").pop()}</span></div>
                <div><span className="text-muted-foreground block">Retention</span><span className="font-mono">{m.retention}</span></div>
                <div><span className="text-muted-foreground block">Pruning</span><span className="font-mono">{m.pruning}</span></div>
                <div><span className="text-muted-foreground block">Update</span><span className="font-mono">{m.update}</span></div>
              </div>

              {/* Agent usage */}
              <div className="grid md:grid-cols-2 gap-2">
                <div className="bg-primary/5 rounded p-2 border border-primary/20">
                  <div className="flex items-center gap-1.5 mb-1">
                    <Bot className="h-3 w-3 text-primary" />
                    <span className="text-[10px] font-medium text-primary">Shopper Agent</span>
                  </div>
                  <p className="text-[11px] text-muted-foreground">{m.agentUse.shopper}</p>
                </div>
                <div className="bg-accent/5 rounded p-2 border border-accent/20">
                  <div className="flex items-center gap-1.5 mb-1">
                    <Cpu className="h-3 w-3 text-accent" />
                    <span className="text-[10px] font-medium text-accent">Inventory Agent</span>
                  </div>
                  <p className="text-[11px] text-muted-foreground">{m.agentUse.inventory}</p>
                </div>
              </div>

              {/* Example payload */}
              <details className="group">
                <summary className="text-[11px] text-muted-foreground cursor-pointer hover:text-foreground flex items-center gap-1">
                  <ArrowRight className="h-3 w-3 group-open:rotate-90 transition-transform" />
                  Example payload
                </summary>
                <pre className="text-[10px] font-mono bg-muted/40 rounded p-2 mt-1 text-muted-foreground whitespace-pre-wrap overflow-x-auto">{m.example}</pre>
              </details>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Memory Workflow Simulation                                         */
/* ------------------------------------------------------------------ */

function MemoryWorkflowSimulation() {
  const [running, setRunning] = useState(false);
  const [step, setStep] = useState(-1);
  const [memoryState, setMemoryState] = useState<Record<string, string[]>>({
    shortTerm: [],
    longTerm: [],
    episodic: [],
    procedural: [],
  });

  const reset = () => {
    setRunning(false);
    setStep(-1);
    setMemoryState({ shortTerm: [], longTerm: [], episodic: [], procedural: [] });
  };

  const runWorkflow = useCallback(async () => {
    reset();
    setRunning(true);
    const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

    // Step 0: User message → short-term
    setStep(0);
    setMemoryState((p) => ({ ...p, shortTerm: ["User: '2-person tent under 200CHF'"] }));
    await delay(800);

    // Step 1: Load user profile → long-term read
    setStep(1);
    setMemoryState((p) => ({ ...p, longTerm: ["Profile: brands=[MSR], priceSens=medium"] }));
    await delay(700);

    // Step 2: RAG episodic search
    setStep(2);
    setMemoryState((p) => ({ ...p, episodic: ["ep-456: camping tent → bundle A (92% success)"] }));
    await delay(800);

    // Step 3: Check procedural patterns
    setStep(3);
    setMemoryState((p) => ({ ...p, procedural: ["pattern: camping+zurich → inventory+logistics (92%)"] }));
    await delay(700);

    // Step 4: Shopper extracts goal (memory-enhanced)
    setStep(4);
    setMemoryState((p) => ({
      ...p,
      shortTerm: [...p.shortTerm, "Goal: {category:camping, budget:200, location:Zurich}"],
    }));
    await delay(800);

    // Step 5: Inventory solves with episodic context
    setStep(5);
    setMemoryState((p) => ({
      ...p,
      episodic: [...p.episodic, "Using episode template → TENT-ALP-2 + MAT-LITE bundle"],
    }));
    await delay(900);

    // Step 6: User accepts → new episode written
    setStep(6);
    setMemoryState((p) => ({
      ...p,
      episodic: [...p.episodic, "NEW ep-790: tent+mat → purchased (185 CHF, 5★)"],
      procedural: [...p.procedural, "Updated: camping+zurich success_rate → 0.93"],
      longTerm: [...p.longTerm, "Updated: lifetimeValue → 1435 CHF"],
    }));
    await delay(600);

    setRunning(false);
  }, []);

  const STEPS = [
    "User message → short-term buffer",
    "Load user profile (long-term)",
    "RAG: episodic memory search",
    "Check procedural patterns",
    "Shopper extracts goal (memory-enhanced)",
    "Inventory solves with episodic context",
    "Outcome → update all memory tiers",
  ];

  const memoryMeta: Record<string, { icon: typeof Clock; color: string; label: string }> = {
    shortTerm: { icon: Clock, color: "text-chart-4", label: "Short-term" },
    longTerm: { icon: HardDrive, color: "text-primary", label: "Long-term" },
    episodic: { icon: BookOpen, color: "text-accent", label: "Episodic" },
    procedural: { icon: Cog, color: "text-chart-2", label: "Procedural" },
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Button size="sm" onClick={running ? undefined : runWorkflow} disabled={running} className="gap-1">
          <Play className="h-3.5 w-3.5" /> Run Memory Workflow
        </Button>
        <Button size="sm" variant="outline" onClick={reset} className="gap-1">
          <RotateCcw className="h-3.5 w-3.5" /> Reset
        </Button>
      </div>

      {/* Progress */}
      <div className="flex gap-1.5 flex-wrap">
        {STEPS.map((s, i) => (
          <Badge key={i} className={`text-[10px] transition-colors ${i <= step ? "bg-primary/20 text-primary" : "bg-muted text-muted-foreground"}`}>
            {i <= step && <CheckCircle2 className="h-3 w-3 mr-1" />}
            Step {i + 1}
          </Badge>
        ))}
      </div>

      {/* Current step description */}
      {step >= 0 && (
        <Card className="border-primary/30 bg-primary/5">
          <CardContent className="py-3">
            <p className="text-sm text-foreground font-medium">{STEPS[step]}</p>
          </CardContent>
        </Card>
      )}

      {/* Memory state panels */}
      <div className="grid md:grid-cols-2 gap-3">
        {Object.entries(memoryMeta).map(([key, meta]) => {
          const Icon = meta.icon;
          const entries = memoryState[key] || [];
          return (
            <Card key={key} className="border-border bg-card">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs flex items-center gap-2">
                  <Icon className={`h-3.5 w-3.5 ${meta.color}`} />
                  {meta.label} Memory
                  <Badge variant="outline" className="text-[10px] ml-auto">{entries.length}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[100px]">
                  {entries.length > 0 ? (
                    <div className="space-y-1">
                      {entries.map((e, i) => (
                        <div key={i} className="text-[11px] text-muted-foreground font-mono bg-muted/40 rounded px-2 py-1">{e}</div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-[11px] text-muted-foreground italic">Empty</p>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Memory Impact Metrics                                              */
/* ------------------------------------------------------------------ */

function MemoryImpactSection() {
  const withoutMemory = [
    { goal: "Goal #1", confidence: 60 },
    { goal: "Goal #5", confidence: 60 },
    { goal: "Goal #10", confidence: 60 },
  ];
  const withMemory = [
    { goal: "Goal #1", confidence: 60 },
    { goal: "Goal #2", confidence: 87 },
    { goal: "Goal #5", confidence: 91 },
    { goal: "Goal #10", confidence: 94 },
  ];

  const policies = [
    { type: "Short-term", storage: "Redis / in-memory", retention: "1 hour", pruning: "Sliding window (oldest first)", update: "Every turn" },
    { type: "Long-term", storage: "Qdrant user_profiles", retention: "Permanent", pruning: "Manual review", update: "Session end" },
    { type: "Episodic", storage: "Qdrant goal_solution_links", retention: "Permanent", pruning: "Success-weighted decay", update: "Every outcome" },
    { type: "Procedural", storage: "Qdrant procedural_memory", retention: "Permanent", pruning: "Success-only retained", update: "Post-episode analysis" },
  ];

  const qdrantConfig = `# Add to existing Qdrant setup
client.create_collection(
    "user_profiles",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)
client.create_payload_index("user_profiles", "userId", PayloadSchemaType.KEYWORD)

client.create_collection(
    "procedural_memory",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)
client.create_payload_index("procedural_memory", "successRate", PayloadSchemaType.FLOAT)
client.create_payload_index("procedural_memory", "category", PayloadSchemaType.KEYWORD)`;

  const promptTemplates = `# Shopper Agent (memory-enhanced):
"User {userId} preferences: {user_profile}
Past 3 successful goals: {episodes}
Current request: '{request}'
Extract structured goal JSON, biased toward past successes."

# Inventory Agent (memory-enhanced):
"Goal: {structured_goal}
3× similar successful episodes (92% conversion): {episodes}
Feasible products: {products}
Learned pattern for {category}+{location}: {procedural}
Propose top 3 bundles ranked by proven success."`;

  return (
    <div className="space-y-6">
      {/* Confidence improvement visualization */}
      <div className="grid md:grid-cols-2 gap-4">
        <Card className="border-destructive/20 bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2 text-destructive">
              <XCircle className="h-4 w-4" /> Without Memory
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {withoutMemory.map((g) => (
              <div key={g.goal} className="flex items-center gap-3 text-xs">
                <span className="w-16 text-muted-foreground">{g.goal}</span>
                <Progress value={g.confidence} className="h-2 flex-1" />
                <span className="font-mono w-10 text-right">{g.confidence}%</span>
              </div>
            ))}
            <p className="text-[10px] text-muted-foreground italic mt-2">Confidence stays flat — no learning</p>
          </CardContent>
        </Card>

        <Card className="border-chart-2/30 bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2 text-chart-2">
              <CheckCircle2 className="h-4 w-4" /> With Tiered Memory
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {withMemory.map((g) => (
              <div key={g.goal} className="flex items-center gap-3 text-xs">
                <span className="w-16 text-muted-foreground">{g.goal}</span>
                <Progress value={g.confidence} className="h-2 flex-1" />
                <span className="font-mono w-10 text-right text-chart-2">{g.confidence}%</span>
              </div>
            ))}
            <p className="text-[10px] text-accent italic mt-2">+34% confidence by Goal #10 · +23% conversion lift</p>
          </CardContent>
        </Card>
      </div>

      {/* Management policies table */}
      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Memory Management Policies</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border text-muted-foreground">
                <th className="text-left py-2 pr-3">Type</th>
                <th className="text-left py-2 pr-3">Storage</th>
                <th className="text-left py-2 pr-3">Retention</th>
                <th className="text-left py-2 pr-3">Pruning</th>
                <th className="text-left py-2">Update Frequency</th>
              </tr>
            </thead>
            <tbody>
              {policies.map((p) => (
                <tr key={p.type} className="border-b border-border/50">
                  <td className="py-2 pr-3 font-medium text-foreground">{p.type}</td>
                  <td className="py-2 pr-3 font-mono text-[10px] text-muted-foreground">{p.storage}</td>
                  <td className="py-2 pr-3 text-muted-foreground">{p.retention}</td>
                  <td className="py-2 pr-3 text-muted-foreground">{p.pruning}</td>
                  <td className="py-2 text-muted-foreground">{p.update}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      {/* Qdrant config + prompt templates */}
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <h3 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
            <Database className="h-4 w-4 text-accent" /> Collection Config
          </h3>
          <Card className="border-border bg-card">
            <CardContent className="p-0">
              <ScrollArea className="h-[220px]">
                <pre className="text-[10px] font-mono p-3 text-muted-foreground whitespace-pre-wrap">{qdrantConfig}</pre>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
            <MessageSquare className="h-4 w-4 text-primary" /> Memory-Enhanced Prompts
          </h3>
          <Card className="border-border bg-card">
            <CardContent className="p-0">
              <ScrollArea className="h-[220px]">
                <pre className="text-[10px] font-mono p-3 text-muted-foreground whitespace-pre-wrap">{promptTemplates}</pre>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function AgenticAIPage() {
  return (
    <div className="p-4 md:p-6 space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="space-y-2 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium">
          <Sparkles className="w-3.5 h-3.5" />
          True Agentic AI
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          From Smart Chatbot to Collaborative Specialists
        </h1>
        <p className="text-muted-foreground max-w-3xl mx-auto text-sm">
          Multi-agent system with tiered memory architecture — short-term, long-term, episodic, and procedural memory mapped to Qdrant collections.
        </p>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="bg-muted/50 h-auto flex-wrap gap-1 justify-center">
          <TabsTrigger value="overview" className="text-xs gap-1"><Network className="h-3 w-3" /> Overview</TabsTrigger>
          <TabsTrigger value="memory" className="text-xs gap-1"><Brain className="h-3 w-3" /> Memory Architecture</TabsTrigger>
          <TabsTrigger value="simulation" className="text-xs gap-1"><Play className="h-3 w-3" /> Memory Workflow</TabsTrigger>
          <TabsTrigger value="impact" className="text-xs gap-1"><TrendingUp className="h-3 w-3" /> Impact & Config</TabsTrigger>
        </TabsList>

        {/* ---- Overview Tab (original content) ---- */}
        <TabsContent value="overview" className="space-y-8">
          {/* Comparison Grid */}
          <div className="grid md:grid-cols-2 gap-5">
            <Card className="border-destructive/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-sm">
                  <div className="w-8 h-8 rounded-full bg-destructive/15 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-destructive" />
                  </div>
                  <div>
                    <div>Single Agent</div>
                    <div className="text-xs font-normal text-muted-foreground">Smart Chatbot with Memory</div>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {SINGLE_AGENT_LIMITS.map((item) => (
                  <div key={item} className="flex items-start gap-2 text-xs text-muted-foreground">
                    <XCircle className="w-3.5 h-3.5 text-destructive shrink-0 mt-0.5" />
                    {item}
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="border-chart-2/30 bg-gradient-to-br from-chart-2/5 to-primary/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-sm">
                  <div className="w-8 h-8 rounded-full bg-chart-2/15 flex items-center justify-center">
                    <Network className="w-4 h-4 text-chart-2" />
                  </div>
                  <div>
                    <div>Multi-Agent System</div>
                    <div className="text-xs font-normal text-muted-foreground">Decoupled Agents = Agentic AI</div>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {MULTI_AGENT_FEATURES.map((item, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs">
                    <CheckCircle2 className="w-3.5 h-3.5 text-chart-2 shrink-0 mt-0.5" />
                    <span><span className="font-semibold">{item.bold}</span>{item.text && ` ${item.text}`}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Shared Memory Visualization */}
          <Card className="bg-card/80">
            <CardContent className="pt-5">
              <div className="flex flex-wrap justify-center items-center gap-3">
                <div className="px-4 py-2 rounded-full bg-primary/15 border border-primary/25 text-primary font-semibold text-xs flex items-center gap-2">
                  <Bot className="w-3.5 h-3.5" /> Shopper Agent
                </div>
                <ArrowRight className="w-4 h-4 text-muted-foreground" />
                <div className="px-4 py-2 rounded-full bg-accent/15 border border-accent/25 text-accent font-semibold text-xs flex items-center gap-2">
                  <Database className="w-3.5 h-3.5" /> Qdrant Memory
                </div>
                <ArrowRight className="w-4 h-4 text-muted-foreground rotate-180" />
                <div className="px-4 py-2 rounded-full bg-chart-2/15 border border-chart-2/25 text-chart-2 font-semibold text-xs flex items-center gap-2">
                  <Cpu className="w-3.5 h-3.5" /> Inventory Agent
                </div>
              </div>
              <div className="flex justify-center gap-2 mt-3">
                {["goals", "solutions", "episodes", "products", "user_profiles", "procedural"].map((col) => (
                  <Badge key={col} variant="outline" className="text-[10px] font-mono">{col}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Three Pillars */}
          <div className="grid md:grid-cols-3 gap-4">
            {PILLARS.map((pillar) => {
              const Icon = pillar.icon;
              return (
                <Card key={pillar.title} className="hover:border-primary/30 transition-colors">
                  <CardContent className="pt-4 space-y-2">
                    <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center">
                      <Icon className={`w-4 h-4 ${pillar.color}`} />
                    </div>
                    <h3 className="font-bold text-sm">{pillar.title}</h3>
                    <p className="text-xs text-muted-foreground">{pillar.description}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Checklist */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-chart-2" />
                Agentic AI Checklist
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-2">
                {AGENTIC_CHECKLIST.map((item) => (
                  <div key={item.label} className="flex items-start gap-2 px-3 py-2 rounded-lg border border-chart-2/20 bg-chart-2/5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-chart-2 shrink-0 mt-0.5" />
                    <div>
                      <div className="text-xs font-medium">{item.label}</div>
                      <div className="text-[10px] text-muted-foreground">{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Transaction Flow */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Zap className="w-4 h-4 text-primary" />
                End-to-End Agent Transaction
              </CardTitle>
            </CardHeader>
            <CardContent>
              <AgentFlow />
            </CardContent>
          </Card>

          {/* Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: "Agent Specialization", value: "2 agents", icon: Users },
              { label: "Memory Collections", value: "6", icon: Database },
              { label: "Episode Reuse", value: "67%", icon: BarChart3 },
              { label: "Conversion Lift", value: "+24%", icon: TrendingUp },
            ].map(({ label, value, icon: Icon }) => (
              <div key={label} className="rounded-xl border border-border bg-card p-3 text-center space-y-1">
                <Icon className="w-4 h-4 text-muted-foreground mx-auto" />
                <div className="text-xl font-bold text-foreground">{value}</div>
                <div className="text-[10px] text-muted-foreground">{label}</div>
              </div>
            ))}
          </div>
        </TabsContent>

        {/* ---- Memory Architecture Tab ---- */}
        <TabsContent value="memory">
          <MemoryArchitectureSection />
        </TabsContent>

        {/* ---- Memory Workflow Simulation Tab ---- */}
        <TabsContent value="simulation">
          <MemoryWorkflowSimulation />
        </TabsContent>

        {/* ---- Impact & Config Tab ---- */}
        <TabsContent value="impact">
          <MemoryImpactSection />
        </TabsContent>
      </Tabs>
    </div>
  );
}
