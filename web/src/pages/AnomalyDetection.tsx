import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Shield, ShieldAlert, Activity, AlertTriangle, CheckCircle2, XCircle,
  Database, Brain, Zap, ArrowRight, Play, RotateCcw, TrendingUp,
  Cpu, HeartPulse, Eye, Lock, Server
} from "lucide-react";

// --- Types ---
type AnomalyEvent = {
  id: string;
  type: "fraud" | "agent_stall" | "inventory" | "qdrant_health";
  severity: "low" | "medium" | "high" | "critical";
  message: string;
  score: number;
  timestamp: string;
  resolved: boolean;
};

type SystemHealth = {
  shopperAgent: "healthy" | "degraded" | "down";
  inventoryAgent: "healthy" | "degraded" | "down";
  qdrantLatency: number;
  episodeSuccessRate: number;
  openGoals: number;
};

// --- Mock data generators ---
const NORMAL_GOALS = [
  "camping gear under 400CHF Zurich",
  "running shoes size 42 waterproof",
  "baby stroller lightweight foldable",
  "hiking boots Gore-Tex men's",
  "sleeping bag -5°C winter",
  "trekking poles carbon fiber pair",
];

const generateNormalEvent = (i: number): AnomalyEvent => ({
  id: `norm-${i}`,
  type: "fraud",
  severity: "low",
  message: NORMAL_GOALS[i % NORMAL_GOALS.length],
  score: 0.12 + Math.random() * 0.45,
  timestamp: new Date(Date.now() - Math.random() * 300000).toISOString(),
  resolved: false,
});

const FRAUD_EVENT: AnomalyEvent = {
  id: "fraud-001",
  type: "fraud",
  severity: "critical",
  message: 'iPhone 15 Pro Max ×47 in 90s — 92% match to known bot campaign',
  score: 0.94,
  timestamp: new Date().toISOString(),
  resolved: false,
};

const AGENT_STALL_EVENT: AnomalyEvent = {
  id: "stall-001",
  type: "agent_stall",
  severity: "high",
  message: "Inventory Agent not polling for 34s",
  score: 0.88,
  timestamp: new Date().toISOString(),
  resolved: false,
};

// --- Metric cards data ---
const IMPACT_METRICS = [
  { type: "Fraudulent Goals", rate: "94%", fp: "<2%", impact: "Prevents bulk fake orders" },
  { type: "Agent Stalls", rate: "100%", fp: "0%", impact: "99.9% uptime guarantee" },
  { type: "Inventory Issues", rate: "89%", fp: "<1%", impact: 'No "promised but unavailable"' },
  { type: "Qdrant Health", rate: "97%", fp: "0%", impact: "Always-available recommendations" },
];

const WORKFLOW_STEPS = [
  { num: 1, title: "DETECT", desc: "Qdrant semantic clustering flags outlier goal", icon: Eye },
  { num: 2, title: "INVESTIGATE", desc: '92% match to "iPhone bot" episode #47 · 23 requests from same /24 subnet', icon: Brain },
  { num: 3, title: "CLASSIFY", desc: "Fraud 95% confidence vs Legit surge 32%", icon: Cpu },
  { num: 4, title: "ACT", desc: "Rate limit IPs, CAPTCHA, notify fraud team", icon: Lock },
  { num: 5, title: "LEARN", desc: "Store fraud episode → future goals auto-blocked", icon: Database },
];

// --- Severity helpers ---
const severityColor = (s: AnomalyEvent["severity"]) =>
  s === "critical" ? "destructive" : s === "high" ? "destructive" : s === "medium" ? "secondary" : "outline";

const healthColor = (h: "healthy" | "degraded" | "down") =>
  h === "healthy" ? "text-green-500" : h === "degraded" ? "text-yellow-500" : "text-destructive";

