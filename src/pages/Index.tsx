import { Link } from "react-router-dom";
import { Database, Zap, ArrowRight, Bot, BookOpen, ShoppingBag, BarChart3, Award } from "lucide-react";
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
