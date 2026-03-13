import { useLocation, Link } from "react-router-dom";
import { ChevronRight, Home } from "lucide-react";
import { cn } from "@/lib/utils";

const ROUTE_LABELS: Record<string, string> = {
  "/": "Dashboard",
  "/chat": "Chat",
  "/dashboard": "Analytics",
  "/visual-search": "Visual Search",
  "/livemap": "Live Map",
  "/store-map": "Store Map",
  "/settings": "Settings",
};

export function Breadcrumbs() {
  const location = useLocation();

  if (location.pathname === "/") return null;

  const segments = location.pathname.split("/").filter(Boolean);
  const crumbs = segments.map((seg, i) => {
    const path = "/" + segments.slice(0, i + 1).join("/");
    return {
      label: ROUTE_LABELS[path] || seg.charAt(0).toUpperCase() + seg.slice(1).replace(/-/g, " "),
      path,
      isLast: i === segments.length - 1,
    };
  });

  // Add tab info from search params
  const tab = new URLSearchParams(location.search).get("tab");
  if (tab) {
    crumbs.push({
      label: tab.charAt(0).toUpperCase() + tab.slice(1).replace(/-/g, " "),
      path: location.pathname + location.search,
      isLast: true,
    });
    if (crumbs.length > 1) crumbs[crumbs.length - 2].isLast = false;
  }

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-xs text-muted-foreground">
      <Link to="/" className="hover:text-foreground transition-colors flex items-center gap-1">
        <Home className="w-3 h-3" />
        <span className="hidden sm:inline">Home</span>
      </Link>
      {crumbs.map((crumb) => (
        <span key={crumb.path} className="flex items-center gap-1">
          <ChevronRight className="w-3 h-3 text-muted-foreground/50" />
          {crumb.isLast ? (
            <span className="text-foreground font-medium">{crumb.label}</span>
          ) : (
            <Link to={crumb.path} className="hover:text-foreground transition-colors">
              {crumb.label}
            </Link>
          )}
        </span>
      ))}
    </nav>
  );
}
