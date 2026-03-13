import { useLocation, Link } from "react-router-dom";
import { Home, MessageSquare, Package, MapPin, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

const MOBILE_TABS = [
  { to: "/", label: "Home", icon: Home, end: true },
  { to: "/chat", label: "Chat", icon: MessageSquare },
  { to: "/dashboard", label: "Dashboard", icon: Package },
  { to: "/livemap", label: "Map", icon: MapPin },
  { to: "/settings", label: "Settings", icon: Settings },
] as const;

export function MobileBottomNav() {
  const location = useLocation();

  const isActive = (path: string, end?: boolean) =>
    end ? location.pathname === path : location.pathname.startsWith(path);

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-border bg-card/95 backdrop-blur-lg md:hidden safe-area-pb">
      <div className="flex items-center justify-around h-14">
        {MOBILE_TABS.map((tab) => {
          const active = isActive(tab.to, tab.end);
          return (
            <Link
              key={tab.to}
              to={tab.to}
              className={cn(
                "flex flex-col items-center justify-center gap-0.5 flex-1 h-full transition-colors",
                active ? "text-primary" : "text-muted-foreground"
              )}
            >
              <tab.icon className={cn("w-5 h-5", active && "text-primary")} />
              <span className="text-[10px] font-medium">{tab.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
