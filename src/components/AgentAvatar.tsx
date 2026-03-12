import { cn } from "@/lib/utils";

type AgentType = "shopper" | "inventory" | "pricing" | "marketing" | "supervisor";

const AGENT_CONFIG: Record<AgentType, { emoji: string; label: string; color: string }> = {
  shopper: { emoji: "👤", label: "Shopper", color: "text-primary" },
  inventory: { emoji: "📦", label: "Inventory", color: "text-accent" },
  pricing: { emoji: "💰", label: "Pricing", color: "text-status-warning" },
  marketing: { emoji: "📣", label: "Marketing", color: "text-status-info" },
  supervisor: { emoji: "🤖", label: "Supervisor", color: "text-status-online" },
};

interface AgentAvatarProps {
  type: AgentType;
  online?: boolean;
  size?: "sm" | "md" | "lg";
}

export function AgentAvatar({ type, online = true, size = "md" }: AgentAvatarProps) {
  const cfg = AGENT_CONFIG[type] || AGENT_CONFIG.shopper;
  const sizeClasses = { sm: "w-8 h-8 text-lg", md: "w-10 h-10 text-xl", lg: "w-14 h-14 text-3xl" };

  return (
    <div className="relative inline-flex flex-col items-center">
      <div className={cn("rounded-xl bg-muted border border-border flex items-center justify-center", sizeClasses[size])}>
        <span>{cfg.emoji}</span>
      </div>
      {online !== undefined && (
        <span
          className={cn(
            "absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-background",
            online ? "bg-status-online animate-pulse-glow" : "bg-muted-foreground"
          )}
        />
      )}
    </div>
  );
}
