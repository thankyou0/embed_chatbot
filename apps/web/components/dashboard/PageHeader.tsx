"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Breadcrumb, type BreadcrumbItem } from "@/components/ui/breadcrumb";

interface PageHeaderProps {
  /** Page title text */
  title: string;
  /** Optional description shown below title */
  description?: string;
  /** Optional icon rendered to the left of the title (lucide icon element) */
  icon?: React.ReactNode;
  /** Right-side actions (buttons, filters, etc.) */
  actions?: React.ReactNode;
  /** Breadcrumb trail. If provided, renders above the title. */
  breadcrumbs?: BreadcrumbItem[];
  /** Additional className on the outer wrapper */
  className?: string;
}

/**
 * Standardised page header used across all dashboard pages.
 *
 * Provides a consistent gradient title, optional description,
 * optional breadcrumb trail, and a responsive actions area that
 * stacks on mobile and aligns inline on desktop.
 */
export function PageHeader({
  title,
  description,
  icon,
  actions,
  breadcrumbs,
  className,
}: PageHeaderProps) {
  return (
    <div className={cn("space-y-2", className)}>
      {breadcrumbs && breadcrumbs.length > 0 && (
        <Breadcrumb items={breadcrumbs} className="mb-1" />
      )}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="min-w-0">
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            {icon && (
              <span className="shrink-0 text-primary">{icon}</span>
            )}
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 to-teal-600">
              {title}
            </span>
          </h1>
          {description && (
            <p className="text-muted-foreground mt-1">{description}</p>
          )}
        </div>

        {actions && (
          <div className="flex items-center gap-2 shrink-0">{actions}</div>
        )}
      </div>
    </div>
  );
}
