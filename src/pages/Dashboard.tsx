import { useQuery } from "@tanstack/react-query";
import { api, MOCK_METRICS, MOCK_GOALS } from "@/lib/api";
import { MetricCard } from "@/components/MetricCard";
import { GoalStatusChip } from "@/components/GoalStatusChip";
import { AgentAvatar } from "@/components/AgentAvatar";
import { Button } from "@/components/ui/button";
import { Database, Zap, Target, Activity, Clock, AlertCircle } from "lucide-react";
import { Link } from "react-router-dom";

export default function DashboardPage() {
  const { data: health, isError: healthErr } = useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    retry: 1,
    refetchInterval: 15000,
  });

  const { data: metrics } = useQuery({
    queryKey: ["metrics"],
    queryFn: api.metrics,
    retry: 1,
    placeholderData: MOCK_METRICS,
    refetchInterval: 10000,
  });

  const { data: goals } = useQuery({
    queryKey: ["goals"],
    queryFn: api.getGoals,
    retry: 1,
    placeholderData: MOCK_GOALS,
  });

  const m = metrics || MOCK_METRICS;
  const g = goals || MOCK_GOALS;
  const isOnline = !healthErr && health?.status === "ok";

  const AGENTS = [
    { type: "supervisor" as const, label: "Supervisor", online: isOnline },
    { type: "shopper" as const, label: "Shopper", online: isOnline },
    { type: "inventory" as const, label: "Inventory", online: isOnline },
    { type: "pricing" as const, label: "Pricing", online: false },
  ];

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-0.5">Multi-Agent Store Supervisor · Qdrant RAG</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${isOnline ? "bg-status-online animate-pulse-glow" : "bg-status-error"}`} />
          <span className="text-sm text-muted-foreground">
            {isOnline ? "Backend online" : "Backend offline (mock data)"}
          </span>
        </div>
      </div>

      {/* Offline banner */}
      {healthErr && (
        <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-status-warning/10 border border-status-warning/30 text-status-warning text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          Backend at localhost:8000 unreachable — showing demo data. Run{" "}
          <code className="font-mono text-xs bg-muted px-1 rounded">docker-compose up</code> to connect.
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="Cache Hit Rate" value={`${(m.cache_hit * 100).toFixed(0)}%`} icon={<Database className="w-4 h-4" />} trend={3} highlight description="Episodic memory reuse" />
        <MetricCard label="P95 Latency" value={m.p95_latency_ms} unit="ms" icon={<Clock className="w-4 h-4" />} trend={-8} description="Last 1000 requests" />
        <MetricCard label="QPS" value={(m.qps ?? 12.4).toFixed(1)} icon={<Zap className="w-4 h-4" />} trend={12} description="Queries per second" />
        <MetricCard label="Total Goals" value={m.total_goals ?? 347} icon={<Target className="w-4 h-4" />} trend={5} description="Active & fulfilled" />
      </div>

      {/* Agents + Goals */}
      <div className="grid lg:grid-cols-3 gap-5">
        {/* Agent Status */}
        <div className="rounded-xl border border-border bg-card p-5 space-y-4">
          <h2 className="font-semibold flex items-center gap-2">
            <Activity className="w-4 h-4 text-primary" /> Agent Status
          </h2>
          <div className="space-y-3">
            {AGENTS.map(({ type, label, online }) => (
              <div key={type} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <AgentAvatar type={type} online={online} size="sm" />
                  <span className="text-sm font-medium">{label}</span>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full ${online ? "bg-status-online/15 text-status-online" : "bg-muted text-muted-foreground"}`}>
                  {online ? "Running" : "Idle"}
                </span>
              </div>
            ))}
          </div>
          <Button variant="outline" size="sm" className="w-full mt-2" asChild>
            <Link to="/agents">View Logs</Link>
          </Button>
        </div>

        {/* Recent Goals */}
        <div className="lg:col-span-2 rounded-xl border border-border bg-card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold flex items-center gap-2">
              <Target className="w-4 h-4 text-primary" /> Recent Goals
            </h2>
            <Button variant="ghost" size="sm" className="text-xs" asChild>
              <Link to="/goals">View all</Link>
            </Button>
          </div>
          <div className="space-y-2">
            {g.slice(0, 5).map((goal) => (
              <div key={goal.id} className="flex items-center gap-3 py-2 border-b border-border last:border-0">
                <GoalStatusChip status={goal.status} />
                <span className="text-sm flex-1 truncate">{goal.text}</span>
                <Link to={`/solutions/${goal.id}`} className="text-xs text-primary hover:underline shrink-0">
                  Solutions →
                </Link>
                <span className="text-xs text-muted-foreground shrink-0">{goal.region}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { to: "/chat", label: "New Chat", icon: "💬" },
          { to: "/goals", label: "View Goals", icon: "🎯" },
          { to: "/metrics", label: "Full Metrics", icon: "📊" },
          { to: "/hackathon", label: "Hackathon", icon: "🏆" },
        ].map(({ to, label, icon }) => (
          <Link key={to} to={to}>
            <div className="rounded-xl border border-border bg-card p-4 flex items-center gap-3 hover:border-primary/30 hover:bg-card/80 transition-all cursor-pointer">
              <span className="text-2xl">{icon}</span>
              <span className="text-sm font-medium">{label}</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
