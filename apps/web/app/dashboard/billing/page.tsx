"use client";

import { useState, useEffect } from "react";
import { toast } from "@/lib/notify-toast";
import { useAuth } from "@/contexts/AuthContext";
import { useHeaderContent } from "@/contexts/HeaderContext";
import {
  Check,
  TrendingUp,
  Calendar,
  CreditCard,
  AlertCircle,
  Download,
  MessageSquare,
  Users,
  Database,
  FileText,
  Zap,
  HardDrive,
  Bot,
} from "lucide-react";
import { SectionLoader, ButtonSpinner } from "@/components/ui/loading";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { apiRequestWithAuth } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { cn } from "@/lib/utils";
import { UsagePredictions } from "@/components/dashboard/UsagePredictions";

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

interface PlanPricing {
  monthly_price: number;
  annual_price: number;
  annual_discount_percent: number;
}

interface PlanFeatures {
  name: string;
  description: string;
  limits: PlanLimits;
  pricing: PlanPricing;
  features: string[];
  popular: boolean;
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

interface Subscription {
  id: string;
  tenant_id: number;
  plan_type: string;
  billing_cycle: string | null;
  status: string;
  current_period_start: string;
  current_period_end: string;
  trial_end: string | null;
  cancelled_at: string | null;
  created_at: string;
  updated_at: string;
}

interface UsageWithLimits {
  current_usage: CurrentUsage;
  plan_limits: PlanLimits;
  usage_percentages: Record<string, number>;
}

interface BillingHistoryItem {
  id: string;
  amount: number;
  description: string;
  invoice_number: string | null;
  payment_status: string;
  billing_period_start: string;
  billing_period_end: string;
  created_at: string;
}

interface BillingOverview {
  subscription: Subscription;
  current_plan: PlanFeatures;
  usage: UsageWithLimits;
  billing_history: BillingHistoryItem[];
  available_plans: PlanFeatures[];
}

export default function BillingPage() {
  const { user, isAdmin } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [billingData, setBillingData] = useState<BillingOverview | null>(null);
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [billingCycle, setBillingCycle] = useState<"monthly" | "annual">(
    "monthly",
  );
  const [showUpgradeDialog, setShowUpgradeDialog] = useState(false);
  const [isUpgrading, setIsUpgrading] = useState(false);
  const { setContent } = useHeaderContent();

  useEffect(() => {
    setContent({ title: "Subscription", description: "Manage your subscription and plan information" });
    return () => setContent(null);
  }, [setContent]);

  useEffect(() => {
    fetchBillingData();
  }, []);

  const fetchBillingData = async () => {
    try {
      setIsLoading(true);
      const token = getAccessToken();
      if (!token) return;

      const data = await apiRequestWithAuth<BillingOverview>(
        "/api/v1/billing/overview",
        token,
        { method: "GET" },
      );
      setBillingData(data);
    } catch (err) {
      console.error("Failed to fetch billing data:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpgrade = async () => {
    if (!selectedPlan || !isAdmin) return;

    try {
      setIsUpgrading(true);
      const token = getAccessToken();
      if (!token) return;

      await apiRequestWithAuth("/api/v1/billing/change-plan", token, {
        method: "POST",
        body: JSON.stringify({
          new_plan: selectedPlan,
          billing_cycle: billingCycle,
        }),
      });

      // Refresh data
      await fetchBillingData();
      setShowUpgradeDialog(false);
      setSelectedPlan(null);
    } catch (err: any) {
      console.error("Failed to upgrade plan:", err);
      toast.error(err.message || "Failed to upgrade plan");
    } finally {
      setIsUpgrading(false);
    }
  };

  const openUpgradeDialog = (planType: string) => {
    setSelectedPlan(planType);
    setShowUpgradeDialog(true);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat("en-US").format(num);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
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
    return <SectionLoader />;
  }

  if (!billingData) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            Failed to load subscription information
          </CardContent>
        </Card>
      </div>
    );
  }

  const {
    subscription,
    current_plan,
    usage,
    billing_history,
    available_plans,
  } = billingData;

  return (
    <div className="space-y-6">

      {/* Current Plan Overview */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Current Plan</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{current_plan.name}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {subscription.billing_cycle
                ? `${formatCurrency(
                    subscription.billing_cycle === "annual"
                      ? current_plan.pricing.annual_price / 12
                      : current_plan.pricing.monthly_price,
                  )}/month`
                : "Free"}
            </p>
            <Badge
              variant={
                subscription.status === "active" ? "default" : "secondary"
              }
              className="mt-2"
            >
              {subscription.status}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Subscription Period
            </CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatDate(subscription.current_period_start)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Renews on {formatDate(subscription.current_period_end)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Next Payment</CardTitle>
            <CreditCard className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {subscription.plan_type === "free"
                ? formatCurrency(0)
                : formatCurrency(
                    subscription.billing_cycle === "annual"
                      ? current_plan.pricing.annual_price
                      : current_plan.pricing.monthly_price,
                  )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Due {formatDate(subscription.current_period_end)}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Usage Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Current Usage</CardTitle>
          <CardDescription>
            Your usage from {formatDate(usage.current_usage.period_start)} to{" "}
            {formatDate(usage.current_usage.period_end)}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Chatbots */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <Bot className="h-4 w-4 text-muted-foreground" />
                <span>Chatbots</span>
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

          {/* Messages (Global Count) */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
                <span>Total Messages (Global)</span>
                <span className="text-xs text-muted-foreground">
                  (persists after bot deletion)
                </span>
              </div>
              <span
                className={cn(
                  "font-medium",
                  getUsageColor(usage.usage_percentages.messages),
                )}
              >
                {formatNumber(usage.current_usage.global_message_count)} /{" "}
                {formatNumber(usage.plan_limits.messages_per_month)}
              </span>
            </div>
            <Progress
              value={Math.min(usage.usage_percentages.messages, 100)}
              className="h-2"
              indicatorClassName={getProgressColor(
                usage.usage_percentages.messages,
              )}
            />
          </div>

          {/* Team Members */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-muted-foreground" />
                <span>Team Members</span>
              </div>
              <span
                className={cn(
                  "font-medium",
                  getUsageColor(usage.usage_percentages.team_members),
                )}
              >
                {usage.current_usage.team_members_count} /{" "}
                {usage.plan_limits.team_members}
              </span>
            </div>
            <Progress
              value={Math.min(usage.usage_percentages.team_members, 100)}
              className="h-2"
              indicatorClassName={getProgressColor(
                usage.usage_percentages.team_members,
              )}
            />
          </div>

          {/* Knowledge Pages */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-muted-foreground" />
                <span>Knowledge Pages</span>
              </div>
              <span
                className={cn(
                  "font-medium",
                  getUsageColor(usage.usage_percentages.knowledge_pages),
                )}
              >
                {formatNumber(usage.current_usage.knowledge_pages_count)} /{" "}
                {formatNumber(usage.plan_limits.knowledge_pages)}
              </span>
            </div>
            <Progress
              value={Math.min(usage.usage_percentages.knowledge_pages, 100)}
              className="h-2"
              indicatorClassName={getProgressColor(
                usage.usage_percentages.knowledge_pages,
              )}
            />
          </div>

          {/* Storage */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <HardDrive className="h-4 w-4 text-muted-foreground" />
                <span>Storage</span>
              </div>
              <span
                className={cn(
                  "font-medium",
                  getUsageColor(usage.usage_percentages.storage),
                )}
              >
                {Math.round(
                  parseFloat(usage.current_usage.storage_mb.toString()),
                )}{" "}
                MB / {formatNumber(usage.plan_limits.storage_mb)} MB
              </span>
            </div>
            <Progress
              value={Math.min(usage.usage_percentages.storage, 100)}
              className="h-2"
              indicatorClassName={getProgressColor(
                usage.usage_percentages.storage,
              )}
            />
          </div>
        </CardContent>
      </Card>

      {/* Usage Predictions */}
      <UsagePredictions
        currentUsage={usage.current_usage}
        planLimits={usage.plan_limits}
        usagePercentages={usage.usage_percentages}
      />

      {/* Payment History (Enhanced) */}
      {billing_history.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Payment History</CardTitle>
                <CardDescription>
                  Your past invoices and payments
                </CardDescription>
              </div>
              <Badge variant="secondary" className="text-xs">
                {billing_history.length} transaction{billing_history.length !== 1 ? "s" : ""}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {/* Table-style header */}
            <div className="hidden sm:grid grid-cols-[1fr_120px_100px_40px] gap-4 px-4 py-2 text-xs font-medium text-muted-foreground uppercase tracking-wider border-b mb-2">
              <span>Description</span>
              <span className="text-right">Amount</span>
              <span className="text-center">Status</span>
              <span></span>
            </div>
            <div className="space-y-1">
              {billing_history.map((item) => (
                <div
                  key={item.id}
                  className="grid sm:grid-cols-[1fr_120px_100px_40px] gap-2 sm:gap-4 items-center py-3 px-4 rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="space-y-0.5">
                    <p className="font-medium text-sm">{item.description}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatDate(item.created_at)}
                      {item.invoice_number && (
                        <span className="ml-2 font-mono text-[10px] text-muted-foreground/70">
                          {item.invoice_number}
                        </span>
                      )}
                    </p>
                    <p className="text-[10px] text-muted-foreground/60">
                      {formatDate(item.billing_period_start)} — {formatDate(item.billing_period_end)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-sm">
                      {formatCurrency(item.amount)}
                    </p>
                  </div>
                  <div className="flex justify-center">
                    <Badge
                      variant={
                        item.payment_status === "paid"
                          ? "default"
                          : item.payment_status === "pending"
                            ? "secondary"
                            : "destructive"
                      }
                      className="text-[10px]"
                    >
                      {item.payment_status}
                    </Badge>
                  </div>
                  <div className="flex justify-end">
                    <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Download invoice">
                      <Download className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Pricing Plans */}
      <div>
        <div className="mb-6">
          <h2 className="text-2xl font-bold">Available Plans</h2>
          <p className="text-muted-foreground">
            Choose the plan that fits your needs
          </p>
        </div>

        <Tabs defaultValue="monthly" className="space-y-6">
          <div className="flex justify-center">
            <TabsList>
              <TabsTrigger value="monthly">Monthly</TabsTrigger>
              <TabsTrigger value="annual">
                Annual
                <Badge variant="secondary" className="ml-2">
                  Save 20%
                </Badge>
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="monthly" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-3">
              {available_plans.map((plan) => (
                <Card
                  key={plan.name}
                  className={cn(
                    "relative",
                    plan.popular && "border-primary shadow-lg",
                    subscription.plan_type === plan.name.toLowerCase() &&
                      "border-green-500",
                  )}
                >
                  {plan.popular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <Badge>Most Popular</Badge>
                    </div>
                  )}
                  {subscription.plan_type === plan.name.toLowerCase() && (
                    <div className="absolute -top-3 right-4">
                      <Badge
                        variant="outline"
                        className="bg-green-500/10 text-green-500 border-green-500"
                      >
                        Current Plan
                      </Badge>
                    </div>
                  )}
                  <CardHeader>
                    <CardTitle>{plan.name}</CardTitle>
                    <CardDescription>{plan.description}</CardDescription>
                    <div className="mt-4">
                      <span className="text-4xl font-bold">
                        {formatCurrency(plan.pricing.monthly_price)}
                      </span>
                      <span className="text-muted-foreground">/month</span>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <ul className="space-y-2">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          <span className="text-sm">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                  <CardFooter>
                    {subscription.plan_type === plan.name.toLowerCase() ? (
                      <Button className="w-full" disabled>
                        Current Plan
                      </Button>
                    ) : (
                      <Button
                        className="w-full"
                        variant={plan.popular ? "default" : "outline"}
                        onClick={() =>
                          openUpgradeDialog(plan.name.toLowerCase())
                        }
                        disabled={!isAdmin}
                      >
                        {subscription.plan_type === "free"
                          ? "Upgrade"
                          : plan.name === "Free"
                            ? "Downgrade"
                            : "Change Plan"}
                      </Button>
                    )}
                  </CardFooter>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="annual" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-3">
              {available_plans.map((plan) => (
                <Card
                  key={plan.name}
                  className={cn(
                    "relative",
                    plan.popular && "border-primary shadow-lg",
                    subscription.plan_type === plan.name.toLowerCase() &&
                      subscription.billing_cycle === "annual" &&
                      "border-green-500",
                  )}
                >
                  {plan.popular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <Badge>Most Popular</Badge>
                    </div>
                  )}
                  {subscription.plan_type === plan.name.toLowerCase() &&
                    subscription.billing_cycle === "annual" && (
                      <div className="absolute -top-3 right-4">
                        <Badge
                          variant="outline"
                          className="bg-green-500/10 text-green-500 border-green-500"
                        >
                          Current Plan
                        </Badge>
                      </div>
                    )}
                  <CardHeader>
                    <CardTitle>{plan.name}</CardTitle>
                    <CardDescription>{plan.description}</CardDescription>
                    <div className="mt-4">
                      <span className="text-4xl font-bold">
                        {formatCurrency(plan.pricing.annual_price / 12)}
                      </span>
                      <span className="text-muted-foreground">/month</span>
                      <div className="text-sm text-muted-foreground mt-1">
                        {formatCurrency(plan.pricing.annual_price)} billed
                        annually
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <ul className="space-y-2">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          <span className="text-sm">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                  <CardFooter>
                    {subscription.plan_type === plan.name.toLowerCase() &&
                    subscription.billing_cycle === "annual" ? (
                      <Button className="w-full" disabled>
                        Current Plan
                      </Button>
                    ) : (
                      <Button
                        className="w-full"
                        variant={plan.popular ? "default" : "outline"}
                        onClick={() => {
                          setBillingCycle("annual");
                          openUpgradeDialog(plan.name.toLowerCase());
                        }}
                        disabled={!isAdmin || plan.name === "Free"}
                      >
                        {plan.name === "Free"
                          ? "Not Available"
                          : subscription.plan_type === "free"
                            ? "Upgrade"
                            : "Change Plan"}
                      </Button>
                    )}
                  </CardFooter>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Admin Warning */}
      {!isAdmin && (
        <Card className="border-amber-500/50 bg-amber-500/10">
          <CardContent className="py-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-amber-500 mt-0.5" />
              <div>
                <p className="font-medium text-amber-500">
                  Admin Access Required
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  Only administrators can change subscription plans. Contact
                  your admin to upgrade or downgrade your plan.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Upgrade Dialog */}
      <Dialog open={showUpgradeDialog} onOpenChange={setShowUpgradeDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Change Subscription Plan</DialogTitle>
            <DialogDescription>
              Confirm your plan change. This will take effect immediately.
            </DialogDescription>
          </DialogHeader>
          {selectedPlan && (
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Selected Plan</Label>
                <div className="p-4 border rounded-lg">
                  <p className="font-medium capitalize">{selectedPlan}</p>
                  <p className="text-sm text-muted-foreground">
                    {
                      available_plans.find(
                        (p) => p.name.toLowerCase() === selectedPlan,
                      )?.description
                    }
                  </p>
                </div>
              </div>

              {selectedPlan !== "free" && (
                <div className="space-y-2">
                  <Label>Payment Cycle</Label>
                  <RadioGroup
                    value={billingCycle}
                    onValueChange={(value) =>
                      setBillingCycle(value as "monthly" | "annual")
                    }
                  >
                    <div className="flex items-center space-x-2 p-3 border rounded-lg">
                      <RadioGroupItem value="monthly" id="monthly" />
                      <Label
                        htmlFor="monthly"
                        className="flex-1 cursor-pointer"
                      >
                        <div className="flex justify-between">
                          <span>Monthly</span>
                          <span className="font-medium">
                            {formatCurrency(
                              available_plans.find(
                                (p) => p.name.toLowerCase() === selectedPlan,
                              )?.pricing.monthly_price || 0,
                            )}
                            /mo
                          </span>
                        </div>
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2 p-3 border rounded-lg">
                      <RadioGroupItem value="annual" id="annual" />
                      <Label htmlFor="annual" className="flex-1 cursor-pointer">
                        <div className="flex justify-between">
                          <div>
                            <span>Annual</span>
                            <Badge variant="secondary" className="ml-2">
                              Save 20%
                            </Badge>
                          </div>
                          <span className="font-medium">
                            {formatCurrency(
                              (available_plans.find(
                                (p) => p.name.toLowerCase() === selectedPlan,
                              )?.pricing.annual_price || 0) / 12,
                            )}
                            /mo
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatCurrency(
                            available_plans.find(
                              (p) => p.name.toLowerCase() === selectedPlan,
                            )?.pricing.annual_price || 0,
                          )}{" "}
                          billed annually
                        </p>
                      </Label>
                    </div>
                  </RadioGroup>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowUpgradeDialog(false)}
              disabled={isUpgrading}
            >
              Cancel
            </Button>
            <Button onClick={handleUpgrade} disabled={isUpgrading}>
              {isUpgrading ? (
                <>
                  <ButtonSpinner />
                  Changing Plan...
                </>
              ) : (
                "Confirm Change"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
