import { Link } from "react-router-dom";
import { Database, Zap, ArrowRight, Bot, BookOpen, ShoppingBag, BarChart3, Award, Sparkles, Brain, ShieldCheck, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";

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
  "complete camping kit weekend Switzerland",
];

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero */}
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
            <span className="text-foreground">Multi-Agent</span>
            <br />
            <span className="text-gradient">Store Supervisor</span>
          </h1>

          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Agentic RAG with Qdrant blackboard architecture. Shopper + Inventory agents,
            episodic memory, 87% cache hit, P95 42ms.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <Button size="lg" className="gradient-primary text-primary-foreground font-semibold shadow-lg hover:opacity-90 gap-2" asChild>
              <Link to="/chat">
                Try Demo <ArrowRight className="w-4 h-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="gap-2" asChild>
              <Link to="/dashboard">
                <BarChart3 className="w-4 h-4" /> Dashboard
              </Link>
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

      {/* Stats */}
      <section className="border-t border-border bg-card/50 py-10 px-6">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {[
            { label: "Cache Hit Rate", value: "87%" },
            { label: "P95 Latency", value: "42ms" },
            { label: "Conversion Lift", value: "+24%" },
            { label: "Qdrant Collections", value: "4" },
          ].map(({ label, value }) => (
            <div key={label}>
              <div className="text-3xl font-bold text-gradient">{value}</div>
              <div className="text-sm text-muted-foreground mt-1">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Appropriate & Effective Use of Generative AI */}
      <section className="py-20 px-6 bg-muted/50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-4">
              <Sparkles className="w-3.5 h-3.5" />
              Generative AI Integration
            </div>
            <h2 className="text-3xl font-bold">🎯 Appropriate & Effective Use of Generative AI</h2>
            <p className="text-muted-foreground mt-2 max-w-2xl mx-auto">
              We deploy LLMs only where they add unique value—language understanding, explanation, and planning—while keeping core business logic deterministic and grounded in real data.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Shopper Agent: Understanding & Structuring */}
            <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <MessageSquare className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-semibold text-lg">Shopper Agent: Understanding & Structuring</h3>
              </div>
              <ul className="space-y-3 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span><strong className="text-foreground">Natural-language understanding:</strong> LLM parses messy, multi-constraint requests into structured "goal" objects. Example: "I need two lightweight hiking backpacks, under 150 each, delivered to Zurich before next Saturday, not neon colors." → structured fields (category, quantity, budget, deadline, location, color preferences).</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span><strong className="text-foreground">Clarifying questions:</strong> When constraints conflict (e.g., budget too low for required delivery date), the LLM asks targeted follow-ups instead of failing—leveraging conversational AI while driving toward a structured spec.</span>
                </li>
              </ul>
            </div>

            {/* Inventory Agent: Explanation & Planning */}
            <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Brain className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-semibold text-lg">Inventory Agent: Explanation & Planning</h3>
              </div>
              <ul className="space-y-3 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span><strong className="text-foreground">Explanation generation:</strong> Calls real inventory APIs for SKUs, prices, lead times. Then LLM ranks options and explains trade-offs ("Option A is cheaper but arrives 2 days later; Option B costs 15 more but meets your trip date.").</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span><strong className="text-foreground">Constraint-aware decisions:</strong> Optimizes for composite objectives (margin, satisfaction, shipping speed), with constraints injected from Qdrant payloads and inventory APIs. The model acts as a planner/explainer, not a black-box optimizer.</span>
                </li>
              </ul>
            </div>
          </div>

          {/* GenAI ↔ Qdrant Interaction */}
          <div className="rounded-xl border border-primary/20 bg-gradient-to-r from-primary/5 to-blue-50/30 p-6 mb-8">
            <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
              <Database className="w-5 h-5 text-primary" />
              GenAI ↔ Qdrant: Retrieval-Augmented Reasoning
            </h3>
            <div className="grid sm:grid-cols-2 gap-6 text-sm">
              <div>
                <h4 className="font-medium text-foreground mb-2">📥 Turning generative outputs into memory</h4>
                <p className="text-muted-foreground">
                  User goals, solution summaries, and outcomes are embedded and stored in Qdrant. Each "episode" pairs goal_text + solution_summary + outcome—creating a long-term, searchable memory of what worked.
                </p>
              </div>
              <div>
                <h4 className="font-medium text-foreground mb-2">🔍 Retrieval-augmented generation</h4>
                <p className="text-muted-foreground">
                  Before proposing a bundle, Inventory Agent retrieves similar past goal–solution pairs from Qdrant and feeds them into the LLM prompt—grounding the model in prior successes, avoiding hallucinated strategies.
                </p>
              </div>
            </div>
          </div>

          {/* Guardrails */}
          <div className="rounded-xl border border-amber-200/50 bg-amber-50/30 p-6 mb-8">
            <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-amber-600" />
              Guardrails: Where We Don't Use GenAI
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Critical business logic remains deterministic—ensuring reliability: GenAI handles fuzzy language and high-level planning; deterministic systems enforce business rules.
            </p>
            <div className="flex flex-wrap gap-2">
              {["Stock availability", "Exact prices", "Shipping constraints", "Structured goal validation", "Qdrant payload updates"].map((item) => (
                <span key={item} className="text-xs px-3 py-1.5 rounded-full bg-background border border-border text-foreground">
                  ✓ {item}
                </span>
              ))}
            </div>
          </div>

          {/* Summary Quote */}
          <div className="rounded-xl bg-gradient-to-r from-primary/10 to-blue-100/50 p-6 border border-primary/20">
            <blockquote className="text-sm text-foreground leading-relaxed">
              "We use LLMs where human-like understanding is needed: the Shopper Agent turns messy natural language into structured goals and asks clarifying questions when constraints conflict. The Inventory Agent uses GenAI to synthesize explanations and trade-offs from hard inventory data. Qdrant provides retrieval-augmented memory—before planning, the Inventory Agent fetches similar successful episodes and feeds them into the LLM, so generative decisions are grounded in what has historically worked. Critical business logic—stock checks, pricing, shipping feasibility—remains deterministic. GenAI never overrides those systems; it orchestrates and explains them. This division of labor makes the generative component both appropriate and reliable."
            </blockquote>
            <p className="text-xs text-muted-foreground mt-3">— Appropriate & Effective Use of GenAI</p>
          </div>
        </div>
      </section>

      {/* Features */}
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

      {/* CTA */}
      <section className="py-16 px-6 border-t border-border text-center">
        <div className="max-w-xl mx-auto space-y-4">
          <h2 className="text-2xl font-bold">Ready to demo?</h2>
          <p className="text-muted-foreground">Start the chat interface or explore the live metrics dashboard.</p>
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
