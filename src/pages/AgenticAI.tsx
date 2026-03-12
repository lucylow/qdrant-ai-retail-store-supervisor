import { useState } from "react";
import {
  ArrowRight, ArrowDown, Database, Bot, Brain, Zap,
  CheckCircle2, XCircle, Layers, Network, TrendingUp,
  Users, Cpu, BarChart3, Sparkles, Quote,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

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
    color: "text-status-warning",
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
  qdrant: "border-status-info/30 bg-status-info/5",
  system: "border-status-online/30 bg-status-online/5",
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
                    ? "border-status-online/30 bg-status-online/5 opacity-60"
                    : TYPE_COLORS[step.type]
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${active ? "text-primary" : "text-muted-foreground"}`} />
                <span className="text-sm flex-1">{step.label}</span>
                {done && <CheckCircle2 className="w-3.5 h-3.5 text-status-online" />}
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
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function AgenticAIPage() {
  return (
    <div className="p-6 space-y-10 animate-fade-in max-w-6xl mx-auto">
      {/* Header */}
      <div className="space-y-3 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium">
          <Sparkles className="w-3.5 h-3.5" />
          True Agentic AI
        </div>
        <h1 className="text-4xl font-bold tracking-tight">
          From Smart Chatbot to Collaborative Specialists
        </h1>
        <p className="text-muted-foreground max-w-3xl mx-auto text-lg">
          Single-agent systems are just chatbots with memory. Real agentic AI emerges when
          multiple autonomous specialists coordinate via shared memory, each contributing unique expertise.
        </p>
      </div>

      {/* ---- Comparison Grid ---- */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Single Agent */}
        <Card className="border-destructive/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-destructive/15 flex items-center justify-center">
                <Bot className="w-5 h-5 text-destructive" />
              </div>
              <div>
                <div className="text-base">Single Agent</div>
                <div className="text-sm font-normal text-muted-foreground">Smart Chatbot with Memory</div>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {SINGLE_AGENT_LIMITS.map((item) => (
              <div key={item} className="flex items-start gap-2 text-sm text-muted-foreground">
                <XCircle className="w-4 h-4 text-destructive shrink-0 mt-0.5" />
                {item}
              </div>
            ))}
            <div className="pt-3 text-center">
              <Badge variant="outline" className="text-destructive border-destructive/30 bg-destructive/5">
                ❌ Limited by monolithic design
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Multi-Agent */}
        <Card className="border-status-online/30 bg-gradient-to-br from-status-online/5 to-primary/5 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-status-online/15 flex items-center justify-center">
                <Network className="w-5 h-5 text-status-online" />
              </div>
              <div>
                <div className="text-base">Multi-Agent System</div>
                <div className="text-sm font-normal text-muted-foreground">Two+ Decoupled Agents = Agentic AI</div>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {MULTI_AGENT_FEATURES.map((item, i) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-status-online shrink-0 mt-0.5" />
                <span>
                  <span className="font-semibold">{item.bold}</span>
                  {item.text && ` ${item.text}`}
                </span>
              </div>
            ))}
            <div className="pt-3 text-center">
              <Badge className="bg-status-online/15 text-status-online border border-status-online/25">
                ✅ Specialization + Coordination + Learning
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ---- Shared Memory Visualization ---- */}
      <Card className="bg-card/80">
        <CardContent className="pt-6">
          <div className="flex flex-wrap justify-center items-center gap-3">
            <div className="px-5 py-3 rounded-full bg-primary/15 border border-primary/25 text-primary font-semibold text-sm flex items-center gap-2">
              <Bot className="w-4 h-4" /> Shopper Agent
            </div>
            <ArrowRight className="w-5 h-5 text-muted-foreground" />
            <div className="px-5 py-3 rounded-full bg-accent/15 border border-accent/25 text-accent font-semibold text-sm flex items-center gap-2">
              <Database className="w-4 h-4" /> Qdrant Memory
            </div>
            <ArrowRight className="w-5 h-5 text-muted-foreground rotate-180" />
            <div className="px-5 py-3 rounded-full bg-status-online/15 border border-status-online/25 text-status-online font-semibold text-sm flex items-center gap-2">
              <Cpu className="w-4 h-4" /> Inventory Agent
            </div>
          </div>
          <p className="text-center text-muted-foreground text-sm mt-4">
            Agents never call each other directly — they coordinate via Qdrant's vector memory.
          </p>
          <div className="flex justify-center gap-2 mt-3">
            {["goals", "solutions", "episodes", "products"].map((col) => (
              <Badge key={col} variant="outline" className="text-xs font-mono">
                {col}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* ---- Key Quote ---- */}
      <div className="border-t border-b border-border py-8 text-center space-y-2">
        <Quote className="w-6 h-6 text-primary mx-auto mb-2" />
        <blockquote className="text-xl font-light italic text-foreground max-w-4xl mx-auto leading-relaxed">
          "True agentic AI: Two autonomous specialists reason independently, coordinate via Qdrant
          semantic memory, execute across inventory systems, and learn from every successful transaction."
        </blockquote>
        <p className="text-sm text-muted-foreground">
          — Hits every agentic AI checkbox while staying laser-focused on retail
        </p>
      </div>

      {/* ---- Three Pillars ---- */}
      <div className="grid md:grid-cols-3 gap-5">
        {PILLARS.map((pillar) => {
          const Icon = pillar.icon;
          return (
            <Card key={pillar.title} className="hover:border-primary/30 transition-colors group">
              <CardContent className="pt-5 space-y-3">
                <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center group-hover:bg-primary/10 transition-colors">
                  <Icon className={`w-5 h-5 ${pillar.color}`} />
                </div>
                <h3 className="font-bold text-lg">{pillar.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{pillar.description}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* ---- Agentic Checklist ---- */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-status-online" />
            Agentic AI Checklist
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-3">
            {AGENTIC_CHECKLIST.map((item) => (
              <div
                key={item.label}
                className="flex items-start gap-3 px-4 py-3 rounded-lg border border-status-online/20 bg-status-online/5"
              >
                <CheckCircle2 className="w-4 h-4 text-status-online shrink-0 mt-0.5" />
                <div>
                  <div className="text-sm font-medium">{item.label}</div>
                  <div className="text-xs text-muted-foreground">{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* ---- Live Transaction Flow ---- */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Zap className="w-4 h-4 text-primary" />
            End-to-End Agent Transaction
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Watch both agents coordinate through Qdrant to fulfill a real shopping goal.
          </p>
        </CardHeader>
        <CardContent>
          <AgentFlow />
        </CardContent>
      </Card>

      {/* ---- Metrics ---- */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: "Agent Specialization", value: "2 agents", icon: Users },
          { label: "Shared Collections", value: "4", icon: Database },
          { label: "Episode Reuse", value: "67%", icon: BarChart3 },
          { label: "Conversion Lift", value: "+24%", icon: TrendingUp },
        ].map(({ label, value, icon: Icon }) => (
          <div key={label} className="rounded-xl border border-border bg-card p-4 text-center space-y-1">
            <Icon className="w-4 h-4 text-muted-foreground mx-auto" />
            <div className="text-2xl font-bold text-gradient">{value}</div>
            <div className="text-xs text-muted-foreground">{label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
