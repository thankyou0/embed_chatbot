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
import { MessageSquare, Plus, X, Loader2 } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { apiRequestWithAuth } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";

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
  const [chatbots, setChatbots] = useState<Chatbot[]>([]);
  const router = useRouter();
  const { isAdmin, isOrgOwner } = useAuth();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [pendingChatbotId, setPendingChatbotId] = useState<string | null>(null);
  const [formData, setFormData] = useState<{
    name: string;
    welcome_message: string;
  }>({ name: "", welcome_message: "Hi! How can I help you today?" });
  const [error, setError] = useState<string | null>(null);

  const fetchChatbots = async () => {
    try {
      const token = getAccessToken();
      if (!token) {
        router.push("/login");
        return;
      }

      const response = await apiRequestWithAuth<{
        chatbots: Chatbot[];
        total: number;
      }>("/api/v1/chatbots", token, { method: "GET" });
      setChatbots(response.chatbots);
    } catch (err) {
      console.error("Failed to fetch chatbots:", err);
    }
  };

  // Fetch chatbots on mount
  useEffect(() => {
    fetchChatbots();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Chatbots</h1>
          <p className="text-muted-foreground">
            Manage your AI chatbots and conversations
          </p>
        </div>
        <Button
          onClick={() => setIsModalOpen(true)}
          disabled={!isAdmin}
          title={!isAdmin ? "Only admins can create chatbots" : ""}
        >
          <Plus className="mr-2 h-4 w-4" />
          Create Chatbot
        </Button>
      </div>

      {/* Chatbots List */}
      {chatbots.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {chatbots.map((chatbot) => (
            <Link
              key={chatbot.id}
              href={`/dashboard/chatbots/${chatbot.id}`}
              onClick={() => setPendingChatbotId(chatbot.id)}
            >
              <Card
                className={
                  "cursor-pointer hover:shadow-md transition-shadow h-full relative overflow-hidden"
                }
              >
                {pendingChatbotId === chatbot.id && (
                  <div className="loading-shimmer" aria-hidden="true" />
                )}
                <CardHeader>
                  <CardTitle>{chatbot.name}</CardTitle>
                  <CardDescription>
                    {chatbot.welcome_message || "No welcome message"}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span>
                      Account type:{" "}
                      {isOrgOwner ? "Org Owner" : isAdmin ? "Admin" : "Member"}
                    </span>
                    <span
                      className={
                        chatbot.status === "active"
                          ? "text-green-600"
                          : chatbot.status === "paused"
                            ? "text-yellow-600"
                            : "text-gray-500"
                      }
                    >
                      {chatbot.status}
                    </span>
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
              <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center">
                <MessageSquare className="h-8 w-8 text-muted-foreground" />
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
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Create New Chatbot</CardTitle>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => {
                    setIsModalOpen(false);
                    setError(null);
                    setFormData({
                      name: "",
                      welcome_message: "Hi! How can I help you today?",
                    });
                  }}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <CardDescription>
                Give your chatbot a name and welcome message
              </CardDescription>
            </CardHeader>
            <form onSubmit={handleCreateChatbot}>
              <CardContent className="space-y-4">
                {error && (
                  <div className="p-3 bg-red-50 border border-red-200 text-red-600 rounded-md text-sm">
                    {error}
                  </div>
                )}

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
              </CardContent>
              <CardContent className="flex justify-end gap-2 pt-0">
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
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <Plus className="mr-2 h-4 w-4" />
                      Create Chatbot
                    </>
                  )}
                </Button>
              </CardContent>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}
