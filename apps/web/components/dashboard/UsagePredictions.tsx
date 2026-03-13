"use client";

import {
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  CheckCircle,
  Calendar,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface UsagePrediction {
  metric: string;
  currentUsage: number;
  limit: number;
  usagePercentage: number;
  daysRemaining: number;
  projectedEndOfPeriod: number;
  projectedPercentage: number;
  trend: "up" | "down" | "stable";
  dailyAverage: number;
}

interface UsagePredictionsProps {
  currentUsage: {
    messages_count: number;
    global_message_count: number;
    conversations_count: number;
    knowledge_pages_count: number;
    team_members_count: number;
    storage_mb: number;
    period_start: string;
    period_end: string;
  };
  planLimits: {
    messages_per_month: number;
    conversations_per_month: number;
    knowledge_pages: number;
    team_members: number;
    storage_mb: number;
  };
  usagePercentages: Record<string, number>;
}

function calculatePredictions(props: UsagePredictionsProps): UsagePrediction[] {
  const { currentUsage, planLimits, usagePercentages } = props;
  const now = new Date();
  const periodStart = new Date(currentUsage.period_start);
  const periodEnd = new Date(currentUsage.period_end);

  const totalDays = Math.max(
    1,
    Math.ceil(
      (periodEnd.getTime() - periodStart.getTime()) / (1000 * 60 * 60 * 24)
    )
  );
  const elapsedDays = Math.max(
    1,
    Math.ceil(
      (now.getTime() - periodStart.getTime()) / (1000 * 60 * 60 * 24)
    )
  );
  const daysRemaining = Math.max(0, totalDays - elapsedDays);

  const metrics: {
    name: string;
    current: number;
    limit: number;
    key: string;
  }[] = [
    {
      name: "Messages",
      current: currentUsage.global_message_count,
      limit: planLimits.messages_per_month,
      key: "messages",
    },
    {
      name: "Knowledge Pages",
      current: currentUsage.knowledge_pages_count,
      limit: planLimits.knowledge_pages,
      key: "knowledge_pages",
    },
    {
      name: "Storage (MB)",
      current: Math.round(parseFloat(currentUsage.storage_mb.toString())),
      limit: planLimits.storage_mb,
      key: "storage",
    },
  ];

  return metrics.map((m) => {
    const dailyAverage = elapsedDays > 0 ? m.current / elapsedDays : 0;
    const projectedTotal = Math.round(m.current + dailyAverage * daysRemaining);
    const projectedPercentage = m.limit > 0 ? (projectedTotal / m.limit) * 100 : 0;

    // Determine trend based on projected vs current rate
    const expectedAtThisPoint = (m.limit * elapsedDays) / totalDays;
    const trend =
      m.current > expectedAtThisPoint * 1.1
        ? "up"
        : m.current < expectedAtThisPoint * 0.9
          ? "down"
          : "stable";

    return {
      metric: m.name,
      currentUsage: m.current,
      limit: m.limit,
      usagePercentage: usagePercentages[m.key] || 0,
      daysRemaining,
      projectedEndOfPeriod: projectedTotal,
      projectedPercentage: Math.min(projectedPercentage, 200),
      trend,
      dailyAverage: Math.round(dailyAverage * 10) / 10,
    };
  });
}

function TrendIcon({ trend }: { trend: "up" | "down" | "stable" }) {
  if (trend === "up") return <TrendingUp className="h-3.5 w-3.5 text-amber-500" />;
  if (trend === "down") return <TrendingDown className="h-3.5 w-3.5 text-emerald-500" />;
  return <Minus className="h-3.5 w-3.5 text-muted-foreground" />;
}

export function UsagePredictions(props: UsagePredictionsProps) {
  const predictions = calculatePredictions(props);

  const anyOverLimit = predictions.some((p) => p.projectedPercentage > 100);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              Usage Predictions
            </CardTitle>
            <CardDescription>
              Projected usage by end of subscription period ({predictions[0]?.daysRemaining} days remaining)
            </CardDescription>
          </div>
          {anyOverLimit && (
            <Badge variant="destructive" className="flex items-center gap-1">
              <AlertTriangle className="h-3 w-3" />
              May exceed limits
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-5">
          {predictions.map((prediction) => {
            const willExceed = prediction.projectedPercentage > 100;
            const isWarning = prediction.projectedPercentage > 80;

            return (
              <div key={prediction.metric} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{prediction.metric}</span>
                    <TrendIcon trend={prediction.trend} />
                  </div>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span>
                      Current: {prediction.currentUsage.toLocaleString()} / {prediction.limit.toLocaleString()}
                    </span>
                  </div>
                </div>

                {/* Current usage bar */}
                <div className="space-y-1">
                  <Progress
                    value={Math.min(prediction.usagePercentage, 100)}
                    className="h-2"
                    indicatorClassName={cn(
                      prediction.usagePercentage >= 90
                        ? "bg-red-500"
                        : prediction.usagePercentage >= 75
                          ? "bg-amber-500"
                          : "bg-emerald-500"
                    )}
                  />
                </div>

                {/* Projected usage */}
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">
                    ~{prediction.dailyAverage}/day avg
                  </span>
                  <span
                    className={cn(
                      "font-medium flex items-center gap-1",
                      willExceed
                        ? "text-red-500"
                        : isWarning
                          ? "text-amber-500"
                          : "text-emerald-500"
                    )}
                  >
                    {willExceed ? (
                      <AlertTriangle className="h-3 w-3" />
                    ) : (
                      <CheckCircle className="h-3 w-3" />
                    )}
                    Projected: {prediction.projectedEndOfPeriod.toLocaleString()}{" "}
                    ({Math.round(prediction.projectedPercentage)}%)
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
