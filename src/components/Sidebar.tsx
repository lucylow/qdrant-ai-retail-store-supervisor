import { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard, MessageSquare, Target, BookOpen,
  ShoppingBag, Activity, BarChart3, PlayCircle,
  Settings, Award, Menu, X, Database, Zap, Layers, Shield, Sparkles, Brain, Cloud, FolderOpen, ShieldCheck, Code2,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { to: "/", label: "Home", icon: Zap },
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/chat", label: "Chat", icon: MessageSquare },
  { to: "/goals", label: "Goals", icon: Target },
  { to: "/episodes", label: "Memory", icon: BookOpen },
  { to: "/products", label: "Products", icon: ShoppingBag },
  { to: "/agents", label: "Agents", icon: Activity },
  { to: "/metrics", label: "Metrics", icon: BarChart3 },
  { to: "/scale", label: "Scale v6", icon: Layers },
  { to: "/qdrant", label: "Qdrant 🏆", icon: Database },
  { to: "/qdrant-cloud", label: "Qdrant Cloud ☁️", icon: Cloud },
  { to: "/enterprise", label: "Enterprise v7", icon: Shield },
  { to: "/genai", label: "GenAI v8 ✨", icon: Sparkles },
  { to: "/evolve", label: "Evolve v9 🧠", icon: Brain },
  { to: "/datasets", label: "Datasets v11 📊", icon: FolderOpen },
  { to: "/gdpr", label: "GDPR v12 🇪🇺", icon: ShieldCheck },
  { to: "/architecture", label: "Architecture v13 🏗️", icon: Code2 },
  { to: "/demo", label: "Demo", icon: PlayCircle },
  { to: "/hackathon", label: "Hackathon", icon: Award },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 h-full z-50 flex flex-col bg-sidebar border-r border-sidebar-border transition-all duration-300",
        collapsed ? "w-16" : "w-56"
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-sidebar-border h-16 shrink-0">
        {!collapsed && (
          <div className="flex items-center gap-2 min-w-0">
            <Database className="w-5 h-5 text-primary shrink-0" />
            <span className="text-sm font-bold text-foreground truncate">Store Supervisor</span>
          </div>
        )}
        {collapsed && <Database className="w-5 h-5 text-primary mx-auto" />}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className={cn(
            "rounded-md p-1.5 hover:bg-sidebar-accent transition-colors text-sidebar-foreground shrink-0",
            collapsed && "mx-auto"
          )}
        >
          {collapsed ? <Menu className="w-4 h-4" /> : <X className="w-4 h-4" />}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto p-2 space-y-0.5 scrollbar-thin">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => {
          const active =
            to === "/" ? location.pathname === "/" : location.pathname.startsWith(to);
          const isQdrant = to === "/qdrant";
          return (
            <NavLink
              key={to}
              to={to}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all",
                active
                  ? "bg-primary/15 text-primary border border-primary/25"
                  : isQdrant
                  ? "text-accent hover:bg-sidebar-accent hover:text-accent border border-transparent hover:border-accent/20"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              )}
              title={collapsed ? label : undefined}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {!collapsed && (
                <span className="flex-1 truncate">{label}</span>
              )}
              {!collapsed && to === "/scale" && (
                <span className="text-xs px-1.5 py-0.5 rounded-full bg-primary/15 text-primary font-mono">v6</span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-sidebar-border shrink-0">
        {!collapsed ? (
          <div className="text-xs text-sidebar-foreground opacity-50">
            <div className="font-medium">GenAI Zurich 2026</div>
            <div>Qdrant Challenge</div>
          </div>
        ) : (
          <Award className="w-4 h-4 text-sidebar-foreground opacity-50 mx-auto" />
        )}
      </div>
    </aside>
  );
}
