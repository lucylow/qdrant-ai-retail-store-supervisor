import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api, MOCK_GOALS, MOCK_PRODUCTS } from "@/lib/api";
import { BundleCard } from "@/components/BundleCard";
import { GoalStatusChip } from "@/components/GoalStatusChip";
import { ProvenanceBadge } from "@/components/ProvenanceBadge";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Package, Zap, Clock, CheckCircle } from "lucide-react";

// Mock solution data for offline mode
function getMockSolution(goalId: string) {
  const goal = MOCK_GOALS.find((g) => g.id === goalId) || MOCK_GOALS[0];
  return {
    id: `sol_${goalId}`,
    goal_id: goalId,
    goal,
    bundles: [
      {
        rank: 1,
        confidence: 0.92,
        cacheHit: true,
        latencyMs: 35,
        products: [
          { id: "p1", name: "MSR Hubba Hubba NX 2", description: "2-person backpacking tent, 1.72kg", price: 189, category: "Tents" },
          { id: "p2", name: "Sea to Summit Spark SP1", description: "3-season sleeping bag", price: 89, category: "Sleeping" },
          { id: "p3", name: "MSR PocketRocket 2", description: "Ultralight backpacking stove", price: 49, category: "Cooking" },
        ],
        totalPrice: 327,
        currency: "CHF",
        eta: "Available today",
        provenance: [
          { id: 1, text: "Episode ep_7234 — 92% similar goal from 2026-03-09", source: "Episodic Memory", score: 0.92 },
          { id: 2, text: "MSR Hubba Hubba NX2 product description", source: "Products DB", score: 0.88 },
        ],
      },
      {
        rank: 2,
        confidence: 0.78,
        cacheHit: false,
        latencyMs: 68,
        products: [
          { id: "p4", name: "Big Agnes Copper Spur HV UL2", description: "Ultralight 2-person tent", price: 249, category: "Tents" },
          { id: "p5", name: "Therm-a-Rest NeoAir XLite", description: "Sleeping pad, R-value 4.2", price: 159, category: "Sleeping" },
        ],
        totalPrice: 408,
        currency: "CHF",
        eta: "2–3 days",
        provenance: [
          { id: 1, text: "Full RAG retrieval from products collection", source: "Products DB", score: 0.78 },
        ],
      },
    ],
  };
}

export default function SolutionsPage() {
  const { goalId } = useParams<{ goalId: string }>();
  const id = goalId || "g1";

  const { data: solution, isLoading } = useQuery({
    queryKey: ["solution", id],
    queryFn: () => api.getSolution(id),
    retry: 1,
    placeholderData: getMockSolution(id) as any,
  });

  const mock = getMockSolution(id);
  const goal = (solution as any)?.goal || mock.goal;
  const bundles = (solution as any)?.bundles || mock.bundles;

  return (
    <div className="p-6 space-y-6 animate-fade-in max-w-4xl">
      {/* Back */}
      <Button variant="ghost" size="sm" className="gap-1.5 -ml-1" asChild>
        <Link to="/goals">
          <ArrowLeft className="w-4 h-4" /> Back to Goals
        </Link>
      </Button>

      {/* Goal header */}
      <div className="rounded-xl border border-border bg-card p-5 space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <Package className="w-4 h-4 text-primary" />
              <span className="text-xs font-mono text-muted-foreground">{id}</span>
            </div>
            <h1 className="text-xl font-bold">{goal?.text || "Goal"}</h1>
          </div>
          {goal?.status && <GoalStatusChip status={goal.status} />}
        </div>
        {goal?.region && (
          <p className="text-sm text-muted-foreground">📍 {goal.region}</p>
        )}
      </div>

      {/* Bundles */}
      <div>
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-primary" />
          {bundles.length} Ranked Solution{bundles.length !== 1 ? "s" : ""}
        </h2>
        <div className="space-y-4">
          {bundles.map((bundle: any, i: number) => (
            <div key={i} className="space-y-2">
              {/* Bundle meta row */}
              <div className="flex items-center gap-3 px-1">
                <span className="text-xs font-bold text-muted-foreground">#{bundle.rank || i + 1}</span>
                {bundle.cacheHit && (
                  <span className="flex items-center gap-1 text-xs text-status-online font-medium">
                    <Zap className="w-3 h-3" /> CACHE HIT
                  </span>
                )}
                {bundle.latencyMs && (
                  <span className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="w-3 h-3" /> {bundle.latencyMs}ms
                  </span>
                )}
              </div>

              <BundleCard
                products={bundle.products || []}
                totalPrice={bundle.totalPrice}
                currency={bundle.currency}
                eta={bundle.eta}
                confidence={bundle.confidence}
              />

              {/* Provenance */}
              {bundle.provenance?.length > 0 && (
                <div className="px-1 flex items-center gap-1.5 flex-wrap">
                  <span className="text-xs text-muted-foreground">Sources:</span>
                  {bundle.provenance.map((p: any) => (
                    <ProvenanceBadge key={p.id} index={p.id} text={p.text} source={p.source} score={p.score} />
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        <Button className="gradient-primary gap-2" asChild>
          <Link to={`/chat?q=${encodeURIComponent(goal?.text || "")}`}>
            <Zap className="w-4 h-4" /> Refine in Chat
          </Link>
        </Button>
        <Button variant="outline" asChild>
          <Link to="/goals">All Goals</Link>
        </Button>
      </div>
    </div>
  );
}
