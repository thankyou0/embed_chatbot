"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Search,
  Bell,
  X,
  Check,
  Info,
  AlertTriangle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { useHeaderContent } from "@/contexts/HeaderContext";
import {
  type Notification,
  loadNotifications,
  seedWelcomeNotifications,
  markRead,
  markAllRead as markAllReadUtil,
  dismissNotification,
  clearAll,
  formatRelativeTime,
} from "@/lib/notifications";

// Notification icon/color maps
const notificationIcons = {
  info: Info,
  warning: AlertTriangle,
  success: Check,
};

const notificationColors = {
  info: "text-blue-500 bg-blue-50 dark:bg-blue-950",
  warning: "text-amber-500 bg-amber-50 dark:bg-amber-950",
  success: "text-emerald-500 bg-emerald-50 dark:bg-emerald-950",
};

interface HeaderProps {
  isCollapsed?: boolean;
}

/** Dispatch Ctrl+K to open the CommandPalette */
function openCommandPalette() {
  window.dispatchEvent(
    new KeyboardEvent("keydown", { key: "k", ctrlKey: true, bubbles: true })
  );
}

export function Header({ isCollapsed }: HeaderProps) {
  const { content } = useHeaderContent();
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // Load notifications from localStorage on mount (seed welcome msgs for new accounts)
  useEffect(() => {
    const existing = loadNotifications();
    if (existing.length > 0) {
      setNotifications(existing);
    } else {
      setNotifications(seedWelcomeNotifications());
    }

    // Listen for notification-update events (fired by notify-toast)
    const handleUpdate = () => setNotifications(loadNotifications());
    window.addEventListener("notification-update", handleUpdate);
    return () => window.removeEventListener("notification-update", handleUpdate);
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleMarkAllRead = useCallback(() => {
    setNotifications((prev) => markAllReadUtil(prev));
  }, []);

  const handleMarkAsRead = useCallback((id: string) => {
    setNotifications((prev) => markRead(prev, id));
  }, []);

  const handleDismiss = useCallback((id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setNotifications((prev) => dismissNotification(prev, id));
  }, []);

  const handleClearAll = useCallback(() => {
    setNotifications(clearAll());
  }, []);

  return (
    <header
      className="sticky top-0 z-30 h-14 border-b border-border bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/60"
      role="banner"
    >
      <div className="flex h-full items-center justify-between px-4 md:px-6 gap-4">

        {/* Left: page title + description from context */}
        {content ? (
          <div className="min-w-0 flex-1">
            <h1 className="text-base font-semibold leading-tight truncate flex items-center gap-2">
              {content.title}
            </h1>
            {content.description && (
              <p className="text-xs text-muted-foreground truncate leading-tight mt-0.5">
                {content.description}
              </p>
            )}
          </div>
        ) : (
          <div className="flex-1" />
        )}

        {/* Right: page actions + search + notifications */}
        <div className="flex items-center gap-2 shrink-0">
          {content?.actions}

          {/* Search trigger — opens CommandPalette */}
          <button
            onClick={openCommandPalette}
            className="hidden md:flex items-center gap-2 h-9 px-3 rounded-md border border-input bg-background text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors min-w-[200px]"
            aria-label="Search (Ctrl+K)"
          >
            <Search className="h-4 w-4 shrink-0" />
            <span className="flex-1 text-left">Search...</span>
            <kbd className="pointer-events-none hidden sm:inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
              <span className="text-xs">⌘</span>K
            </kbd>
          </button>
          {/* Mobile search icon */}
          <Button
            variant="ghost"
            size="icon"
            onClick={openCommandPalette}
            className="md:hidden h-9 w-9 text-muted-foreground hover:text-foreground"
            aria-label="Search (Ctrl+K)"
          >
            <Search className="h-4 w-4" />
          </Button>

          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-9 w-9 relative"
                aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ""}`}
              >
                <Bell className="h-4 w-4" />
                {unreadCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-red-500 text-[10px] font-bold text-white flex items-center justify-center">
                    {unreadCount}
                  </span>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80 p-0">
              <div className="flex items-center justify-between px-4 py-3 border-b">
                <span className="font-semibold text-sm">Notifications</span>
                <div className="flex items-center gap-2">
                  {unreadCount > 0 && (
                    <button
                      onClick={handleMarkAllRead}
                      className="text-xs text-primary hover:underline"
                    >
                      Mark all read
                    </button>
                  )}
                  {notifications.length > 0 && unreadCount === 0 && (
                    <button
                      onClick={handleClearAll}
                      className="text-xs text-destructive hover:underline"
                    >
                      Clear all
                    </button>
                  )}
                </div>
              </div>
              <div className="max-h-80 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="py-10 text-center">
                    <Bell className="h-8 w-8 mx-auto text-muted-foreground/30 mb-2" />
                    <p className="text-sm font-medium text-muted-foreground">
                      You&apos;re all caught up!
                    </p>
                    <p className="text-xs text-muted-foreground/60 mt-1">
                      No new notifications
                    </p>
                  </div>
                ) : (
                  notifications.map((notification) => {
                    const Icon = notificationIcons[notification.type];
                    return (
                      <div
                        key={notification.id}
                        onClick={() => handleMarkAsRead(notification.id)}
                        className={cn(
                          "group flex items-start gap-3 px-4 py-3 hover:bg-accent/50 cursor-pointer transition-colors border-b last:border-0",
                          !notification.read && "bg-accent/20"
                        )}
                      >
                        <div
                          className={cn(
                            "mt-0.5 p-1.5 rounded-full shrink-0",
                            notificationColors[notification.type]
                          )}
                        >
                          <Icon className="h-3 w-3" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2">
                            <p className="text-sm font-medium truncate">
                              {notification.title}
                            </p>
                            <div className="flex items-center gap-1.5 shrink-0">
                              {!notification.read && (
                                <span className="h-2 w-2 rounded-full bg-primary" />
                              )}
                              <button
                                onClick={(e) => handleDismiss(notification.id, e)}
                                className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-foreground p-0.5 rounded"
                                aria-label="Dismiss notification"
                              >
                                <X className="h-3 w-3" />
                              </button>
                            </div>
                          </div>
                          <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                            {notification.message}
                          </p>
                          <p className="text-[10px] text-muted-foreground/60 mt-1">
                            {formatRelativeTime(notification.createdAt)}
                          </p>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}

