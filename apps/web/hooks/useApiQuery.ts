import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryOptions,
  type UseMutationOptions,
} from "@tanstack/react-query";
import { apiRequestWithAuth } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

// ── Generic authenticated GET hook ──────────────────────────
export function useApiQuery<T>(
  queryKey: unknown[],
  endpoint: string,
  options?: Omit<UseQueryOptions<T, Error>, "queryKey" | "queryFn">,
) {
  return useQuery<T, Error>({
    queryKey,
    queryFn: async () => {
      const token = getAccessToken();
      if (!token) throw new Error("Not authenticated");
      return apiRequestWithAuth<T>(endpoint, token, { method: "GET" });
    },
    ...options,
  });
}

// ── Generic authenticated mutation hook ─────────────────────
export function useApiMutation<TData, TVariables = void>(
  endpoint: string | ((variables: TVariables) => string),
  method: string = "POST",
  options?: Omit<
    UseMutationOptions<TData, Error, TVariables>,
    "mutationFn"
  >,
) {
  const queryClient = useQueryClient();

  return useMutation<TData, Error, TVariables>({
    mutationFn: async (variables) => {
      const token = getAccessToken();
      if (!token) throw new Error("Not authenticated");
      const url = typeof endpoint === "function" ? endpoint(variables) : endpoint;
      return apiRequestWithAuth<TData>(url, token, {
        method,
        ...(variables !== undefined && method !== "DELETE"
          ? { body: JSON.stringify(variables) }
          : {}),
      });
    },
    ...options,
  });
}

// ── Convenience: invalidate related queries after mutation ──
export function useInvalidateQueries() {
  const queryClient = useQueryClient();
  return (keys: unknown[][]) => {
    keys.forEach((key) => queryClient.invalidateQueries({ queryKey: key }));
  };
}

// ── Query key factory ───────────────────────────────────────
export const queryKeys = {
  chatbots: {
    all: ["chatbots"] as const,
    list: () => [...queryKeys.chatbots.all, "list"] as const,
    detail: (id: string) => [...queryKeys.chatbots.all, id] as const,
    stats: (id: string) => [...queryKeys.chatbots.all, id, "stats"] as const,
    knowledge: (id: string) =>
      [...queryKeys.chatbots.all, id, "knowledge"] as const,
    appearance: (id: string) =>
      [...queryKeys.chatbots.all, id, "appearance"] as const,
    activities: (id: string, page?: number) =>
      [...queryKeys.chatbots.all, id, "activities", page] as const,
    notifications: (id: string) =>
      [...queryKeys.chatbots.all, id, "notifications"] as const,
  },
  analytics: {
    all: ["analytics"] as const,
    overview: (chatbotId: string, period: string) =>
      [...queryKeys.analytics.all, "overview", chatbotId, period] as const,
    unanswered: (chatbotId: string, period: string) =>
      [...queryKeys.analytics.all, "unanswered", chatbotId, period] as const,
  },
  usage: {
    all: ["usage"] as const,
    overview: () => [...queryKeys.usage.all, "overview"] as const,
    limits: (chatbotId?: string) =>
      [...queryKeys.usage.all, "limits", chatbotId] as const,
  },
  members: {
    all: ["members"] as const,
    list: () => [...queryKeys.members.all, "list"] as const,
  },
  developer: {
    all: ["developer"] as const,
    failures: (chatbotId?: string) =>
      [...queryKeys.developer.all, "failures", chatbotId] as const,
  },
} as const;
