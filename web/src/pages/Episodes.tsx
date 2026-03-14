import { useQuery } from "@tanstack/react-query";
import { api, MOCK_EPISODES } from "@/lib/api";
import { Clock, MapPin, CheckCircle, Search } from "lucide-react";
import { useState } from "react";

export default function EpisodesPage() {
  const [search, setSearch] = useState("");

  const { data: episodes = MOCK_EPISODES } = useQuery({
    queryKey: ["episodes"],
    queryFn: api.getEpisodes,
    retry: 1,
    placeholderData: MOCK_EPISODES,
  });

  const filtered = episodes.filter(ep =>
    !search || ep.goal_text?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">Episodic Memory</h1>
        <p className="text-sm text-muted-foreground">Agent-learned episodes stored in Qdrant. Power the 87% cache hit rate.</p>
      </div>

      <div className="flex items-center gap-2 max-w-sm bg-muted border border-border rounded-lg px-3 py-2">
        <Search className="w-3.5 h-3.5 text-muted-foreground" />
        <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search episodes…" className="bg-transparent text-sm outline-none flex-1 placeholder:text-muted-foreground" />
      </div>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-6 top-0 bottom-0 w-px bg-border" />

        <div className="space-y-4">
          {filtered.map((ep, i) => (
            <div key={ep.id} className="relative pl-14 animate-fade-in" style={{ animationDelay: `${i * 60}ms` }}>
              {/* Dot */}
              <div className="absolute left-4 top-4 w-4 h-4 rounded-full bg-primary/20 border-2 border-primary flex items-center justify-center">
                <div className="w-1.5 h-1.5 rounded-full bg-primary" />
              </div>

              <div className="rounded-xl border border-border bg-card p-4 hover:border-primary/30 transition-colors space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium">"{ep.goal_text}"</p>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <div className="w-16 h-1.5 rounded-full bg-muted overflow-hidden">
                      <div className="h-full bg-status-online rounded-full" style={{ width: `${(ep.success_rate || 0) * 100}%` }} />
                    </div>
                    <CheckCircle className="w-3.5 h-3.5 text-status-online" />
                    <span className="text-xs font-medium text-status-online">{((ep.success_rate || 0) * 100).toFixed(0)}%</span>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  {ep.region && <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{ep.region}</span>}
                  {ep.timestamp && <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{new Date(ep.timestamp).toLocaleDateString()}</span>}
                  <span className="font-mono text-xs text-muted-foreground/60">{ep.id}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
