"use client";

import * as React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

/* ─────────────────────────────────────────────────────────────────────────────
 * ErrorBoundary
 * Catches unhandled errors in child components and renders a fallback UI.
 *
 * Usage:
 *   <ErrorBoundary>
 *     <SomeComponent />
 *   </ErrorBoundary>
 *
 *   <ErrorBoundary fallback={<CustomFallback />}>
 *     <SomeComponent />
 *   </ErrorBoundary>
 * ────────────────────────────────────────────────────────────────────────── */

interface ErrorBoundaryProps {
  children: React.ReactNode;
  /** Custom fallback UI. If not provided, uses the default error card. */
  fallback?: React.ReactNode;
  /** Compact mode (for small sections like tabs/cards). */
  compact?: boolean;
  /** Called when an error is caught. */
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  /** Custom className for the wrapper. */
  className?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("ErrorBoundary caught:", error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <ErrorFallback
          error={this.state.error}
          onRetry={this.handleRetry}
          compact={this.props.compact}
          className={this.props.className}
        />
      );
    }

    return this.props.children;
  }
}

/* ─────────────────────────────────────────────────────────────────────────────
 * ErrorFallback
 * Default error UI used by ErrorBoundary. Can also be used standalone.
 * ────────────────────────────────────────────────────────────────────────── */

interface ErrorFallbackProps {
  error?: Error | null;
  onRetry?: () => void;
  compact?: boolean;
  className?: string;
}

function ErrorFallback({
  error,
  onRetry,
  compact = false,
  className,
}: ErrorFallbackProps) {
  if (compact) {
    return (
      <div
        className={cn(
          "flex flex-col items-center justify-center gap-3 py-8 px-4 text-center",
          className,
        )}
      >
        <AlertTriangle className="h-8 w-8 text-destructive" />
        <div>
          <p className="text-sm font-medium text-foreground">
            Something went wrong
          </p>
          {error?.message && (
            <p className="text-xs text-muted-foreground mt-1 max-w-sm">
              {error.message}
            </p>
          )}
        </div>
        {onRetry && (
          <Button variant="outline" size="sm" onClick={onRetry}>
            <RefreshCw className="mr-2 h-3 w-3" />
            Try Again
          </Button>
        )}
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center min-h-[400px]",
        className,
      )}
    >
      <Card className="max-w-md w-full">
        <CardContent className="flex flex-col items-center gap-4 pt-6 text-center">
          <div className="h-12 w-12 rounded-full bg-destructive/10 flex items-center justify-center">
            <AlertTriangle className="h-6 w-6 text-destructive" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-foreground">
              Something went wrong
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              An unexpected error occurred. Please try again.
            </p>
          </div>
          {error?.message && (
            <pre className="text-xs text-muted-foreground bg-muted p-3 rounded-md w-full overflow-auto max-h-24 text-left">
              {error.message}
            </pre>
          )}
          {onRetry && (
            <Button onClick={onRetry} className="mt-2">
              <RefreshCw className="mr-2 h-4 w-4" />
              Try Again
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export { ErrorBoundary, ErrorFallback };