// --- Component ---
export default function AnomalyDetection() {
  const [demoPhase, setDemoPhase] = useState<"normal" | "attack" | "learned">("normal");
  const [events, setEvents] = useState<AnomalyEvent[]>(() =>
    Array.from({ length: 6 }, (_, i) => generateNormalEvent(i))
  );
  const [health, setHealth] = useState<SystemHealth>({
    shopperAgent: "healthy",
    inventoryAgent: "healthy",
    qdrantLatency: 28,
    episodeSuccessRate: 0.91,
    openGoals: 3,
  });
  const [episodeCount, setEpisodeCount] = useState(127);
  const [fraudAccuracy, setFraudAccuracy] = useState(0.94);

  // Simulate attack
  const runDemo = useCallback(() => {
    // Phase 1: normal
    setDemoPhase("normal");
    setEvents(Array.from({ length: 6 }, (_, i) => generateNormalEvent(i)));
    setHealth({ shopperAgent: "healthy", inventoryAgent: "healthy", qdrantLatency: 28, episodeSuccessRate: 0.91, openGoals: 3 });

    // Phase 2: attack after 2s
    setTimeout(() => {
      setDemoPhase("attack");
      setEvents((prev) => [FRAUD_EVENT, AGENT_STALL_EVENT, ...prev.slice(0, 4)]);
      setHealth({ shopperAgent: "healthy", inventoryAgent: "degraded", qdrantLatency: 142, episodeSuccessRate: 0.78, openGoals: 12 });
    }, 2000);

    // Phase 3: learned after 5s
    setTimeout(() => {
      setDemoPhase("learned");
      setEvents((prev) =>
        prev.map((e) => (e.severity === "critical" || e.severity === "high" ? { ...e, resolved: true } : e))
      );
      setHealth({ shopperAgent: "healthy", inventoryAgent: "healthy", qdrantLatency: 31, episodeSuccessRate: 0.93, openGoals: 2 });
      setEpisodeCount((c) => c + 1);
      setFraudAccuracy(0.95);
    }, 5000);
  }, []);

  // Auto-run on mount
  useEffect(() => { runDemo(); }, [runDemo]);

  return (
    <div className="p-4 md:p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Shield className="h-6 w-6 text-primary" />
            Anomaly Detection
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Dual-layer detection: user behavior fraud + system health monitoring via Qdrant episodic memory
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={demoPhase === "attack" ? "destructive" : demoPhase === "learned" ? "default" : "secondary"} className="text-xs">
            {demoPhase === "normal" && "✅ Normal"}
            {demoPhase === "attack" && "🚨 Attack Detected"}
            {demoPhase === "learned" && "🧠 Learned & Blocked"}
          </Badge>
          <Button size="sm" variant="outline" onClick={runDemo}>
            <RotateCcw className="h-3 w-3 mr-1" /> Replay
          </Button>
        </div>
      </div>

      {/* System Health Bar */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <Card className="border-border">
          <CardContent className="p-3 text-center">
            <p className="text-xs text-muted-foreground">Shopper Agent</p>
            <p className={`text-sm font-bold ${healthColor(health.shopperAgent)}`}>
              {health.shopperAgent.toUpperCase()}
            </p>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="p-3 text-center">
            <p className="text-xs text-muted-foreground">Inventory Agent</p>
            <p className={`text-sm font-bold ${healthColor(health.inventoryAgent)}`}>
              {health.inventoryAgent.toUpperCase()}
            </p>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="p-3 text-center">
            <p className="text-xs text-muted-foreground">Qdrant Latency</p>
            <p className={`text-sm font-bold ${health.qdrantLatency > 100 ? "text-destructive" : "text-green-500"}`}>
              {health.qdrantLatency}ms
            </p>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="p-3 text-center">
            <p className="text-xs text-muted-foreground">Episode Success</p>
            <p className={`text-sm font-bold ${health.episodeSuccessRate < 0.8 ? "text-yellow-500" : "text-green-500"}`}>
              {(health.episodeSuccessRate * 100).toFixed(0)}%
            </p>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="p-3 text-center">
            <p className="text-xs text-muted-foreground">Open Goals</p>
            <p className={`text-sm font-bold ${health.openGoals > 10 ? "text-destructive" : "text-foreground"}`}>
              {health.openGoals}
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="live" className="space-y-4">
        <TabsList>
          <TabsTrigger value="live">Live Feed</TabsTrigger>
          <TabsTrigger value="workflow">Resolution Workflow</TabsTrigger>
          <TabsTrigger value="metrics">Impact Metrics</TabsTrigger>
          <TabsTrigger value="code">Implementation</TabsTrigger>
        </TabsList>

        {/* ─── Live Feed ─── */}
        <TabsContent value="live" className="space-y-4">
          <div className="grid md:grid-cols-3 gap-4">
            {/* Goal Stream */}
            <Card className="md:col-span-2 border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Activity className="h-4 w-4" /> Goal Stream
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {events.map((e) => (
                  <div
                    key={e.id}
                    className={`flex items-center justify-between p-2 rounded-lg text-sm border ${
                      e.severity === "critical"
                        ? "border-destructive bg-destructive/10"
                        : e.severity === "high"
                        ? "border-yellow-600 bg-yellow-950/20"
                        : "border-border bg-muted/30"
                    }`}
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      {e.severity === "critical" ? (
                        <ShieldAlert className="h-4 w-4 text-destructive shrink-0" />
                      ) : e.severity === "high" ? (
                        <AlertTriangle className="h-4 w-4 text-yellow-500 shrink-0" />
                      ) : (
                        <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                      )}
                      <span className="truncate">{e.message}</span>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <span className="text-xs text-muted-foreground">{e.score.toFixed(2)}</span>
                      <Badge variant={severityColor(e.severity)} className="text-[10px]">
                        {e.severity}
                      </Badge>
                      {e.resolved && (
                        <Badge variant="outline" className="text-[10px] text-green-500 border-green-600">
                          resolved
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Detection Stats */}
            <div className="space-y-4">
              <Card className="border-border">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Database className="h-4 w-4" /> Episodic Memory
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold">{episodeCount}</p>
                  <p className="text-xs text-muted-foreground">fraud episodes stored</p>
                  <div className="mt-3">
                    <p className="text-xs text-muted-foreground mb-1">Fraud Accuracy</p>
                    <Progress value={fraudAccuracy * 100} className="h-2" />
                    <p className="text-xs text-right mt-1">{(fraudAccuracy * 100).toFixed(0)}%</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-border">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" /> Learning Progress
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-xs">
                  {[
                    { run: "Run 1", episodes: 0, accuracy: "62%", status: "Cold start" },
                    { run: "Run 2", episodes: 15, accuracy: "89%", status: "Learning" },
                    { run: "Run 3", episodes: 127, accuracy: "94%", status: "Optimized" },
                  ].map((r) => (
                    <div key={r.run} className="flex items-center justify-between">
                      <span className="text-muted-foreground">{r.run}</span>
                      <span>{r.episodes} eps</span>
                      <Badge variant="outline" className="text-[10px]">{r.accuracy}</Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Qdrant Queries */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Server className="h-4 w-4" /> Qdrant Real-Time Queries
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-3 font-mono text-xs">
                <div className="bg-muted/50 p-3 rounded-lg">
                  <p className="text-muted-foreground mb-1"># Goal clustering</p>
                  <p>recent_goals = qdrant.search(</p>
                  <p className="pl-4">collection="goals",</p>
                  <p className="pl-4">filter={`{"created_at": ">now-5m"}`},</p>
                  <p className="pl-4">limit=50</p>
                  <p>)</p>
                  <p className="text-green-500 mt-1">→ {health.openGoals} open goals</p>
                </div>
                <div className="bg-muted/50 p-3 rounded-lg">
                  <p className="text-muted-foreground mb-1"># Success rate</p>
                  <p>success = qdrant.count(</p>
                  <p className="pl-4">collection="episodes",</p>
                  <p className="pl-4">filter={`{"success": True}`}</p>
                  <p>)</p>
                  <p className="text-green-500 mt-1">→ {(health.episodeSuccessRate * 100).toFixed(0)}% rate</p>
                </div>
                <div className="bg-muted/50 p-3 rounded-lg">
                  <p className="text-muted-foreground mb-1"># Anomaly score</p>
                  <p>score = len([g for g in</p>
                  <p className="pl-4">recent if g.score {">"} 0.95])</p>
                  <p className="pl-4">/ total</p>
                  <p className={`mt-1 ${demoPhase === "attack" ? "text-destructive" : "text-green-500"}`}>
                    → {demoPhase === "attack" ? "0.94 🚨 ANOMALY" : "0.12 ✅ normal"}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── Resolution Workflow ─── */}
        <TabsContent value="workflow" className="space-y-4">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="text-sm">Agentic Anomaly Resolution Workflow</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col md:flex-row items-stretch gap-2">
                {WORKFLOW_STEPS.map((step, i) => (
                  <div key={step.num} className="flex items-center gap-2 flex-1">
                    <div className="bg-muted/50 border border-border rounded-xl p-4 flex-1 text-center">
                      <step.icon className="h-6 w-6 mx-auto mb-2 text-primary" />
                      <p className="font-bold text-sm">{step.num}. {step.title}</p>
                      <p className="text-xs text-muted-foreground mt-1">{step.desc}</p>
                    </div>
                    {i < WORKFLOW_STEPS.length - 1 && (
                      <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0 hidden md:block" />
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Demo Story */}
          <div className="grid md:grid-cols-3 gap-4">
            <Card className="border-green-800/50 bg-green-950/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500" /> Screen 1: Normal
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-xs">
                <div className="bg-muted/30 p-2 rounded">🛒 camping gear, Zurich</div>
                <div className="bg-muted/30 p-2 rounded">👟 running shoes size 42</div>
                <div className="bg-muted/30 p-2 rounded">🚼 baby stroller under 300</div>
                <p className="text-muted-foreground mt-2">All goals {"<"} 0.7 anomaly score ✅</p>
              </CardContent>
            </Card>

            <Card className="border-destructive/50 bg-destructive/5">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <ShieldAlert className="h-4 w-4 text-destructive" /> Screen 2: Attack
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-xs">
                <div className="bg-destructive/10 border border-destructive/30 p-2 rounded">📱 iPhone 15 Pro Max</div>
                <div className="bg-destructive/10 border border-destructive/30 p-2 rounded">📱 iPhone 15 Pro Max</div>
                <div className="bg-destructive/10 border border-destructive/30 p-2 rounded">📱 iPhone 15 Pro Max</div>
                <p className="text-muted-foreground">... 44 more in 90s</p>
                <p className="text-destructive text-[10px]">Score: 0.94 · IP: 23 from 192.168.1.0/24</p>
                <p className="text-green-500 text-[10px]">→ Auto-blocked + fraud alert sent</p>
              </CardContent>
            </Card>

            <Card className="border-primary/30 bg-primary/5">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Brain className="h-4 w-4 text-primary" /> Screen 3: Learned
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-xs">
                <div className="bg-muted/30 p-2 rounded border-l-2 border-green-500">✅ "iPhone bot #238" stored</div>
                <div className="bg-muted/30 p-2 rounded border-l-2 border-green-500">✅ Future goals auto-flagged</div>
                <div className="bg-muted/30 p-2 rounded">Fraud accuracy: <span className="text-green-500">94%</span> (127/135)</div>
                <p className="text-muted-foreground mt-2">System blocks similar attacks instantly</p>
              </CardContent>
            </Card>
          </div>

          {/* Pitch */}
          <Card className="border-border bg-muted/30">
            <CardContent className="p-6 text-center">
              <p className="text-lg italic text-muted-foreground">
                "Built-in anomaly detection uses the same Qdrant memory that powers recommendations — fraud patterns, agent stalls, and system issues get stored as episodes and auto-blocked next time."
              </p>
              <p className="text-xs text-muted-foreground mt-2">— Making the system production-grade resilient</p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── Impact Metrics ─── */}
        <TabsContent value="metrics">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <HeartPulse className="h-4 w-4" /> Business Impact Metrics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Anomaly Type</TableHead>
                    <TableHead>Detection Rate</TableHead>
                    <TableHead>False Positives</TableHead>
                    <TableHead>Business Impact</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {IMPACT_METRICS.map((m) => (
                    <TableRow key={m.type}>
                      <TableCell className="font-medium">{m.type}</TableCell>
                      <TableCell className="text-green-500 font-bold">{m.rate}</TableCell>
                      <TableCell>{m.fp}</TableCell>
                      <TableCell className="text-muted-foreground">{m.impact}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Killer Metric */}
          <Card className="mt-4 border-primary/50 bg-primary/5">
            <CardContent className="p-6 text-center">
              <p className="text-5xl font-black text-primary">94%</p>
              <p className="text-sm text-muted-foreground mt-1">fraud detection rate with {"<"}2% false positives</p>
              <p className="text-xs text-muted-foreground mt-2">
                Supported by Qdrant episodic retrieval lifting conversion +27%
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── Code ─── */}
        <TabsContent value="code">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <Zap className="h-4 w-4" /> Anomaly Detector Agent (runs every 30s)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted/50 p-4 rounded-lg text-xs overflow-x-auto font-mono leading-relaxed">
{`def detect_anomalies():
    # 1. Goal clustering anomalies
    recent_goals = qdrant.scroll("goals", limit=100, with_vectors=True)
    clusters = dbscan_cluster([g.vector for g in recent_goals], eps=0.1)
    outliers = [g for g in recent_goals if g.cluster == -1]

    # 2. Agent health
    open_goals = qdrant.count("goals", {"status": "open"})
    if open_goals > 10:
        alert("Inventory Agent stalled")

    # 3. Success rate degradation
    success_rate = qdrant.count("episodes", {"success": True}) / total
    if success_rate < 0.7:
        alert("Recommendation quality degrading")

    # 4. Store confirmed anomalies as episodes
    if len(outliers) > threshold:
        embed_and_store("fraudulent_goal_cluster", outliers)
        # Future matching goals auto-blocked`}
              </pre>
            </CardContent>
          </Card>

          {/* Qdrant queries */}
          <Card className="mt-4 border-border">
            <CardHeader>
              <CardTitle className="text-sm">Qdrant-Powered Detection Queries</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <pre className="bg-muted/50 p-3 rounded-lg text-xs font-mono">
{`# Real-time outlier detection on incoming goals
recent_goals = qdrant.search(
    collection="goals",
    query_vector=embed(suspicious_goal),
    filter={"created_at": ">now-5m"},
    limit=50
)
anomaly_score = len([g for g in recent_goals if g.score > 0.95]) / 50
if anomaly_score > 0.8:  # 80% identical goals
    flag_as_fraud()`}
              </pre>
              <pre className="bg-muted/50 p-3 rounded-lg text-xs font-mono">
{`# Agent heartbeat via payload counts
open_goals_5m = qdrant.count(
    collection="goals",
    filter={"status": "open", "created_at": ">now-5m"}
)
if open_goals_5m > 10:
    alert("Inventory Agent stalled")`}
              </pre>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
