"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { Sidebar } from "@/components/dashboard/Sidebar";
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
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar isCollapsed={isCollapsed} setIsCollapsed={setIsCollapsed} />
      <div
        className={cn(
          "transition-all duration-300 ease-in-out",
          isCollapsed ? "lg:pl-20" : "lg:pl-64",
        )}
      >
        <main className="p-8">{children}</main>
      </div>
    </div>
  );
}
