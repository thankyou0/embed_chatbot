"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { MessageSquare, Plus, Clock, Activity } from "lucide-react";
import { ButtonSpinner } from "@/components/ui/loading";
import { SkeletonChatbotList } from "@/components/ui/skeleton";
import { useHeaderContent } from "@/contexts/HeaderContext";
import { ErrorMessage } from "@/components/ui/error-message";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { apiRequestWithAuth } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface Chatbot {
  id: string;
  name: string;
  welcome_message: string | null;
  status: "draft" | "active" | "paused";
  created_at: string;
  permission_level: string;
  can_manage_knowledge?: boolean;
  can_manage_appearance?: boolean;
  can_resolve_queries?: boolean;
  can_view_analytics_billing?: boolean;
}

export default function ChatbotsPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [isFetchingChatbots, setIsFetchingChatbots] = useState(true);
  const [chatbots, setChatbots] = useState<Chatbot[]>([]);
  const router = useRouter();
  const { user, isAdmin, loading: authLoading } = useAuth();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [pendingChatbotId, setPendingChatbotId] = useState<string | null>(null);
  const [formData, setFormData] = useState<{
    name: string;
    welcome_message: string;
  }>({ name: "", welcome_message: "Hi! How can I help you today?" });
  const [error, setError] = useState<string | null>(null);
  const { setContent } = useHeaderContent();

  useEffect(() => {
    setContent({
      title: "Chatbots",
      description: "Manage your AI chatbots and conversations",
      actions: isAdmin ? (
        <Button
          onClick={() => setIsModalOpen(true)}
          className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-md shadow-emerald-500/20"
        >
          <Plus className="mr-2 h-4 w-4" />
          Create Chatbot
        </Button>
      ) : null,
    });
    return () => setContent(null);
  }, [setContent, isAdmin]);

  const fetchChatbots = async () => {
    try {
      setIsFetchingChatbots(true);
      const token = getAccessToken();
      if (!token) {
        // Token should exist if auth completed successfully
        // This can happen if auth failed - dashboard layout will redirect
        return;
      }

      const response = await apiRequestWithAuth<{
        chatbots: Chatbot[];
        total: number;
      }>("/api/v1/chatbots", token, { method: "GET" });
      setChatbots(response.chatbots);
    } catch (err) {
      console.error("Failed to fetch chatbots:", err);
    } finally {
      setIsFetchingChatbots(false);
    }
  };

  // Fetch chatbots on mount (after auth is loaded and user exists)
  useEffect(() => {
    if (!authLoading && user) {
      fetchChatbots();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading, user]);

  const handleCreateChatbot = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const token = getAccessToken();
      if (!token) {
        router.push("/login");
        return;
      }

      const response = await apiRequestWithAuth<Chatbot>(
        "/api/v1/chatbots",
        token,
        {
          method: "POST",
          body: JSON.stringify({
            name: formData.name,
            welcome_message: formData.welcome_message || null,
          }),
        },
      );

      // Reset form and close modal
      setFormData({
        name: "",
        welcome_message: "Hi! How can I help you today?",
      });
      setIsModalOpen(false);

      // Navigate directly to the new chatbot page
      // DO NOT reset loading state here - let it continue to show during navigation
      router.push(`/dashboard/chatbots/${response.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to create chatbot");
      setIsLoading(false);
    }
    // Intentionally omitted finally block to keep loading state active during navigation
  };

  return (
    <div className="space-y-6">

      {/* Chatbots List */}
      {isFetchingChatbots ? (
        <SkeletonChatbotList />
      ) : chatbots.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {chatbots.map((chatbot) => (
            <Link
              key={chatbot.id}
              href={`/dashboard/chatbots/${chatbot.id}`}
              onClick={() => setPendingChatbotId(chatbot.id)}
            >
              <Card
                className={
                  "cursor-pointer hover:shadow-lg hover:border-emerald-200 dark:hover:border-emerald-800 transition-all duration-200 h-full relative overflow-hidden group"
                }
              >
                {pendingChatbotId === chatbot.id && (
                  <div className="loading-shimmer" aria-hidden="true" />
                )}
                {/* Color accent top bar based on status */}
                <div
                  className={cn(
                    "h-1 w-full",
                    chatbot.status === "active"
                      ? "bg-gradient-to-r from-emerald-500 to-teal-500"
                      : chatbot.status === "paused"
                        ? "bg-gradient-to-r from-amber-400 to-orange-400"
                        : "bg-gradient-to-r from-gray-300 to-gray-400"
                  )}
                />
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-3 min-w-0">
                      {/* Avatar with initials */}
                      <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-sm group-hover:shadow-md group-hover:scale-105 transition-all shrink-0">
                        <span className="text-white font-bold text-sm">
                          {chatbot.name
                            .split(" ")
                            .map((w) => w[0])
                            .slice(0, 2)
                            .join("")
                            .toUpperCase()}
                        </span>
                      </div>
                      <div className="min-w-0">
                        <CardTitle className="text-base truncate">
                          {chatbot.name}
                        </CardTitle>
                        <div className="flex items-center gap-1.5 mt-1">
                          <Badge
                            variant={
                              chatbot.status === "active"
                                ? "active"
                                : chatbot.status === "paused"
                                  ? "paused"
                                  : "draft"
                            }
                            className="text-[10px] h-5"
                          >
                            <span
                              className={cn(
                                "inline-block w-1.5 h-1.5 rounded-full mr-1",
                                chatbot.status === "active"
                                  ? "bg-emerald-400"
                                  : chatbot.status === "paused"
                                    ? "bg-amber-400"
                                    : "bg-gray-400"
                              )}
                            />
                            {chatbot.status}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                  {chatbot.welcome_message && (
                    <CardDescription className="mt-2 line-clamp-2 text-xs">
                      {chatbot.welcome_message}
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent className="pt-0">
                  {/* Mini stats row */}
                  <div className="flex items-center gap-4 py-2 px-3 rounded-lg bg-muted/40 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1.5" title="Role">
                      <Activity className="h-3.5 w-3.5" />
                      <span>{(chatbot.permission_level || "member").charAt(0).toUpperCase() + (chatbot.permission_level || "member").slice(1)}</span>
                    </div>
                    <div className="flex items-center gap-1.5" title="Created">
                      <Clock className="h-3.5 w-3.5" />
                      <span>
                        {new Date(chatbot.created_at).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                        })}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>No chatbots yet</CardTitle>
            <CardDescription>
              {isAdmin
                ? "Get started by creating your first AI chatbot"
                : "Contact your organization admin to get assigned to a chatbot"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-12 space-y-4">
              <div className="h-16 w-16 rounded-full bg-gradient-to-br from-emerald-100 to-teal-100 flex items-center justify-center">
                <MessageSquare className="h-8 w-8 text-emerald-500" />
              </div>
              <div className="text-center space-y-2">
                <h3 className="text-lg font-semibold">
                  {isAdmin
                    ? "Create your first chatbot"
                    : "No Chatbots Available"}
                </h3>
                <p className="text-sm text-muted-foreground max-w-sm">
                  {isAdmin
                    ? "Build custom AI chatbots for your website, customer support, or internal tools."
                    : "You don't have access to any chatbots yet. Ask your organization admin to assign you to a chatbot."}
                </p>
              </div>
              {isAdmin && (
                <Button onClick={() => setIsModalOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Chatbot
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Create Chatbot Modal */}
      {isModalOpen && (
      <Dialog open={isModalOpen} onOpenChange={(open) => {
        if (!open) {
          setIsModalOpen(false);
          setError(null);
          setFormData({ name: "", welcome_message: "Hi! How can I help you today?" });
        }
      }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Create New Chatbot</DialogTitle>
            <DialogDescription>
              Give your chatbot a name and welcome message
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateChatbot}>
            <div className="space-y-4 py-2">
              <ErrorMessage message={error} />

              <div className="space-y-2">
                <Label htmlFor="name">Chatbot Name</Label>
                <Input
                  id="name"
                  placeholder="My Awesome Chatbot"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="welcome_message">Welcome Message</Label>
                <Textarea
                  id="welcome_message"
                  placeholder="Hi! How can I help you today?"
                  value={formData.welcome_message}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      welcome_message: e.target.value,
                    })
                  }
                  rows={3}
                  disabled={isLoading}
                />
              </div>
            </div>
            <DialogFooter className="mt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setIsModalOpen(false);
                  setError(null);
                  setFormData({
                    name: "",
                    welcome_message: "Hi! How can I help you today?",
                  });
                }}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isLoading || !formData.name.trim()}
                className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white"
              >
                {isLoading ? (
                  <>
                    <ButtonSpinner />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Chatbot
                  </>
                )}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      )}
    </div>
  );
}
