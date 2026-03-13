"use client";

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import {
  Bot,
  BarChart3,
  CreditCard,
  Settings,
  Code2,
  Sun,
  Moon,
  LogOut,
  Search,
  Command,
  ArrowRight,
  Hash,
  Keyboard,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface CommandItem {
  id: string;
  label: string;
  description?: string;
  icon: React.ReactNode;
  action: () => void;
  keywords: string[];
  group: string;
}

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const router = useRouter();
  const { logout, isAdmin } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  const close = useCallback(() => {
    setOpen(false);
    setQuery("");
    setSelectedIndex(0);
  }, []);

  const commands: CommandItem[] = useMemo(
    () => [
      {
        id: "chatbots",
        label: "Go to Chatbots",
        description: "Manage your chatbots",
        icon: <Bot className="h-4 w-4" />,
        action: () => {
          router.push("/dashboard/chatbots");
          close();
        },
        keywords: ["chatbot", "bot", "manage", "list"],
        group: "Navigation",
      },
      {
        id: "analytics",
        label: "Go to Analytics",
        description: "View performance metrics",
        icon: <BarChart3 className="h-4 w-4" />,
        action: () => {
          router.push("/dashboard/analytics");
          close();
        },
        keywords: ["analytics", "stats", "metrics", "data"],
        group: "Navigation",
      },
      {
        id: "usage",
        label: "Go to Usage",
        description: "Subscription and usage",
        icon: <CreditCard className="h-4 w-4" />,
        action: () => {
          router.push("/dashboard/usage");
          close();
        },
        keywords: ["usage", "payment", "plan", "subscription"],
        group: "Navigation",
      },
      {
        id: "settings",
        label: "Go to Settings",
        description: "Account preferences",
        icon: <Settings className="h-4 w-4" />,
        action: () => {
          router.push("/dashboard/settings");
          close();
        },
        keywords: ["settings", "config", "preferences", "account"],
        group: "Navigation",
      },
      {
        id: "developer",
        label: "Go to Developer Logs",
        description: "API and debug logs",
        icon: <Code2 className="h-4 w-4" />,
        action: () => {
          router.push("/dashboard/developer");
          close();
        },
        keywords: ["developer", "logs", "api", "debug"],
        group: "Navigation",
      },
      {
        id: "toggle-theme",
        label: theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode",
        description: `Currently ${theme} mode`,
        icon: theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />,
        action: () => {
          toggleTheme();
          close();
        },
        keywords: ["theme", "dark", "light", "mode", "toggle"],
        group: "Actions",
      },
      {
        id: "logout",
        label: "Logout",
        description: "Sign out of your account",
        icon: <LogOut className="h-4 w-4" />,
        action: () => {
          logout();
          close();
        },
        keywords: ["logout", "sign out", "exit"],
        group: "Actions",
      },
    ],
    [router, close, theme, toggleTheme, logout, isAdmin]
  );

  const filtered = useMemo(() => {
    if (!query.trim()) return commands;
    const q = query.toLowerCase();
    return commands.filter(
      (cmd) =>
        cmd.label.toLowerCase().includes(q) ||
        cmd.description?.toLowerCase().includes(q) ||
        cmd.keywords.some((kw) => kw.includes(q))
    );
  }, [query, commands]);

  // Group commands
  const grouped = useMemo(() => {
    const groups: Record<string, CommandItem[]> = {};
    filtered.forEach((cmd) => {
      if (!groups[cmd.group]) groups[cmd.group] = [];
      groups[cmd.group].push(cmd);
    });
    return groups;
  }, [filtered]);

  const flatFiltered = useMemo(() => filtered, [filtered]);

  // Keyboard shortcut to open
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Focus input when opened
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  // Keyboard navigation
  useEffect(() => {
    if (!open) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          setSelectedIndex((prev) => Math.min(prev + 1, flatFiltered.length - 1));
          break;
        case "ArrowUp":
          e.preventDefault();
          setSelectedIndex((prev) => Math.max(prev - 1, 0));
          break;
        case "Enter":
          e.preventDefault();
          if (flatFiltered[selectedIndex]) {
            flatFiltered[selectedIndex].action();
          }
          break;
        case "Escape":
          e.preventDefault();
          close();
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, selectedIndex, flatFiltered, close]);

  // Reset selection when query changes
  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  // Scroll selected item into view
  useEffect(() => {
    if (!listRef.current) return;
    const selected = listRef.current.querySelector("[data-selected='true']");
    if (selected) {
      selected.scrollIntoView({ block: "nearest" });
    }
  }, [selectedIndex]);

  if (!open) return null;

  let flatIndex = -1;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
        onClick={close}
        aria-hidden="true"
      />

      {/* Command Palette */}
      <div
        className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]"
        role="dialog"
        aria-modal="true"
        aria-label="Command palette"
      >
        <div className="w-full max-w-lg bg-popover border rounded-xl shadow-2xl overflow-hidden animate-in fade-in-0 zoom-in-95 duration-150">
          {/* Search input */}
          <div className="flex items-center border-b px-4 gap-2">
            <Command className="h-4 w-4 text-muted-foreground shrink-0" />
            <input
              ref={inputRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type a command or search..."
              className="flex-1 bg-transparent py-3.5 text-sm outline-none placeholder:text-muted-foreground"
              aria-label="Command palette search"
            />
            <kbd className="hidden sm:inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
              ESC
            </kbd>
          </div>

          {/* Results */}
          <div ref={listRef} className="max-h-72 overflow-y-auto py-2" role="listbox">
            {flatFiltered.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">
                No commands found for &ldquo;{query}&rdquo;
              </div>
            ) : (
              Object.entries(grouped).map(([group, items]) => (
                <div key={group}>
                  <p className="px-4 py-1.5 text-[10px] font-semibold tracking-wider uppercase text-muted-foreground">
                    {group}
                  </p>
                  {items.map((cmd) => {
                    flatIndex++;
                    const idx = flatIndex;
                    const isSelected = selectedIndex === idx;
                    return (
                      <button
                        key={cmd.id}
                        data-selected={isSelected}
                        onClick={cmd.action}
                        onMouseEnter={() => setSelectedIndex(idx)}
                        className={cn(
                          "w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors",
                          isSelected
                            ? "bg-accent text-accent-foreground"
                            : "text-foreground hover:bg-accent/50"
                        )}
                        role="option"
                        aria-selected={isSelected}
                      >
                        <span className="text-muted-foreground">{cmd.icon}</span>
                        <div className="flex-1 text-left">
                          <span className="font-medium">{cmd.label}</span>
                          {cmd.description && (
                            <span className="ml-2 text-xs text-muted-foreground">
                              {cmd.description}
                            </span>
                          )}
                        </div>
                        {isSelected && (
                          <ArrowRight className="h-3 w-3 text-muted-foreground" />
                        )}
                      </button>
                    );
                  })}
                </div>
              ))
            )}
          </div>

          {/* Footer hint */}
          <div className="flex items-center justify-between border-t px-4 py-2 text-[10px] text-muted-foreground">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <kbd className="inline-flex h-4 items-center rounded border bg-muted px-1 font-mono">↑↓</kbd>
                Navigate
              </span>
              <span className="flex items-center gap-1">
                <kbd className="inline-flex h-4 items-center rounded border bg-muted px-1 font-mono">↵</kbd>
                Select
              </span>
              <span className="flex items-center gap-1">
                <kbd className="inline-flex h-4 items-center rounded border bg-muted px-1 font-mono">esc</kbd>
                Close
              </span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
