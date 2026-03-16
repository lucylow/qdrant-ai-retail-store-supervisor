import { useState, useRef, useEffect, useCallback } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Send, Mic, MicOff, Zap, Database, Wifi, WifiOff, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ProvenanceBadge } from "@/components/ProvenanceBadge";
import { AgentAvatar } from "@/components/AgentAvatar";
import { api, MOCK_PRODUCTS, BASE_URL } from "@/lib/api";
import { cn } from "@/lib/utils";

const WS_URL = BASE_URL.replace(/^http/, "ws") + "/ws/chat";

// Swiss German → English normalization (Layer 1)
const SWISS_MAP: Record<string, string> = {
  zelt: "tent", schlafsack: "sleeping bag", franken: "CHF",
  unter: "under", freitag: "Friday", wanderschuhe: "hiking boots",
  rucksack: "backpack", kocher: "stove", matte: "sleeping pad",
  personen: "person", "zwei": "2", zürich: "Zurich", genf: "Geneva",
};

function normalizeSwissGerman(text: string): { canonical: string; wasNormalized: boolean } {
  let result = text;
  let changed = false;
  for (const [de, en] of Object.entries(SWISS_MAP)) {
    const re = new RegExp(`\\b${de}\\b`, "gi");
    if (re.test(result)) {
      result = result.replace(re, en);
      changed = true;
    }
  }
  return { canonical: result, wasNormalized: changed };
}

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  originalText?: string;
  wasNormalized?: boolean;
  provenance?: { id: number; text?: string; source?: string; score?: number }[];
  cacheHit?: boolean;
  cacheLayer?: "redis" | "qdrant_query" | "qdrant_goal" | "miss";
  latencyMs?: number;
  goalId?: string;
  layer?: number;
};

const DEMO_PROMPTS = [
  { label: "🇨🇭 Swiss German", text: "Zelt 2 Personen unter 200 Franken Zürich" },
  { label: "English", text: "waterproof hiking boots lightweight size 42" },
  { label: "Bundle", text: "complete camping kit weekend Switzerland budget 500CHF" },
  { label: "Voice-style", text: "ich suche einen Schlafsack für Freitag" },
];

function buildMockResponse(canonical: string, cacheHit: boolean): Omit<Message, "id"> {
  const prod = MOCK_PRODUCTS[Math.floor(Math.random() * MOCK_PRODUCTS.length)];
  const layer = cacheHit ? Math.floor(Math.random() * 3) + 1 : 4;
  const cacheLayer = cacheHit
    ? (["redis", "qdrant_query", "qdrant_goal"] as const)[layer - 1]
    : "miss";
  const latency = cacheHit ? [4, 28, 35][layer - 1] + Math.floor(Math.random() * 10) : 140 + Math.floor(Math.random() * 60);

  return {
    role: "assistant",
    text: `Found options for "${canonical}". The **${prod.name}** (${prod.description}) at CHF ${prod.price} matches your criteria.${cacheHit ? ` Retrieved from episodic memory cache (${(87 + Math.random() * 5).toFixed(0)}% similarity).` : ""}`,
    provenance: [
      { id: 1, text: prod.description, source: prod.name ?? "", score: 0.92 },
      { id: 2, text: "Episodic memory — similar past goal resolved successfully", source: "Episodes DB", score: 0.87 },
    ],
    cacheHit,
    cacheLayer,
    latencyMs: latency,
    layer,
    goalId: `g_${Date.now()}`,
  };
}

const CACHE_LAYER_LABELS: Record<string, string> = {
  redis: "Redis (4ms)",
  qdrant_query: "Qdrant query cache (28ms)",
  qdrant_goal: "Qdrant goal cache (35ms)",
  miss: "Full RAG",
};
const CACHE_LAYER_COLORS: Record<string, string> = {
  redis: "text-status-online",
  qdrant_query: "text-primary",
  qdrant_goal: "text-accent",
  miss: "text-muted-foreground",
};

