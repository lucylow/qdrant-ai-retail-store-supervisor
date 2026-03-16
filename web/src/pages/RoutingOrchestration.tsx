import { useState, useEffect, useCallback } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Network, GitBranch, ArrowRight, Play, RotateCcw, Zap, Brain, 
  CheckCircle2, XCircle, Clock, ArrowDownRight, Layers, 
  MessageSquare, Database, Activity, Target, Shield, Users
} from "lucide-react";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

type GoalStatus = "open" | "routed" | "dispatched" | "inventory_checked" | "fulfilled" | "failed";
type AgentType = "shopper" | "inventory" | "pricing" | "logistics";
type Outcome = "pending" | "success" | "fail" | "partial";

interface Goal {
  goalId: string;
  userId: string;
  rawUtterance: string;
  category: string;
  budgetMax?: number;
  location: string;
  status: GoalStatus;
  agentAssignments: AgentType[];
  createdAt: string;
}

interface Solution {
  solutionId: string;
  goalId: string;
  agentId: AgentType;
  products: { sku: string; qty: number }[];
  summary: string;
  confidence: number;
  outcome: Outcome;
}

interface Episode {
  episodeId: string;
  goalId: string;
  solutionId: string;
  success: boolean;
  revenue: number;
  feedbackTags: string[];
  similarityScore: number;
}

interface LogEntry {
  ts: string;
  level: "info" | "warn" | "success" | "error";
  msg: string;
}

/* ------------------------------------------------------------------ */
/*  Mock helpers                                                       */
/* ------------------------------------------------------------------ */

const AGENT_META: Record<AgentType, { label: string; color: string; icon: typeof Brain }> = {
  shopper:   { label: "Shopper",   color: "bg-primary/20 text-primary",       icon: Users },
  inventory: { label: "Inventory", color: "bg-accent/20 text-accent",         icon: Database },
  pricing:   { label: "Pricing",   color: "bg-chart-4/20 text-chart-4",       icon: Target },
  logistics: { label: "Logistics", color: "bg-chart-2/20 text-chart-2",       icon: Zap },
};

const STATUS_BADGE: Record<GoalStatus, string> = {
  open:              "bg-muted text-muted-foreground",
  routed:            "bg-primary/20 text-primary",
  dispatched:        "bg-accent/20 text-accent",
  inventory_checked: "bg-chart-2/20 text-chart-2",
  fulfilled:         "bg-chart-2/20 text-chart-2",
  failed:            "bg-destructive/20 text-destructive",
};

const uid = () => Math.random().toString(36).slice(2, 8);

/* ------------------------------------------------------------------ */
/*  1 · Overview tab                                                   */
/* ------------------------------------------------------------------ */

