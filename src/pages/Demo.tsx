import { useState } from "react";
import { Link } from "react-router-dom";
import { PlayCircle, ChevronRight, Zap, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { BundleCard } from "@/components/BundleCard";

const DEMO_SCRIPTS = [
  {
    id: "d1",
    title: "2-Person Tent Weekend",
    query: "2-person tent under 200CHF Zurich Friday",
    description: "Classic Zurich outdoor scenario. Demos episodic cache hit.",
    expectedLatency: "35ms",
    cacheHit: true,
  },
  {
    id: "d2",
    title: "Hiking Boot Finder",
    query: "waterproof hiking boots size 42 lightweight Switzerland",
    description: "Size-constrained product search with regional context.",
    expectedLatency: "58ms",
    cacheHit: false,
  },
  {
    id: "d3",
    title: "Complete Camping Kit",
    query: "complete camping kit weekend Switzerland budget 500CHF",
    description: "Multi-product bundle assembly with Inventory agent.",
    expectedLatency: "42ms",
    cacheHit: true,
  },
  {
    id: "d4",
    title: "Winter Sleeping Bag",
    query: "sleeping bag -5 degrees winter Switzerland",
    description: "Spec-driven retrieval: temperature rating, weight, price.",
    expectedLatency: "48ms",
    cacheHit: false,
  },
];

const MOCK_BUNDLE = {
  products: [
    { id: "p1", name: "MSR Hubba Hubba NX 2", price: 189 },
    { id: "p2", name: "Sea to Summit Sleeping Bag", price: 89 },
    { id: "p3", name: "JetBoil Flash Stove", price: 49 },
  ],
  totalPrice: 327,
  currency: "CHF",
  eta: "Available today",
  confidence: 0.91,
};

export default function DemoPage() {
  const [running, setRunning] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, boolean>>({});

  const runDemo = (id: string) => {
    setRunning(id);
    setTimeout(() => {
      setResults((prev) => ({ ...prev, [id]: true }));
      setRunning(null);
    }, 1500);
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">Demo Scripts</h1>
        <p className="text-sm text-muted-foreground">Pre-canned queries for hackathon demo. Run in ~5 minutes.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {DEMO_SCRIPTS.map((script) => (
          <div key={script.id} className="rounded-xl border border-border bg-card p-5 space-y-3 hover:border-primary/30 transition-colors">
            <div className="flex items-start justify-between gap-2">
              <h3 className="font-semibold">{script.title}</h3>
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground shrink-0">
                <Clock className="w-3 h-3" />
                {script.expectedLatency}
                {script.cacheHit && (
                  <span className="flex items-center gap-0.5 text-status-online">
                    <Zap className="w-3 h-3" />HIT
                  </span>
                )}
              </div>
            </div>
            <p className="text-xs text-muted-foreground italic">"{script.query}"</p>
            <p className="text-sm text-muted-foreground">{script.description}</p>

            {results[script.id] && (
              <div className="animate-fade-in">
                <BundleCard {...MOCK_BUNDLE} goalText={script.query} />
              </div>
            )}

            <div className="flex gap-2 pt-1">
              <Button
                size="sm"
                onClick={() => runDemo(script.id)}
                disabled={running === script.id}
                className="gradient-primary gap-1.5 flex-1"
              >
                {running === script.id ? (
                  <>
                    <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    Running…
                  </>
                ) : (
                  <>
                    <PlayCircle className="w-3.5 h-3.5" /> Run Demo
                  </>
                )}
              </Button>
              <Button size="sm" variant="outline" className="gap-1" asChild>
                <Link to={`/chat?q=${encodeURIComponent(script.query)}`}>
                  Chat <ChevronRight className="w-3 h-3" />
                </Link>
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
