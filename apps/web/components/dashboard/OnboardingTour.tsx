"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Bot,
  BarChart3,
  CreditCard,
  Settings,
  Command,
  Sparkles,
  ArrowRight,
  X,
  CheckCircle2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface TourStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  action?: { label: string; href: string };
}

const TOUR_STORAGE_KEY = "embedchat-onboarding-completed";

const tourSteps: TourStep[] = [
  {
    id: "welcome",
    title: "Welcome to EmbedChat! 🎉",
    description:
      "Let's take a quick tour to help you get started with your AI chatbot platform.",
    icon: <Sparkles className="h-6 w-6" />,
  },
  {
    id: "chatbots",
    title: "Create Your First Chatbot",
    description:
      "Head over to the Chatbots page to create and configure your AI assistant. You can customize its appearance, knowledge base, and behavior.",
    icon: <Bot className="h-6 w-6" />,
    action: { label: "Go to Chatbots", href: "/dashboard/chatbots" },
  },
  {
    id: "analytics",
    title: "Track Performance",
    description:
      "The Analytics page shows real-time metrics about your chatbot's performance, including session counts, message volumes, and deflection rates.",
    icon: <BarChart3 className="h-6 w-6" />,
    action: { label: "View Analytics", href: "/dashboard/analytics" },
  },
  {
    id: "usage",
    title: "Manage Your Plan",
    description:
      "Check your usage, compare plans, and manage your subscription from the Usage page. Start with the free tier and upgrade as you grow.",
    icon: <CreditCard className="h-6 w-6" />,
    action: { label: "See Plans", href: "/dashboard/usage" },
  },
  {
    id: "shortcuts",
    title: "Pro Tip: Keyboard Shortcuts",
    description:
      "Press Ctrl+K (or ⌘K on Mac) anytime to open the Command Palette for quick navigation and actions. It's the fastest way to get around!",
    icon: <Command className="h-6 w-6" />,
  },
];

export function OnboardingTour() {
  const [isVisible, setIsVisible] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [isCompleting, setIsCompleting] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Check if tour has been completed
    try {
      const completed = localStorage.getItem(TOUR_STORAGE_KEY);
      if (!completed) {
        // Show tour after a brief delay for page to render
        const timer = setTimeout(() => setIsVisible(true), 1500);
        return () => clearTimeout(timer);
      }
    } catch {}
  }, []);

  const completeTour = useCallback(() => {
    setIsCompleting(true);
    try {
      localStorage.setItem(TOUR_STORAGE_KEY, new Date().toISOString());
    } catch {}
    setTimeout(() => {
      setIsVisible(false);
      setIsCompleting(false);
    }, 300);
  }, []);

  const nextStep = useCallback(() => {
    if (currentStep < tourSteps.length - 1) {
      setCurrentStep((prev) => prev + 1);
    } else {
      completeTour();
    }
  }, [currentStep, completeTour]);

  const prevStep = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
    }
  }, [currentStep]);

  const skipTour = useCallback(() => {
    completeTour();
  }, [completeTour]);

  if (!isVisible) return null;

  const step = tourSteps[currentStep];
  const isLastStep = currentStep === tourSteps.length - 1;
  const progress = ((currentStep + 1) / tourSteps.length) * 100;

  return (
    <>
      {/* Backdrop */}
      <div
        className={cn(
          "fixed inset-0 z-[60] bg-black/40 backdrop-blur-sm transition-opacity duration-300",
          isCompleting ? "opacity-0" : "opacity-100"
        )}
        onClick={skipTour}
        aria-hidden="true"
      />

      {/* Tour Card */}
      <div
        className={cn(
          "fixed z-[60] bottom-6 right-6 w-full max-w-sm transition-all duration-300",
          isCompleting ? "opacity-0 translate-y-4" : "opacity-100 translate-y-0"
        )}
        role="dialog"
        aria-modal="true"
        aria-label="Onboarding tour"
      >
        <div className="bg-card border rounded-xl shadow-2xl overflow-hidden">
          {/* Progress bar */}
          <div className="h-1 bg-muted">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
              role="progressbar"
              aria-valuenow={currentStep + 1}
              aria-valuemin={1}
              aria-valuemax={tourSteps.length}
            />
          </div>

          <div className="p-6">
            {/* Header with close button */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500/10 to-teal-500/10 text-emerald-600 dark:text-emerald-400">
                  {step.icon}
                </div>
                <div>
                  <h3 className="font-semibold text-base">{step.title}</h3>
                  <p className="text-[10px] text-muted-foreground mt-0.5">
                    Step {currentStep + 1} of {tourSteps.length}
                  </p>
                </div>
              </div>
              <button
                onClick={skipTour}
                className="text-muted-foreground hover:text-foreground transition-colors p-1"
                aria-label="Close tour"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Description */}
            <p className="text-sm text-muted-foreground leading-relaxed mb-5">
              {step.description}
            </p>

            {/* Action link */}
            {step.action && (
              <button
                onClick={() => {
                  router.push(step.action!.href);
                  nextStep();
                }}
                className="inline-flex items-center gap-1.5 text-sm font-medium text-primary hover:underline mb-4"
              >
                {step.action.label}
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            )}

            {/* Step indicators */}
            <div className="flex items-center gap-1.5 mb-4">
              {tourSteps.map((_, idx) => (
                <div
                  key={idx}
                  className={cn(
                    "h-1.5 rounded-full transition-all duration-300",
                    idx === currentStep
                      ? "w-6 bg-emerald-500"
                      : idx < currentStep
                        ? "w-1.5 bg-emerald-500/50"
                        : "w-1.5 bg-muted-foreground/20"
                  )}
                />
              ))}
            </div>

            {/* Navigation buttons */}
            <div className="flex items-center justify-between">
              <div>
                {currentStep > 0 ? (
                  <Button variant="ghost" size="sm" onClick={prevStep}>
                    Back
                  </Button>
                ) : (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={skipTour}
                    className="text-muted-foreground"
                  >
                    Skip tour
                  </Button>
                )}
              </div>
              <Button
                size="sm"
                onClick={nextStep}
                className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white"
              >
                {isLastStep ? (
                  <>
                    <CheckCircle2 className="h-3.5 w-3.5 mr-1.5" />
                    Get Started
                  </>
                ) : (
                  <>
                    Next
                    <ArrowRight className="h-3.5 w-3.5 ml-1.5" />
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
