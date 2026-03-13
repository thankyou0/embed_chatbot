"use client";

import React from "react";
import { useRouter } from "next/navigation";
import {
  BarChart3,
  MessageSquare,
  Database,
  TrendingUp,
  Users,
  Settings,
  Download,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import {
  OverlayLoader,
  InlineSpinner,
} from "@/components/ui/loading";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { ChatbotStats, RecentActivity } from "../types";

interface OverviewTabProps {
  chatbotId: string;
  stats: ChatbotStats | null;
  recentActivity: RecentActivity[];
  recentActivityPage: number;
  recentActivityTotal: number;
  recentActivityTotalPages: number;
  isLoadingRecentActivity: boolean;
  isExportingRecentActivity: boolean;
  navigationTarget: "analytics" | "usage" | null;
  setNavigationTarget: (target: "analytics" | "usage" | null) => void;
  setActiveTab: (tab: string) => void;
  fetchRecentActivity: (page?: number) => void;
  handleExportRecentActivity: () => void;
  getActivityPaginationItems: () => Array<number | "ellipsis-left" | "ellipsis-right">;
}

export function OverviewTab({
  chatbotId,
  stats,
  recentActivity,
  recentActivityPage,
  recentActivityTotal,
  recentActivityTotalPages,
  isLoadingRecentActivity,
  isExportingRecentActivity,
  navigationTarget,
  setNavigationTarget,
  setActiveTab,
  fetchRecentActivity,
  handleExportRecentActivity,
  getActivityPaginationItems,
}: OverviewTabProps) {
  const router = useRouter();

  return (
    <div className="space-y-6">
      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-l-4 border-l-emerald-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Conversations
            </CardTitle>
            <div className="p-2 rounded-lg bg-emerald-50">
              <MessageSquare className="h-4 w-4 text-emerald-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-600">
              {stats?.total_conversations || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              {stats?.total_conversations === 0
                ? "New chatbot"
                : "Active conversations"}
            </p>
          </CardContent>
        </Card>

        <Card
          className="cursor-pointer hover:bg-muted/50 transition-colors border-l-4 border-l-emerald-500"
          onClick={() => setActiveTab("knowledge")}
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Knowledge Sources
            </CardTitle>
            <div className="p-2 rounded-lg bg-emerald-50">
              <Database className="h-4 w-4 text-emerald-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-600">
              {stats?.total_knowledge_sources || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              {stats?.knowledge_breakdown?.total_crawled_urls || 0} crawl sites
              •{" "}
              {stats?.knowledge_breakdown?.total_uploaded_files || 0} files •{" "}
              {stats?.knowledge_breakdown?.total_qa_pairs || 0} Q&A
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-teal-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Knowledge Base Size
            </CardTitle>
            <div className="p-2 rounded-lg bg-teal-50">
              <Database className="h-4 w-4 text-teal-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-teal-600">
              {stats?.total_kb_size
                ? stats.total_kb_size >= 1024 * 1024
                  ? `${(stats.total_kb_size / (1024 * 1024)).toFixed(2)} MB`
                  : `${(stats.total_kb_size / 1024).toFixed(1)} KB`
                : "0.0 KB"}
            </div>
            <p className="text-xs text-muted-foreground">
              Total indexed content
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks to manage your chatbot</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <Button
              variant="outline"
              className={cn(
                "h-auto flex-col items-start p-4 relative overflow-hidden",
                navigationTarget === "analytics" &&
                  "bg-accent/40 ring-1 ring-primary/30",
              )}
              disabled={navigationTarget !== null}
              onClick={() => {
                setNavigationTarget("analytics");
                router.push(`/dashboard/analytics?chatbot_id=${chatbotId}`);
              }}
            >
              {navigationTarget === "analytics" && (
                <div className="loading-shimmer" aria-hidden="true" />
              )}
              <BarChart3 className="h-5 w-5 mb-2" />
              <div className="text-left">
                <div className="font-semibold">View Analytics</div>
                <div className="text-xs text-muted-foreground mt-1">
                  See usage and performance
                </div>
              </div>
            </Button>
            <Button
              variant="outline"
              className={cn(
                "h-auto flex-col items-start p-4 relative overflow-hidden",
                navigationTarget === "usage" &&
                  "bg-accent/40 ring-1 ring-primary/30",
              )}
              disabled={navigationTarget !== null}
              onClick={() => {
                setNavigationTarget("usage");
                router.push(`/dashboard/usage?chatbot_id=${chatbotId}`);
              }}
            >
              {navigationTarget === "usage" && (
                <div className="loading-shimmer" aria-hidden="true" />
              )}
              <TrendingUp className="h-5 w-5 mb-2" />
              <div className="text-left">
                <div className="font-semibold">Show Usage</div>
                <div className="text-xs text-muted-foreground mt-1">
                  Message counts and usage
                </div>
              </div>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest updates and changes to this chatbot
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline">{recentActivityTotal} total</Badge>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleExportRecentActivity}
              disabled={isExportingRecentActivity}
            >
              {isExportingRecentActivity ? (
                <InlineSpinner size="sm" className="mr-2" />
              ) : (
                <Download className="h-4 w-4 mr-2" />
              )}
              Export All
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="relative">
            {recentActivity.length > 0 ? (
              <div
                className={cn(
                  "space-y-4 transition-opacity",
                  isLoadingRecentActivity ? "opacity-60" : "opacity-100",
                )}
              >
                {recentActivity.map((item) => {
                  const isTeamActivity =
                    item.type === "team_member_added" ||
                    item.type === "team_member_updated" ||
                    item.type === "team_member_removed" ||
                    item.type === "team_permissions_updated";

                  return (
                    <div
                      key={item.id}
                      className="flex items-start gap-4 text-sm"
                    >
                      <div
                        className={cn(
                          "mt-1 p-1.5 rounded-full",
                          item.type === "knowledge_source"
                            ? "bg-emerald-50 text-emerald-600"
                            : item.type === "conversation"
                              ? "bg-emerald-50 text-emerald-600"
                              : isTeamActivity
                                ? "bg-teal-50 text-teal-600"
                                : "bg-slate-100 text-slate-600",
                        )}
                      >
                        {item.type === "knowledge_source" ? (
                          <Database className="h-3.5 w-3.5" />
                        ) : item.type === "conversation" ? (
                          <MessageSquare className="h-3.5 w-3.5" />
                        ) : isTeamActivity ? (
                          <Users className="h-3.5 w-3.5" />
                        ) : (
                          <Settings className="h-3.5 w-3.5" />
                        )}
                      </div>
                      <div className="flex-1 space-y-0.5">
                        <p className="font-medium text-foreground">
                          {item.description}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(item.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  );
                })}
                <div className="flex items-center justify-between border-t pt-3">
                  <p className="text-xs text-muted-foreground">
                    Page{" "}
                    {recentActivityTotalPages > 0 ? recentActivityPage : 0}{" "}
                    of {recentActivityTotalPages}
                  </p>
                  <div className="flex items-center gap-1">
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      className="h-8 w-8"
                      disabled={
                        recentActivityPage <= 1 || isLoadingRecentActivity
                      }
                      onClick={() =>
                        fetchRecentActivity(recentActivityPage - 1)
                      }
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    {getActivityPaginationItems().map((pageItem, index) =>
                      typeof pageItem === "number" ? (
                        <Button
                          type="button"
                          key={pageItem}
                          variant={
                            pageItem === recentActivityPage
                              ? "default"
                              : "outline"
                          }
                          size="icon"
                          className="h-8 w-8"
                          disabled={isLoadingRecentActivity}
                          onClick={() => fetchRecentActivity(pageItem)}
                        >
                          {pageItem}
                        </Button>
                      ) : (
                        <span
                          key={`${pageItem}-${index}`}
                          className="px-2 text-sm text-muted-foreground"
                        >
                          ...
                        </span>
                      ),
                    )}
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      className="h-8 w-8"
                      disabled={
                        recentActivityTotalPages === 0 ||
                        recentActivityPage >= recentActivityTotalPages ||
                        isLoadingRecentActivity
                      }
                      onClick={() =>
                        fetchRecentActivity(recentActivityPage + 1)
                      }
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="min-h-[72px] flex items-center text-sm text-muted-foreground">
                {isLoadingRecentActivity
                  ? "Loading recent activity..."
                  : "No recent activity to display."}
              </div>
            )}
            {isLoadingRecentActivity && recentActivity.length > 0 && (
              <OverlayLoader />
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
