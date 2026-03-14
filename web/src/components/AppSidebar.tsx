import {
  Home, MessageSquare, BarChart3, Settings, Database,
  ShoppingCart, Package, Clock, CreditCard, Brain,
  Wrench, ChevronDown, AlertCircle, MapPin, Search,
  Calendar, TrendingUp, Shield, Zap, Eye,
} from "lucide-react";
import { NavLink } from "@/components/NavLink";
import { useLocation } from "react-router-dom";
import { useState } from "react";
import { cn } from "@/lib/utils";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
  useSidebar,
} from "@/components/ui/sidebar";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

// ── Navigation Structure ─────────────────────────────────────────────────────
type NavItem = {
  to: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number | string;
  badgeColor?: string;
  end?: boolean;
};

type NavGroup = {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  items: NavItem[];
  defaultOpen?: boolean;
};

const TOP_ITEMS: NavItem[] = [
  { to: "/", label: "Dashboard", icon: Home, end: true },
  { to: "/chat", label: "Chat", icon: MessageSquare },
];

const NAV_GROUPS: NavGroup[] = [
  {
    label: "Orders",
    icon: ShoppingCart,
    defaultOpen: false,
    items: [
      { to: "/dashboard?tab=overview", label: "All Orders", icon: ShoppingCart },
      { to: "/dashboard?tab=agents", label: "Pickup Pending", icon: Clock, badge: 23, badgeColor: "bg-status-warning/20 text-status-warning" },
      { to: "/dashboard?tab=routing", label: "TWINT Payments", icon: CreditCard },
    ],
  },
  {
    label: "Inventory",
    icon: Package,
    defaultOpen: false,
    items: [
      { to: "/dashboard?tab=collections", label: "Stock Levels", icon: Package, badge: 12, badgeColor: "bg-status-error/20 text-status-error" },
      { to: "/dashboard?tab=analytics", label: "Holiday Forecasts", icon: Calendar },
      { to: "/dashboard?tab=anomaly", label: "Anomaly Detection", icon: AlertCircle },
    ],
  },
  {
    label: "Schedule",
    icon: Clock,
    defaultOpen: false,
    items: [
      { to: "/livemap", label: "Live Map", icon: MapPin },
      { to: "/store-map", label: "Store Map", icon: MapPin },
    ],
  },
  {
    label: "AI Agents",
    icon: Brain,
    defaultOpen: false,
    items: [
      { to: "/dashboard?tab=agents", label: "Agent Status", icon: Brain },
      { to: "/dashboard?tab=models", label: "AI Models", icon: Zap },
      { to: "/dashboard?tab=search", label: "Advanced Search", icon: Search },
      { to: "/dashboard?tab=mcp", label: "MCP Tools", icon: Wrench },
      { to: "/visual-search", label: "Visual Search", icon: Eye },
    ],
  },
  {
    label: "Analytics",
    icon: BarChart3,
    defaultOpen: false,
    items: [
      { to: "/dashboard?tab=metrics", label: "Metrics", icon: TrendingUp },
      { to: "/dashboard?tab=rag", label: "RAG Comparison", icon: Database },
      { to: "/dashboard?tab=cache", label: "Semantic Cache", icon: Zap },
    ],
  },
];

const BOTTOM_ITEMS: NavItem[] = [
  { to: "/settings", label: "Settings", icon: Settings },
];

