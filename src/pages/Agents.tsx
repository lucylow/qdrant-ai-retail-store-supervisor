import { AgentAvatar } from "@/components/AgentAvatar";
import { Activity, Clock, Zap, GitMerge, Lock, CheckCircle } from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

type LogEntry = { id: number; time: string; agent: string; message: string; type: "info" | "success" | "warning" };

const SAMPLE_LOGS: LogEntry[] = [
  { id: 1, time: "14:32:01", agent: "Supervisor", message: "New goal received: '2-person tent Zurich'", type: "info" },
  { id: 2, time: "14:32:01", agent: "Shopper", message: "Parsing goal intent → category: Tents, budget: 200CHF", type: "info" },
  { id: 3, time: "14:32:02", agent: "Inventory", message: "Searching Qdrant episodes collection (similar: 0.92)", type: "info" },
  { id: 4, time: "14:32:02", agent: "Inventory", message: "CACHE HIT! Episode ep_7234 (92% similar, 35ms)", type: "success" },
  { id: 5, time: "14:32:03", agent: "Inventory", message: "Bundle prepared: MSR Hubba Hubba NX2 + Accessories", type: "success" },
  { id: 6, time: "14:32:03", agent: "Supervisor", message: "Goal fulfilled. Writing episode to Qdrant.", type: "success" },
];

const AGENTS = [
  {
    type: "supervisor" as const, label: "Supervisor", role: "Routing & orchestration",
    online: true, latency: "12ms", goals: 347,
    semaphoreSlots: 4, usedSlots: 2,
    pipeline: ["Receive goal", "Route to agent", "Rank solutions", "SSE stream"],
    collections: ["zurich_goals", "zurich_solutions"],
  },
  {
    type: "shopper" as const, label: "Shopper", role: "Goal parsing & intent",
    online: true, latency: "18ms", goals: 289,
    semaphoreSlots: 4, usedSlots: 1,
    pipeline: ["Normalize Swiss-DE", "Extract constraints", "Upsert goal", "Embed text"],
    collections: ["zurich_goals", "zurich_query_cache"],
  },
  {
    type: "inventory" as const, label: "Inventory", role: "Bundle generation & RAG",
    online: true, latency: "42ms", goals: 289,
    semaphoreSlots: 4, usedSlots: 3,
    pipeline: ["Search episodes", "Multi-coll retrieval", "RRF fusion", "Bundle rank"],
    collections: ["zurich_products", "zurich_episodes"],
  },
  {
    type: "pricing" as const, label: "Pricing", role: "Price optimization",
    online: false, latency: "—", goals: 0,
    semaphoreSlots: 4, usedSlots: 0,
    pipeline: ["Load pricing model", "Fetch market data", "Score bundles", "Apply discount"],
    collections: ["zurich_products"],
  },
  {
    type: "marketing" as const, label: "Marketing", role: "Campaign suggestions",
    online: false, latency: "—", goals: 0,
    semaphoreSlots: 4, usedSlots: 0,
    pipeline: ["Segment users", "Generate copy", "A/B test", "Track lift"],
    collections: ["zurich_goals", "zurich_episodes"],
  },
];

// Agentic pipeline flow steps
const PIPELINE_STEPS = [
  { label: "ShopperAgent", icon: "🛒", desc: "Parse utterance → upsert goal (atomic CAS)", latency: "18ms", color: "border-primary/40 bg-primary/5 text-primary" },
  { label: "InventoryAgent", icon: "📦", desc: "Search episodes → retrieve products → RRF bundle", latency: "42ms", color: "border-accent/40 bg-accent/5 text-accent" },
  { label: "SupervisorAgent", icon: "🎯", desc: "Rank bundles → assemble provenance → SSE stream", latency: "12ms", color: "border-status-online/40 bg-status-online/5 text-status-online" },
];