function OverviewTab() {
  const patterns = [
    {
      title: "Router (Stateless Classifier)",
      desc: "Classify each task + context → pick specialist agents (possibly parallel). Best for one-shot multi-tool queries.",
      icon: GitBranch,
      example: "If intent ∈ {shopping} → Shopper; stock question → Inventory",
    },
    {
      title: "Sub-agent / Supervisor",
      desc: "A conductor agent reasons step-by-step and calls other agents as tools, merging outputs into a single conversational surface.",
      icon: Brain,
      example: "Supervisor decomposes 'compare tents under 200' → Inventory + Pricing + Shopper merge",
    },
    {
      title: "Handoff (State-Driven)",
      desc: "State machine passes control from one agent to another as the workflow state changes — intake → triage → expert.",
      icon: ArrowDownRight,
      example: "Goal status open → routed → dispatched → inventory_checked → fulfilled",
    },
  ];

  const orchestratorSteps = [
    { step: "Intent + Capability Routing", detail: "Inputs: user request, workflow state, metadata. Outputs: collaboration pattern, agent set." },
    { step: "Context Assembly", detail: "Pull episodes, goals, docs from Qdrant. Trim per-agent context (each gets only what it needs)." },
    { step: "Dispatch + Execution", detail: "Call agents with local context + tools. Support parallel runs, collect partial results." },
    { step: "Merge + Next-Step Decision", detail: "Merge outputs (ensemble pattern). Decide: done, branch, escalate, or call another agent." },
    { step: "Logging + Learning", detail: "Log route chosen, agents run, quality signals. Adapt routing policies over time." },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-foreground mb-1">Core Routing Patterns</h2>
        <p className="text-sm text-muted-foreground mb-4">Three composable strategies combined by the orchestrator.</p>
        <div className="grid md:grid-cols-3 gap-4">
          {patterns.map((p) => (
            <Card key={p.title} className="border-border bg-card">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <p.icon className="h-5 w-5 text-primary" />
                  <CardTitle className="text-sm">{p.title}</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-xs text-muted-foreground">{p.desc}</p>
                <code className="block text-[10px] bg-muted/60 rounded p-2 text-accent font-mono">{p.example}</code>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-foreground mb-3">Orchestrator Loop</h2>
        <div className="relative space-y-0">
          {orchestratorSteps.map((s, i) => (
            <div key={i} className="flex gap-4 items-start">
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary">{i + 1}</div>
                {i < orchestratorSteps.length - 1 && <div className="w-px flex-1 bg-border min-h-[24px]" />}
              </div>
              <div className="pb-4">
                <p className="text-sm font-medium text-foreground">{s.step}</p>
                <p className="text-xs text-muted-foreground">{s.detail}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  2 · State Machine tab                                              */
/* ------------------------------------------------------------------ */

function StateMachineTab() {
  const transitions = [
    { from: "open", to: "routed", trigger: "Router classifies goal type & selects agents", agent: "orchestrator" },
    { from: "routed", to: "dispatched", trigger: "Dispatcher sends context to assigned agents", agent: "orchestrator" },
    { from: "dispatched", to: "inventory_checked", trigger: "Inventory agent writes solutions to blackboard", agent: "inventory" },
    { from: "inventory_checked", to: "fulfilled", trigger: "Shopper presents options, user accepts", agent: "shopper" },
    { from: "inventory_checked", to: "failed", trigger: "No feasible solutions or user rejects all", agent: "shopper" },
    { from: "dispatched", to: "failed", trigger: "All agents fail or timeout exceeded", agent: "orchestrator" },
  ];

  const blackboardRules = [
    "Agents coordinate only via Qdrant collections — no direct agent-to-agent calls",
    "Goal status field is the single source of truth for workflow progression",
    "Inventory polls goals with status='open'; Shopper polls solutions with goalId filter",
    "State transitions are atomic upserts — prevents race conditions",
    "Each transition logs timestamp + agent_id for full audit trail",
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-foreground mb-3">Goal State Machine</h2>
        <div className="flex flex-wrap items-center gap-2 mb-4">
          {["open", "routed", "dispatched", "inventory_checked", "fulfilled"].map((s, i, arr) => (
            <div key={s} className="flex items-center gap-2">
              <Badge className={STATUS_BADGE[s as GoalStatus] + " text-xs"}>{s}</Badge>
              {i < arr.length - 1 && <ArrowRight className="h-3 w-3 text-muted-foreground" />}
            </div>
          ))}
        </div>
      </div>

      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Transition Table</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border text-muted-foreground">
                  <th className="text-left py-2 pr-3">From</th>
                  <th className="text-left py-2 pr-3">To</th>
                  <th className="text-left py-2 pr-3">Trigger</th>
                  <th className="text-left py-2">Agent</th>
                </tr>
              </thead>
              <tbody>
                {transitions.map((t, i) => (
                  <tr key={i} className="border-b border-border/50">
                    <td className="py-2 pr-3"><Badge variant="outline" className="text-[10px]">{t.from}</Badge></td>
                    <td className="py-2 pr-3"><Badge variant="outline" className="text-[10px]">{t.to}</Badge></td>
                    <td className="py-2 pr-3 text-muted-foreground">{t.trigger}</td>
                    <td className="py-2"><Badge className="text-[10px] bg-primary/10 text-primary">{t.agent}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Blackboard Coordination Rules</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {blackboardRules.map((r, i) => (
              <li key={i} className="flex gap-2 text-xs text-muted-foreground">
                <Shield className="h-3.5 w-3.5 text-accent mt-0.5 shrink-0" />
                {r}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  3 · Dispatcher Code tab                                            */
/* ------------------------------------------------------------------ */

function DispatcherCodeTab() {
  const tsCode = `interface Goal {
  goalId: string;
  userId: string;
  rawUtterance: string;
  structured: {
    category: string;
    budgetMax?: number;
    location: string;
    deadline?: string;
  };
  status: 'open' | 'inventory_checked' | 'fulfilled' | 'failed';
  agentAssignments: string[];
}

class TaskDispatcher {
  private memory: QdrantClient;  // goals collection
  private agents: Record<AgentType, AgentFn>;

  async dispatch(userRequest: string, userId: string) {
    // 1. Shopper agent extracts structured goal
    const goal = await this.createStructuredGoal(userRequest, userId);

    // 2. Write to blackboard (Qdrant goals collection)
    await this.memory.upsert("goals", [goalToPoint(goal)]);

    // 3. Route: classify which agents should run
    const assignments = this.routeGoal(goal);
    goal.agentAssignments = assignments;

    // 4. Execute agents in parallel where possible
    const results = await Promise.allSettled(
      assignments.map(id => this.executeAgent(id, goal))
    );

    // 5. Collect solutions, update goal status
    goal.status = results.some(r => r.status === 'fulfilled')
      ? 'inventory_checked' : 'failed';
    return goal;
  }

  private routeGoal(goal: Goal): AgentType[] {
    const agents: AgentType[] = ['shopper'];
    if (goal.structured.category)  agents.push('inventory');
    if (goal.structured.budgetMax) agents.push('pricing');
    if (goal.structured.deadline)  agents.push('logistics');
    return agents;
  }

  private async executeAgent(agentId: AgentType, goal: Goal) {
    // RAG context: similar episodes + goal payload
    const episodes = await this.memory.search(
      "goal_solution_links",
      embed(goal.rawUtterance),
      { filter: { success: true }, limit: 3 }
    );
    return this.agents[agentId]({ goal, episodes });
  }
}`;

  const feedbackCode = `class FeedbackLoop {
  async processFeedback(
    goalId: string,
    solutionId: string,
    outcome: 'success' | 'fail' | 'partial',
    feedbackTags: string[] = [],
    revenue: number = 0
  ) {
    // 1. Update solution outcome in Qdrant
    await qdrant.setPayload("solutions", solutionId, { outcome });

    // 2. Create episodic memory record
    const episode = {
      episodeId: uuid(),
      goalId, solutionId,
      success: outcome === 'success',
      revenue, feedbackTags,
      similarityScore: computeEpisodeValue(outcome, revenue)
    };

    // 3. Embed & upsert to goal_solution_links
    const vec = embed(episodeSummary(episode));
    await qdrant.upsert("goal_solution_links", [
      { id: episode.episodeId, vector: vec, payload: episode }
    ]);

    // 4. Update goal status
    await qdrant.setPayload("goals", goalId, {
      status: outcome === 'success' ? 'fulfilled' : 'failed'
    });

    // 5. Emit learning signal for agent policy updates
    this.updateAgentPolicies(episode);
  }
}`;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-foreground mb-1">Task Dispatcher</h2>
        <p className="text-xs text-muted-foreground mb-3">Dynamic routing + parallel agent dispatch with Qdrant-backed blackboard.</p>
        <Card className="border-border bg-card">
          <CardContent className="p-0">
            <ScrollArea className="h-[420px]">
              <pre className="text-[11px] font-mono p-4 text-muted-foreground leading-relaxed whitespace-pre-wrap">{tsCode}</pre>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-foreground mb-1">Feedback Loop</h2>
        <p className="text-xs text-muted-foreground mb-3">Every outcome creates an episodic record for future RAG retrieval.</p>
        <Card className="border-border bg-card">
          <CardContent className="p-0">
            <ScrollArea className="h-[340px]">
              <pre className="text-[11px] font-mono p-4 text-muted-foreground leading-relaxed whitespace-pre-wrap">{feedbackCode}</pre>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  4 · Live Simulation tab                                            */
/* ------------------------------------------------------------------ */

function SimulationTab() {
  const [running, setRunning] = useState(false);
  const [step, setStep] = useState(-1);
  const [goal, setGoal] = useState<Goal | null>(null);
  const [solutions, setSolutions] = useState<Solution[]>([]);
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);

  const addLog = useCallback((level: LogEntry["level"], msg: string) => {
    setLogs((p) => [...p, { ts: new Date().toISOString().slice(11, 19), level, msg }]);
  }, []);

  const reset = () => {
    setRunning(false);
    setStep(-1);
    setGoal(null);
    setSolutions([]);
    setEpisodes([]);
    setLogs([]);
  };

  const runSimulation = useCallback(async () => {
    reset();
    setRunning(true);

    const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));
    const gid = `goal-${uid()}`;

    // Step 0 — User request
    setStep(0);
    addLog("info", "User: '2-person tent under 200 CHF, Zurich by Friday'");
    await delay(800);

    // Step 1 — Shopper parses goal
    setStep(1);
    const g: Goal = {
      goalId: gid, userId: "user_123", rawUtterance: "2-person tent under 200 CHF, Zurich by Friday",
      category: "camping", budgetMax: 200, location: "Zurich",
      status: "open", agentAssignments: [], createdAt: new Date().toISOString(),
    };
    setGoal(g);
    addLog("success", `Shopper parsed goal → ${gid} | status=open`);
    await delay(700);

    // Step 2 — Router classifies
    setStep(2);
    const agents: AgentType[] = ["shopper", "inventory", "pricing"];
    g.agentAssignments = agents;
    g.status = "routed";
    setGoal({ ...g });
    addLog("info", `Router → agents: ${agents.join(", ")}`);
    await delay(600);

    // Step 3 — Dispatch
    setStep(3);
    g.status = "dispatched";
    setGoal({ ...g });
    addLog("info", "Dispatcher: parallel execution started (inventory ∥ pricing)");
    await delay(1000);

    // Step 4 — Solutions arrive
    setStep(4);
    const sols: Solution[] = [
      { solutionId: `sol-${uid()}`, goalId: gid, agentId: "inventory", products: [{ sku: "TENT-ALP-2", qty: 1 }, { sku: "MAT-LITE", qty: 2 }], summary: "Alpine 2P tent + 2 mats = 185 CHF, ETA Fri", confidence: 0.89, outcome: "pending" },
      { solutionId: `sol-${uid()}`, goalId: gid, agentId: "pricing", products: [{ sku: "TENT-ALP-2", qty: 1 }], summary: "Tent only @ 10% off = 108 CHF", confidence: 0.74, outcome: "pending" },
    ];
    setSolutions(sols);
    g.status = "inventory_checked";
    setGoal({ ...g });
    addLog("success", `Inventory: 2 solutions written (conf 0.89, 0.74)`);
    await delay(800);

    // Step 5 — Shopper presents & user accepts
    setStep(5);
    sols[0].outcome = "success";
    sols[1].outcome = "partial";
    setSolutions([...sols]);
    g.status = "fulfilled";
    setGoal({ ...g });
    addLog("success", "Shopper: user accepted solution 1");
    await delay(600);

    // Step 6 — Feedback loop
    setStep(6);
    const ep: Episode = {
      episodeId: `ep-${uid()}`, goalId: gid, solutionId: sols[0].solutionId,
      success: true, revenue: 185, feedbackTags: ["good_value", "fast_delivery"], similarityScore: 0.91,
    };
    setEpisodes([ep]);
    addLog("success", `Feedback loop: episode stored (value=${ep.similarityScore.toFixed(2)})`);
    addLog("info", "Agent policies updated — routing weights adjusted");
    await delay(400);

    setRunning(false);
  }, [addLog]);

  const STEP_LABELS = [
    "User Request",
    "Shopper Parse",
    "Router Classify",
    "Dispatch Agents",
    "Solutions Arrive",
    "User Accepts",
    "Feedback Loop",
  ];

  const logColor: Record<LogEntry["level"], string> = {
    info: "text-muted-foreground",
    warn: "text-chart-4",
    success: "text-chart-2",
    error: "text-destructive",
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Button size="sm" onClick={running ? undefined : runSimulation} disabled={running} className="gap-1">
          <Play className="h-3.5 w-3.5" /> Run Simulation
        </Button>
        <Button size="sm" variant="outline" onClick={reset} className="gap-1">
          <RotateCcw className="h-3.5 w-3.5" /> Reset
        </Button>
      </div>

      {/* Progress steps */}
      <div className="flex gap-1.5 flex-wrap">
        {STEP_LABELS.map((l, i) => (
          <Badge key={i} className={`text-[10px] transition-colors ${i <= step ? "bg-primary/20 text-primary" : "bg-muted text-muted-foreground"}`}>
            {i <= step && <CheckCircle2 className="h-3 w-3 mr-1" />}
            {l}
          </Badge>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {/* Goal state */}
        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Target className="h-4 w-4 text-primary" /> Goal State
            </CardTitle>
          </CardHeader>
          <CardContent>
            {goal ? (
              <div className="space-y-2 text-xs">
                <div className="flex justify-between"><span className="text-muted-foreground">ID</span><code className="text-accent">{goal.goalId}</code></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Status</span><Badge className={STATUS_BADGE[goal.status] + " text-[10px]"}>{goal.status}</Badge></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Category</span><span>{goal.category}</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Budget</span><span>{goal.budgetMax} CHF</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Location</span><span>{goal.location}</span></div>
                <div className="flex justify-between items-start"><span className="text-muted-foreground">Agents</span>
                  <div className="flex gap-1 flex-wrap justify-end">
                    {goal.agentAssignments.map((a) => (
                      <Badge key={a} className={AGENT_META[a].color + " text-[10px]"}>{AGENT_META[a].label}</Badge>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-muted-foreground italic">Waiting for simulation…</p>
            )}
          </CardContent>
        </Card>

        {/* Solutions */}
        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Layers className="h-4 w-4 text-accent" /> Solutions
            </CardTitle>
          </CardHeader>
          <CardContent>
            {solutions.length > 0 ? (
              <div className="space-y-3">
                {solutions.map((s) => (
                  <div key={s.solutionId} className="bg-muted/40 rounded p-2 space-y-1 text-xs">
                    <div className="flex justify-between">
                      <Badge className={AGENT_META[s.agentId].color + " text-[10px]"}>{AGENT_META[s.agentId].label}</Badge>
                      <Badge variant="outline" className="text-[10px]">{s.outcome}</Badge>
                    </div>
                    <p className="text-muted-foreground">{s.summary}</p>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">Confidence</span>
                      <Progress value={s.confidence * 100} className="h-1.5 flex-1" />
                      <span className="font-mono text-[10px]">{(s.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground italic">No solutions yet…</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Episodic + Logs */}
      <div className="grid md:grid-cols-2 gap-4">
        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Brain className="h-4 w-4 text-chart-4" /> Episodic Memory
            </CardTitle>
          </CardHeader>
          <CardContent>
            {episodes.length > 0 ? episodes.map((e) => (
              <div key={e.episodeId} className="bg-muted/40 rounded p-2 space-y-1 text-xs">
                <div className="flex justify-between">
                  <code className="text-accent text-[10px]">{e.episodeId}</code>
                  {e.success ? <CheckCircle2 className="h-3.5 w-3.5 text-chart-2" /> : <XCircle className="h-3.5 w-3.5 text-destructive" />}
                </div>
                <div className="flex gap-1 flex-wrap">
                  {e.feedbackTags.map((t) => <Badge key={t} variant="outline" className="text-[10px]">{t}</Badge>)}
                </div>
                <p className="text-muted-foreground">Revenue: {e.revenue} CHF · Similarity: {e.similarityScore.toFixed(2)}</p>
              </div>
            )) : <p className="text-xs text-muted-foreground italic">No episodes yet…</p>}
          </CardContent>
        </Card>

        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Activity className="h-4 w-4 text-primary" /> Execution Log
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[180px]">
              <div className="space-y-1">
                {logs.map((l, i) => (
                  <div key={i} className="flex gap-2 text-[11px] font-mono">
                    <span className="text-muted-foreground shrink-0">{l.ts}</span>
                    <span className={logColor[l.level]}>{l.msg}</span>
                  </div>
                ))}
                {logs.length === 0 && <p className="text-xs text-muted-foreground italic">Press "Run Simulation" to start</p>}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  5 · Routing Logic tab                                              */
/* ------------------------------------------------------------------ */

function RoutingLogicTab() {
  const rules = [
    { condition: "intent ∈ {shopping, browse, compare}", agents: ["shopper"], pattern: "Single agent" },
    { condition: "goal has category field", agents: ["shopper", "inventory"], pattern: "Parallel" },
    { condition: "goal has budgetMax", agents: ["shopper", "inventory", "pricing"], pattern: "Parallel" },
    { condition: "goal has deadline or location", agents: ["shopper", "inventory", "logistics"], pattern: "Parallel" },
    { condition: "all agents fail or timeout > 30s", agents: ["orchestrator"], pattern: "Escalation" },
    { condition: "solution.confidence < 0.5", agents: ["shopper"], pattern: "Human-in-loop" },
  ];

  const tradeoffs = [
    { aspect: "Centralized supervisor", pro: "Easy to reason about, full audit trail", con: "Can bottleneck under high load" },
    { aspect: "Blackboard + polling", pro: "Scales easily, data-driven, observable", con: "Polling latency, eventual consistency" },
    { aspect: "Static rules", pro: "Deterministic, debuggable", con: "Brittle, can't adapt" },
    { aspect: "Learned router", pro: "Adapts to minimize latency/cost", con: "Needs training data, less interpretable" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-foreground mb-3">Routing Rules</h2>
        <Card className="border-border bg-card">
          <CardContent className="pt-4">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border text-muted-foreground">
                  <th className="text-left py-2 pr-3">Condition</th>
                  <th className="text-left py-2 pr-3">Agents Activated</th>
                  <th className="text-left py-2">Pattern</th>
                </tr>
              </thead>
              <tbody>
                {rules.map((r, i) => (
                  <tr key={i} className="border-b border-border/50">
                    <td className="py-2 pr-3 text-muted-foreground font-mono text-[11px]">{r.condition}</td>
                    <td className="py-2 pr-3">
                      <div className="flex gap-1 flex-wrap">
                        {r.agents.map((a) => (
                          <Badge key={a} className={`text-[10px] ${AGENT_META[a as AgentType]?.color || "bg-muted text-muted-foreground"}`}>
                            {AGENT_META[a as AgentType]?.label || a}
                          </Badge>
                        ))}
                      </div>
                    </td>
                    <td className="py-2"><Badge variant="outline" className="text-[10px]">{r.pattern}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-foreground mb-3">Design Trade-offs</h2>
        <div className="grid md:grid-cols-2 gap-3">
          {tradeoffs.map((t) => (
            <Card key={t.aspect} className="border-border bg-card">
              <CardContent className="pt-4 space-y-2">
                <p className="text-sm font-medium text-foreground">{t.aspect}</p>
                <div className="flex gap-1 items-start text-xs">
                  <CheckCircle2 className="h-3.5 w-3.5 text-chart-2 mt-0.5 shrink-0" />
                  <span className="text-muted-foreground">{t.pro}</span>
                </div>
                <div className="flex gap-1 items-start text-xs">
                  <XCircle className="h-3.5 w-3.5 text-destructive mt-0.5 shrink-0" />
                  <span className="text-muted-foreground">{t.con}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  6 · Metrics tab                                                    */
/* ------------------------------------------------------------------ */

function MetricsTab() {
  const metrics = [
    { metric: "Routing Accuracy", value: "94.2%", desc: "Correct agent set selected by router", trend: "+2.1%" },
    { metric: "Time to First Solution", value: "1.8s", desc: "Goal created → first solution upserted", trend: "-0.3s" },
    { metric: "Parallel Efficiency", value: "87%", desc: "% of dispatches using parallel execution", trend: "+5%" },
    { metric: "Feedback Loop Latency", value: "340ms", desc: "Outcome → episodic memory write", trend: "-60ms" },
    { metric: "Episode Reuse Rate", value: "62%", desc: "Solutions informed by episodic memory", trend: "+8%" },
    { metric: "Goal Resolution Rate", value: "91.3%", desc: "Goals reaching fulfilled status", trend: "+1.7%" },
    { metric: "Escalation Rate", value: "4.1%", desc: "Goals requiring human-in-the-loop", trend: "-0.9%" },
    { metric: "Agent Coordination Lag", value: "120ms", desc: "Mean polling interval between agents", trend: "-30ms" },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-foreground">Orchestration Metrics</h2>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {metrics.map((m) => (
          <Card key={m.metric} className="border-border bg-card">
            <CardContent className="pt-4 space-y-1">
              <p className="text-[11px] text-muted-foreground">{m.metric}</p>
              <p className="text-xl font-bold text-foreground">{m.value}</p>
              <div className="flex justify-between items-center">
                <p className="text-[10px] text-muted-foreground">{m.desc}</p>
                <Badge className="text-[10px] bg-chart-2/20 text-chart-2">{m.trend}</Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Root page                                                          */
/* ------------------------------------------------------------------ */

export default function RoutingOrchestration() {
  return (
    <div className="p-4 md:p-6 space-y-4">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Network className="h-5 w-5 text-primary" />
          <h1 className="text-xl font-bold text-foreground">Routing & Orchestration</h1>
        </div>
        <p className="text-sm text-muted-foreground">
          Task dispatcher, state machine, and feedback loop for multi-agent coordination via Qdrant blackboard.
        </p>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="bg-muted/50 h-auto flex-wrap gap-1">
          <TabsTrigger value="overview" className="text-xs gap-1"><GitBranch className="h-3 w-3" /> Patterns</TabsTrigger>
          <TabsTrigger value="state" className="text-xs gap-1"><ArrowRight className="h-3 w-3" /> State Machine</TabsTrigger>
          <TabsTrigger value="code" className="text-xs gap-1"><Layers className="h-3 w-3" /> Dispatcher Code</TabsTrigger>
          <TabsTrigger value="simulation" className="text-xs gap-1"><Play className="h-3 w-3" /> Live Simulation</TabsTrigger>
          <TabsTrigger value="routing" className="text-xs gap-1"><Network className="h-3 w-3" /> Routing Logic</TabsTrigger>
          <TabsTrigger value="metrics" className="text-xs gap-1"><Activity className="h-3 w-3" /> Metrics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview"><OverviewTab /></TabsContent>
        <TabsContent value="state"><StateMachineTab /></TabsContent>
        <TabsContent value="code"><DispatcherCodeTab /></TabsContent>
        <TabsContent value="simulation"><SimulationTab /></TabsContent>
        <TabsContent value="routing"><RoutingLogicTab /></TabsContent>
        <TabsContent value="metrics"><MetricsTab /></TabsContent>
      </Tabs>
    </div>
  );
}
