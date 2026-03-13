"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { HeaderProvider } from "@/contexts/HeaderContext";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import { CommandPalette } from "@/components/dashboard/CommandPalette";
import { OnboardingTour } from "@/components/dashboard/OnboardingTour";
import { PageLoader } from "@/components/ui/loading";
import { ErrorBoundary } from "@/components/ui/error-boundary";
import { cn } from "@/lib/utils";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, tenant, loading } = useAuth();
  const router = useRouter();
  const [isCollapsed, setIsCollapsed] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  if (loading) {
    return <PageLoader message="Loading..." />;
  }

  if (!user) {
    return null;
  }

  return (
    <HeaderProvider>
    <div className="min-h-screen bg-gradient-to-br from-slate-50/80 via-gray-50/50 to-emerald-50/40 dark:from-gray-950 dark:via-gray-950 dark:to-gray-950">
      {/* Skip to content link for keyboard/screen reader users */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-[100] focus:top-4 focus:left-4 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-md focus:shadow-lg focus:text-sm focus:font-medium"
      >
        Skip to main content
      </a>
      <Sidebar isCollapsed={isCollapsed} setIsCollapsed={setIsCollapsed} />
      <CommandPalette />
      <OnboardingTour />
      <div
        className={cn(
          "transition-all duration-300 ease-in-out",
          isCollapsed ? "lg:pl-20" : "lg:pl-64",
        )}
      >
        <Header isCollapsed={isCollapsed} />
        <main id="main-content" className="p-4 md:p-6 lg:p-8" role="main" tabIndex={-1}>
          <ErrorBoundary>{children}</ErrorBoundary>
        </main>
      </div>
    </div>
    </HeaderProvider>
  );
}
