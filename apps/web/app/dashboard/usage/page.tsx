"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import {
  TrendingUp,
  MessageSquare,
  Users,
  AlertCircle,
  RefreshCcw,
  Database,
  HardDrive,
  Bot,
  Filter,
  DollarSign,
  Calendar,
  CreditCard,
} from "lucide-react";
import { PageLoader } from "@/components/ui/loading";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { apiRequestWithAuth } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { cn } from "@/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface ChatbotUsageData {
  chatbot_id: string;
  chatbot_name: string;
  message_count: number;
  conversation_count: number;
  knowledge_pages_count: number;
  storage_mb: number;
  created_at: string;
}

interface PlanLimits {
  chatbots: number;
  messages_per_month: number;
  conversations_per_month: number;
  knowledge_pages: number;
  knowledge_files: number;
  team_members: number;
  api_calls_per_month: number;
  storage_mb: number;
}

interface CurrentUsage {
  chatbots_count: number;
  messages_count: number;
  global_message_count: number;
  conversations_count: number;
  knowledge_pages_count: number;
  knowledge_files_count: number;
  team_members_count: number;
  api_calls_count: number;
  storage_mb: number;
  period_start: string;
  period_end: string;
}

interface UsageWithLimits {
  current_usage: CurrentUsage;
  plan_limits: PlanLimits;
  usage_percentages: Record<string, number>;
}

interface Subscription {
  id: string;
  tenant_id: number;
  plan_type: string;
  billing_cycle: string | null;
  status: string;
  current_period_start: string;
  current_period_end: string;
}

interface PlanFeatures {
  name: string;
  description: string;
  limits: PlanLimits;
}

interface BillingOverview {
  subscription: Subscription;
  current_plan: PlanFeatures;
  usage: UsageWithLimits;
}

interface ChatbotOption {
  id: string;
  name: string;
  can_view_analytics_billing?: boolean;
  permission_level?: string;
}

