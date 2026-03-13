import * as React from "react";
import { cn } from "@/lib/utils";

/* ─────────────────────────────────────────────────────────────────────────────
 * Skeleton
 * Base animated placeholder. Uses a subtle pulse animation on a muted bg.
 * Compose these to create loading states that match your final layout.
 * ────────────────────────────────────────────────────────────────────────── */

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-muted", className)}
      {...props}
    />
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
 * SkeletonCard
 * Dashboard stat card placeholder (icon + title + number).
 * ────────────────────────────────────────────────────────────────────────── */

function SkeletonCard({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "rounded-xl border bg-card p-6 space-y-4",
        className,
      )}
    >
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-8 w-8 rounded-lg" />
      </div>
      <Skeleton className="h-8 w-16" />
      <Skeleton className="h-3 w-32" />
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
 * SkeletonStatGrid
 * Row of 3 stat cards (matches Overview tab quick stats).
 * ────────────────────────────────────────────────────────────────────────── */

function SkeletonStatGrid({ columns = 3 }: { columns?: number }) {
  return (
    <div
      className="grid gap-4"
      style={{
        gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`,
      }}
    >
      {Array.from({ length: columns }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
 * SkeletonTable
 * Table-like rows (header + N body rows).
 * ────────────────────────────────────────────────────────────────────────── */

function SkeletonTable({
  rows = 5,
  columns = 4,
  className,
}: {
  rows?: number;
  columns?: number;
  className?: string;
}) {
  return (
    <div className={cn("rounded-xl border bg-card overflow-hidden", className)}>
      {/* Header */}
      <div className="border-b px-6 py-4 flex gap-6">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton
            key={i}
            className="h-4"
            style={{ width: `${Math.random() * 40 + 60}px` }}
          />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIdx) => (
        <div
          key={rowIdx}
          className={cn(
            "px-6 py-4 flex items-center gap-6",
            rowIdx < rows - 1 && "border-b",
          )}
        >
          {Array.from({ length: columns }).map((_, colIdx) => (
            <Skeleton
              key={colIdx}
              className="h-4"
              style={{ width: `${Math.random() * 60 + 40}px` }}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
 * SkeletonActivityList
 * Matches the recent activity list layout.
 * ────────────────────────────────────────────────────────────────────────── */

function SkeletonActivityList({ items = 5 }: { items?: number }) {
  return (
    <div className="rounded-xl border bg-card">
      <div className="px-6 py-4 border-b flex items-center justify-between">
        <Skeleton className="h-5 w-32" />
        <Skeleton className="h-8 w-20 rounded-md" />
      </div>
      <div className="divide-y">
        {Array.from({ length: items }).map((_, i) => (
          <div key={i} className="px-6 py-3 flex items-center gap-3">
            <Skeleton className="h-8 w-8 rounded-full shrink-0" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/3" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
 * SkeletonChatbotPage
 * Full chatbot detail page skeleton (header + tabs + overview).
 * ────────────────────────────────────────────────────────────────────────── */

function SkeletonChatbotPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-3">
          <Skeleton className="h-7 w-48" />
          <Skeleton className="h-5 w-16 rounded-full" />
          <Skeleton className="h-5 w-20 rounded-full" />
        </div>
        <Skeleton className="h-4 w-64" />
      </div>
      {/* Tabs */}
      <Skeleton className="h-10 w-full max-w-xl rounded-lg" />
      {/* Stats */}
      <SkeletonStatGrid columns={3} />
      {/* Activity */}
      <SkeletonActivityList />
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
 * SkeletonChatbotList
 * Grid of chatbot cards for the chatbots list page.
 * ────────────────────────────────────────────────────────────────────────── */

function SkeletonChatbotList({ count = 6 }: { count?: number }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-xl border bg-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-5 w-14 rounded-full" />
          </div>
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
          <div className="flex gap-2 pt-2">
            <Skeleton className="h-9 w-20 rounded-md" />
            <Skeleton className="h-9 w-20 rounded-md" />
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
 * SkeletonDashboardPage
 * Generic dashboard page skeleton (heading + stat grid + table).
 * ────────────────────────────────────────────────────────────────────────── */

function SkeletonDashboardPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-80" />
      </div>
      <SkeletonStatGrid columns={4} />
      <SkeletonTable rows={6} columns={5} />
    </div>
  );
}

export {
  Skeleton,
  SkeletonCard,
  SkeletonStatGrid,
  SkeletonTable,
  SkeletonActivityList,
  SkeletonChatbotPage,
  SkeletonChatbotList,
  SkeletonDashboardPage,
};
