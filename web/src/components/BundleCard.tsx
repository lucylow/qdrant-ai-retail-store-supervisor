import { ShoppingBag, Clock, CheckCircle } from "lucide-react";
import type { Product } from "@/lib/api";
import { cn } from "@/lib/utils";

interface BundleCardProps {
  products: Product[];
  totalPrice?: number;
  currency?: string;
  eta?: string;
  confidence?: number;
  goalText?: string;
}

export function BundleCard({ products, totalPrice, currency = "CHF", eta, confidence, goalText }: BundleCardProps) {
  return (
    <div className="rounded-xl border border-border bg-card p-5 space-y-4 hover:border-primary/30 transition-colors">
      {goalText && (
        <p className="text-sm text-muted-foreground italic">"{goalText}"</p>
      )}
      <div className="space-y-2">
        {products.map((p, i) => (
          <div key={p.id || i} className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <ShoppingBag className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
              <span className="text-sm truncate">{p.name || p.title}</span>
            </div>
            {p.price !== undefined && (
              <span className="text-sm font-medium text-primary shrink-0">{currency} {p.price}</span>
            )}
          </div>
        ))}
      </div>
      <div className="flex items-center justify-between pt-2 border-t border-border">
        <div className="flex items-center gap-3">
          {totalPrice !== undefined && (
            <span className="font-bold text-lg text-gradient">{currency} {totalPrice}</span>
          )}
          {eta && (
            <span className="flex items-center gap-1 text-xs text-muted-foreground">
              <Clock className="w-3 h-3" /> {eta}
            </span>
          )}
        </div>
        {confidence !== undefined && (
          <div className="flex items-center gap-2">
            <div className="w-20 h-1.5 rounded-full bg-muted overflow-hidden">
              <div
                className={cn("h-full rounded-full transition-all", confidence > 0.7 ? "bg-status-online" : confidence > 0.4 ? "bg-status-warning" : "bg-status-error")}
                style={{ width: `${confidence * 100}%` }}
              />
            </div>
            <CheckCircle className="w-3.5 h-3.5 text-status-online" />
            <span className="text-xs text-muted-foreground">{(confidence * 100).toFixed(0)}%</span>
          </div>
        )}
      </div>
    </div>
  );
}
