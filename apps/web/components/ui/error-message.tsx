"use client";

import * as React from "react";
import { AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface ErrorMessageProps {
  /** Error text to display. If falsy, the component renders nothing. */
  message?: string | null;
  /** Visual style variant */
  variant?: "banner" | "inline";
  /** Optional icon — defaults to AlertCircle for banner, none for inline */
  icon?: React.ReactNode;
  /** Additional className */
  className?: string;
}

/**
 * Standardised error message used across the dashboard.
 *
 * - **banner** (default): rounded box with destructive background, icon + text.
 *   Use for page-level or section-level errors.
 * - **inline**: small red text. Use for form-field validation errors.
 *
 * Renders nothing when `message` is falsy — safe to use inline without
 * conditional wrappers.
 */
export function ErrorMessage({
  message,
  variant = "banner",
  icon,
  className,
}: ErrorMessageProps) {
  if (!message) return null;

  if (variant === "inline") {
    return (
      <p className={cn("text-sm text-destructive", className)}>{message}</p>
    );
  }

  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive",
        className,
      )}
    >
      {icon ?? <AlertCircle className="h-5 w-5 shrink-0" />}
      <span>{message}</span>
    </div>
  );
}

/**
 * Standardised success message with similar styling.
 */
export function SuccessMessage({
  message,
  icon,
  className,
}: Omit<ErrorMessageProps, "variant">) {
  if (!message) return null;

  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-lg border border-success/30 bg-success/10 p-3 text-sm text-success",
        className,
      )}
    >
      {icon ?? (
        <svg
          className="h-5 w-5 shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 13l4 4L19 7"
          />
        </svg>
      )}
      <span>{message}</span>
    </div>
  );
}
