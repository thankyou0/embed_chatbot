"use client";

import * as React from "react";
import Link from "next/link";
import { ChevronRight, Home } from "lucide-react";
import { cn } from "@/lib/utils";

export interface BreadcrumbItem {
  /** Display label */
  label: string;
  /** Route to navigate to. Omit for the current (last) item. */
  href?: string;
  /** Optional icon rendered before the label */
  icon?: React.ReactNode;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
  /** Additional className on the outer <nav> */
  className?: string;
  /** Show a Home icon as the first crumb (default: true) */
  showHome?: boolean;
}

/**
 * Reusable breadcrumb navigation bar for dashboard pages.
 *
 * Usage:
 * ```tsx
 * <Breadcrumb items={[
 *   { label: "Chatbots", href: "/dashboard" },
 *   { label: "MyChatbot", href: "/dashboard/chatbots/abc" },
 *   { label: "Appearance" },
 * ]} />
 * ```
 */
export function Breadcrumb({
  items,
  className,
  showHome = true,
}: BreadcrumbProps) {
  const allItems: BreadcrumbItem[] = showHome
    ? [{ label: "Dashboard", href: "/dashboard", icon: <Home className="h-3.5 w-3.5" /> }, ...items]
    : items;

  return (
    <nav
      aria-label="Breadcrumb"
      className={cn("flex items-center text-sm text-muted-foreground", className)}
    >
      <ol className="flex items-center gap-1.5 flex-wrap">
        {allItems.map((item, index) => {
          const isLast = index === allItems.length - 1;

          return (
            <li key={index} className="flex items-center gap-1.5">
              {index > 0 && (
                <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/50 shrink-0" aria-hidden />
              )}
              {isLast ? (
                <span
                  className="font-medium text-foreground truncate max-w-[200px]"
                  aria-current="page"
                >
                  {item.icon && <span className="inline-flex mr-1 align-middle">{item.icon}</span>}
                  {item.label}
                </span>
              ) : item.href ? (
                <Link
                  href={item.href}
                  className="inline-flex items-center gap-1 hover:text-foreground transition-colors truncate max-w-[200px]"
                >
                  {item.icon && <span className="shrink-0">{item.icon}</span>}
                  {item.label}
                </Link>
              ) : (
                <span className="truncate max-w-[200px]">
                  {item.icon && <span className="inline-flex mr-1 align-middle">{item.icon}</span>}
                  {item.label}
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