export default function UsagePage() {
  const searchParams = useSearchParams();
  const chatbotIdParam = searchParams.get("chatbot_id");
  const router = useRouter();
  const { user, isAdmin } = useAuth();

  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [billingData, setBillingData] = useState<BillingOverview | null>(null);
  const [chatbots, setChatbots] = useState<ChatbotOption[]>([]);
  const [filteredChatbots, setFilteredChatbots] = useState<ChatbotOption[]>([]);
  const [perBotUsage, setPerBotUsage] = useState<ChatbotUsageData[]>([]);
  const [previousBotStats, setPreviousBotStats] =
    useState<ChatbotUsageData | null>(null);
  const [selectedChatbot, setSelectedChatbot] = useState<string>(
    chatbotIdParam || "all",
  );
  const [error, setError] = useState<string | null>(null);

  const handleChatbotSelection = (value: string) => {
    // Store current bot stats before changing
    if (selectedChatbot !== "all" && perBotUsage.length > 0) {
      const current = perBotUsage.find((u) => u.chatbot_id === selectedChatbot);
      if (current) {
        setPreviousBotStats(current);
      }
    }

    setSelectedChatbot(value);
    const queryString = value === "all" ? "" : `?chatbot_id=${value}`;
    router.replace(`/dashboard/usage${queryString}`);
  };

  // Fetch billing and usage data
  const fetchData = async (showLoader = false) => {
    try {
      if (showLoader) {
        setIsLoading(true);
      } else {
        setIsRefreshing(true);
      }
      const token = getAccessToken();
      if (!token) return;

      // Fetch billing overview (includes usage with limits)
      const billing = await apiRequestWithAuth<BillingOverview>(
        "/api/v1/billing/overview",
        token,
        { method: "GET" },
      );
      setBillingData(billing);

      // Fetch per-chatbot usage
      const params = new URLSearchParams();
      if (selectedChatbot !== "all") {
        params.append("chatbot_id", selectedChatbot);
      }

      const usageResp = await apiRequestWithAuth<{
        per_chatbot_usage: ChatbotUsageData[];
      }>(`/api/v1/usage/overview?${params.toString()}`, token, {
        method: "GET",
      });
      setPerBotUsage(usageResp.per_chatbot_usage || []);
      setPreviousBotStats(null); // Clear previous stats once new data arrives

      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to fetch data");
      console.error("Error fetching data:", err);
    } finally {
      if (showLoader) {
        setIsLoading(false);
      } else {
        setIsRefreshing(false);
      }
    }
  };

  // Fetch chatbots for filter
  const fetchChatbots = async () => {
    try {
      const token = getAccessToken();
      if (!token) return;

      const response = await apiRequestWithAuth<{ chatbots: ChatbotOption[] }>(
        "/api/v1/chatbots",
        token,
        { method: "GET" },
      );

      setChatbots(response.chatbots);

      // For non-admins, filter to only chatbots they have analytics/billing permission for
      if (!isAdmin) {
        const filtered = response.chatbots.filter(
          (bot) =>
            bot.can_view_analytics_billing === true ||
            bot.permission_level === "full_access",
        );
        setFilteredChatbots(filtered);
        // If no chatbots available, set first filtered one as selected
        if (filtered.length > 0 && selectedChatbot === "all") {
          setSelectedChatbot(filtered[0].id);
        }
      } else {
        setFilteredChatbots(response.chatbots);
      }
    } catch (err) {
      console.error("Failed to fetch chatbots:", err);
    }
  };

  useEffect(() => {
    fetchChatbots();
    fetchData(true);
  }, []);

  useEffect(() => {
    if (!isLoading) {
      fetchData(false);
    }
  }, [selectedChatbot]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const formatNumber = (num: number | string) => {
    const value = typeof num === "string" ? parseFloat(num) : num;
    return new Intl.NumberFormat("en-US").format(value || 0);
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return "text-red-500";
    if (percentage >= 75) return "text-amber-500";
    return "text-green-500";
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 90) return "bg-red-500";
    if (percentage >= 75) return "bg-amber-500";
    return "bg-green-500";
  };

  if (isLoading) {
    return <PageLoader message="Loading usage & billing data..." />;
  }

  if (!billingData) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 to-teal-600">Usage & Billing</h1>
          <p className="text-muted-foreground mt-2">
            Track your usage and billing information
          </p>
        </div>
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-red-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-red-900 dark:text-red-300">Error</p>
                <p className="text-sm text-red-800">
                  {error || "Failed to load billing information"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const { subscription, current_plan, usage } = billingData;
  const filteredBotUsage =
    selectedChatbot !== "all"
      ? perBotUsage.filter((u) => u.chatbot_id === selectedChatbot)
      : perBotUsage;

  const currentBotStats =
    selectedChatbot !== "all"
      ? perBotUsage.find((u) => u.chatbot_id === selectedChatbot) ||
        previousBotStats
      : null;

  // Use bot-specific usage for progress bars if a bot is selected
  const displayUsage = currentBotStats
    ? {
        ...usage.current_usage,
        messages_count: currentBotStats.message_count,
        conversations_count: currentBotStats.conversation_count,
        knowledge_pages_count: currentBotStats.knowledge_pages_count,
        storage_mb: currentBotStats.storage_mb,
      }
    : usage.current_usage;

  // Recalculate percentages for the progress bars if bot is selected
  const displayPercentages = currentBotStats
    ? {
        ...usage.usage_percentages,
        messages:
          (currentBotStats.message_count /
            usage.plan_limits.messages_per_month) *
          100,
        conversations:
          (currentBotStats.conversation_count /
            usage.plan_limits.conversations_per_month) *
          100,
        knowledge_pages:
          (currentBotStats.knowledge_pages_count /
            usage.plan_limits.knowledge_pages) *
          100,
        storage:
          (currentBotStats.storage_mb / usage.plan_limits.storage_mb) * 100,
      }
    : usage.usage_percentages;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 to-teal-600">Usage & Billing</h1>
          <p className="text-muted-foreground mt-1">
            Track your usage, limits, and billing information
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 bg-card border rounded-md px-3 py-1">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <select
              value={selectedChatbot}
              onChange={(e) => handleChatbotSelection(e.target.value)}
              className="bg-transparent border-0 focus:ring-0 text-sm h-8 outline-none cursor-pointer min-w-[200px] text-foreground"
            >
              {(isAdmin ||
                (!isAdmin &&
                  filteredChatbots.length > 0 &&
                  filteredChatbots.length === chatbots.length)) && (
                <option value="all" className="bg-background text-foreground">All Chatbots (Total Usage)</option>
              )}
              {filteredChatbots.map((bot) => (
                <option key={bot.id} value={bot.id} className="bg-background text-foreground">
                  {bot.name}
                </option>
              ))}
            </select>
          </div>
          <Button
            onClick={() => fetchData(false)}
            variant="outline"
            size="icon"
          >
            <RefreshCcw
              className={cn(
                "h-4 w-4",
                (isLoading || isRefreshing) && "animate-spin",
              )}
            />
          </Button>
        </div>
      </div>

      {/* Current Plan & Billing Period */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-l-4 border-l-emerald-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Current Plan
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize text-emerald-600">
              {subscription.plan_type}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {current_plan.description}
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              <Calendar className="h-4 w-4 inline mr-1" />
              Billing Period
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm font-medium">
              {formatDate(usage.current_usage.period_start)}
            </div>
            <p className="text-xs text-muted-foreground">
              to {formatDate(usage.current_usage.period_end)}
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-emerald-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              <CreditCard className="h-4 w-4 inline mr-1" />
              Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Badge
              variant={
                subscription.status === "active" ? "default" : "secondary"
              }
              className="text-sm"
            >
              {subscription.status}
            </Badge>
          </CardContent>
        </Card>
      </div>

      {/* Usage Metrics with Limits */}
      <Card>
        <CardHeader>
          <CardTitle>
            {selectedChatbot === "all"
              ? "Account Usage Overview"
              : `${currentBotStats?.chatbot_name} Usage Overview`}
          </CardTitle>
          <CardDescription>
            {selectedChatbot === "all"
              ? "Your total account usage compared to plan limits"
              : `Usage for ${currentBotStats?.chatbot_name}`}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Messages */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">
                  {selectedChatbot === "all"
                    ? "Global Messages (Total)"
                    : `Messages for ${currentBotStats?.chatbot_name}`}
                </span>
              </div>
              <span
                className={cn(
                  "font-medium text-lg",
                  selectedChatbot === "all" ? getUsageColor(displayPercentages.messages) : "",
                )}
              >
                {selectedChatbot === "all"
                  ? formatNumber(displayUsage.global_message_count)
                  : formatNumber(displayUsage.messages_count)}
                {selectedChatbot === "all" && (
                  <> / {formatNumber(usage.plan_limits.messages_per_month)}</>
                )}
              </span>
            </div>
            {selectedChatbot === "all" && (
              <>
                <Progress
                  value={Math.min(displayPercentages.messages, 100)}
                  className="h-2"
                  indicatorClassName={getProgressColor(displayPercentages.messages)}
                />
                <p className="text-xs text-muted-foreground">
                  {displayPercentages.messages.toFixed(1)}% of monthly limit
                </p>
              </>
            )}
          </div>

          {/* Chatbots - Only show if All selected, otherwise show as context if desired, or skip */}
          {selectedChatbot === "all" && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <Bot className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium">Chatbots</span>
                </div>
                <span
                  className={cn(
                    "font-medium",
                    getUsageColor(usage.usage_percentages.chatbots),
                  )}
                >
                  {usage.current_usage.chatbots_count} /{" "}
                  {usage.plan_limits.chatbots}
                </span>
              </div>
              <Progress
                value={Math.min(usage.usage_percentages.chatbots, 100)}
                className="h-2"
                indicatorClassName={getProgressColor(
                  usage.usage_percentages.chatbots,
                )}
              />
            </div>
          )}

          {/* Conversations */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">
                  {selectedChatbot === "all"
                    ? "Total Conversations"
                    : `Conversations for ${currentBotStats?.chatbot_name}`}
                </span>
              </div>
              <span
                className={cn(
                  "font-medium",
                  selectedChatbot === "all" ? getUsageColor(displayPercentages.conversations) : "",
                )}
              >
                {formatNumber(displayUsage.conversations_count)}
                {selectedChatbot === "all" && (
                  <> / {formatNumber(usage.plan_limits.conversations_per_month)}</>
                )}
              </span>
            </div>
            {selectedChatbot === "all" && (
              <Progress
                value={Math.min(displayPercentages.conversations, 100)}
                className="h-2"
                indicatorClassName={getProgressColor(
                  displayPercentages.conversations,
                )}
              />
            )}
          </div>

          {/* Knowledge Pages */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">
                  {selectedChatbot === "all"
                    ? "Knowledge Pages (Total)"
                    : `Knowledge Pages for ${currentBotStats?.chatbot_name}`}
                </span>
              </div>
              <span
                className={cn(
                  "font-medium",
                  selectedChatbot === "all" ? getUsageColor(displayPercentages.knowledge_pages) : "",
                )}
              >
                {formatNumber(displayUsage.knowledge_pages_count)}
                {selectedChatbot === "all" && (
                  <> / {formatNumber(usage.plan_limits.knowledge_pages)}</>
                )}
              </span>
            </div>
            {selectedChatbot === "all" && (
              <Progress
                value={Math.min(displayPercentages.knowledge_pages, 100)}
                className="h-2"
                indicatorClassName={getProgressColor(
                  displayPercentages.knowledge_pages,
                )}
              />
            )}
          </div>

          {/* Storage */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <HardDrive className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">
                  {selectedChatbot === "all"
                    ? "Storage (Total)"
                    : `Storage for ${currentBotStats?.chatbot_name}`}
                </span>
              </div>
              <span
                className={cn(
                  "font-medium",
                  selectedChatbot === "all" ? getUsageColor(displayPercentages.storage) : "",
                )}
              >
                {(Number(displayUsage.storage_mb) || 0).toFixed(2)} MB
                {selectedChatbot === "all" && (
                  <> / {formatNumber(usage.plan_limits.storage_mb)} MB</>
                )}
              </span>
            </div>
            {selectedChatbot === "all" && (
              <Progress
                value={Math.min(displayPercentages.storage, 100)}
                className="h-2"
                indicatorClassName={getProgressColor(
                  usage.usage_percentages.storage,
                )}
              />
            )}
          </div>
        </CardContent>
      </Card>

      {/* Important Notes */}
      <Card className="bg-muted/50">
        <CardHeader>
          <CardTitle className="text-base">📌 Important Notes</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>
            <strong>Global Message Count:</strong> Tracks all messages across
            your account and persists even if chatbots are deleted. This
            prevents circumventing limits by recreating bots.
          </p>
          <p>
            <strong>Current Messages:</strong> Shows messages from active
            chatbots only (deleted with the bot).
          </p>
          <p>
            <strong>Limits:</strong> When you reach your plan limits, further
            actions will be blocked until you upgrade or the period resets.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
