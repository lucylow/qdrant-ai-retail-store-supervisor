import { TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: number; // positive = up
  icon?: React.ReactNode;
  description?: string;
  highlight?: boolean;
}

export function MetricCard({ label, value, unit, trend, icon, description, highlight }: MetricCardProps) {
  return (
    <div className={cn(
      "rounded-xl border border-border bg-card p-5 flex flex-col gap-3 transition-all hover:border-primary/30",
      highlight && "border-primary/40 glow-primary"
    )}>
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground font-medium">{label}</span>
        {icon && <span className="text-muted-foreground">{icon}</span>}
      </div>
      <div className="flex items-end gap-2">
        <span className={cn("text-3xl font-bold tracking-tight", highlight && "text-gradient")}>
          {value}
        </span>
        {unit && <span className="text-muted-foreground text-sm mb-1">{unit}</span>}
        {trend !== undefined && (
          <span className={cn("flex items-center text-xs font-medium mb-1 ml-auto", trend >= 0 ? "text-status-online" : "text-status-error")}>
            {trend >= 0 ? <TrendingUp className="w-3 h-3 mr-0.5" /> : <TrendingDown className="w-3 h-3 mr-0.5" />}
            {Math.abs(trend)}%
          </span>
        )}
      </div>
      {description && <p className="text-xs text-muted-foreground">{description}</p>}
    </div>
  );
}
