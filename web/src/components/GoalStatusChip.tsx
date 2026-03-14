import { cn } from "@/lib/utils";

type GoalStatus = "open" | "pending" | "fulfilled" | "failed";

const STATUS_CONFIG: Record<GoalStatus, { label: string; classes: string }> = {
  open: { label: "Open", classes: "bg-status-info/15 text-status-info border-status-info/30" },
  pending: { label: "Pending", classes: "bg-status-warning/15 text-status-warning border-status-warning/30" },
  fulfilled: { label: "Fulfilled", classes: "bg-status-online/15 text-status-online border-status-online/30" },
  failed: { label: "Failed", classes: "bg-status-error/15 text-status-error border-status-error/30" },
};

export function GoalStatusChip({ status }: { status: GoalStatus }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.open;
  return (
    <span className={cn("inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border", cfg.classes)}>
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5" />
      {cfg.label}
    </span>
  );
}
