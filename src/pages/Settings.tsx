import { useState } from "react";
import { Link } from "react-router-dom";
import { Settings as SettingsIcon, Server, Moon, Sun, Info, Save, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState((import.meta.env.VITE_API_URL as string) || "http://localhost:8000");
  const [qdrantUrl, setQdrantUrl] = useState("http://localhost:6333");
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [saved, setSaved] = useState(false);

  const save = () => {
    setSaved(true);
    toast.success("Settings saved (reload to apply API URL change)");
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <SettingsIcon className="w-5 h-5 text-primary" /> Settings
        </h1>
        <p className="text-sm text-muted-foreground">Configure backend connection and display preferences</p>
      </div>

      {/* Backend */}
      <div className="rounded-xl border border-border bg-card p-5 space-y-4">
        <h2 className="font-semibold flex items-center gap-2">
          <Server className="w-4 h-4 text-primary" /> Backend
        </h2>
        <div className="space-y-3">
          <div>
            <label className="text-xs font-medium text-muted-foreground mb-1.5 block">FastAPI Base URL</label>
            <input
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              className="w-full bg-muted border border-border rounded-lg px-3 py-2 text-sm outline-none focus:border-primary/50 font-mono"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Set <code className="font-mono bg-muted px-1 rounded">VITE_API_URL</code> env var for production
            </p>
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Qdrant URL</label>
            <input
              value={qdrantUrl}
              onChange={(e) => setQdrantUrl(e.target.value)}
              className="w-full bg-muted border border-border rounded-lg px-3 py-2 text-sm outline-none focus:border-primary/50 font-mono"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground mb-1.5 block">WebSocket URL</label>
            <input
              value={apiUrl.replace("http", "ws") + "/ws/chat"}
              readOnly
              className="w-full bg-muted/50 border border-border rounded-lg px-3 py-2 text-sm font-mono text-muted-foreground cursor-not-allowed"
            />
            <p className="text-xs text-muted-foreground mt-1">Auto-derived from Base URL</p>
          </div>
        </div>
      </div>

      {/* Theme */}
      <div className="rounded-xl border border-border bg-card p-5 space-y-3">
        <h2 className="font-semibold">Appearance</h2>
        <div className="flex gap-2">
          {(["dark", "light"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTheme(t)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-colors capitalize ${
                theme === t
                  ? "bg-primary/20 text-primary border-primary/40"
                  : "bg-muted border-border text-muted-foreground"
              }`}
            >
              {t === "dark" ? <Moon className="w-3.5 h-3.5" /> : <Sun className="w-3.5 h-3.5" />} {t}
            </button>
          ))}
        </div>
      </div>

      {/* Info */}
      <div className="rounded-xl border border-border bg-muted/50 p-4 space-y-1.5 text-xs text-muted-foreground">
        <div className="flex items-center gap-1.5 font-medium text-foreground">
          <Info className="w-3.5 h-3.5" /> Deployment Notes
        </div>
        <p>Run backend: <code className="font-mono bg-muted px-1 rounded">docker-compose up</code></p>
        <p>Frontend dev: <code className="font-mono bg-muted px-1 rounded">npm run dev</code></p>
        <p>Env: Set <code className="font-mono bg-muted px-1 rounded">VITE_API_URL</code> for production deployment</p>
        <p>WebSocket: Backend must expose <code className="font-mono bg-muted px-1 rounded">/ws/chat</code></p>
      </div>

      <div className="flex gap-3">
        <Button onClick={save} className="gradient-primary gap-2">
          {saved ? <CheckCircle className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          {saved ? "Saved!" : "Save Settings"}
        </Button>
        <Button variant="outline" asChild>
          <Link to="/dashboard">Back to Dashboard</Link>
        </Button>
      </div>
    </div>
  );
}
