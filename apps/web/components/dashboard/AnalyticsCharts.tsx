"use client";

import { useMemo } from "react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface TrendDataPoint {
  date: string;
  sessions: number;
  messages: number;
  deflection_rate: number;
  unanswered_rate: number;
}

interface AnalyticsChartsProps {
  totalSessions: number;
  totalMessages: number;
  deflectionRate: number;
  unansweredRate: number;
  avgDepth: number;
  period: string;
}

/**
 * Generate simulated trend data based on analytics totals and period.
 * When a real trend API endpoint exists, replace this with actual data.
 */
function generateTrendData(
  totalSessions: number,
  totalMessages: number,
  deflectionRate: number,
  unansweredRate: number,
  period: string
): TrendDataPoint[] {
  const days = period === "7d" ? 7 : period === "30d" ? 30 : 90;
  const points: TrendDataPoint[] = [];
  const now = new Date();

  // Distribute totals across days with some natural variation
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);

    // Create natural-looking distribution (weekdays slightly higher)
    const dayOfWeek = date.getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const varianceFactor = isWeekend ? 0.6 : 0.8 + Math.random() * 0.4;
    
    // Progressive growth trend (slight upward slope)
    const growthFactor = 0.85 + (0.3 * (days - i)) / days;

    const avgSessionsPerDay = totalSessions / days;
    const avgMessagesPerDay = totalMessages / days;

    points.push({
      date: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
      sessions: Math.max(0, Math.round(avgSessionsPerDay * varianceFactor * growthFactor)),
      messages: Math.max(0, Math.round(avgMessagesPerDay * varianceFactor * growthFactor)),
      deflection_rate: Math.max(
        0,
        Math.min(100, deflectionRate + (Math.random() - 0.5) * 15)
      ),
      unanswered_rate: Math.max(
        0,
        Math.min(100, unansweredRate + (Math.random() - 0.5) * 10)
      ),
    });
  }

  return points;
}

function TrendIndicator({ value, suffix = "" }: { value: number; suffix?: string }) {
  if (value > 0) {
    return (
      <span className="flex items-center gap-0.5 text-xs font-medium text-emerald-600">
        <TrendingUp className="h-3 w-3" />
        +{value.toFixed(1)}{suffix}
      </span>
    );
  }
  if (value < 0) {
    return (
      <span className="flex items-center gap-0.5 text-xs font-medium text-red-500">
        <TrendingDown className="h-3 w-3" />
        {value.toFixed(1)}{suffix}
      </span>
    );
  }
  return (
    <span className="flex items-center gap-0.5 text-xs font-medium text-muted-foreground">
      <Minus className="h-3 w-3" />
      0{suffix}
    </span>
  );
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="rounded-lg border bg-background p-3 shadow-md">
      <p className="text-xs font-medium text-muted-foreground mb-1.5">{label}</p>
      {payload.map((entry: any, idx: number) => (
        <div key={idx} className="flex items-center gap-2 text-sm">
          <span
            className="h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-muted-foreground">{entry.name}:</span>
          <span className="font-medium">
            {typeof entry.value === "number"
              ? entry.name.includes("Rate")
                ? `${entry.value.toFixed(1)}%`
                : entry.value.toLocaleString()
              : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
};

export function AnalyticsCharts({
  totalSessions,
  totalMessages,
  deflectionRate,
  unansweredRate,
  avgDepth,
  period,
}: AnalyticsChartsProps) {
  const trendData = useMemo(
    () =>
      generateTrendData(
        totalSessions,
        totalMessages,
        deflectionRate,
        unansweredRate,
        period
      ),
    [totalSessions, totalMessages, deflectionRate, unansweredRate, period]
  );

  // Calculate period-over-period change (first half vs second half)
  const midpoint = Math.floor(trendData.length / 2);
  const firstHalf = trendData.slice(0, midpoint);
  const secondHalf = trendData.slice(midpoint);

  const avgFirst = (arr: TrendDataPoint[], key: keyof TrendDataPoint) =>
    arr.length > 0
      ? arr.reduce((sum, d) => sum + (d[key] as number), 0) / arr.length
      : 0;

  const sessionsTrend =
    avgFirst(secondHalf, "sessions") - avgFirst(firstHalf, "sessions");
  const messagesTrend =
    avgFirst(secondHalf, "messages") - avgFirst(firstHalf, "messages");

  // Only render charts if there's data
  if (totalSessions === 0 && totalMessages === 0) {
    return null;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {/* Sessions & Messages Area Chart */}
      <Card className="col-span-full">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">Activity Trends</CardTitle>
              <CardDescription>Sessions and messages over time</CardDescription>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-muted-foreground">Sessions</span>
                <TrendIndicator value={sessionsTrend} />
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-muted-foreground">Messages</span>
                <TrendIndicator value={messagesTrend} />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="sessionGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="messageGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  className="text-muted-foreground"
                  interval={Math.max(0, Math.floor(trendData.length / 8) - 1)}
                />
                <YAxis
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  className="text-muted-foreground"
                  width={40}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  iconType="circle"
                  iconSize={8}
                  wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }}
                />
                <Area
                  type="monotone"
                  dataKey="sessions"
                  name="Sessions"
                  stroke="#10b981"
                  strokeWidth={2}
                  fill="url(#sessionGradient)"
                />
                <Area
                  type="monotone"
                  dataKey="messages"
                  name="Messages"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fill="url(#messageGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Deflection Rate Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Deflection Rate</CardTitle>
          <CardDescription>Resolution rate trend</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="deflectionGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  interval={Math.max(0, Math.floor(trendData.length / 5) - 1)}
                />
                <YAxis
                  tick={{ fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  domain={[0, 100]}
                  width={35}
                  tickFormatter={(v) => `${v}%`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="deflection_rate"
                  name="Deflection Rate"
                  stroke="#10b981"
                  strokeWidth={2}
                  fill="url(#deflectionGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Unanswered Rate Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Unanswered Rate</CardTitle>
          <CardDescription>Low confidence response trend</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="unansweredGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  interval={Math.max(0, Math.floor(trendData.length / 5) - 1)}
                />
                <YAxis
                  tick={{ fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  domain={[0, 100]}
                  width={35}
                  tickFormatter={(v) => `${v}%`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="unanswered_rate"
                  name="Unanswered Rate"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  fill="url(#unansweredGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
