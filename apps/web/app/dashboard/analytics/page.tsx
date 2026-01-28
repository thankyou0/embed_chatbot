"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  BarChart3,
  MessageSquare,
  Users,
  CheckCircle,
  AlertCircle,
  Loader2,
  Filter,
  RefreshCcw,
  Download,
  TrendingUp,
  TrendingDown,
  CheckSquare,
  Square,
} from "lucide-react";
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
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Checkbox } from "@/components/ui/checkbox";
import { apiRequestWithAuth } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface AnalyticsOverview {
  total_sessions: number;
  total_messages: number;
  avg_messages_per_session: number;
  deflection_rate: number;
  unanswered_rate: number;
  period: string;
}

interface UnansweredQuerySample {
  id: string;
  content: string;
  created_at: string;
}

interface UnansweredQuery {
  query: string;
  count: number;
  avg_confidence: number;
  first_asked: string;
  last_asked: string;
  sample_messages: UnansweredQuerySample[];
}

interface UnansweredQueriesResponse {
  queries: UnansweredQuery[];
  total_unanswered: number;
}

interface ChatbotOption {
  id: string;
  name: string;
}

export default function AnalyticsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const chatbotIdParam = searchParams.get("chatbot_id");

  const [isLoading, setIsLoading] = useState(true);
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [unansweredQueries, setUnansweredQueries] =
    useState<UnansweredQueriesResponse | null>(null);
  const [reportedQueries, setReportedQueries] =
    useState<UnansweredQueriesResponse | null>(null);
  const [chatbots, setChatbots] = useState<ChatbotOption[]>([]);
  const [selectedChatbot, setSelectedChatbot] = useState<string>(
    chatbotIdParam || "all",
  );
  const [period, setPeriod] = useState<string>("30d");
  const [queryTab, setQueryTab] = useState<string>("missing_info");
  const [selectedQueries, setSelectedQueries] = useState<string[]>([]);
  const [isResolving, setIsResolving] = useState(false);

  useEffect(() => {
    fetchChatbots();
  }, []);

  useEffect(() => {
    fetchAnalytics();
  }, [selectedChatbot, period, queryTab]);

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
    } catch (err) {
      console.error("Failed to fetch chatbots:", err);
    }
  };

  const fetchAnalytics = async () => {
    try {
      setIsLoading(true);
      const token = getAccessToken();
      if (!token) return;

      let url = `/api/v1/chatbots/analytics/overview?period=${period}`;
      if (selectedChatbot !== "all") {
        url += `&chatbot_id=${selectedChatbot}`;
      }

      const response = await apiRequestWithAuth<AnalyticsOverview>(url, token, {
        method: "GET",
      });
      setAnalytics(response);

      // Fetch unanswered queries if a specific chatbot is selected
      if (selectedChatbot !== "all") {
        // Fetch missing_info queries
        const missingInfoUrl = `/api/v1/chatbots/${selectedChatbot}/analytics/unanswered?period=${period}&limit=20&query_type=missing_info`;
        const missingInfoResponse =
          await apiRequestWithAuth<UnansweredQueriesResponse>(
            missingInfoUrl,
            token,
            { method: "GET" },
          );
        setUnansweredQueries(missingInfoResponse);

        // Fetch reported queries
        const reportedUrl = `/api/v1/chatbots/${selectedChatbot}/analytics/unanswered?period=${period}&limit=20&query_type=reported`;
        const reportedResponse =
          await apiRequestWithAuth<UnansweredQueriesResponse>(
            reportedUrl,
            token,
            { method: "GET" },
          );
        setReportedQueries(reportedResponse);
      } else {
        setUnansweredQueries(null);
        setReportedQueries(null);
      }
    } catch (err) {
      console.error("Failed to fetch analytics:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChatbotChange = (value: string) => {
    setSelectedChatbot(value);
    if (value === "all") {
      router.push("/dashboard/analytics");
    } else {
      router.push(`/dashboard/analytics?chatbot_id=${value}`);
    }
  };

  const handlePeriodChange = (value: string) => {
    setPeriod(value);
  };

  const exportToCSV = () => {
    const currentQueries =
      queryTab === "missing_info" ? unansweredQueries : reportedQueries;
    if (!currentQueries) return;

    const csvContent = [
      ["Query", "Count", "Avg Confidence", "First Asked", "Last Asked"],
      ...currentQueries.queries.map((q) => [
        q.query,
        q.count.toString(),
        q.avg_confidence.toString(),
        new Date(q.first_asked).toLocaleDateString(),
        new Date(q.last_asked).toLocaleDateString(),
      ]),
    ]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${queryTab}-queries-${period}.csv`;
    a.click();
  };

  const getPeriodLabel = (p: string) => {
    switch (p) {
      case "7d":
        return "Last 7 days";
      case "30d":
        return "Last 30 days";
      case "90d":
        return "Last 90 days";
      default:
        return "Last 30 days";
    }
  };

  const handleBulkResolve = async () => {
    if (selectedQueries.length === 0 || selectedChatbot === "all") return;
    if (
      !confirm(
        `Are you sure you want to mark ${selectedQueries.length} query/queries as resolved?`,
      )
    )
      return;

    try {
      setIsResolving(true);
      const token = getAccessToken();
      if (!token) return;

      await apiRequestWithAuth(
        `/api/v1/chatbots/${selectedChatbot}/analytics/unanswered/resolve`,
        token,
        {
          method: "POST",
          body: JSON.stringify({ queries: selectedQueries }),
        },
      );

      setSelectedQueries([]);
      await fetchAnalytics();
    } catch (err: any) {
      alert(err.message || "Failed to resolve queries");
    } finally {
      setIsResolving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Monitor your chatbot performance and user engagement
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 bg-card border rounded-md px-3 py-1">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <select
              value={selectedChatbot}
              onChange={(e) => handleChatbotChange(e.target.value)}
              className="bg-transparent border-0 focus:ring-0 text-sm h-8 outline-none cursor-pointer min-w-[150px]"
            >
              <option value="all">All Chatbots</option>
              {chatbots.map((bot) => (
                <option key={bot.id} value={bot.id}>
                  {bot.name}
                </option>
              ))}
            </select>
          </div>
          <Button
            variant="outline"
            size="icon"
            className="h-10 w-10"
            onClick={fetchAnalytics}
            disabled={isLoading}
          >
            <RefreshCcw
              className={cn("h-4 w-4", isLoading && "animate-spin")}
            />
          </Button>
        </div>
      </div>

      {/* Date Range Picker */}
      <Tabs value={period} onValueChange={handlePeriodChange}>
        <TabsList>
          <TabsTrigger value="7d">Last 7 days</TabsTrigger>
          <TabsTrigger value="30d">Last 30 days</TabsTrigger>
          <TabsTrigger value="90d">Last 90 days</TabsTrigger>
        </TabsList>
      </Tabs>

      {isLoading ? (
        <div className="flex items-center justify-center py-24">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : (
        <>
          {/* Metrics Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Sessions
                </CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analytics?.total_sessions || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  {getPeriodLabel(period)}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Messages
                </CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analytics?.total_messages || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  User and bot exchanges
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Avg. Depth
                </CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analytics?.avg_messages_per_session || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Messages per session
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Deflection Rate
                </CardTitle>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {analytics?.deflection_rate || 0}%
                </div>
                <p className="text-xs text-muted-foreground">
                  Resolved without escalation
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Unanswered Rate
                </CardTitle>
                <AlertCircle className="h-4 w-4 text-orange-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  {analytics?.unanswered_rate || 0}%
                </div>
                <p className="text-xs text-muted-foreground">
                  Low confidence responses
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Deflection Rate Visualization */}
          {analytics && (
            <Card>
              <CardHeader>
                <CardTitle>Deflection Rate</CardTitle>
                <CardDescription>
                  Percentage of conversations resolved without human
                  intervention
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Success Rate</span>
                    <span className="font-medium">
                      {analytics.deflection_rate}%
                    </span>
                  </div>
                  <Progress value={analytics.deflection_rate} className="h-2" />
                </div>
                <p className="text-sm text-muted-foreground">
                  {Math.round(
                    (analytics.deflection_rate / 100) *
                      analytics.total_sessions,
                  )}{" "}
                  of {analytics.total_sessions} sessions resolved successfully
                </p>
              </CardContent>
            </Card>
          )}

          {/* Unanswered Queries Section */}
          {selectedChatbot !== "all" &&
            (unansweredQueries || reportedQueries) && (
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Unanswered Queries</CardTitle>
                      <CardDescription>
                        Questions your chatbot struggled to answer or users
                        reported
                      </CardDescription>
                    </div>
                    {((queryTab === "missing_info" &&
                      unansweredQueries?.queries.length) ||
                      (queryTab === "reported" &&
                        reportedQueries?.queries.length)) && (
                      <Button variant="outline" size="sm" onClick={exportToCSV}>
                        <Download className="h-4 w-4 mr-2" />
                        Export CSV
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  {/* Tabs for query types */}
                  <Tabs
                    value={queryTab}
                    onValueChange={(v) => {
                      setQueryTab(v);
                      setSelectedQueries([]);
                    }}
                    className="mb-4"
                  >
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger
                        value="missing_info"
                        className="flex items-center gap-2"
                      >
                        <AlertCircle className="h-4 w-4" />
                        Missing Info ({unansweredQueries?.queries.length || 0})
                      </TabsTrigger>
                      <TabsTrigger
                        value="reported"
                        className="flex items-center gap-2"
                      >
                        <MessageSquare className="h-4 w-4" />
                        Reported ({reportedQueries?.queries.length || 0})
                      </TabsTrigger>
                    </TabsList>
                  </Tabs>

                  {(() => {
                    const currentQueries =
                      queryTab === "missing_info"
                        ? unansweredQueries
                        : reportedQueries;

                    if (
                      !currentQueries ||
                      currentQueries.queries.length === 0
                    ) {
                      return (
                        <div className="text-center py-12">
                          <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                          <p className="text-muted-foreground">
                            {queryTab === "missing_info"
                              ? "No missing information queries found"
                              : "No reported queries found"}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Your chatbot is performing well!
                          </p>
                        </div>
                      );
                    }

                    return (
                      <div className="space-y-4">
                        <div className="flex items-center justify-between mb-4">
                          <div className="text-sm text-muted-foreground">
                            Total{" "}
                            {queryTab === "missing_info"
                              ? "unanswered"
                              : "reported"}
                            :{" "}
                            <span className="font-medium">
                              {currentQueries.total_unanswered}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            {selectedQueries.length > 0 && (
                              <Button
                                variant="default"
                                size="sm"
                                onClick={handleBulkResolve}
                                disabled={isResolving}
                              >
                                {isResolving ? (
                                  <>
                                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                    Resolving...
                                  </>
                                ) : (
                                  <>
                                    <CheckCircle className="h-4 w-4 mr-2" />
                                    Resolve Selected ({selectedQueries.length})
                                  </>
                                )}
                              </Button>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center justify-between bg-muted/20 p-2 rounded-md mb-2">
                          <div className="flex items-center gap-2">
                            <Checkbox
                              checked={
                                selectedQueries.length ===
                                  currentQueries.queries.length &&
                                currentQueries.queries.length > 0
                              }
                              onCheckedChange={(checked: boolean) => {
                                if (checked) {
                                  setSelectedQueries(
                                    currentQueries.queries.map((q) => q.query),
                                  );
                                } else {
                                  setSelectedQueries([]);
                                }
                              }}
                            />
                            <span className="text-sm font-medium">
                              Select All
                            </span>
                          </div>
                        </div>

                        <div className="space-y-3">
                          {currentQueries.queries.map((query, idx) => (
                            <div
                              key={idx}
                              className={cn(
                                "border rounded-lg p-4 space-y-2 transition-colors",
                                selectedQueries.includes(query.query) &&
                                  "bg-blue-50/30 border-blue-200",
                              )}
                            >
                              <div className="flex items-start justify-between gap-4">
                                <div className="flex items-start gap-3 flex-1">
                                  <Checkbox
                                    checked={selectedQueries.includes(
                                      query.query,
                                    )}
                                    onCheckedChange={(checked: boolean) => {
                                      if (checked) {
                                        setSelectedQueries([
                                          ...selectedQueries,
                                          query.query,
                                        ]);
                                      } else {
                                        setSelectedQueries(
                                          selectedQueries.filter(
                                            (q) => q !== query.query,
                                          ),
                                        );
                                      }
                                    }}
                                    className="mt-1"
                                  />
                                  <div className="flex-1 space-y-1">
                                    <p className="font-medium">{query.query}</p>
                                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                                      <span>
                                        {queryTab === "missing_info"
                                          ? "Asked"
                                          : "Reported"}{" "}
                                        {query.count} times
                                      </span>
                                      <span>•</span>
                                      <span>
                                        Last:{" "}
                                        {new Date(
                                          query.last_asked,
                                        ).toLocaleDateString()}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                                <Badge
                                  variant={
                                    query.avg_confidence < 0.5
                                      ? "destructive"
                                      : "secondary"
                                  }
                                >
                                  {Math.round(query.avg_confidence * 100)}%
                                  confidence
                                </Badge>
                              </div>
                              <div className="space-y-1">
                                <Progress
                                  value={query.avg_confidence * 100}
                                  className={cn(
                                    "h-1",
                                    query.avg_confidence < 0.5
                                      ? "bg-red-100"
                                      : "bg-yellow-100",
                                  )}
                                />
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })()}
                </CardContent>
              </Card>
            )}

          {selectedChatbot === "all" && (
            <Card>
              <CardContent className="py-12">
                <div className="text-center space-y-2">
                  <AlertCircle className="h-12 w-12 text-muted-foreground/20 mx-auto" />
                  <p className="text-muted-foreground">
                    Select a specific chatbot to view unanswered queries
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
