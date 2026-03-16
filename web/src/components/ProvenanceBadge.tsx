import { cn } from "@/lib/utils";

interface ProvenanceBadgeProps {
  index: number;
  text?: string;
  source?: string;
  score?: number;
}

export function ProvenanceBadge({ index, text, source, score }: ProvenanceBadgeProps) {
  return (
    <span
      className="inline-flex items-center cursor-pointer group relative"
      title={text || source}
    >
      <span className="text-xs font-mono bg-primary/20 text-primary border border-primary/30 rounded px-1 py-0.5 hover:bg-primary/30 transition-colors">
        [{index}]
      </span>
      {(text || source) && (
        <span className={cn(
          "absolute bottom-full left-0 z-50 w-64 p-2 rounded-lg bg-popover border border-border text-xs text-popover-foreground shadow-xl",
          "hidden group-hover:block"
        )}>
          {source && <div className="font-medium text-primary mb-1">{source}</div>}
          {text && <div className="text-muted-foreground line-clamp-3">{text}</div>}
          {score !== undefined && <div className="mt-1 text-status-info">Score: {(score * 100).toFixed(0)}%</div>}
        </span>
      )}
    </span>
  );
}
