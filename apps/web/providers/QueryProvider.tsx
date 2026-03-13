"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Stale after 30 seconds — avoids unnecessary re-fetches for
            // dashboard data that doesn't change every second.
            staleTime: 30 * 1000,
            // Cache for 5 minutes even when there are no active observers
            gcTime: 5 * 60 * 1000,
            // Don't re-fetch every time the window re-gains focus
            refetchOnWindowFocus: false,
            // Retry once on failure
            retry: 1,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