export default function AgentsPage() {
  const [logs, setLogs] = useState<LogEntry[]>(SAMPLE_LOGS);
  const [live, setLive] = useState(false);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState<number | null>(null);
  const [pipelineRunning, setPipelineRunning] = useState(false);

  useEffect(() => {
    if (!live) return;
    const interval = setInterval(() => {
      const msgs = [
        { agent: "Shopper", message: `Polling for new goals… (${Math.floor(Math.random() * 5)} pending)`, type: "info" as const },
        { agent: "Inventory", message: `Qdrant search latency: ${Math.floor(25 + Math.random() * 40)}ms`, type: "info" as const },
        { agent: "Supervisor", message: `Cache hit rate: ${(80 + Math.random() * 10).toFixed(1)}%`, type: "success" as const },
        { agent: "Inventory", message: `CACHE HIT ep_${Math.floor(Math.random() * 9999)} (${(88 + Math.random() * 5).toFixed(0)}% similar)`, type: "success" as const },
        { agent: "Shopper", message: `Swiss-DE normalized: "Zelt" → "tent", "Franken" → "CHF"`, type: "info" as const },
      ];
      const pick = msgs[Math.floor(Math.random() * msgs.length)];
      setLogs(prev => [{ ...pick, id: Date.now(), time: new Date().toLocaleTimeString() }, ...prev.slice(0, 49)]);
    }, 2000);
    return () => clearInterval(interval);
  }, [live]);

  const runPipeline = async () => {
    setPipelineRunning(true);
    setActiveStep(null);
    for (let i = 0; i < PIPELINE_STEPS.length; i++) {
      await new Promise((r) => setTimeout(r, 600));
      setActiveStep(i);
    }
    setPipelineRunning(false);
  };

  const LOG_COLORS = { info: "text-muted-foreground", success: "text-status-online", warning: "text-status-warning" };

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">Agent Monitor</h1>
        <p className="text-sm text-muted-foreground">Live agent status · Semaphore pools · Qdrant pipeline</p>
      </div>

      {/* Agent cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {AGENTS.map((agent) => {
          const open = expandedAgent === agent.type;
          return (
            <div
              key={agent.type}
              onClick={() => setExpandedAgent(open ? null : agent.type)}
              className={cn(
                "rounded-xl border bg-card p-4 space-y-3 transition-all cursor-pointer",
                agent.online ? "border-border hover:border-primary/30" : "border-border opacity-60",
                open ? "ring-1 ring-primary/30" : ""
              )}
            >
              <div className="flex items-center justify-between">
                <AgentAvatar type={agent.type} online={agent.online} size="md" />
                <span className={cn("text-xs px-2 py-0.5 rounded-full", agent.online ? "bg-status-online/15 text-status-online" : "bg-muted text-muted-foreground")}>
                  {agent.online ? "Running" : "Idle"}
                </span>
              </div>
              <div>
                <div className="font-semibold text-sm">{agent.label}</div>
                <div className="text-xs text-muted-foreground">{agent.role}</div>
              </div>
              <div className="flex gap-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{agent.latency}</span>
                <span className="flex items-center gap-1"><Zap className="w-3 h-3" />{agent.goals}</span>
              </div>

              {/* Semaphore slots */}
              <div className="space-y-1">
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Lock className="w-3 h-3" />
                  <span>Semaphore({agent.semaphoreSlots})</span>
                  <span className={cn("ml-auto font-mono", agent.usedSlots > 0 ? "text-primary" : "text-muted-foreground")}>
                    {agent.usedSlots}/{agent.semaphoreSlots}
                  </span>
                </div>
                <div className="flex gap-1">
                  {Array.from({ length: agent.semaphoreSlots }).map((_, i) => (
                    <div
                      key={i}
                      className={cn(
                        "flex-1 h-1.5 rounded-full transition-colors",
                        i < agent.usedSlots ? "bg-primary" : "bg-muted"
                      )}
                    />
                  ))}
                </div>
              </div>

              {/* Expanded: pipeline + collections */}
              {open && (
                <div className="pt-2 border-t border-border space-y-2.5 animate-fade-in">
                  <div className="space-y-1">
                    <div className="text-xs font-medium text-muted-foreground">Pipeline steps</div>
                    {agent.pipeline.map((step, i) => (
                      <div key={i} className="text-xs flex items-center gap-1.5 text-muted-foreground">
                        <span className="w-4 h-4 rounded-full bg-muted flex items-center justify-center text-[10px] font-bold shrink-0">{i + 1}</span>
                        {step}
                      </div>
                    ))}
                  </div>
                  <div className="space-y-1">
                    <div className="text-xs font-medium text-muted-foreground">Qdrant collections</div>
                    {agent.collections.map((c) => (
                      <div key={c} className="text-xs font-mono text-primary truncate">{c}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Agentic pipeline visualizer */}
      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <div className="flex items-center gap-2">
            <GitMerge className="w-4 h-4 text-primary" />
            <h2 className="font-semibold text-sm">Agentic Pipeline — Shopper → Inventory → Supervisor</h2>
          </div>
          <button
            onClick={runPipeline}
            disabled={pipelineRunning}
            className={cn(
              "text-xs px-3 py-1.5 rounded-full border transition-colors flex items-center gap-1.5",
              pipelineRunning ? "bg-muted border-border text-muted-foreground" : "bg-primary/10 border-primary/30 text-primary hover:bg-primary/20"
            )}
          >
            {pipelineRunning ? <><Activity className="w-3 h-3 animate-pulse" /> Running…</> : <><Zap className="w-3 h-3" /> Simulate Goal</>}
          </button>
        </div>
        <div className="p-5">
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
                    <div className="text-xs text-muted-foreground leading-tight">{step.desc}</div>
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
        </div>
      </div>

      {/* Semaphore pool overview */}
      <div className="rounded-xl border border-border bg-card p-5 space-y-4">
        <div className="flex items-center gap-2">
          <Lock className="w-4 h-4 text-primary" />
          <h2 className="font-semibold text-sm">Semaphore Pool — 16 Concurrent Slots / Store</h2>
        </div>
        <div className="grid grid-cols-4 sm:grid-cols-8 gap-1.5">
          {Array.from({ length: 16 }).map((_, i) => {
            const usedByAgent = i < 2 ? "Supervisor" : i < 3 ? "Shopper" : i < 6 ? "Inventory" : null;
            return (
              <div
                key={i}
                className={cn(
                  "h-8 rounded-md border text-xs flex items-center justify-center font-medium transition-colors",
                  usedByAgent === "Supervisor" ? "bg-primary/20 border-primary/40 text-primary" :
                  usedByAgent === "Shopper" ? "bg-accent/20 border-accent/40 text-accent" :
                  usedByAgent === "Inventory" ? "bg-status-info/20 border-status-info/40 text-status-info" :
                  "bg-muted/40 border-border text-muted-foreground/40"
                )}
              >
                {usedByAgent ? usedByAgent[0] : "·"}
              </div>
            );
          })}
        </div>
        <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
          {[
            { label: "S = Supervisor", color: "bg-primary/20 text-primary" },
            { label: "s = Shopper", color: "bg-accent/20 text-accent" },
            { label: "I = Inventory", color: "bg-status-info/20 text-status-info" },
            { label: "· = Free", color: "bg-muted/40 text-muted-foreground" },
          ].map(({ label, color }) => (
            <span key={label} className={cn("px-2 py-0.5 rounded text-xs", color)}>{label}</span>
          ))}
          <span className="ml-auto">6 / 16 slots active</span>
        </div>
      </div>

      {/* Live logs */}
      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="font-semibold flex items-center gap-2"><Activity className="w-4 h-4 text-primary" /> Execution Logs</h2>
          <button
            onClick={() => setLive(!live)}
            className={cn("text-xs px-3 py-1.5 rounded-full border transition-colors", live ? "bg-status-online/15 text-status-online border-status-online/30" : "bg-muted border-border text-muted-foreground")}
          >
            {live ? "● Live" : "○ Start Live"}
          </button>
        </div>
        <div className="font-mono text-xs p-4 space-y-1 max-h-80 overflow-y-auto scrollbar-thin bg-background/50">
          {logs.map((log) => (
            <div key={log.id} className={cn("flex gap-3", LOG_COLORS[log.type])}>
              <span className="opacity-50 shrink-0">{log.time}</span>
              <span className="text-primary shrink-0">[{log.agent}]</span>
              <span>{log.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
