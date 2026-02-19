import * as React from "react";
import { cn } from "@/lib/utils";

/* ─────────────────────────────────────────────────────────────────────────────
 * Spinner
 * Base animated spinner using a clean rotating arc (no Loader2 dependency).
 * Uses currentColor so it inherits color from parent context.
 * ────────────────────────────────────────────────────────────────────────── */
const spinnerSizes = {
  xs: "h-3 w-3",
  sm: "h-4 w-4",
  md: "h-5 w-5",
  lg: "h-8 w-8",
  xl: "h-12 w-12",
} as const;

type SpinnerSize = keyof typeof spinnerSizes;

interface SpinnerProps extends React.HTMLAttributes<SVGSVGElement> {
  size?: SpinnerSize;
}

function Spinner({ size = "md", className, ...props }: SpinnerProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={cn("animate-spin", spinnerSizes[size], className)}
      {...props}
    >
      <path d="M21 12a9 9 0 1 1-6.219-8.56" />
    </svg>
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
 * PageLoader
 * Full-page centered loading state with optional message.
 * Used for route transitions, auth checks, initial data fetches.
 * ────────────────────────────────────────────────────────────────────────── */
interface PageLoaderProps {
  message?: string;
  className?: string;
  /** When true, uses min-h-screen. Otherwise uses min-h-[60vh]. */
  fullScreen?: boolean;
}

function PageLoader({
  message,
  className,
  fullScreen = true,
}: PageLoaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3",
        fullScreen ? "min-h-screen" : "min-h-[60vh]",
        className
      )}
    >
      <div className="relative">
        <div className="h-10 w-10 rounded-full border-2 border-muted" />
        <div className="absolute inset-0 h-10 w-10 rounded-full border-2 border-t-primary animate-spin" />
      </div>
      {message && (
        <p className="text-sm text-muted-foreground animate-pulse">{message}</p>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
 * SectionLoader
 * For loading states within cards, panels, modals, tabs.
 * Lighter weight than PageLoader.
 * ────────────────────────────────────────────────────────────────────────── */
interface SectionLoaderProps {
  message?: string;
  className?: string;
  /** Height of the loading container. Default: min-h-[400px] */
  minHeight?: string;
}

function SectionLoader({
  message,
  className,
  minHeight = "min-h-[400px]",
}: SectionLoaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3",
        minHeight,
        className
      )}
    >
      <Spinner size="lg" className="text-muted-foreground" />
      {message && (
        <p className="text-sm text-muted-foreground">{message}</p>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
 * ButtonSpinner
 * Replaces Loader2 inside buttons. Always h-4 w-4 with mr-2 spacing.
 * ────────────────────────────────────────────────────────────────────────── */
interface ButtonSpinnerProps {
  className?: string;
}

function ButtonSpinner({ className }: ButtonSpinnerProps) {
  return <Spinner size="sm" className={cn("mr-2 shrink-0", className)} />;
}

/* ─────────────────────────────────────────────────────────────────────────────
 * InlineSpinner
 * Tiny spinner for status badges, icon buttons, overlay indicators.
 * No margin — size and spacing controlled by parent.
 * ────────────────────────────────────────────────────────────────────────── */
interface InlineSpinnerProps extends React.HTMLAttributes<SVGSVGElement> {
  size?: SpinnerSize;
}

function InlineSpinner({ size = "sm", className, ...props }: InlineSpinnerProps) {
  return <Spinner size={size} className={className} {...props} />;
}

/* ─────────────────────────────────────────────────────────────────────────────
 * OverlayLoader
 * Semi-transparent overlay with centered spinner, for refreshing existing content.
 * ────────────────────────────────────────────────────────────────────────── */
interface OverlayLoaderProps {
  className?: string;
}

function OverlayLoader({ className }: OverlayLoaderProps) {
  return (
    <div
      className={cn(
        "absolute inset-0 flex items-center justify-center pointer-events-none",
        className
      )}
    >
      <div className="rounded-md bg-background/80 px-3 py-2 border shadow-sm">
        <Spinner size="sm" className="text-primary" />
      </div>
    </div>
  );
}

export {
  Spinner,
  PageLoader,
  SectionLoader,
  ButtonSpinner,
  InlineSpinner,
  OverlayLoader,
};
export type { SpinnerSize, SpinnerProps };
