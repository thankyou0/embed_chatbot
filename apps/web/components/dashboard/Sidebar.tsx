"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { getAccessToken } from "@/lib/auth";
import { apiRequestWithAuth } from "@/lib/api";
import { cn } from "@/lib/utils";
import {
  MessageSquare,
  BarChart3,
  CreditCard,
  Settings,
  Menu,
  X,
  User as UserIcon,
  Building2,
  ArrowRight,
  ChevronDown,
  Users,
  TrendingUp,
  Tag,
  ChevronLeft,
  Wrench,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const navigation = [
  {
    name: "Chatbots",
    href: "/dashboard/chatbots",
    icon: MessageSquare,
    requiresAdmin: false,
    requiresKnowledgePermission: false,
  },
  {
    name: "Analytics",
    href: "/dashboard/analytics",
    icon: BarChart3,
    requiresAdmin: false,
    requiresKnowledgePermission: false,
  }, // Members see filtered view
  {
    name: "Usage & Billing",
    href: "/dashboard/usage",
    icon: TrendingUp,
    requiresAdmin: false,
    requiresKnowledgePermission: false,
  }, // Members see filtered view
  {
    name: "Pricing",
    href: "/dashboard/pricing",
    icon: Tag,
    requiresAdmin: true,
    requiresKnowledgePermission: false,
  }, // Only admins
  {
    name: "Developer Logs",
    href: "/dashboard/developer",
    icon: Wrench,
    requiresAdmin: false,
    requiresKnowledgePermission: true,
  },
  {
    name: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
    requiresAdmin: true,
    requiresKnowledgePermission: false,
  }, // Only admins (includes team management)
];

// Admin-only navigation items
const adminNavigation: any[] = [];

interface SidebarProps {
  isCollapsed?: boolean;
  setIsCollapsed?: (value: boolean) => void;
}

export function Sidebar({ isCollapsed = false, setIsCollapsed }: SidebarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [hasAnalyticsPermission, setHasAnalyticsPermission] = useState(false);
  const [hasKnowledgePermission, setHasKnowledgePermission] = useState(false);
  const [pendingHref, setPendingHref] = useState<string | null>(null);
  const pathname = usePathname();
  const { user, tenant, logout, isAdmin } = useAuth();

  // Extract chatbot ID from pathname if we're on a chatbot-specific page
  // Path format: /dashboard/chatbots/[chatbotId]/...
  const chatbotIdMatch = pathname.match(/\/dashboard\/chatbots\/([^\/]+)/);
  const currentChatbotId = chatbotIdMatch ? chatbotIdMatch[1] : null;

  // Check if user has analytics/knowledge permissions on any chatbot
  useEffect(() => {
    const checkPermissions = async () => {
      if (isAdmin) {
        setHasAnalyticsPermission(true);
        setHasKnowledgePermission(true);
        return;
      }

      try {
        const token = getAccessToken();
        if (!token) return;

        const response = await apiRequestWithAuth<{ chatbots: any[] }>(
          "/api/v1/chatbots",
          token,
          { method: "GET" },
        );

        // Check if user has at least one chatbot with analytics permission
        const hasPermission = response.chatbots.some(
          (bot) =>
            bot.can_view_analytics_billing === true ||
            bot.permission_level === "owner" ||
            bot.permission_level === "admin",
        );
        setHasAnalyticsPermission(hasPermission);

        const hasKnowledge = response.chatbots.some(
          (bot) =>
            bot.can_manage_knowledge === true ||
            bot.permission_level === "owner" ||
            bot.permission_level === "admin" ||
            bot.permission_level === "editor",
        );
        setHasKnowledgePermission(hasKnowledge);
      } catch (err) {
        console.error("Failed to check analytics permission:", err);
        setHasAnalyticsPermission(false);
        setHasKnowledgePermission(false);
      }
    };

    checkPermissions();
  }, [isAdmin]);

  useEffect(() => {
    setPendingHref(null);
  }, [pathname]);

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? (
            <X className="h-6 w-6" />
          ) : (
            <Menu className="h-6 w-6" />
          )}
        </Button>
      </div>

      {/* Sidebar */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-40 bg-card border-r border-border transform transition-all duration-300 ease-in-out lg:translate-x-0 flex flex-col",
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full",
          isCollapsed ? "w-20" : "w-64",
        )}
      >
        <div className="flex flex-col h-full">
          <div
            className={cn(
              "flex items-center h-16 border-b border-border transition-all justify-between px-3",
              isCollapsed ? "px-2" : "px-6",
            )}
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shrink-0 shadow-lg shadow-indigo-500/20">
                <MessageSquare className="h-6 w-6 text-white" />
              </div>
              {!isCollapsed && (
                <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600 tracking-tight">
                  Chatbot SaaS
                </span>
              )}
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsCollapsed?.(!isCollapsed)}
              className="h-8 w-8 rounded-lg border border-border hover:bg-accent hidden lg:flex"
            >
              <ChevronLeft
                className={cn(
                  "h-4 w-4 transition-transform",
                  isCollapsed && "rotate-180",
                )}
              />
            </Button>
          </div>
          <nav
            className={cn(
              "flex-1 py-6 space-y-1 transition-all",
              isCollapsed
                ? "px-2 overflow-hidden"
                : "px-4 overflow-y-auto custom-scrollbar",
            )}
          >
            {navigation
              // Filter out admin-only items for non-admin users
              // Show Analytics and Usage & Billing to users with analytics permission
              .filter((item) => {
                if (item.requiresAdmin && !isAdmin) return false;
                if (
                  (item.name === "Analytics" ||
                    item.name === "Usage & Billing") &&
                  !isAdmin &&
                  !hasAnalyticsPermission
                ) {
                  return false; // Hide analytics/billing if user lacks permission
                }
                if (
                  item.requiresKnowledgePermission &&
                  !isAdmin &&
                  !hasKnowledgePermission
                ) {
                  return false;
                }
                return true;
              })
              .map((item) => {
                const isActive =
                  pathname === item.href ||
                  (item.href !== "/dashboard" &&
                    pathname.startsWith(item.href));

                // Dynamically update analytics/usage links if chatbot is selected
                let href = item.href;
                if (
                  (item.name === "Analytics" ||
                    item.name === "Usage & Billing") &&
                  currentChatbotId &&
                  currentChatbotId !== "new"
                ) {
                  href = `${item.href}?chatbot_id=${currentChatbotId}`;
                }

                return (
                  <Link
                    key={item.name}
                    href={href}
                    onClick={(e) => {
                      // Only show loading animation if navigating to a different page
                      if (!isActive) {
                        setPendingHref(href);
                      } else {
                        e.preventDefault();
                      }
                      setMobileMenuOpen(false);
                    }}
                    className={cn(
                      "flex items-center text-sm font-medium rounded-lg transition-all group relative",
                      isCollapsed ? "justify-center p-3" : "px-4 py-3",
                      isActive
                        ? "bg-primary text-primary-foreground shadow-md shadow-primary/20"
                        : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                      pendingHref === href &&
                        !isActive &&
                        "bg-accent/60 text-foreground ring-1 ring-primary/30",
                    )}
                  >
                    <item.icon
                      className={cn("h-5 w-5 shrink-0", !isCollapsed && "mr-3")}
                    />
                    {!isCollapsed && <span>{item.name}</span>}
                    {pendingHref === href && !isActive && isCollapsed && (
                      <span className="absolute -right-1.5 top-1.5 h-2 w-2 rounded-full bg-primary animate-pulse" />
                    )}
                    {isCollapsed && (
                      <div className="absolute left-full ml-2 px-2 py-1 bg-popover text-popover-foreground text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50 shadow-md">
                        {item.name}
                      </div>
                    )}
                  </Link>
                );
              })}

            {/* Admin-only navigation */}
            {isAdmin && adminNavigation.length > 0 && (
              <>
                <div
                  className={cn(
                    "pt-4 pb-2",
                    isCollapsed ? "flex justify-center" : "px-4",
                  )}
                >
                  {isCollapsed ? (
                    <div className="h-px w-8 bg-border" />
                  ) : (
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Admin
                    </p>
                  )}
                </div>
                {adminNavigation.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className={cn(
                        "flex items-center text-sm font-medium rounded-lg transition-all group relative",
                        isCollapsed ? "justify-center p-3" : "px-4 py-3",
                        isActive
                          ? "bg-primary text-primary-foreground shadow-md shadow-primary/20"
                          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                      )}
                    >
                      <item.icon
                        className={cn(
                          "h-5 w-5 shrink-0",
                          !isCollapsed && "mr-3",
                        )}
                      />
                      {!isCollapsed && <span>{item.name}</span>}
                      {isCollapsed && (
                        <div className="absolute left-full ml-2 px-2 py-1 bg-popover text-popover-foreground text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50 shadow-md">
                          {item.name}
                        </div>
                      )}
                    </Link>
                  );
                })}
              </>
            )}
          </nav>

          {/* Account Details at Bottom */}
          {user && (
            <div
              className={cn(
                "border-t border-border mt-auto transition-all",
                isCollapsed ? "p-2" : "p-4",
              )}
            >
              <Card
                className={cn(
                  "border-0 shadow-none bg-muted/30 overflow-hidden",
                  isCollapsed ? "rounded-xl" : "p-0",
                )}
              >
                <div
                  className={cn(
                    "flex flex-col",
                    isCollapsed ? "p-2 space-y-4" : "p-4 space-y-2",
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div
                      className={cn(
                        "flex items-center min-w-0",
                        isCollapsed ? "flex-col" : "space-x-2 flex-1",
                      )}
                    >
                      <div className="h-10 w-10 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center shrink-0 shadow-sm">
                        <span className="text-white font-bold text-xs">
                          {(user.name ||
                            user.username ||
                            user.email)[0].toUpperCase()}
                        </span>
                      </div>
                      {!isCollapsed && (
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold truncate leading-none mb-1">
                            {user.name || `@${user.username}`}
                          </p>
                          <p className="text-xs text-muted-foreground truncate font-medium">
                            {user.email}
                          </p>
                        </div>
                      )}
                    </div>
                    {!isCollapsed && (
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 hover:bg-muted"
                          >
                            <ChevronDown className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-48 p-0">
                          <DropdownMenuItem
                            onClick={() => {
                              logout();
                              setMobileMenuOpen(false);
                            }}
                            className="text-red-600 focus:text-red-600 focus:bg-red-50 rounded-none cursor-pointer"
                          >
                            <ArrowRight className="mr-2 h-4 w-4" />
                            Logout
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    )}
                  </div>
                  {tenant && !isCollapsed && (
                    <div className="flex items-center space-x-2 pt-2 border-t border-border">
                      <div className="w-5 h-5 rounded bg-muted flex items-center justify-center">
                        <Building2 className="h-3 w-3 text-muted-foreground shrink-0" />
                      </div>
                      <p className="text-xs text-muted-foreground truncate font-medium">
                        {tenant.name}
                      </p>
                    </div>
                  )}
                  {isCollapsed && (
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                      onClick={() => logout()}
                    >
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>

      {/* Overlay for mobile */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}
    </>
  );
}