// ── Collapsible Nav Group ────────────────────────────────────────────────────
function CollapsibleNavGroup({ group, collapsed }: { group: NavGroup; collapsed: boolean }) {
  const location = useLocation();
  const isGroupActive = group.items.some((item) => {
    if (item.to.includes("?")) {
      return location.pathname + location.search === item.to;
    }
    return location.pathname === item.to;
  });
  const [open, setOpen] = useState(group.defaultOpen || isGroupActive);

  if (collapsed) {
    // In collapsed mode, show only the first item's icon
    return (
      <SidebarMenuItem>
        <SidebarMenuButton asChild isActive={isGroupActive}>
          <NavLink
            to={group.items[0]?.to || "/"}
            className="hover:bg-sidebar-accent/50"
            activeClassName="bg-primary/15 text-primary font-medium"
          >
            <group.icon className="mr-2 h-4 w-4" />
          </NavLink>
        </SidebarMenuButton>
      </SidebarMenuItem>
    );
  }

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <CollapsibleTrigger className="flex items-center w-full px-3 py-2 text-xs font-semibold uppercase tracking-wider text-sidebar-foreground/50 hover:text-sidebar-foreground/80 transition-colors">
        <group.icon className="h-3.5 w-3.5 mr-2 shrink-0" />
        <span className="flex-1 text-left">{group.label}</span>
        {group.items.some((i) => i.badge) && !open && (
          <span className="w-2 h-2 rounded-full bg-status-warning mr-1.5 shrink-0" />
        )}
        <ChevronDown className={cn("h-3 w-3 transition-transform shrink-0", open && "rotate-180")} />
      </CollapsibleTrigger>
      <CollapsibleContent>
        <SidebarMenu className="pl-2">
          {group.items.map((item) => (
            <SidebarMenuItem key={item.to + item.label}>
              <SidebarMenuButton asChild isActive={
                item.to.includes("?")
                  ? location.pathname + location.search === item.to
                  : location.pathname === item.to
              }>
                <NavLink
                  to={item.to}
                  className="hover:bg-sidebar-accent/50 flex items-center"
                  activeClassName="bg-primary/15 text-primary font-medium"
                >
                  <item.icon className="mr-2 h-3.5 w-3.5" />
                  <span className="flex-1 truncate text-sm">{item.label}</span>
                  {item.badge && (
                    <span className={cn(
                      "text-[10px] font-semibold px-1.5 py-0.5 rounded-full ml-auto",
                      item.badgeColor || "bg-primary/20 text-primary"
                    )}>
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </CollapsibleContent>
    </Collapsible>
  );
}

// ── Main Sidebar ─────────────────────────────────────────────────────────────
export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const location = useLocation();

  const isActive = (path: string, end?: boolean) => {
    if (end) return location.pathname === path;
    if (path.includes("?")) return location.pathname + location.search === path;
    return location.pathname.startsWith(path);
  };

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="border-b border-sidebar-border px-3 py-3">
        <div className="flex items-center gap-2 min-w-0">
          <Database className="w-5 h-5 text-primary shrink-0" />
          {!collapsed && (
            <div className="min-w-0">
              <div className="text-sm font-bold text-sidebar-foreground truncate">
                Dynamic Vector
              </div>
              <div className="text-[10px] text-sidebar-foreground/50 truncate">
                Store Supervisor
              </div>
            </div>
          )}
        </div>
      </SidebarHeader>

      <SidebarContent className="overflow-y-auto">
        {/* Top-level items */}
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {TOP_ITEMS.map((item) => (
                <SidebarMenuItem key={item.to}>
                  <SidebarMenuButton asChild isActive={isActive(item.to, item.end)}>
                    <NavLink
                      to={item.to}
                      end={item.end}
                      className="hover:bg-sidebar-accent/50"
                      activeClassName="bg-primary/15 text-primary font-medium"
                    >
                      <item.icon className="mr-2 h-4 w-4" />
                      {!collapsed && <span>{item.label}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Collapsible groups */}
        <SidebarGroup>
          {!collapsed && (
            <SidebarGroupLabel className="text-[10px] uppercase tracking-widest text-sidebar-foreground/30 px-3">
              Operations
            </SidebarGroupLabel>
          )}
          <SidebarGroupContent>
            <SidebarMenu>
              {NAV_GROUPS.map((group) => (
                <CollapsibleNavGroup key={group.label} group={group} collapsed={collapsed} />
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Bottom items */}
        <SidebarGroup className="mt-auto">
          <SidebarGroupContent>
            <SidebarMenu>
              {BOTTOM_ITEMS.map((item) => (
                <SidebarMenuItem key={item.to}>
                  <SidebarMenuButton asChild isActive={isActive(item.to)}>
                    <NavLink
                      to={item.to}
                      className="hover:bg-sidebar-accent/50"
                      activeClassName="bg-primary/15 text-primary font-medium"
                    >
                      <item.icon className="mr-2 h-4 w-4" />
                      {!collapsed && <span>{item.label}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border p-3">
        {!collapsed && (
          <div className="text-[10px] text-sidebar-foreground/40">
            <div className="font-medium">GenAI Zurich 2026</div>
            <div>Qdrant Challenge</div>
          </div>
        )}
      </SidebarFooter>
    </Sidebar>
  );
}
