"use client";

import { useState, useEffect } from "react";
import {
  Check,
  Zap,
  Tag,
  Loader2,
  AlertCircle,
  ArrowRight,
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { apiRequestWithAuth } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { cn } from "@/lib/utils";

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

interface BillingResponse {
  available_plans: PlanFeatures[];
  current_plan: PlanFeatures;
}

export default function PricingPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [plans, setPlans] = useState<PlanFeatures[]>([]);
  const [currentPlan, setCurrentPlan] = useState<string | null>(null);
  const [billingCycle, setBillingCycle] = useState<"monthly" | "annual">(
    "monthly",
  );
  const [error, setError] = useState<string | null>(null);
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [showDialog, setShowDialog] = useState(false);
  const [isChangingPlan, setIsChangingPlan] = useState(false);

  const fetchPlans = async () => {
    try {
      setIsLoading(true);
      const token = getAccessToken();
      if (!token) return;

      const response = await apiRequestWithAuth<BillingResponse>(
        "/api/v1/billing/overview",
        token,
        { method: "GET" },
      );

      setPlans(response.available_plans);
      setCurrentPlan(response.current_plan.name.toLowerCase());
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to fetch pricing plans");
      console.error("Error fetching plans:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, []);

  const openDialog = (planType: string) => {
    setSelectedPlan(planType);
    setShowDialog(true);
  };

  const handleChangePlan = async () => {
    if (!selectedPlan) return;
    try {
      setIsChangingPlan(true);
      const token = getAccessToken();
      if (!token) return;

      const cycle = selectedPlan === "free" ? "monthly" : billingCycle;

      await apiRequestWithAuth("/api/v1/billing/change-plan", token, {
        method: "POST",
        body: JSON.stringify({
          new_plan: selectedPlan,
          billing_cycle: cycle,
        }),
      });

      await fetchPlans();
      setShowDialog(false);
      setSelectedPlan(null);
    } catch (err: any) {
      console.error("Failed to change plan:", err);
      alert(err.message || "Failed to change plan");
    } finally {
      setIsChangingPlan(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading pricing plans...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Pricing & Plans</h1>
        <p className="text-muted-foreground mt-2">
          Choose the perfect plan for your chatbot needs
        </p>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-red-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Error</p>
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Billing Cycle Toggle */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center gap-4">
            <span
              className={cn(
                "text-sm font-medium",
                billingCycle === "monthly"
                  ? "text-foreground"
                  : "text-muted-foreground",
              )}
            >
              Monthly
            </span>
            <button
              onClick={() =>
                setBillingCycle(
                  billingCycle === "monthly" ? "annual" : "monthly",
                )
              }
              className="relative inline-flex h-6 w-11 items-center rounded-full bg-muted"
            >
              <span
                className={cn(
                  "inline-block h-4 w-4 transform rounded-full bg-background transition-transform",
                  billingCycle === "annual" && "translate-x-5",
                )}
              />
            </button>
            <span
              className={cn(
                "text-sm font-medium",
                billingCycle === "annual"
                  ? "text-foreground"
                  : "text-muted-foreground",
              )}
            >
              Annual
              {billingCycle === "annual" && (
                <Badge variant="secondary" className="ml-2">
                  Save 20%
                </Badge>
              )}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((plan) => {
          const isCurrentPlan = currentPlan === plan.name.toLowerCase();
          const price =
            billingCycle === "monthly"
              ? plan.pricing.monthly_price
              : plan.pricing.annual_price;
          const pricePerMonth =
            billingCycle === "annual" ? (Number(price) / 12).toFixed(2) : price;

          return (
            <div
              key={plan.name}
              className={cn("relative", plan.popular && "md:scale-105 md:z-10")}
            >
              <Card
                className={cn(
                  "flex flex-col h-full",
                  plan.popular && "border-primary shadow-lg",
                  isCurrentPlan && "border-green-500",
                )}
              >
                {/* Popular Badge */}
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge className="bg-primary">Most Popular</Badge>
                  </div>
                )}

                {/* Current Plan Badge */}
                {isCurrentPlan && (
                  <div className="absolute -top-3 right-4">
                    <Badge className="bg-green-600">Current Plan</Badge>
                  </div>
                )}

                <CardHeader>
                  <CardTitle>{plan.name}</CardTitle>
                  <CardDescription>{plan.description}</CardDescription>

                  {/* Price */}
                  <div className="mt-4">
                    <div className="flex items-baseline gap-1">
                      <span className="text-4xl font-bold">
                        ${pricePerMonth}
                      </span>
                      <span className="text-muted-foreground">/month</span>
                    </div>
                    {billingCycle === "annual" && (
                      <p className="text-sm text-muted-foreground mt-1">
                        Billed ${price}/year
                      </p>
                    )}
                  </div>

                  {isCurrentPlan ? (
                    <Button className="w-full mt-4" variant="outline">
                      <Check className="mr-2 h-4 w-4" />
                      Current Plan
                    </Button>
                  ) : (
                    <Button
                      className="w-full mt-4"
                      onClick={() => openDialog(plan.name.toLowerCase())}
                    >
                      {plan.name === "Free" ? "Downgrade" : "Upgrade Now"}
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  )}
                </CardHeader>

                <CardContent className="flex-1">
                  <div className="space-y-4">
                    {/* Features */}
                    <div>
                      <h4 className="font-semibold mb-2">Features</h4>
                      <ul className="space-y-2">
                        {plan.features.map((feature, idx) => (
                          <li
                            key={idx}
                            className="flex items-start gap-2 text-sm"
                          >
                            <Check className="h-4 w-4 text-green-600 shrink-0 mt-0.5" />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Limits */}
                    <div className="border-t pt-4">
                      <h4 className="font-semibold mb-2">Limits</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">
                            Chatbots
                          </span>
                          <span className="font-medium">
                            {plan.limits.chatbots}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">
                            Messages/month
                          </span>
                          <span className="font-medium">
                            {plan.limits.messages_per_month.toLocaleString()}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">
                            Knowledge Pages
                          </span>
                          <span className="font-medium">
                            {plan.limits.knowledge_pages}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Storage</span>
                          <span className="font-medium">
                            {plan.limits.storage_mb}MB
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">
                            Team Members
                          </span>
                          <span className="font-medium">
                            {plan.limits.team_members}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          );
        })}
      </div>

      {/* FAQ or Info Section */}
      <Card>
        <CardHeader>
          <CardTitle>Need more information?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-semibold mb-1">Message Count</h4>
            <p className="text-sm text-muted-foreground">
              Global message count persists across chatbot deletions and
              recreations. This prevents users from circumventing limits by
              deleting and recreating bots.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-1">Knowledge Limits</h4>
            <p className="text-sm text-muted-foreground">
              Knowledge pages and file uploads are reset when you delete a
              chatbot, as they are specific to each chatbot's configuration.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-1">Need a custom plan?</h4>
            <p className="text-sm text-muted-foreground">
              Contact our sales team for enterprise licensing and custom
              requirements.
            </p>
          </div>
        </CardContent>
      </Card>

      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Plan Change</DialogTitle>
            <DialogDescription>
              This is a mock purchase. Your limits will update immediately.
            </DialogDescription>
          </DialogHeader>
          {selectedPlan && (
            <div className="py-2">
              <p className="font-medium capitalize">{selectedPlan}</p>
              <p className="text-sm text-muted-foreground">
                Billing: {selectedPlan === "free" ? "monthly" : billingCycle}
              </p>
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowDialog(false)}
              disabled={isChangingPlan}
            >
              Cancel
            </Button>
            <Button onClick={handleChangePlan} disabled={isChangingPlan}>
              {isChangingPlan ? "Processing..." : "Confirm"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
