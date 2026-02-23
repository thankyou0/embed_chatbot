"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { apiRequestWithAuth } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { AlertCircle, RefreshCcw, ShieldAlert, Wrench } from "lucide-react";
import { SectionLoader, ButtonSpinner } from "@/components/ui/loading";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type SeverityFilter = "all" | "error" | "warning";

interface ChatbotOption {
  id: string;
  name: string;
  can_manage_knowledge?: boolean;
  permission_level?: string;
}

interface KnowledgeFailureIncident {
  knowledge_source_id: string;
  tenant_id: number;
  tenant_name: string;
  chatbot_id: string;
  chatbot_name: string;
  source_type: "crawled_url" | "uploaded_file" | "qa_pair";
  source_url: string | null;
  status: "pending" | "processing" | "crawling" | "completed" | "failed";
  severity: "error" | "warning";
  message: string;
  pages_found: number;
  created_at: string;
  updated_at: string;
  last_crawl_status: "success" | "partial" | "failed" | null;
  last_crawl_completed_at: string | null;
}

interface KnowledgeFailureResponse {
  incidents: KnowledgeFailureIncident[];
  total: number;
}

const SOURCE_TYPE_LABELS: Record<KnowledgeFailureIncident["source_type"], string> =
  {
    crawled_url: "Crawled URL",
    uploaded_file: "Uploaded File",
    qa_pair: "Q&A",
  };

