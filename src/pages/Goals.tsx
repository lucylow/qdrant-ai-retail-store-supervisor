import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, MOCK_GOALS } from "@/lib/api";
import { GoalStatusChip } from "@/components/GoalStatusChip";
import { Button } from "@/components/ui/button";
import { Plus, Filter, MapPin, Search } from "lucide-react";
import { toast } from "sonner";

const REGIONS = ["All", "Zurich", "Geneva", "Basel", "Bern"];
const STATUSES = ["all", "open", "pending", "fulfilled", "failed"];

export default function GoalsPage() {
  const qc = useQueryClient();
  const [region, setRegion] = useState("All");
  const [status, setStatus] = useState("all");
  const [search, setSearch] = useState("");
  const [newGoal, setNewGoal] = useState("");
  const [newRegion, setNewRegion] = useState("Zurich");

  const { data: goals = MOCK_GOALS } = useQuery({
    queryKey: ["goals"],
    queryFn: api.getGoals,
    retry: 1,
    placeholderData: MOCK_GOALS,
  });

  const createMutation = useMutation({
    mutationFn: ({ text, region }: { text: string; region: string }) => api.createGoal(text, region),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["goals"] });
      setNewGoal("");
      toast.success("Goal created!");
    },
    onError: () => {
      toast.error("Failed to create goal (backend offline)");
    },
  });

  const filtered = goals.filter((g) => {
    if (region !== "All" && g.region !== region) return false;
    if (status !== "all" && g.status !== status) return false;
    if (search && !g.text.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Goals Explorer</h1>
          <p className="text-sm text-muted-foreground">User intent goals tracked by Shopper agent</p>
        </div>
        <span className="text-sm text-muted-foreground">{filtered.length} goals</span>
      </div>

      {/* Create new goal */}
      <div className="rounded-xl border border-border bg-card p-4 space-y-3">
        <h2 className="text-sm font-semibold flex items-center gap-2"><Plus className="w-4 h-4 text-primary" /> New Goal</h2>
        <div className="flex gap-2">
          <input
            value={newGoal}
            onChange={(e) => setNewGoal(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && newGoal.trim() && createMutation.mutate({ text: newGoal, region: newRegion })}
            placeholder="e.g. 2-person tent under 200CHF Zurich"
            className="flex-1 bg-muted border border-border rounded-lg px-3 py-2 text-sm outline-none focus:border-primary/50"
          />
          <select value={newRegion} onChange={(e) => setNewRegion(e.target.value)} className="bg-muted border border-border rounded-lg px-3 py-2 text-sm outline-none">
            {REGIONS.filter(r => r !== "All").map(r => <option key={r}>{r}</option>)}
          </select>
          <Button onClick={() => newGoal.trim() && createMutation.mutate({ text: newGoal, region: newRegion })} disabled={createMutation.isPending} className="gradient-primary">
            <Plus className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="flex items-center gap-2 flex-1 min-w-[180px] bg-muted border border-border rounded-lg px-3 py-2">
          <Search className="w-3.5 h-3.5 text-muted-foreground" />
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search goals…" className="bg-transparent text-sm outline-none flex-1 placeholder:text-muted-foreground" />
        </div>
        <div className="flex items-center gap-1.5 flex-wrap">
          <Filter className="w-3.5 h-3.5 text-muted-foreground" />
          {REGIONS.map(r => (
            <button key={r} onClick={() => setRegion(r)} className={`text-xs px-2.5 py-1 rounded-full border transition-colors ${region === r ? "bg-primary/20 text-primary border-primary/40" : "bg-muted border-border text-muted-foreground hover:border-primary/30"}`}>
              {r}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-1.5 flex-wrap">
          {STATUSES.map(s => (
            <button key={s} onClick={() => setStatus(s)} className={`text-xs px-2.5 py-1 rounded-full border transition-colors capitalize ${status === s ? "bg-primary/20 text-primary border-primary/40" : "bg-muted border-border text-muted-foreground hover:border-primary/30"}`}>
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Goal</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">Region</th>
              <th className="text-left px-4 py-3 font-medium text-muted-foreground">ID</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((goal) => (
              <tr key={goal.id} className="border-b border-border last:border-0 hover:bg-muted/30 transition-colors">
                <td className="px-4 py-3 text-foreground">{goal.text}</td>
                <td className="px-4 py-3"><GoalStatusChip status={goal.status} /></td>
                <td className="px-4 py-3 text-muted-foreground flex items-center gap-1">
                  <MapPin className="w-3 h-3" />{goal.region}
                </td>
                <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{goal.id}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="py-12 text-center text-muted-foreground">No goals match your filters.</div>
        )}
      </div>
    </div>
  );
}
