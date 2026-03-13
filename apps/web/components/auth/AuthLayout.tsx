"use client";

import * as React from "react";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { SectionLoader } from "@/components/ui/loading";
import { cn } from "@/lib/utils";

interface AuthLayoutProps {
  /** Lucide icon element shown in the branded logo circle */
  icon?: React.ReactNode;
  /** Card title (e.g. "Welcome back") */
  title: string;
  /** Card description / subtitle */
  description?: string;
  /** Card body + footer via children. Typically a <form> wrapping CardContent + CardFooter */
  children: React.ReactNode;
  /** Additional className on the Card */
  cardClassName?: string;
}

/**
 * Shared auth page shell providing:
 * - Full-screen centred layout with brand gradient background
 * - ThemeToggle in the corner
 * - Optional branded icon circle above the card
 * - Consistent Card with shadow, ring, and dark-mode styling
 *
 * Usage:
 * ```tsx
 * <AuthLayout icon={<MessageSquare />} title="Welcome back" description="Sign in to continue">
 *   <form>
 *     <CardContent>…fields…</CardContent>
 *     <CardFooter>…buttons…</CardFooter>
 *   </form>
 * </AuthLayout>
 * ```
 */
export function AuthLayout({
  icon,
  title,
  description,
  children,
  cardClassName,
}: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-50 via-white to-teal-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 px-4 py-8">
      <ThemeToggle />
      <div className="w-full max-w-md">
        {icon && (
          <div className="flex justify-center mb-8">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/25">
              {icon}
            </div>
          </div>
        )}
        <Card
          className={cn(
            "w-full max-w-md shadow-xl border-0 ring-1 ring-black/5 dark:ring-white/10 dark:shadow-2xl",
            cardClassName,
          )}
        >
          <CardHeader className="space-y-1 text-center">
            <CardTitle className="text-2xl font-bold">{title}</CardTitle>
            {description && (
              <CardDescription>{description}</CardDescription>
            )}
          </CardHeader>
          {children}
        </Card>
      </div>
    </div>
  );
}

/**
 * Minimal loading shell that matches the auth layout background.
 * Use as a Suspense fallback or loading state for auth pages.
 */
export function AuthLayoutSkeleton() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-50 via-white to-teal-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 px-4 py-8">
      <ThemeToggle />
      <div className="w-full max-w-md">
        <Card className="w-full max-w-md shadow-xl border-0 ring-1 ring-black/5 dark:ring-white/10 dark:shadow-2xl">
          <CardContent className="pt-6">
            <SectionLoader minHeight="min-h-[100px]" />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