export default function DeveloperLogsPage() {
  const { isAdmin } = useAuth();
  const [chatbots, setChatbots] = useState<ChatbotOption[]>([]);
  const [incidents, setIncidents] = useState<KnowledgeFailureIncident[]>([]);
  const [selectedChatbot, setSelectedChatbot] = useState("all");
  const [severity, setSeverity] = useState<SeverityFilter>("all");
  const [days, setDays] = useState("14");
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<Date | null>(null);

  const accessibleChatbots = useMemo(() => {
    if (isAdmin) {
      return chatbots;
    }
    return chatbots.filter(
      (bot) =>
        bot.can_manage_knowledge === true ||
        bot.permission_level === "owner" ||
        bot.permission_level === "admin" ||
        bot.permission_level === "editor",
    );
  }, [chatbots, isAdmin]);

  const summary = useMemo(() => {
    const errors = incidents.filter((incident) => incident.severity === "error");
    const warnings = incidents.filter(
      (incident) => incident.severity === "warning",
    );
    const impactedChatbots = new Set(incidents.map((item) => item.chatbot_id));

    return {
      total: incidents.length,
      errors: errors.length,
      warnings: warnings.length,
      impactedChatbots: impactedChatbots.size,
    };
  }, [incidents]);

  useEffect(() => {
    void bootstrap();
  }, []);

  useEffect(() => {
    if (!isLoading) {
      void fetchIncidents(false);
    }
  }, [selectedChatbot, severity, days, search]);

  async function bootstrap() {
    try {
      setIsLoading(true);
      await fetchChatbots();
      await fetchIncidents(true);
    } finally {
      setIsLoading(false);
    }
  }

  async function fetchChatbots() {
    const token = getAccessToken();
    if (!token) {
      return;
    }

    const response = await apiRequestWithAuth<{ chatbots: ChatbotOption[] }>(
      "/api/v1/chatbots",
      token,
      { method: "GET" },
    );
    setChatbots(response.chatbots || []);
  }

  async function fetchIncidents(withLoader: boolean) {
    const token = getAccessToken();
    if (!token) {
      return;
    }

    try {
      if (withLoader) {
        setIsLoading(true);
      } else {
        setIsRefreshing(true);
      }

      const params = new URLSearchParams({
        severity,
        days,
        limit: "200",
      });

      if (selectedChatbot !== "all") {
        params.set("chatbot_id", selectedChatbot);
      }
      if (search.trim()) {
        params.set("search", search.trim());
      }

      const response = await apiRequestWithAuth<KnowledgeFailureResponse>(
        `/api/v1/chatbots/developer/knowledge-failures?${params.toString()}`,
        token,
        { method: "GET" },
      );
      setIncidents(response.incidents || []);
      setError(null);
      setLastUpdatedAt(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load logs");
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }

  function formatDate(value: string | null) {
    if (!value) return "-";
    return new Date(value).toLocaleString();
  }

  if (isLoading) {
    return <SectionLoader message="Loading developer logs..." minHeight="min-h-[60vh]" />;
  }

  if (!isAdmin && accessibleChatbots.length === 0) {
    return (
      <Card className="border-amber-200 bg-amber-50">
        <CardContent className="pt-6 flex items-start gap-3 text-amber-800">
          <ShieldAlert className="h-5 w-5 mt-0.5 shrink-0" />
          <div>
            <p className="font-medium">No access to developer logs</p>
            <p className="text-sm">
              You need knowledge-management permission on at least one chatbot.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
            <Wrench className="h-5 w-5 text-emerald-600" />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 to-teal-600">Developer Logs</span>
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Failures and warnings for knowledge sources with tenant/chatbot context.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {lastUpdatedAt && (
            <p className="text-xs text-muted-foreground">
              Updated {lastUpdatedAt.toLocaleTimeString()}
            </p>
          )}
          <Button
            variant="outline"
            onClick={() => void fetchIncidents(false)}
            disabled={isRefreshing}
          >
            {isRefreshing && <ButtonSpinner className="mr-0" />}
            <RefreshCcw className="h-4 w-4 mr-2" />
            {isRefreshing ? "Refreshing..." : "Refresh"}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-emerald-500">
          <CardHeader className="pb-2">
            <CardDescription>Total Incidents</CardDescription>
            <CardTitle className="text-2xl text-emerald-600">{summary.total}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="border-l-4 border-l-red-500">
          <CardHeader className="pb-2">
            <CardDescription>Errors</CardDescription>
            <CardTitle className="text-2xl text-red-600">{summary.errors}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="border-l-4 border-l-amber-500">
          <CardHeader className="pb-2">
            <CardDescription>Warnings</CardDescription>
            <CardTitle className="text-2xl text-amber-600">
              {summary.warnings}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card className="border-l-4 border-l-teal-500">
          <CardHeader className="pb-2">
            <CardDescription>Impacted Chatbots</CardDescription>
            <CardTitle className="text-2xl text-teal-600">{summary.impactedChatbots}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Filters</CardTitle>
          <CardDescription>
            Narrow down failures by chatbot, severity, and timeframe.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <select
            value={selectedChatbot}
            onChange={(e) => setSelectedChatbot(e.target.value)}
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
          >
            <option value="all">All chatbots</option>
            {accessibleChatbots.map((bot) => (
              <option key={bot.id} value={bot.id}>
                {bot.name}
              </option>
            ))}
          </select>

          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value as SeverityFilter)}
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
          >
            <option value="all">All severities</option>
            <option value="error">Errors only</option>
            <option value="warning">Warnings only</option>
          </select>

          <select
            value={days}
            onChange={(e) => setDays(e.target.value)}
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
          >
            <option value="1">Last 24 hours</option>
            <option value="7">Last 7 days</option>
            <option value="14">Last 14 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>

          <Input
            placeholder="Search URL, message, chatbot..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </CardContent>
      </Card>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6 flex items-start gap-3 text-red-700">
            <AlertCircle className="h-5 w-5 mt-0.5 shrink-0" />
            <div>
              <p className="font-medium">Could not load developer logs</p>
              <p className="text-sm">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Incident Stream</CardTitle>
          <CardDescription>
            Tenant and chatbot-aware failures from recent knowledge processing jobs.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {incidents.length === 0 ? (
            <div className="rounded-lg border border-dashed p-8 text-center text-muted-foreground">
              <ShieldAlert className="h-5 w-5 mx-auto mb-2 opacity-70" />
              No incidents found for the selected filters.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Last Seen</TableHead>
                  <TableHead>Tenant</TableHead>
                  <TableHead>Chatbot</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Message</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {incidents.map((incident) => (
                  <TableRow key={`${incident.knowledge_source_id}-${incident.updated_at}`}>
                    <TableCell className="text-xs text-muted-foreground">
                      {formatDate(
                        incident.last_crawl_completed_at || incident.updated_at,
                      )}
                    </TableCell>
                    <TableCell className="whitespace-nowrap">
                      {incident.tenant_name}
                    </TableCell>
                    <TableCell>
                      <Link
                        href={`/dashboard/chatbots/${incident.chatbot_id}`}
                        className="font-medium hover:underline"
                      >
                        {incident.chatbot_name}
                      </Link>
                    </TableCell>
                    <TableCell className="max-w-[260px]">
                      <div className="space-y-1">
                        <Badge variant="secondary">
                          {SOURCE_TYPE_LABELS[incident.source_type]}
                        </Badge>
                        <p
                          className="text-xs text-muted-foreground truncate"
                          title={incident.source_url || ""}
                        >
                          {incident.source_url || "(No source URL)"}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          incident.severity === "error" ? "destructive" : "warning"
                        }
                      >
                        {incident.severity}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          incident.status === "failed" ? "destructive" : "secondary"
                        }
                      >
                        {incident.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="max-w-[420px]">
                      <p className="text-sm line-clamp-2" title={incident.message}>
                        {incident.message}
                      </p>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