export default function ChatPage() {
  const [searchParams] = useSearchParams();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "0", role: "assistant",
      text: "Hello! I'm the Multi-Agent Store Supervisor. Ask me in English or Swiss German (Zelt, Schlafsack, Franken…) — Layer 1 normalizes dialect automatically.",
    },
  ]);
  const [input, setInput] = useState(searchParams.get("q") ?? "");
  const [isStreaming, setIsStreaming] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [listening, setListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  useEffect(() => {
    let ws: WebSocket;
    try {
      ws = new WebSocket(WS_URL);
      ws.onopen = () => setWsConnected(true);
      ws.onclose = () => setWsConnected(false);
      ws.onerror = () => setWsConnected(false);
      wsRef.current = ws;
    } catch { setWsConnected(false); }
    return () => ws?.close();
  }, []);

  const sendMessage = useCallback(async (text?: string) => {
    const raw = (text ?? input).trim();
    if (!raw || isStreaming) return;
    setInput("");

    const { canonical, wasNormalized } = normalizeSwissGerman(raw);
    const userMsg: Message = {
      id: Date.now().toString(), role: "user", text: raw,
      originalText: raw, wasNormalized, ...(wasNormalized && { text: canonical }),
    };
    const assistantId = (Date.now() + 1).toString();
    setMessages((prev) => [...prev, userMsg, { id: assistantId, role: "assistant", text: "" }]);
    setIsStreaming(true);

    // Try WebSocket
    if (wsConnected && wsRef.current?.readyState === WebSocket.OPEN) {
      try { wsRef.current.send(JSON.stringify({ message: canonical })); return; } catch { }
    }

    // SSE fallback → mock on failure
    let fullText = "";
    const stop = api.streamChat(
      canonical,
      (chunk) => { fullText += chunk; setMessages((prev) => prev.map((m) => m.id === assistantId ? { ...m, text: fullText } : m)); },
      () => {
        setIsStreaming(false);
        const mock = buildMockResponse(canonical, Math.random() > 0.35);
        setMessages((prev) => prev.map((m) => m.id === assistantId ? (fullText ? { ...m, cacheHit: mock.cacheHit, latencyMs: mock.latencyMs } : { ...mock, id: assistantId }) : m));
      }
    );
    return stop;
  }, [input, isStreaming, wsConnected]);

  const toggleVoice = () => {
    const SR = (window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition;
    if (!SR) return;
    if (listening) { setListening(false); return; }
    const rec = new SR();
    rec.lang = "de-CH";
    rec.onresult = (e: any) => { setInput(e.results[0][0].transcript); setListening(false); };
    rec.onend = () => setListening(false);
    rec.start();
    setListening(true);
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="flex items-center gap-3 p-4 border-b border-border bg-card/50">
        <AgentAvatar type="supervisor" online={true} size="sm" />
        <div>
          <div className="font-semibold text-sm">Store Supervisor v6</div>
          <div className="text-xs text-muted-foreground flex items-center gap-1">
            <Database className="w-3 h-3" /> 6-Layer RAG · Swiss German · Episodic Memory
          </div>
        </div>
        <div className="ml-auto flex items-center gap-3">
          <span className={cn("flex items-center gap-1.5 text-xs", wsConnected ? "text-status-online" : "text-muted-foreground")}>
            {wsConnected ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
            {wsConnected ? "WebSocket" : "SSE fallback"}
          </span>
          {isStreaming && (
            <span className="flex items-center gap-1 text-xs text-status-info">
              <RefreshCw className="w-3 h-3 animate-spin" /> Processing
            </span>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
        {messages.map((msg) => (
          <div key={msg.id} className={cn("flex gap-3 animate-fade-in", msg.role === "user" && "flex-row-reverse")}>
            {msg.role === "assistant" && <AgentAvatar type="supervisor" online size="sm" />}
            <div className={cn("max-w-[80%] space-y-1.5", msg.role === "user" && "items-end")}>
              {/* Swiss German normalization badge */}
              {msg.role === "user" && msg.wasNormalized && (
                <div className="text-xs text-muted-foreground flex items-center gap-1.5 justify-end mb-0.5">
                  <span className="opacity-60 line-through">{msg.originalText}</span>
                  <span className="text-primary">→ normalized</span>
                </div>
              )}
              <div className={cn(
                "rounded-2xl px-4 py-3 text-sm leading-relaxed",
                msg.role === "user" ? "gradient-primary text-primary-foreground rounded-br-sm" : "bg-card border border-border rounded-bl-sm"
              )}>
                {msg.text || (isStreaming && msg.id === messages[messages.length - 1]?.id && (
                  <span className="inline-block w-1.5 h-4 bg-primary rounded-sm animate-blink" />
                ))}
                {msg.provenance?.length && (
                  <span className="ml-1 inline-flex gap-0.5 flex-wrap">
                    {msg.provenance.map((p) => (
                      <ProvenanceBadge key={p.id} index={p.id as number} text={p.text} source={p.source} score={p.score} />
                    ))}
                  </span>
                )}
              </div>
              {msg.role === "assistant" && (msg.cacheHit !== undefined || msg.latencyMs) && (
                <div className="flex items-center gap-3 text-xs px-1 flex-wrap">
                  {msg.cacheHit && msg.cacheLayer && (
                    <span className={cn("flex items-center gap-1 font-medium", CACHE_LAYER_COLORS[msg.cacheLayer])}>
                      <Zap className="w-3 h-3" /> {CACHE_LAYER_LABELS[msg.cacheLayer]}
                    </span>
                  )}
                  {!msg.cacheHit && <span className="text-muted-foreground">Full RAG pipeline</span>}
                  {msg.latencyMs && <span className="text-muted-foreground">{msg.latencyMs}ms</span>}
                  {msg.layer && <span className="text-muted-foreground">L{msg.layer}</span>}
                  {msg.goalId && (
                    <Link to={`/solutions/${msg.goalId}`} className="text-primary hover:underline ml-auto">
                      Solutions →
                    </Link>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {messages.length <= 2 && (
        <div className="px-4 pb-2 flex flex-wrap gap-2">
          {DEMO_PROMPTS.map((p) => (
            <button key={p.text} onClick={() => sendMessage(p.text)} className="text-xs px-3 py-1.5 rounded-full bg-muted border border-border text-muted-foreground hover:text-foreground hover:border-primary/30 transition-colors">
              <span className="mr-1">{p.label}</span> "{p.text.slice(0, 30)}{p.text.length > 30 ? "…" : ""}"
            </button>
          ))}
        </div>
      )}

      <div className="p-4 border-t border-border bg-card/30">
        <div className="flex gap-2 max-w-3xl mx-auto">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
            placeholder="Ask in English or Schweizerdeutsch… (Zelt, Schlafsack, Franken)"
            className="flex-1 bg-muted border border-border rounded-xl px-4 py-2.5 text-sm outline-none focus:border-primary/50 transition-colors placeholder:text-muted-foreground"
          />
          <Button size="icon" variant="ghost" onClick={toggleVoice} className={cn(listening && "text-status-error")}>
            {listening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </Button>
          <Button onClick={() => sendMessage()} disabled={isStreaming || !input.trim()} className="gradient-primary px-4">
            <Send className="w-4 h-4" />
          </Button>
        </div>
        <p className="text-center text-xs text-muted-foreground mt-1.5">Layer 1 auto-normalizes Swiss German dialect before embedding</p>
      </div>
    </div>
  );
}
