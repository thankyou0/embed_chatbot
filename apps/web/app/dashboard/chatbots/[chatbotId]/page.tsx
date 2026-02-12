"use client";

import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useForm, Controller, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  ChevronRight,
  Settings,
  Eye,
  Loader2,
  Database,
  Palette,
  MessageSquare,
  Code,
  BarChart3,
  Plus,
  Sparkles,
  Globe,
  Check,
  X as CloseIcon,
  Search,
  RefreshCcw,
  RefreshCw,
  ExternalLink,
  Upload,
  FileText,
  Trash2,
  AlertCircle,
  HelpCircle,
  Edit2,
  CheckSquare,
  Square,
  Save,
  Users,
  CheckCircle2,
  X,
  TrendingUp,
  Download,
  ChevronLeft,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { CrawlScheduleModal } from "@/components/dashboard/CrawlScheduleModal";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { apiRequestWithAuth } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { ChatbotWidgetPreview } from "@/components/chatbot/WidgetPreview";
import { ChatbotTeamSettings } from "@/components/dashboard/ChatbotTeamSettings";
import { CrawlSourcePanel } from "@/components/dashboard/CrawlSourcePanel";
import { QABundlePanel } from "@/components/dashboard/QABundlePanel";
import { ChevronDown, ChevronUp, MoreHorizontal } from "lucide-react";

interface ChatbotDetail {
  id: string;
  tenant_id: number;
  name: string;
  description: string | null;
  status: "draft" | "active" | "paused";
  created_by: number;
  created_at: string;
  updated_at: string;
  permission_level: "owner" | "admin" | "editor" | "viewer";
  // Granular permissions
  can_manage_knowledge: boolean;
  can_manage_appearance: boolean;
  can_resolve_queries: boolean;
  can_view_analytics_billing: boolean;
}

interface KnowledgeSource {
  id: string;
  chatbot_id: string;
  source_type: "crawled_url" | "uploaded_file" | "qa_pair";
  source_url: string | null;
  status: "pending" | "processing" | "crawling" | "completed" | "failed";
  pages_found: number;
  error_message: string | null; // Error messages or warnings (e.g., quota reached)
  created_at: string;
  updated_at: string;
  files?: {
    id: string;
    filename: string;
    file_size: number;
    mime_type: string;
  }[];
  qa_pairs?: QAPair[];
  pages?: CrawledPage[];
}

interface CrawledPage {
  id: string;
  knowledge_source_id: string;
  url: string;
  title: string | null;
  is_product?: boolean;
  created_at: string;
}

interface QAPair {
  id: string;
  question: string;
  answer: string;
  created_at: string;
  updated_at: string;
}

interface RecentActivity {
  id: string;
  type:
    | "knowledge_source"
    | "conversation"
    | "status_change"
    | "team_member_added"
    | "team_member_updated"
    | "team_member_removed"
    | "team_permissions_updated"
    | "crawl_failed"
    | "embedding_failed";
  description: string;
  created_at: string;
}

interface KnowledgeSourceBreakdown {
  total_crawled_urls: number;
  total_uploaded_files: number;
  total_qa_pairs: number;
  total_crawled_pages: number;
  total_file_size: number;
  total_qa_count: number;
}

interface ChatbotStats {
  total_conversations: number;
  total_knowledge_sources: number;
  active_knowledge_sources: number;
  total_kb_size: number;
  knowledge_breakdown: KnowledgeSourceBreakdown;
}

interface RecentActivityListResponse {
  activities: RecentActivity[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

type FilePreviewType = "image" | "pdf" | "text";

const appearanceSchema = z.object({
  primary_color: z.string().regex(/^#[0-9A-Fa-f]{6}$/, "Invalid hex color"),
  header_text: z.string().min(1, "Header text is required").max(255),
  avatar_url: z.string().nullable(),
  position: z.enum(["bottom-right", "bottom-left"]),
  offset_x: z.number().int().optional().default(0),
  offset_y: z.number().int().optional().default(0),
  welcome_message: z.string().nullable(),
  initial_suggestions: z.array(z.string()),
  show_branding: z.boolean(),
});

type AppearanceFormData = z.infer<typeof appearanceSchema>;

interface AppearanceData extends AppearanceFormData {
  id: string;
  chatbot_id: string;
  created_at: string;
  updated_at: string;
}

export default function ChatbotDetailPage() {
  const params = useParams();
  const router = useRouter();
  const chatbotId = params.chatbotId as string;
  const { isAdmin, isOrgOwner } = useAuth();

  const [chatbot, setChatbot] = useState<ChatbotDetail | null>(null);
  const [knowledgeSources, setKnowledgeSources] = useState<KnowledgeSource[]>(
    [],
  );
  const [stats, setStats] = useState<ChatbotStats | null>(null);
  const RECENT_ACTIVITY_PAGE_SIZE = 10;
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [recentActivityPage, setRecentActivityPage] = useState(1);
  const [recentActivityTotal, setRecentActivityTotal] = useState(0);
  const [recentActivityTotalPages, setRecentActivityTotalPages] = useState(0);
  const [isLoadingRecentActivity, setIsLoadingRecentActivity] = useState(false);
  const [isExportingRecentActivity, setIsExportingRecentActivity] =
    useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingKnowledge, setIsLoadingKnowledge] = useState(false);
  const [hasLoadedKnowledge, setHasLoadedKnowledge] = useState(false);
  const [hasLoadedAppearance, setHasLoadedAppearance] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [knowledgeTab, setKnowledgeTab] = useState("crawl");
  const [navigationTarget, setNavigationTarget] = useState<
    "analytics" | "usage" | null
  >(null);

  // Knowledge base state
  const [isAddKnowledgeOpen, setIsAddKnowledgeOpen] = useState(false);
  const [knowledgeType, setKnowledgeType] = useState<"url" | "file" | "qa">(
    "url",
  );
  const [newUrl, setNewUrl] = useState("");
  const [isCrawling, setIsCrawling] = useState(false);
  const [uploadFiles, setUploadFiles] = useState<FileList | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [previewingFileId, setPreviewingFileId] = useState<string | null>(null);
  const [isFilePreviewOpen, setIsFilePreviewOpen] = useState(false);
  const [filePreviewTitle, setFilePreviewTitle] = useState("");
  const [filePreviewType, setFilePreviewType] = useState<FilePreviewType>("text");
  const [filePreviewObjectUrl, setFilePreviewObjectUrl] = useState<string | null>(
    null,
  );
  const [filePreviewText, setFilePreviewText] = useState("");

  // Selection state
  const [selectedPages, setSelectedPages] = useState<string[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [selectedQAs, setSelectedQAs] = useState<string[]>([]);
  const [isBulkDeleting, setIsBulkDeleting] = useState(false);

  // QA state
  const [newQA, setNewQA] = useState({ question: "", answer: "" });
  const [editingQA, setEditingQA] = useState<QAPair | null>(null);
  const [isQAOpen, setIsQAOpen] = useState(false);
  const [qaXlsx, setQaXlsx] = useState<File | null>(null);

  // Appearance state
  const [appearance, setAppearance] = useState<AppearanceData | null>(null);
  const [isLoadingAppearance, setIsLoadingAppearance] = useState(false);
  const [isSavingAppearance, setIsSavingAppearance] = useState(false);
  const [appearanceError, setAppearanceError] = useState<string | null>(null);
  const [appearanceSuccessMessage, setAppearanceSuccessMessage] = useState<
    string | null
  >(null);
  const [newSuggestion, setNewSuggestion] = useState("");
  const [embedCopyStatus, setEmbedCopyStatus] = useState<string | null>(null);
  const avatarInputRef = useRef<HTMLInputElement>(null);

  // Settings state
  const [settingsSubTab, setSettingsSubTab] = useState("general");
  const [isSavingSettings, setIsSavingSettings] = useState(false);
  const [settingsSuccess, setSettingsSuccess] = useState<string | null>(null);
  const [settingsError, setSettingsError] = useState<string | null>(null);

  // Crawl scheduling state
  const [isCrawlScheduleOpen, setIsCrawlScheduleOpen] = useState(false);
  const [selectedCrawlSource, setSelectedCrawlSource] = useState<any | null>(
    null,
  );

  // Polling state - only poll when we explicitly start a crawl
  const [isPolling, setIsPolling] = useState(false);
  const [pollingStartTime, setPollingStartTime] = useState<number | null>(null);
  const MAX_POLLING_DURATION = 5 * 60 * 1000; // 5 minutes max polling
  const [manuallyStartedCrawl, setManuallyStartedCrawl] = useState(false);
  const [pollingTimedOut, setPollingTimedOut] = useState(false);

  // Toast notification state for crawl status changes
  const [toastMessage, setToastMessage] = useState<{
    type: "success" | "error" | "info";
    message: string;
  } | null>(null);
  const previousKnowledgeSourcesRef = useRef<KnowledgeSource[]>([]);
  const lastFetchTimeRef = useRef<number>(0);
  const autoDeletedSourcesRef = useRef<Set<string>>(new Set());

  // Appearance form setup
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    control,
    formState: { errors, isDirty },
  } = useForm<AppearanceFormData>({
    resolver: zodResolver(appearanceSchema),
    mode: "onChange", // Enable real-time validation and updates
    defaultValues: {
      primary_color: "#3B82F6",
      header_text: "Chat Support",
      avatar_url: null,
      position: "bottom-right",
      offset_x: 0,
      offset_y: 0,
      welcome_message: "Hi! How can I help you today?",
      initial_suggestions: [],
      show_branding: true,
    },
  });

  // Use useWatch for real-time updates - this triggers re-renders when values change
  const watchedPrimaryColor = useWatch({
    control,
    name: "primary_color",
    defaultValue: "#3B82F6",
  });
  const watchedHeaderText = useWatch({
    control,
    name: "header_text",
    defaultValue: "Chat Support",
  });
  const watchedWelcomeMessage = useWatch({
    control,
    name: "welcome_message",
    defaultValue: null,
  });
  const watchedAvatarUrl = useWatch({
    control,
    name: "avatar_url",
    defaultValue: null,
  });
  const watchedPosition = useWatch({
    control,
    name: "position",
    defaultValue: "bottom-right",
  });
  const watchedOffsetX = useWatch({
    control,
    name: "offset_x",
    defaultValue: 0,
  });
  const watchedOffsetY = useWatch({
    control,
    name: "offset_y",
    defaultValue: 0,
  });
  const watchedInitialSuggestions = useWatch({
    control,
    name: "initial_suggestions",
    defaultValue: [],
  });
  const watchedShowBranding = useWatch({
    control,
    name: "show_branding",
    defaultValue: true,
  });

  // Create watched values object for widget preview
  const watchedAppearanceValues = {
    primary_color: watchedPrimaryColor ?? "#3B82F6",
    header_text: watchedHeaderText ?? "Chat Support",
    welcome_message: watchedWelcomeMessage ?? null,
    avatar_url: watchedAvatarUrl ?? null,
    position: watchedPosition ?? "bottom-right",
    offset_x: watchedOffsetX ?? 0,
    offset_y: watchedOffsetY ?? 0,
    initial_suggestions: watchedInitialSuggestions ?? [],
    show_branding:
      watchedShowBranding !== undefined ? watchedShowBranding : true,
  };

  const formData = watch();
  // Keep primaryColor for backward compatibility
  const primaryColor = watchedPrimaryColor ?? watch("primary_color");

  useEffect(() => {
    const initializePage = async () => {
      // 1. High Priority: Get basic info, stats, and appearance (for widget preview)
      await fetchChatbotDetails();
      fetchChatbotStats();
      fetchRecentActivity(1);
      fetchAppearance();

      // 2. Medium Priority: Prefetch knowledge base in background
      // This is usually the largest payload, so we delay it slightly
      setTimeout(() => {
        if (!hasLoadedKnowledge) fetchKnowledgeSources();
      }, 1000);
    };

    initializePage();
  }, [chatbotId]);

  const fetchRecentActivity = async (
    page = 1,
    showLoading = true,
  ): Promise<void> => {
    try {
      if (showLoading) setIsLoadingRecentActivity(true);
      const token = getAccessToken();
      if (!token) return;

      const timestamp = new Date().getTime();
      const response = await apiRequestWithAuth<RecentActivityListResponse>(
        `/api/v1/chatbots/${chatbotId}/activities?page=${page}&page_size=${RECENT_ACTIVITY_PAGE_SIZE}&t=${timestamp}`,
        token,
        {
          method: "GET",
          cache: "no-store" as RequestCache,
        },
      );

      setRecentActivity(response.activities || []);
      setRecentActivityTotal(response.total || 0);
      setRecentActivityTotalPages(response.total_pages || 0);
      setRecentActivityPage(response.page || 1);
    } catch (err) {
      console.error("Failed to fetch recent activity:", err);
    } finally {
      if (showLoading) setIsLoadingRecentActivity(false);
    }
  };

  const fetchChatbotStats = async () => {
    try {
      const token = getAccessToken();
      if (!token) return;

      const timestamp = new Date().getTime();
      const response = await apiRequestWithAuth<ChatbotStats>(
        `/api/v1/chatbots/${chatbotId}/stats?t=${timestamp}`,
        token,
        {
          method: "GET",
          cache: "no-store" as RequestCache,
        },
      );
      setStats(response);
      fetchRecentActivity(recentActivityPage, false);
    } catch (err) {
      console.error("Failed to fetch stats:", err);
    }
  };

  // Polling for crawling sources - runs whenever we detect active processing
  useEffect(() => {
    // Check for crawling/pending/processing status (case-insensitive)
    const hasCrawlingSources = knowledgeSources.some((s) => {
      const status = s.status?.toLowerCase();
      return (
        status === "processing" || status === "pending" || status === "crawling"
      );
    });

    // Detect status changes and show toast notifications
    if (previousKnowledgeSourcesRef.current.length > 0) {
      knowledgeSources.forEach((current) => {
        const previous = previousKnowledgeSourcesRef.current.find(
          (p) => p.id === current.id,
        );
        if (previous && previous.status !== current.status) {
          // Status changed!
          console.log(
            `✅ Status changed for ${current.source_url}: ${previous.status} → ${current.status}`,
          );

          const getSourceDisplayName = (source: KnowledgeSource) => {
            if (source.source_type === "crawled_url") return source.source_url;
            if (
              source.source_type === "uploaded_file" &&
              source.files &&
              source.files.length > 0
            ) {
              return source.files[0].filename;
            }
            if (source.source_type === "qa_pair") return "Q&A pairs";
            return "Knowledge source";
          };

          const getActionVerb = (source: KnowledgeSource) => {
            if (source.source_type === "crawled_url") return "Crawl";
            if (source.source_type === "uploaded_file") return "Processing";
            if (source.source_type === "qa_pair") return "Q&A processing";
            return "Processing";
          };

          const displayName = getSourceDisplayName(current);
          const verb = getActionVerb(current);

          if (current.status === "completed") {
            // Check if there's a warning message (like quota reached)
            if (
              current.error_message &&
              current.error_message.toLowerCase().includes("quota")
            ) {
              setToastMessage({
                type: "info", // Use "info" for warnings (yellow/blue)
                message: current.error_message, // Show the quota warning
              });
            } else {
              setToastMessage({
                type: "success",
                message: `${verb} completed for ${displayName}`,
              });
            }
          } else if (current.status === "failed") {
            setToastMessage({
              type: "error",
              message:
                current.error_message || `${verb} failed for ${displayName}`,
            });
          }
          // Refresh stats when any status changes
          fetchChatbotStats();
        }
      });
      // 2. Handle auto-cleanup for failed empty crawl sources
      knowledgeSources.forEach((s) => {
        if (
          s.source_type === "crawled_url" &&
          s.status === "failed" &&
          (s.pages_found === 0 || !s.pages || s.pages.length === 0) &&
          !autoDeletedSourcesRef.current.has(s.id)
        ) {
          console.log(`🧹 Auto-cleaning failed empty source: ${s.id}`);
          autoDeletedSourcesRef.current.add(s.id);

          setToastMessage({
            type: "error",
            message: s.error_message || `Crawl failed for ${s.source_url}`,
          });

          // Trigger silent deletion
          handleDeleteSource(s.id, undefined, true);
        }
      });
    }
    previousKnowledgeSourcesRef.current = knowledgeSources;

    // Stop polling if all crawls/processing are complete
    if (!hasCrawlingSources && isPolling) {
      console.log(
        "✅ All process items complete, stopping polling and performing final sync",
      );
      setIsPolling(false);
      setPollingStartTime(null);
      setManuallyStartedCrawl(false);

      // Perform one final sync to ensure everything is up to date
      fetchKnowledgeSources(false);
      fetchChatbotStats();
      return;
    }

    // Start polling if we have active crawls and aren't polling yet
    if (!isPolling && hasCrawlingSources && !pollingTimedOut) {
      console.log("🚀 Starting polling - active crawls detected");
      setIsPolling(true);
      setPollingStartTime(Date.now());
    } else if (!isPolling && hasCrawlingSources && pollingTimedOut) {
      console.log(
        "⏱️ Polling disabled after timeout; waiting for manual refresh",
      );
    }
  }, [knowledgeSources, manuallyStartedCrawl, isPolling, pollingTimedOut]);

  // Separate effect for the actual polling interval
  useEffect(() => {
    if (!isPolling) return;

    console.log("🔄 Polling started - checking every 2 seconds");

    const interval = setInterval(async () => {
      console.log("📡 Polling tick - fetching latest sources and stats...");

      // Update both sources and stats for immediate feedback
      await fetchKnowledgeSources(false);
      await fetchChatbotStats();

      // Check if we've exceeded max polling duration
      if (
        pollingStartTime &&
        Date.now() - pollingStartTime > MAX_POLLING_DURATION
      ) {
        console.log("Polling timeout reached, stopping automatic refresh");
        setIsPolling(false);
        setPollingStartTime(null);
        setPollingTimedOut(true);
        setToastMessage({
          type: "info",
          message:
            "Polling stopped after 5 minutes. Refresh manually if processing continues.",
        });
        return;
      }
    }, 2000); // Poll every 2 seconds for faster updates

    return () => {
      console.log("🛑 Polling stopped - cleaning up interval");
      clearInterval(interval);
    };
  }, [isPolling, pollingStartTime]);

  // Auto-hide toast after 5 seconds
  useEffect(() => {
    if (toastMessage) {
      const timer = setTimeout(() => setToastMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [toastMessage]);

  const fetchChatbotDetails = async () => {
    try {
      setIsLoading(true);
      const token = getAccessToken();
      if (!token) {
        router.push("/login");
        return;
      }

      const response = await apiRequestWithAuth<ChatbotDetail>(
        `/api/v1/chatbots/${chatbotId}`,
        token,
        { method: "GET" },
      );

      setChatbot(response);
      setError(null);
    } catch (err: any) {
      console.error("Failed to fetch chatbot:", err);
      setError(err.message || "Failed to load chatbot");
      // Redirect to chatbots list if not found or no permission
      if (err.message?.includes("404") || err.message?.includes("403")) {
        setTimeout(() => router.push("/dashboard/chatbots"), 2000);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const fetchKnowledgeSources = async (
    showLoading = true,
  ): Promise<KnowledgeSource[] | null> => {
    try {
      if (showLoading) setIsLoadingKnowledge(true);
      const token = getAccessToken();
      if (!token) return null;

      // Add a timestamp to bust any potential caches during polling
      const timestamp = new Date().getTime();

      // Update last fetch time reference to prevent race conditions from slow responses
      const requestTimestamp = timestamp;
      lastFetchTimeRef.current = Math.max(
        lastFetchTimeRef.current,
        requestTimestamp,
      );

      const response = await apiRequestWithAuth<KnowledgeSource[]>(
        `/api/v1/chatbots/${chatbotId}/knowledge-sources?t=${timestamp}`,
        token,
        {
          method: "GET",
          cache: "no-store" as RequestCache,
        },
      );

      // Only process if this is the newest request
      if (requestTimestamp < lastFetchTimeRef.current) {
        console.log("⏭ Skipping stale knowledge source response");
        return null;
      }

      console.log(
        "📦 Fetched knowledge sources:",
        response.map((ks) => ({
          url: ks.source_url,
          status: ks.status,
        })),
      );

      setKnowledgeSources(response);
      setHasLoadedKnowledge(true);
      return response;
    } catch (err) {
      console.error("Failed to fetch knowledge sources:", err);
      return null;
    } finally {
      if (showLoading) setIsLoadingKnowledge(false);
    }
  };

  const fetchAppearance = async () => {
    try {
      setIsLoadingAppearance(true);
      const token = getAccessToken();
      if (!token) return;

      const response = await apiRequestWithAuth<AppearanceData>(
        `/api/v1/chatbots/${chatbotId}/appearance`,
        token,
        { method: "GET" },
      );

      setAppearance(response);
      setHasLoadedAppearance(true);
      // Set form values
      Object.keys(response).forEach((key) => {
        if (
          key !== "id" &&
          key !== "chatbot_id" &&
          key !== "created_at" &&
          key !== "updated_at"
        ) {
          setValue(
            key as keyof AppearanceFormData,
            response[key as keyof AppearanceData],
          );
        }
      });

      setAppearanceError(null);
    } catch (err: any) {
      console.error("Failed to fetch appearance:", err);
      setAppearanceError(err.message || "Failed to load appearance settings");
    } finally {
      setIsLoadingAppearance(false);
    }
  };

  const handleCrawl = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUrl.trim()) return;

    try {
      setIsCrawling(true);
      const token = getAccessToken();
      1;
      if (!token) return;

      // Get the response which includes the new knowledge source
      const newSource = await apiRequestWithAuth<KnowledgeSource>(
        `/api/v1/chatbots/${chatbotId}/crawl`,
        token,
        {
          method: "POST",
          body: JSON.stringify({ base_url: newUrl }),
        },
      );

      // Optimistically add the new source to the state immediately
      setKnowledgeSources((prev) => {
        // Check if it already exists (avoid duplicates)
        const exists = prev.some((s) => s.id === newSource.id);
        if (exists) {
          // Update existing source
          return prev.map((s) => (s.id === newSource.id ? newSource : s));
        }
        // Add new source
        return [...prev, newSource];
      });

      setNewUrl("");
      setIsAddKnowledgeOpen(false);

      // Refresh to get the latest data (including pages as they're crawled)
      await fetchKnowledgeSources();
      // Refresh stats after adding knowledge source
      await fetchChatbotStats();

      // Enable polling BEFORE fetching to ensure the polling effect recognizes active sources
      setPollingTimedOut(false);
      setManuallyStartedCrawl(true);
      setIsPolling(true);
      setPollingStartTime(Date.now());
    } catch (err: any) {
      alert(err.message || "Failed to start crawl");
    } finally {
      setIsCrawling(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFiles || uploadFiles.length === 0) return;

    try {
      setIsUploading(true);
      const token = getAccessToken();
      if (!token) return;

      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      // Upload files sequentially
      for (let i = 0; i < uploadFiles.length; i++) {
        const file = uploadFiles[i];
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(
          `${API_URL}/api/v1/chatbots/${chatbotId}/upload`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
            },
            body: formData,
          },
        );

        if (!response.ok) {
          const errData = await response.json();
          const errorMessage = errData.detail || "Unknown error";
          throw new Error(`Failed to upload ${file.name}: ${errorMessage}`);
        }
      }

      setUploadFiles(null);
      setIsAddKnowledgeOpen(false);

      // Update both sources and stats for immediate feedback
      await fetchKnowledgeSources(false);
      await fetchChatbotStats();

      // Enable polling BEFORE fetching to ensure the polling effect recognizes active sources
      setPollingTimedOut(false);
      setManuallyStartedCrawl(true);
      setIsPolling(true);
      setPollingStartTime(Date.now());
    } catch (err: any) {
      alert(err.message || "Failed to upload files");
    } finally {
      setIsUploading(false);
    }
  };

  const handleQASubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = getAccessToken();
      if (!token) return;

      if (editingQA) {
        await apiRequestWithAuth(`/api/v1/chatbots/qa/${editingQA.id}`, token, {
          method: "PATCH",
          body: JSON.stringify(newQA),
        });
      } else {
        await apiRequestWithAuth(`/api/v1/chatbots/${chatbotId}/qa`, token, {
          method: "POST",
          body: JSON.stringify(newQA),
        });
      }

      setNewQA({ question: "", answer: "" });
      setEditingQA(null);
      await fetchKnowledgeSources();
      // Refresh stats after adding QA
      fetchChatbotStats();

      setToastMessage({
        type: "success",
        message: editingQA ? "QA pair updated" : "QA pair added successfully",
      });
    } catch (err: any) {
      setToastMessage({
        type: "error",
        message: err.message || "Failed to save QA pair",
      });
    }
  };

  const handleQAXlsxUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!qaXlsx) return;

    try {
      const token = getAccessToken();
      if (!token) return;

      const formData = new FormData();
      formData.append("file", qaXlsx);

      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${API_URL}/api/v1/chatbots/${chatbotId}/qa/upload`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        },
      );

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Upload failed");
      }

      setQaXlsx(null);

      await fetchKnowledgeSources();
      await fetchChatbotStats();

      // Enable polling for QA upload processing
      setPollingTimedOut(false);
      setManuallyStartedCrawl(true);
      setIsPolling(true);
      setPollingStartTime(Date.now());
    } catch (err: any) {
      alert(err.message || "Failed to upload XLSX");
    }
  };

  const handleDeleteQA = async (qaId: string) => {
    if (!confirm("Are you sure you want to delete this QA pair?")) return;
    try {
      const token = getAccessToken();
      if (!token) return;
      await apiRequestWithAuth(`/api/v1/chatbots/qa/${qaId}`, token, {
        method: "DELETE",
      });
      await fetchKnowledgeSources();
      // Refresh stats after deleting QA
      fetchChatbotStats();
    } catch (err: any) {
      alert(err.message || "Failed to delete QA");
    }
  };

  const handleDeleteSource = async (
    sourceId: string,
    customMessage?: string,
    silent: boolean = false,
  ) => {
    const message =
      customMessage ||
      "Are you sure you want to delete this knowledge source and all its data?";
    if (!silent && !confirm(message)) return;

    try {
      const token = getAccessToken();
      if (!token) return;

      await apiRequestWithAuth(
        `/api/v1/chatbots/knowledge-sources/${sourceId}`,
        token,
        { method: "DELETE" },
      );

      await fetchKnowledgeSources();
      // Refresh stats after deleting source
      fetchChatbotStats();
    } catch (err: any) {
      alert(err.message || "Failed to delete source");
    }
  };

  const handleDeletePage = async (pageId: string) => {
    if (!confirm("Are you sure you want to delete this page?")) return;
    try {
      const token = getAccessToken();
      if (!token) return;
      await apiRequestWithAuth(`/api/v1/chatbots/pages/${pageId}`, token, {
        method: "DELETE",
      });

      // Refresh knowledge sources and check for empty crawl sources
      const updatedSources = await fetchKnowledgeSources();
      if (updatedSources) {
        const crawlSources = updatedSources.filter(
          (s) => s.source_type === "crawled_url",
        );
        const emptyCrawlSources = crawlSources.filter((source) => {
          return !source.pages || source.pages.length === 0;
        });

        // Delete empty crawl sources
        if (emptyCrawlSources.length > 0) {
          for (const source of emptyCrawlSources) {
            try {
              await apiRequestWithAuth(
                `/api/v1/chatbots/knowledge-sources/${source.id}`,
                token,
                { method: "DELETE" },
              );
            } catch (err) {
              console.error(
                `Failed to delete empty crawl source ${source.id}:`,
                err,
              );
            }
          }
          // Refresh again after deleting empty sources
          await fetchKnowledgeSources();
        }
      }
      // Refresh stats after deleting page
      fetchChatbotStats();
    } catch (err: any) {
      alert(err.message || "Failed to delete page");
    }
  };

  const handleOpenUploadedFile = async (
    sourceId: string,
    file: {
      id: string;
      filename: string;
      mime_type: string;
    },
  ) => {
    try {
      const token = getAccessToken();
      if (!token) return;

      setPreviewingFileId(file.id);
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const mime = file.mime_type?.toLowerCase() || "";
      const isImage = mime.startsWith("image/");
      const isPdf = mime === "application/pdf";

      if (isImage || isPdf) {
        const response = await fetch(
          `${API_URL}/api/v1/chatbots/knowledge-sources/${sourceId}/files/${file.id}/content`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        );
        if (!response.ok) {
          let errorMessage = "Failed to open file";
          try {
            const errData = await response.json();
            errorMessage = errData?.detail || errData?.error || errorMessage;
          } catch {
            // ignore JSON parse errors and use fallback message
          }
          throw new Error(errorMessage);
        }
        const blob = await response.blob();
        if (filePreviewObjectUrl) URL.revokeObjectURL(filePreviewObjectUrl);
        const blobUrl = URL.createObjectURL(blob);
        setFilePreviewObjectUrl(blobUrl);
        setFilePreviewText("");
        setFilePreviewType(isImage ? "image" : "pdf");
      } else {
        const response = await fetch(
          `${API_URL}/api/v1/chatbots/knowledge-sources/${sourceId}/files/${file.id}/preview-text`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        );
        if (!response.ok) {
          let errorMessage = "Failed to open file";
          try {
            const errData = await response.json();
            errorMessage = errData?.detail || errData?.error || errorMessage;
          } catch {
            // ignore JSON parse errors and use fallback message
          }
          throw new Error(errorMessage);
        }
        const data = await response.json();
        if (filePreviewObjectUrl) URL.revokeObjectURL(filePreviewObjectUrl);
        setFilePreviewObjectUrl(null);
        setFilePreviewText(data?.text || "No preview text available.");
        setFilePreviewType("text");
      }
      setFilePreviewTitle(file.filename);
      setIsFilePreviewOpen(true);
    } catch (err: any) {
      alert(err.message || "Failed to open file");
    } finally {
      setPreviewingFileId(null);
    }
  };

  const handleFilePreviewOpenChange = (open: boolean) => {
    setIsFilePreviewOpen(open);
    if (!open) {
      if (filePreviewObjectUrl) URL.revokeObjectURL(filePreviewObjectUrl);
      setFilePreviewObjectUrl(null);
      setFilePreviewText("");
      setFilePreviewTitle("");
      setFilePreviewType("text");
    }
  };

  const handleBulkDelete = async (type: "pages" | "files" | "qa") => {
    const ids =
      type === "pages"
        ? selectedPages
        : type === "files"
          ? selectedFiles
          : selectedQAs;
    if (ids.length === 0) return;
    if (!confirm(`Are you sure you want to delete ${ids.length} items?`))
      return;

    try {
      setIsBulkDeleting(true);
      const token = getAccessToken();
      if (!token) return;

      let endpoint = "";
      if (type === "pages")
        endpoint = `/api/v1/chatbots/${chatbotId}/pages/bulk-delete`;
      else if (type === "files")
        endpoint = `/api/v1/chatbots/${chatbotId}/knowledge-sources/bulk-delete`;
      else if (type === "qa")
        endpoint = `/api/v1/chatbots/${chatbotId}/qa/bulk-delete`;

      await apiRequestWithAuth(endpoint, token, {
        method: "POST",
        body: JSON.stringify({ ids }),
      });

      // Reset selection
      if (type === "pages") setSelectedPages([]);
      else if (type === "files") setSelectedFiles([]);
      else if (type === "qa") setSelectedQAs([]);

      // Refresh knowledge sources to get updated state
      const updatedSources = await fetchKnowledgeSources();

      // If pages were deleted, check for empty crawl sources and delete them
      if (type === "pages" && updatedSources) {
        // Find crawl sources with no pages
        const crawlSources = updatedSources.filter(
          (s) => s.source_type === "crawled_url",
        );
        const emptyCrawlSources = crawlSources.filter((source) => {
          // Check if source has any pages
          return !source.pages || source.pages.length === 0;
        });

        // Delete empty crawl sources
        if (emptyCrawlSources.length > 0) {
          for (const source of emptyCrawlSources) {
            try {
              await apiRequestWithAuth(
                `/api/v1/chatbots/knowledge-sources/${source.id}`,
                token,
                { method: "DELETE" },
              );
            } catch (err) {
              console.error(
                `Failed to delete empty crawl source ${source.id}:`,
                err,
              );
            }
          }
          // Refresh again after deleting empty sources
          await fetchKnowledgeSources();
        }
        // Refresh stats after deleting pages
        fetchChatbotStats();
      }

      if (type === "qa") {
        // Refresh stats after deleting QA
        fetchChatbotStats();
      }

      if (type === "files") {
        // Refresh stats after deleting files
        fetchChatbotStats();
      }
    } catch (err: any) {
      alert(err.message || "Bulk delete failed");
    } finally {
      setIsBulkDeleting(false);
    }
  };

  const handleToggleStatus = async () => {
    if (!chatbot) return;

    try {
      const token = getAccessToken();
      if (!token) return;

      const newStatus = chatbot.status === "active" ? "paused" : "active";

      await apiRequestWithAuth(`/api/v1/chatbots/${chatbotId}`, token, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus }),
      });

      // Refresh chatbot data and stats to update overview and recent activity
      fetchChatbotDetails();
      fetchChatbotStats();
    } catch (err) {
      console.error("Failed to toggle status:", err);
    }
  };

  const handleDeleteChatbot = async () => {
    if (
      !confirm(
        "Are you sure you want to delete this chatbot? This action cannot be undone.",
      )
    )
      return;

    try {
      const token = getAccessToken();
      if (!token) return;

      await apiRequestWithAuth(`/api/v1/chatbots/${chatbotId}`, token, {
        method: "DELETE",
      });

      router.push("/dashboard/chatbots");
    } catch (err: any) {
      alert(err.message || "Failed to delete chatbot");
    }
  };

  const handleExportRecentActivity = async () => {
    try {
      setIsExportingRecentActivity(true);
      const token = getAccessToken();
      if (!token) return;

      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${API_URL}/api/v1/chatbots/${chatbotId}/activities/export`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || "Failed to export activity");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const contentDisposition = response.headers.get("Content-Disposition");
      const filenameMatch = contentDisposition?.match(/filename=\"?([^"]+)\"?/);
      const filename =
        filenameMatch?.[1] || `chatbot_activities_${chatbotId}.csv`;

      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setToastMessage({
        type: "error",
        message: err.message || "Failed to export activity",
      });
    } finally {
      setIsExportingRecentActivity(false);
    }
  };

  const getActivityPaginationItems = (): Array<
    number | "ellipsis-left" | "ellipsis-right"
  > => {
    if (recentActivityTotalPages <= 0) return [];
    if (recentActivityTotalPages <= 7) {
      return Array.from(
        { length: recentActivityTotalPages },
        (_, index) => index + 1,
      );
    }

    const items: Array<number | "ellipsis-left" | "ellipsis-right"> = [1];
    const start = Math.max(2, recentActivityPage - 1);
    const end = Math.min(recentActivityTotalPages - 1, recentActivityPage + 1);

    if (start > 2) items.push("ellipsis-left");
    for (let page = start; page <= end; page += 1) {
      items.push(page);
    }
    if (end < recentActivityTotalPages - 1) items.push("ellipsis-right");

    items.push(recentActivityTotalPages);
    return items;
  };

  const handleSettingsSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!chatbot) return;

    try {
      setIsSavingSettings(true);
      setSettingsError(null);
      const token = getAccessToken();
      if (!token) return;

      const formData = new FormData(e.currentTarget);
      const name = formData.get("name") as string;
      const status = formData.get("status") as "draft" | "active" | "paused";

      await apiRequestWithAuth(`/api/v1/chatbots/${chatbotId}`, token, {
        method: "PATCH",
        body: JSON.stringify({ name, status }),
      });

      setSettingsSuccess("Settings saved successfully!");
      fetchChatbotDetails();
      fetchChatbotStats();
      setTimeout(() => setSettingsSuccess(null), 3000);
    } catch (err: any) {
      setSettingsError(err.message || "Failed to save settings");
    } finally {
      setIsSavingSettings(false);
    }
  };

  const handleAppearanceSubmit = async (data: AppearanceFormData) => {
    try {
      setIsSavingAppearance(true);
      const token = getAccessToken();
      if (!token) return;

      await apiRequestWithAuth(
        `/api/v1/chatbots/${chatbotId}/appearance`,
        token,
        {
          method: "PATCH",
          body: JSON.stringify(data),
        },
      );

      setAppearanceSuccessMessage("Appearance settings saved successfully!");
      setTimeout(() => setAppearanceSuccessMessage(null), 3000);

      // Refresh to reset isDirty
      await fetchAppearance();
    } catch (err: any) {
      console.error("Failed to save appearance:", err);
      setAppearanceError(err.message || "Failed to save appearance settings");
    } finally {
      setIsSavingAppearance(false);
    }
  };

  const handleAddSuggestion = () => {
    if (newSuggestion.trim()) {
      const currentSuggestions = formData.initial_suggestions || [];
      setValue(
        "initial_suggestions",
        [...currentSuggestions, newSuggestion.trim()],
        { shouldDirty: true },
      );
      setNewSuggestion("");
    }
  };

  const handleRemoveSuggestion = (index: number) => {
    const currentSuggestions = formData.initial_suggestions || [];
    setValue(
      "initial_suggestions",
      currentSuggestions.filter((_, i) => i !== index),
      { shouldDirty: true },
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error || !chatbot) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {error?.includes("404") ? "Chatbot Not Found" : "Access Denied"}
          </h2>
          <p className="text-gray-600 mb-4">
            {error || "You don't have permission to view this chatbot."}
          </p>
          <Button onClick={() => router.push("/dashboard/chatbots")}>
            Back to Chatbots
          </Button>
        </div>
      </div>
    );
  }

  const canEdit = ["owner", "admin", "editor"].includes(
    chatbot.permission_level,
  );
  const accountTypeLabel = isOrgOwner
    ? "Org Owner"
    : isAdmin
      ? "Admin"
      : "Member";

  // Permission-based visibility
  const canViewKnowledge =
    chatbot.can_manage_knowledge ||
    chatbot.permission_level === "owner" ||
    chatbot.permission_level === "admin";
  const canViewAppearance =
    chatbot.can_manage_appearance ||
    chatbot.permission_level === "owner" ||
    chatbot.permission_level === "admin";
  const canViewSettings =
    chatbot.permission_level === "owner" ||
    chatbot.permission_level === "admin";
  const canResolveQueries =
    chatbot.can_resolve_queries ||
    chatbot.permission_level === "owner" ||
    chatbot.permission_level === "admin";
  const canViewAnalyticsBilling =
    chatbot.can_view_analytics_billing ||
    chatbot.permission_level === "owner" ||
    chatbot.permission_level === "admin";

  // Helper function to extract QA pairs from knowledge sources
  const getQAPairs = (): QAPair[] => {
    return knowledgeSources
      .filter((s) => s.source_type === "qa_pair" && s.qa_pairs)
      .flatMap((s) => s.qa_pairs || []);
  };

  const qaPairs = getQAPairs();

  // Knowledge base filtering
  const crawlSources = knowledgeSources.filter(
    (s) => s.source_type === "crawled_url",
  );
  const fileSources = knowledgeSources.filter(
    (s) => s.source_type === "uploaded_file",
  );
  const qaSources = knowledgeSources.filter((s) => s.source_type === "qa_pair");

  // Flattened pages for crawl tab
  const allCrawledPages = crawlSources.flatMap((s) =>
    (s.pages || []).map((p) => ({
      ...p,
      status: s.status,
      source_url: s.source_url,
    })),
  );

  // Show all crawl sources for total visibility (even failed or newly added)
  const crawlSourcesWithPages = crawlSources;

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {toastMessage && (
        <div
          className={`fixed top-4 right-4 z-50 max-w-md px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 animate-in slide-in-from-top-2 ${
            toastMessage.type === "error"
              ? "bg-red-100 border border-red-300 text-red-800"
              : toastMessage.type === "success"
                ? "bg-green-100 border border-green-300 text-green-800"
                : "bg-blue-100 border border-blue-300 text-blue-800"
          }`}
        >
          {toastMessage.type === "error" && (
            <AlertCircle className="h-5 w-5 flex-shrink-0" />
          )}
          {toastMessage.type === "success" && (
            <CheckCircle2 className="h-5 w-5 flex-shrink-0" />
          )}
          {toastMessage.type === "info" && (
            <RefreshCw className="h-5 w-5 flex-shrink-0" />
          )}
          <p className="text-sm font-medium">{toastMessage.message}</p>
          <button
            onClick={() => setToastMessage(null)}
            className="ml-auto p-1 hover:bg-black/10 rounded"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Header - Reduced Width */}
      <div className="flex items-center justify-between max-w-4xl">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">
              <Link
                href="/dashboard/chatbots"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                Chatbots
              </Link>
              <ChevronRight className="h-4 w-4 inline-block mx-2 text-muted-foreground" />
              <span>{chatbot.name}</span>
            </h1>
            <Badge
              variant={
                chatbot.status === "active"
                  ? "success"
                  : chatbot.status === "paused"
                    ? "warning"
                    : "secondary"
              }
            >
              {chatbot.status.charAt(0).toUpperCase() + chatbot.status.slice(1)}
            </Badge>
            <Badge variant="outline" className="text-xs">
              {accountTypeLabel}
            </Badge>
          </div>
          {chatbot.description && (
            <p className="text-gray-600 text-sm">{chatbot.description}</p>
          )}
        </div>
      </div>

      {/* Tab Navigation - Full Width Content */}
      <Tabs
        value={activeTab}
        onValueChange={(value) => {
          setActiveTab(value);
          // Handle on-demand loading if background prefetch hasn't finished
          if (value === "knowledge" && !hasLoadedKnowledge)
            fetchKnowledgeSources();
          if (value === "appearance" && !hasLoadedAppearance) fetchAppearance();
          if (value === "overview") {
            fetchChatbotStats();
            fetchRecentActivity(recentActivityPage);
          }
        }}
        className="w-full"
      >
        {/* Calculate visible tabs for grid columns */}
        {(() => {
          const visibleTabs = [
            true, // Overview always visible
            canViewKnowledge, // Knowledge
            canViewAppearance, // Appearance
            true, // Install always visible
            canViewSettings, // Settings
          ].filter(Boolean).length;

          return (
            <TabsList
              className={`grid w-full lg:w-auto`}
              style={{
                gridTemplateColumns: `repeat(${visibleTabs}, minmax(0, 1fr))`,
              }}
            >
              <TabsTrigger value="overview" className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                <span className="hidden sm:inline">Overview</span>
              </TabsTrigger>
              {canViewKnowledge && (
                <TabsTrigger
                  value="knowledge"
                  className="flex items-center gap-2"
                >
                  <Database className="h-4 w-4" />
                  <span className="hidden sm:inline">Add Knowledge</span>
                </TabsTrigger>
              )}
              {canViewAppearance && (
                <TabsTrigger
                  value="appearance"
                  className="flex items-center gap-2"
                >
                  <Palette className="h-4 w-4" />
                  <span className="hidden sm:inline">Appearance</span>
                </TabsTrigger>
              )}
              <TabsTrigger value="install" className="flex items-center gap-2">
                <Code className="h-4 w-4" />
                <span className="hidden sm:inline">Install</span>
              </TabsTrigger>
              {canViewSettings && (
                <TabsTrigger
                  value="settings"
                  className="flex items-center gap-2"
                >
                  <Settings className="h-4 w-4" />
                  <span className="hidden sm:inline">Settings</span>
                </TabsTrigger>
              )}
            </TabsList>
          );
        })()}

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Quick Stats */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Conversations
                </CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
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
              className="cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => setActiveTab("knowledge")}
            >
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Knowledge Sources
                </CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {stats?.total_knowledge_sources || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  {stats?.knowledge_breakdown?.total_crawled_urls || 0} crawl
                  sites •{" "}
                  {stats?.knowledge_breakdown?.total_uploaded_files || 0} files
                  • {stats?.knowledge_breakdown?.total_qa_pairs || 0} Q&A
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Knowledge Base Size
                </CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
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
              <CardDescription>
                Common tasks to manage your chatbot
              </CardDescription>
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
                      Message counts and billing
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
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
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
                                ? "bg-blue-100 text-blue-600"
                                : item.type === "conversation"
                                  ? "bg-green-100 text-green-600"
                                  : isTeamActivity
                                    ? "bg-purple-100 text-purple-600"
                                    : "bg-gray-100 text-gray-600",
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
                            <p className="font-medium text-gray-900">
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
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="rounded-md bg-background/80 px-3 py-2 border shadow-sm">
                      <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Knowledge Base Tab */}
        <TabsContent value="knowledge" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Add Knowledge</CardTitle>
                <CardDescription>
                  Manage the data sources your chatbot learns from
                </CardDescription>
              </div>
              {canEdit && (
                <Button onClick={() => setIsAddKnowledgeOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Source
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {isAddKnowledgeOpen && (
                <div className="mb-6 p-4 border rounded-lg bg-muted/30">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex bg-muted p-1 rounded-md">
                      <Button
                        variant={
                          knowledgeType === "url" ? "secondary" : "ghost"
                        }
                        size="sm"
                        onClick={() => setKnowledgeType("url")}
                        className="text-xs"
                      >
                        <Globe className="h-3 w-3 mr-1" /> Website
                      </Button>
                      <Button
                        variant={
                          knowledgeType === "file" ? "secondary" : "ghost"
                        }
                        size="sm"
                        onClick={() => setKnowledgeType("file")}
                        className="text-xs"
                      >
                        <Upload className="h-3 w-3 mr-1" /> File
                      </Button>
                      <Button
                        variant={knowledgeType === "qa" ? "secondary" : "ghost"}
                        size="sm"
                        onClick={() => setKnowledgeType("qa")}
                        className="text-xs"
                      >
                        <HelpCircle className="h-3 w-3 mr-1" /> Q&A
                      </Button>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsAddKnowledgeOpen(false)}
                      type="button"
                    >
                      <CloseIcon className="h-4 w-4" />
                    </Button>
                  </div>

                  {knowledgeType === "url" ? (
                    <form onSubmit={handleCrawl} className="space-y-4">
                      <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        <p className="text-sm text-blue-800">
                          <strong>💡 Tip:</strong> Add your website URL that
                          contains information you want your bot to learn from.
                          The bot will crawl and index the content from the
                          pages it finds.
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <div className="flex-1 space-y-1">
                          <Label htmlFor="url">Website URL</Label>
                          <Input
                            id="url"
                            placeholder="https://example.com/docs"
                            value={newUrl}
                            onChange={(e) => setNewUrl(e.target.value)}
                            required
                          />
                        </div>
                        <div className="self-end">
                          <Button
                            type="submit"
                            disabled={isCrawling || !newUrl.trim()}
                          >
                            {isCrawling ? (
                              <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Starting...
                              </>
                            ) : (
                              <>
                                <Search className="h-4 w-4 mr-2" />
                                Crawl URL
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        We&apos;ll crawl the website and process its content for
                        your chatbot.
                      </p>
                    </form>
                  ) : knowledgeType === "file" ? (
                    <form onSubmit={handleFileUpload} className="space-y-4">
                      <div className="mb-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                        <p className="text-sm text-green-800">
                          <strong>💡 Tip:</strong> Upload policy documents,
                          product guides, presentations (PPT), PDFs, or any
                          files related to your product, firm, or website that
                          you want the bot to reference.
                        </p>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="file">
                          Upload Files (PDF, DOCX, TXT, MD)
                        </Label>
                        <div className="flex gap-2">
                          <Input
                            id="file"
                            type="file"
                            multiple
                            accept=".pdf,.docx,.txt,.md"
                            onChange={(e) => setUploadFiles(e.target.files)}
                            className="flex-1"
                            required
                          />
                          <Button
                            type="submit"
                            disabled={
                              isUploading ||
                              !uploadFiles ||
                              uploadFiles.length === 0
                            }
                          >
                            {isUploading ? (
                              <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Uploading...
                              </>
                            ) : (
                              <>
                                <Upload className="h-4 w-4 mr-2" />
                                Upload
                              </>
                            )}
                          </Button>
                        </div>
                        <p className="text-xs text-muted-foreground flex items-center gap-1">
                          <AlertCircle className="h-3 w-3" /> Max file size 10MB
                        </p>
                      </div>
                    </form>
                  ) : (
                    <div className="space-y-6">
                      <div className="mb-3 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                        <p className="text-sm text-purple-800">
                          <strong>💡 Tip:</strong> Add frequently asked
                          questions (FAQs) from your site or any specific
                          questions you want your bot to answer consistently.
                          This ensures accurate responses for common queries.
                        </p>
                      </div>
                      <form onSubmit={handleQASubmit} className="space-y-4">
                        <div className="grid gap-4">
                          <div className="space-y-1">
                            <Label htmlFor="q">Question</Label>
                            <Input
                              id="q"
                              value={newQA.question}
                              onChange={(e) =>
                                setNewQA({ ...newQA, question: e.target.value })
                              }
                              placeholder="e.g. What are your opening hours?"
                              required
                            />
                          </div>
                          <div className="space-y-1">
                            <Label htmlFor="a">Answer</Label>
                            <Input
                              id="a"
                              value={newQA.answer}
                              onChange={(e) =>
                                setNewQA({ ...newQA, answer: e.target.value })
                              }
                              placeholder="e.g. We are open from 9 AM to 6 PM."
                              required
                            />
                          </div>
                        </div>
                        <Button type="submit">
                          {editingQA ? "Update QA Pair" : "Add QA Pair"}
                        </Button>
                        {editingQA && (
                          <Button
                            variant="ghost"
                            className="ml-2"
                            onClick={() => {
                              setEditingQA(null);
                              setNewQA({ question: "", answer: "" });
                            }}
                          >
                            Cancel
                          </Button>
                        )}
                      </form>

                      <div className="pt-4 border-t">
                        <Label className="text-xs font-semibold uppercase text-muted-foreground">
                          Or Bulk Upload (XLSX)
                        </Label>
                        <div className="mt-2 mb-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                          <p className="text-sm text-amber-800 mb-2">
                            <strong>📊 Excel Format:</strong> Your XLSX file
                            should contain two columns:
                          </p>
                          <ul className="text-xs text-amber-700 ml-4 space-y-1 list-disc">
                            <li>
                              <strong>Column A:</strong> &quot;question&quot; -
                              The question text
                            </li>
                            <li>
                              <strong>Column B:</strong> &quot;answer&quot; -
                              The corresponding answer
                            </li>
                            <li>
                              First row should be the header row with column
                              names
                            </li>
                            <li>Each subsequent row represents one Q&A pair</li>
                          </ul>
                        </div>
                        <form
                          onSubmit={handleQAXlsxUpload}
                          className="mt-2 flex gap-2"
                        >
                          <Input
                            type="file"
                            accept=".xlsx,.xls"
                            onChange={(e) =>
                              setQaXlsx(e.target.files?.[0] || null)
                            }
                            className="flex-1"
                          />
                          <Button
                            type="submit"
                            variant="outline"
                            disabled={!qaXlsx}
                          >
                            <Upload className="h-4 w-4 mr-2" /> Upload XLSX
                          </Button>
                        </form>
                      </div>
                    </div>
                  )}
                </div>
              )}

              <Tabs
                value={knowledgeTab}
                onValueChange={setKnowledgeTab}
                className="w-full"
              >
                <TabsList className="mb-4">
                  <TabsTrigger value="crawl" className="gap-2">
                    <Globe className="h-4 w-4" /> Crawl{" "}
                    {allCrawledPages.length > 0 && (
                      <Badge variant="secondary" className="ml-1 h-5 px-1">
                        {allCrawledPages.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="files" className="gap-2">
                    <FileText className="h-4 w-4" /> Files{" "}
                    {fileSources.length > 0 && (
                      <Badge variant="secondary" className="ml-1 h-5 px-1">
                        {fileSources.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="qa" className="gap-2">
                    <MessageSquare className="h-4 w-4" /> Q&A{" "}
                    {qaPairs.length > 0 && (
                      <Badge variant="secondary" className="ml-1 h-5 px-1">
                        {qaPairs.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                </TabsList>

                {isLoadingKnowledge ? (
                  <div className="flex justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                  </div>
                ) : (
                  <>
                    {/* Crawl Tab Content */}
                    <TabsContent value="crawl" className="space-y-4">
                      {isCrawlScheduleOpen && selectedCrawlSource && (
                        <CrawlScheduleModal
                          knowledgeSourceId={selectedCrawlSource.id}
                          sourceUrl={selectedCrawlSource.source_url || ""}
                          pagesCount={selectedCrawlSource.pages_found || 0}
                          lastSynced={selectedCrawlSource.updated_at ?? null}
                          onClose={() => {
                            setIsCrawlScheduleOpen(false);
                            setSelectedCrawlSource(null);
                          }}
                          onSync={async () => {
                            // Show toast that sync has started
                            setToastMessage({
                              type: "info",
                              message:
                                "Crawl started. This may take a few minutes...",
                            });
                            // Enable polling to track crawl progress
                            setManuallyStartedCrawl(true);
                            // Fetch immediately to get updated status (crawling)
                            await fetchKnowledgeSources();
                            // Also refresh stats
                            fetchChatbotStats();
                          }}
                        />
                      )}
                      {crawlSourcesWithPages.length > 0 ? (
                        <div className="space-y-4">
                          {Array.from(
                            new Map(
                              crawlSourcesWithPages.map((ks) => [
                                ks.source_url,
                                ks,
                              ]),
                            ).values(),
                          ).map((ks) => (
                            <CrawlSourcePanel
                              key={ks.id}
                              source={ks}
                              pages={allCrawledPages.filter(
                                (p) => p.source_url === ks.source_url,
                              )}
                              selectedPages={selectedPages}
                              onSelectionChange={setSelectedPages}
                              onSchedule={() => {
                                setSelectedCrawlSource(ks);
                                setIsCrawlScheduleOpen(true);
                              }}
                              onDeleteSelected={() => handleBulkDelete("pages")}
                              isBulkDeleting={isBulkDeleting}
                            />
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-12 border-2 border-dashed rounded-xl">
                          <Globe className="h-12 w-12 mx-auto text-gray-300 mb-3" />
                          <p className="text-gray-500">
                            No crawled pages found
                          </p>
                          <Button
                            variant="link"
                            onClick={() => {
                              setKnowledgeType("url");
                              setIsAddKnowledgeOpen(true);
                            }}
                          >
                            Add website URL
                          </Button>
                        </div>
                      )}
                    </TabsContent>

                    {/* Files Tab Content */}
                    <TabsContent value="files" className="space-y-4">
                      {fileSources.length > 0 && (
                        <div className="flex items-center justify-between bg-muted/20 p-2 rounded-md mb-2">
                          <div className="flex items-center gap-2">
                            <Checkbox
                              checked={
                                selectedFiles.length === fileSources.length &&
                                fileSources.length > 0
                              }
                              onCheckedChange={(checked: boolean) => {
                                if (checked)
                                  setSelectedFiles(
                                    fileSources.map((s) => s.id),
                                  );
                                else setSelectedFiles([]);
                              }}
                            />
                            <span className="text-sm font-medium">
                              Select All
                            </span>
                          </div>
                          {selectedFiles.length > 0 && (
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => handleBulkDelete("files")}
                              disabled={isBulkDeleting}
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete {selectedFiles.length}
                            </Button>
                          )}
                        </div>
                      )}

                      {fileSources.length > 0 ? (
                        <div className="space-y-2">
                          {fileSources.map((source) => (
                            <div
                              key={source.id}
                              className={`flex items-center justify-between p-3 border rounded-lg hover:bg-muted/5 transition-colors ${
                                selectedFiles.includes(source.id)
                                  ? "bg-blue-50/30 border-blue-200"
                                  : ""
                              }`}
                            >
                              <div className="flex items-center gap-3">
                                <Checkbox
                                  checked={selectedFiles.includes(source.id)}
                                  onCheckedChange={(checked: boolean) => {
                                    if (checked)
                                      setSelectedFiles([
                                        ...selectedFiles,
                                        source.id,
                                      ]);
                                    else
                                      setSelectedFiles(
                                        selectedFiles.filter(
                                          (id) => id !== source.id,
                                        ),
                                      );
                                  }}
                                />
                                <div className="h-8 w-8 rounded bg-blue-50 flex items-center justify-center text-blue-600">
                                  <FileText className="h-4 w-4" />
                                </div>
                                <div>
                                  <div className="font-medium text-sm">
                                    {source.files && source.files.length > 0
                                      ? source.files[0].filename
                                      : "Uploaded File"}
                                  </div>
                                  <div className="text-xs text-muted-foreground">
                                    {source.files && source.files.length > 0
                                      ? `${(
                                          source.files[0].file_size / 1024
                                        ).toFixed(1)} KB`
                                      : ""}{" "}
                                    •{" "}
                                    {new Date(
                                      source.created_at,
                                    ).toLocaleDateString()}
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge
                                  variant={
                                    source.status === "completed"
                                      ? "success"
                                      : "secondary"
                                  }
                                  className="text-[10px] px-1 h-4"
                                >
                                  {source.status}
                                </Badge>
                                {source.status === "completed" &&
                                  source.files?.[0] && (
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      className="h-8"
                                      disabled={
                                        previewingFileId === source.files[0].id
                                      }
                                      onClick={() =>
                                        handleOpenUploadedFile(
                                          source.id,
                                          source.files![0],
                                        )
                                      }
                                      title="Open file"
                                    >
                                      {previewingFileId ===
                                      source.files[0].id ? (
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                      ) : (
                                        "Show"
                                      )}
                                    </Button>
                                  )}
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                                  onClick={() => handleDeleteSource(source.id)}
                                  title="Delete file"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-12 border-2 border-dashed rounded-xl">
                          <FileText className="h-12 w-12 mx-auto text-gray-300 mb-3" />
                          <p className="text-gray-500">No files uploaded yet</p>
                          <Button
                            variant="link"
                            onClick={() => {
                              setKnowledgeType("file");
                              setIsAddKnowledgeOpen(true);
                            }}
                          >
                            Upload your first file
                          </Button>
                        </div>
                      )}
                    </TabsContent>

                    {/* Q&A Tab Content */}
                    {/* Q&A Tab Content */}
                    <TabsContent value="qa" className="space-y-4">
                      {(() => {
                        const qaSources = knowledgeSources.filter(
                          (s) =>
                            s.source_type === "qa_pair" &&
                            s.source_url !== "manual" &&
                            s.files?.length === 0, // Ensure it's not just a file upload but a logical bundle
                        );

                        // Standalone QAs (manual source) + unassigned ones?
                        // Actually, list_qa_pairs returns ALL pairs.
                        // We need to filter pairs that belong to "manual" source for the standalone list
                        // But wait, the previous code showed ALL pairs.
                        // If we show bundles, we should NOT show their pairs in the main list.
                        // So we need to separate them.

                        const bundleIds = qaSources.map((s) => s.id);
                        const standaloneQAs = qaPairs.filter(
                          (qa) =>
                            !knowledgeSources.some(
                              (ks) =>
                                ks.id === (qa as any).knowledge_source_id && // Assuming we can get KS ID from QA pair
                                bundleIds.includes(ks.id),
                            ),
                        );

                        // The current QA query doesn't return knowledge_source_id on the QA object in the interface
                        // We might need to rely on the knowledgeSources structure if it includes qa_pairs
                        // Let's check the interface... KnowledgeSource has qa_pairs? Yes: qa_pairs?: QAPair[];

                        // Better approach:
                        // Iterate through knowledgeSources to render bundles.
                        // Also show a section for "Manual Q&A" if the "manual" source exists.

                        const manualSource = knowledgeSources.find(
                          (s) =>
                            s.source_type === "qa_pair" &&
                            s.source_url === "manual",
                        );

                        // Fallback: if we can't find manual source but we have pairs that don't belong to known bundles
                        // For now, let's treat `qaPairs` as the source of truth for ALL, but we want to visually group.
                        // If `qaPairs` contains everything, we need to filter out those we display in panels.

                        // Actually, usage of KnowledgeSourceResponse in backend for upload_qa_xlsx returns a KS with pre-loaded qa_pairs.
                        // But `fetchKnowledgeSources` might not load all qa_pairs for every source to avoid payload size?
                        // Let's assume for now we use the `knowledgeSources` array which hopefully includes `qa_pairs` if updated properly.
                        // The `upload_qa_xlsx` returns the KS with pairs. `list_knowledge_sources` normally doesn't include potentially huge lists of pairs?
                        // Wait, `ChatbotService.list_knowledge_sources` just returns KnowledgeSource objects.
                        // The frontend 'qaPairs' state comes from `fetchQAPairs`.

                        // We need to match pairs to sources.
                        // The QAPair interface in frontend doesn't have knowledge_source_id.
                        // Let's assume we render:
                        // 1. QA Bundles (from knowledgeSources) -> BUT we need the pairs for them.
                        // If the QA pair list API doesn't return source_id, we can't separate them easily on frontend without changing API.
                        // Looking at backend `list_qa_pairs`: it returns `QAPairResponse` which DOES have `knowledge_source_id`.
                        // The frontend `QAPair` interface just missed it. Let's update the interface first.

                        return (
                          <>
                            {/* Render Bundles */}
                            {qaSources.map((source) => {
                              // Find pairs for this source
                              const sourcePairs = qaPairs
                                .filter(
                                  (qa: any) =>
                                    qa.knowledge_source_id === source.id,
                                )
                                .sort((a, b) => {
                                  const timeA = new Date(
                                    a.created_at || 0,
                                  ).getTime();
                                  const timeB = new Date(
                                    b.created_at || 0,
                                  ).getTime();
                                  if (timeA !== timeB) return timeA - timeB;
                                  return a.id.localeCompare(b.id);
                                });

                              return (
                                <QABundlePanel
                                  key={source.id}
                                  source={source as any}
                                  qaPairs={sourcePairs}
                                  selectedPairs={selectedQAs}
                                  onSelectionChange={setSelectedQAs}
                                  onDeleteSource={() =>
                                    handleDeleteSource(
                                      source.id,
                                      `Are you sure you want to delete this bundle? It contains ${sourcePairs.length} Q&A pairs. Bundle: ${source.source_url}`,
                                    )
                                  }
                                  onDeleteSelectedPairs={() =>
                                    handleBulkDelete("qa")
                                  }
                                  isDeleting={isBulkDeleting}
                                  onEditPair={(qa) => {
                                    setEditingQA(qa as any);
                                    setNewQA({
                                      question: qa.question,
                                      answer: qa.answer,
                                    });
                                    setKnowledgeType("qa");
                                    setIsAddKnowledgeOpen(true);
                                    window.scrollTo({
                                      top: 0,
                                      behavior: "smooth",
                                    });
                                  }}
                                  onDeletePair={handleDeleteQA}
                                />
                              );
                            })}

                            <div className="my-4 border-t" />

                            <div className="space-y-4">
                              <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                                Manual Q&A Pairs
                              </h3>

                              {/* Filter standalone pairs */}
                              {(() => {
                                const standalone = qaPairs
                                  .filter((qa: any) => {
                                    // Include if it belongs to "manual" source OR if we can't find its source in the bundles list
                                    return !bundleIds.includes(
                                      qa.knowledge_source_id,
                                    );
                                  })
                                  .sort((a, b) => {
                                    const timeA = new Date(
                                      a.created_at || 0,
                                    ).getTime();
                                    const timeB = new Date(
                                      b.created_at || 0,
                                    ).getTime();
                                    if (timeA !== timeB) return timeA - timeB;
                                    return a.id.localeCompare(b.id);
                                  });

                                if (
                                  standalone.length === 0 &&
                                  qaSources.length === 0
                                ) {
                                  return (
                                    <div className="text-center py-12 border-2 border-dashed rounded-xl">
                                      <MessageSquare className="h-12 w-12 mx-auto text-gray-300 mb-3" />
                                      <p className="text-gray-500">
                                        No Q&A pairs added
                                      </p>
                                      <Button
                                        variant="link"
                                        onClick={() => {
                                          setKnowledgeType("qa");
                                          setIsAddKnowledgeOpen(true);
                                        }}
                                      >
                                        Add Q&A manually
                                      </Button>
                                    </div>
                                  );
                                }

                                if (standalone.length === 0)
                                  return (
                                    <p className="text-sm text-muted-foreground italic">
                                      No manual Q&A pairs.
                                    </p>
                                  );

                                return (
                                  <>
                                    {standalone.length > 0 && (
                                      <div className="flex items-center justify-between bg-muted/20 p-2 rounded-md mb-2">
                                        <div className="flex items-center gap-2">
                                          <Checkbox
                                            checked={
                                              standalone.length > 0 &&
                                              standalone.every((q) =>
                                                selectedQAs.includes(q.id),
                                              )
                                            }
                                            onCheckedChange={(
                                              checked: boolean,
                                            ) => {
                                              if (checked) {
                                                // Add all standalone IDs
                                                const newSelected = [
                                                  ...selectedQAs,
                                                  ...standalone
                                                    .map((q) => q.id)
                                                    .filter(
                                                      (id) =>
                                                        !selectedQAs.includes(
                                                          id,
                                                        ),
                                                    ),
                                                ];
                                                setSelectedQAs(newSelected);
                                              } else {
                                                // Remove all standalone IDs
                                                const standaloneIds =
                                                  standalone.map((q) => q.id);
                                                setSelectedQAs(
                                                  selectedQAs.filter(
                                                    (id) =>
                                                      !standaloneIds.includes(
                                                        id,
                                                      ),
                                                  ),
                                                );
                                              }
                                            }}
                                          />
                                          <span className="text-sm font-medium">
                                            Select All ({standalone.length})
                                          </span>
                                        </div>
                                        {selectedQAs.filter((id) =>
                                          standalone.find((q) => q.id === id),
                                        ).length > 0 && (
                                          <Button
                                            variant="destructive"
                                            size="sm"
                                            onClick={() =>
                                              handleBulkDelete("qa")
                                            }
                                            disabled={isBulkDeleting}
                                          >
                                            <Trash2 className="h-4 w-4 mr-2" />
                                            Delete Selected
                                          </Button>
                                        )}
                                      </div>
                                    )}

                                    <div className="space-y-3">
                                      {standalone.map((qa) => (
                                        <div
                                          key={qa.id}
                                          className={`p-4 border rounded-lg bg-card shadow-sm hover:shadow-md transition-all ${
                                            selectedQAs.includes(qa.id)
                                              ? "bg-blue-50/30 border-blue-200"
                                              : ""
                                          }`}
                                        >
                                          <div className="flex justify-between items-start gap-4">
                                            <div className="flex items-start gap-3 flex-1">
                                              <Checkbox
                                                className="mt-1"
                                                checked={selectedQAs.includes(
                                                  qa.id,
                                                )}
                                                onCheckedChange={(
                                                  checked: boolean,
                                                ) => {
                                                  if (checked)
                                                    setSelectedQAs([
                                                      ...selectedQAs,
                                                      qa.id,
                                                    ]);
                                                  else
                                                    setSelectedQAs(
                                                      selectedQAs.filter(
                                                        (id) => id !== qa.id,
                                                      ),
                                                    );
                                                }}
                                              />
                                              <div className="flex-1 min-w-0">
                                                <div className="font-semibold text-sm mb-1">
                                                  Q: {qa.question}
                                                </div>
                                                <div className="text-sm text-muted-foreground bg-muted/30 p-2 rounded border-l-2 border-blue-500 line-clamp-2">
                                                  A: {qa.answer}
                                                </div>
                                              </div>
                                            </div>
                                            <div className="flex gap-1 shrink-0">
                                              <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-8 w-8"
                                                onClick={() => {
                                                  setEditingQA(qa);
                                                  setNewQA({
                                                    question: qa.question,
                                                    answer: qa.answer,
                                                  });
                                                  setKnowledgeType("qa");
                                                  setIsAddKnowledgeOpen(true);
                                                  window.scrollTo({
                                                    top: 0,
                                                    behavior: "smooth",
                                                  });
                                                }}
                                                title="Edit QA pair"
                                              >
                                                <Edit2 className="h-4 w-4" />
                                              </Button>
                                              <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                                                onClick={() =>
                                                  handleDeleteQA(qa.id)
                                                }
                                                title="Delete QA pair"
                                              >
                                                <Trash2 className="h-4 w-4" />
                                              </Button>
                                            </div>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </>
                                );
                              })()}
                            </div>
                          </>
                        );
                      })()}
                    </TabsContent>
                  </>
                )}
              </Tabs>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Appearance Tab */}
        <TabsContent value="appearance" className="space-y-4">
          {appearanceError && (
            <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
              {appearanceError}
            </div>
          )}

          {appearanceSuccessMessage && (
            <div className="p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg">
              {appearanceSuccessMessage}
            </div>
          )}

          <form onSubmit={handleSubmit(handleAppearanceSubmit)}>
            <div className="max-w-4xl">
              {/* Settings Form */}
              <div className="space-y-6">
                {/* General Settings */}
                <Card>
                  <CardHeader>
                    <CardTitle>General</CardTitle>
                    <CardDescription>
                      Basic chatbot appearance settings
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="header_text">Header Text</Label>
                      <Controller
                        name="header_text"
                        control={control}
                        render={({ field }) => (
                          <Input
                            {...field}
                            id="header_text"
                            placeholder="Chat Support"
                            onChange={(e) => {
                              console.log(
                                "✏️ Header Text onChange:",
                                e.target.value,
                              );
                              field.onChange(e.target.value);
                            }}
                          />
                        )}
                      />
                      {errors.header_text && (
                        <p className="text-sm text-red-600 mt-1">
                          {errors.header_text.message}
                        </p>
                      )}
                    </div>

                    <div>
                      <Label htmlFor="primary_color">Primary Color</Label>
                      <div className="flex gap-2">
                        <input
                          id="primary_color"
                          type="color"
                          value={watchedPrimaryColor || "#3B82F6"}
                          onChange={(e) => {
                            console.log(
                              "🎨 Color picker onChange:",
                              e.target.value,
                            );
                            setValue("primary_color", e.target.value, {
                              shouldDirty: true,
                            });
                          }}
                          className="w-16 h-10 p-1 border rounded cursor-pointer"
                        />
                        <Input
                          value={watchedPrimaryColor || ""}
                          onChange={(e) => {
                            console.log(
                              "🎨 Color input onChange:",
                              e.target.value,
                            );
                            setValue("primary_color", e.target.value, {
                              shouldDirty: true,
                            });
                          }}
                          placeholder="#3B82F6"
                          className="flex-1"
                        />
                      </div>
                      {errors.primary_color && (
                        <p className="text-sm text-red-600 mt-1">
                          {errors.primary_color.message}
                        </p>
                      )}
                    </div>

                    <div>
                      <Label htmlFor="welcome_message">Welcome Message</Label>
                      <Textarea
                        id="welcome_message"
                        {...register("welcome_message")}
                        placeholder="Hi! How can I help you today?"
                        rows={3}
                      />
                    </div>

                    <div>
                      <Label htmlFor="avatar_url">Avatar URL</Label>
                      <div className="space-y-2">
                        <Input
                          id="avatar_url"
                          {...register("avatar_url")}
                          placeholder="https://example.com/avatar.png"
                        />
                        <input
                          ref={avatarInputRef}
                          type="file"
                          accept="image/*"
                          style={{ display: "none" }}
                          onChange={async (e) => {
                            const file = e.target.files?.[0];
                            if (!file) return;
                            try {
                              const token = getAccessToken();
                              if (!token) return;
                              const API_URL =
                                process.env.NEXT_PUBLIC_API_URL ||
                                "http://localhost:8000";
                              const formData = new FormData();
                              formData.append("avatar", file);
                              const res = await fetch(
                                `${API_URL}/api/v1/chatbots/${chatbotId}/avatar`,
                                {
                                  method: "POST",
                                  headers: {
                                    Authorization: `Bearer ${token}`,
                                  },
                                  body: formData,
                                },
                              );
                              if (res.ok) {
                                fetchAppearance();
                                setAppearanceSuccessMessage(
                                  "Avatar uploaded successfully!",
                                );
                                setTimeout(
                                  () => setAppearanceSuccessMessage(null),
                                  3000,
                                );
                              } else {
                                const err = await res
                                  .json()
                                  .catch(() => ({ detail: "Upload failed" }));
                                setAppearanceError(
                                  err.detail || "Avatar upload failed",
                                );
                              }
                            } catch (err) {
                              setAppearanceError("Avatar upload error");
                            } finally {
                              if (avatarInputRef.current)
                                avatarInputRef.current.value = "";
                            }
                          }}
                        />
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          className="w-full"
                          onClick={() => avatarInputRef.current?.click()}
                        >
                          <Upload className="h-4 w-4 mr-2" />
                          Upload Custom Avatar
                        </Button>
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="position">Position</Label>
                      <RadioGroup
                        value={formData.position}
                        onValueChange={(value) =>
                          setValue(
                            "position",
                            value as "bottom-right" | "bottom-left",
                            { shouldDirty: true },
                          )
                        }
                        className="flex gap-6 mt-2"
                      >
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem
                            value="bottom-left"
                            id="bottom-left"
                          />
                          <Label htmlFor="bottom-left">Bottom Left</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem
                            value="bottom-right"
                            id="bottom-right"
                          />
                          <Label htmlFor="bottom-right">Bottom Right</Label>
                        </div>
                      </RadioGroup>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="offset_x">Offset X (px)</Label>
                        <Controller
                          name="offset_x"
                          control={control}
                          render={({ field }) => (
                            <Input
                              {...field}
                              id="offset_x"
                              type="number"
                              placeholder="0"
                              value={field.value ?? 0}
                              onChange={(e) => {
                                const value =
                                  e.target.value === ""
                                    ? 0
                                    : parseInt(e.target.value, 10) || 0;
                                field.onChange(value);
                              }}
                            />
                          )}
                        />
                        {errors.offset_x && (
                          <p className="text-sm text-red-600 mt-1">
                            {errors.offset_x.message}
                          </p>
                        )}
                      </div>
                      <div>
                        <Label htmlFor="offset_y">Offset Y (px)</Label>
                        <Controller
                          name="offset_y"
                          control={control}
                          render={({ field }) => (
                            <Input
                              {...field}
                              id="offset_y"
                              type="number"
                              placeholder="0"
                              value={field.value ?? 0}
                              onChange={(e) => {
                                const value =
                                  e.target.value === ""
                                    ? 0
                                    : parseInt(e.target.value, 10) || 0;
                                field.onChange(value);
                              }}
                            />
                          )}
                        />
                        {errors.offset_y && (
                          <p className="text-sm text-red-600 mt-1">
                            {errors.offset_y.message}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Switch
                        id="show_branding"
                        checked={formData.show_branding}
                        onCheckedChange={(checked) =>
                          setValue("show_branding", checked, {
                            shouldDirty: true,
                          })
                        }
                      />
                      <Label htmlFor="show_branding">Show branding</Label>
                    </div>
                  </CardContent>
                </Card>

                {/* Initial Suggestions */}
                <Card>
                  <CardHeader>
                    <CardTitle>Initial Suggestions</CardTitle>
                    <CardDescription>
                      Suggested questions to help users start conversations
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex gap-2">
                      <Input
                        placeholder="Add a suggestion..."
                        value={newSuggestion}
                        onChange={(e) => setNewSuggestion(e.target.value)}
                        onKeyPress={(e) =>
                          e.key === "Enter" &&
                          (e.preventDefault(), handleAddSuggestion())
                        }
                      />
                      <Button
                        type="button"
                        onClick={handleAddSuggestion}
                        size="sm"
                      >
                        Add
                      </Button>
                    </div>

                    <div className="space-y-2">
                      {(formData.initial_suggestions || []).map(
                        (suggestion, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-2 bg-muted rounded"
                          >
                            <span className="text-sm">{suggestion}</span>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => handleRemoveSuggestion(index)}
                              className="h-6 w-6 p-0 text-red-500 hover:text-red-700"
                            >
                              ×
                            </Button>
                          </div>
                        ),
                      )}
                    </div>
                  </CardContent>
                </Card>

                {/* Save Button */}
                <div className="flex justify-end">
                  <Button
                    type="submit"
                    disabled={isSavingAppearance || !isDirty}
                  >
                    {isSavingAppearance ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Save Changes
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </form>
        </TabsContent>

        {/* Install Tab */}
        <TabsContent value="install" className="space-y-6">
          {/* Quick Start Guide */}
          <Card className="border-purple-200 bg-purple-50/30">
            <CardHeader>
              <div className="flex items-start gap-3">
                <div className="h-10 w-10 rounded-lg bg-purple-600 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
                <div>
                  <CardTitle>Quick Start Guide</CardTitle>
                  <CardDescription className="mt-1">
                    Get your chatbot live on your website in 3 simple steps
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-semibold text-sm">
                    1
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm mb-1">
                      Choose Your Integration Method
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Select between JavaScript Widget (recommended) or iframe
                      embed below based on your platform.
                    </p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-semibold text-sm">
                    2
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm mb-1">
                      Copy and Paste the Code
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Copy the code snippet and paste it into your website's
                      HTML, just before the closing{" "}
                      <code className="bg-purple-100 px-1.5 py-0.5 rounded text-xs">
                        &lt;/body&gt;
                      </code>{" "}
                      tag.
                    </p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-semibold text-sm">
                    3
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm mb-1">
                      Test Your Chatbot
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Refresh your website and look for the chat widget in the
                      bottom corner. Click it to start chatting!
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* JavaScript Widget (Recommended) */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    JavaScript Widget
                    <Badge
                      variant="secondary"
                      className="bg-green-100 text-green-700"
                    >
                      Recommended
                    </Badge>
                  </CardTitle>
                  <CardDescription className="mt-1">
                    Best for most websites. Lightweight, fully customizable, and
                    works with any platform.
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <p className="text-sm">
                    <strong>Automatic updates:</strong> Changes to appearance
                    and settings sync instantly
                  </p>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <p className="text-sm">
                    <strong>Lightweight:</strong> Only ~15KB gzipped, won't slow
                    down your site
                  </p>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <p className="text-sm">
                    <strong>Mobile responsive:</strong> Optimized for all
                    devices and screen sizes
                  </p>
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="text-sm font-semibold mb-3">
                  Installation Code
                </h4>
                <div className="bg-slate-950 text-slate-50 p-4 rounded-md font-mono text-sm overflow-x-auto">
                  <pre id="embed-script">{`<script src="${
                    process.env.NEXT_PUBLIC_WIDGET_URL ||
                    process.env.NEXT_PUBLIC_APP_URL ||
                    "http://localhost:3001"
                  }/widget.umd.js"></script>
<script>
  ChatbotWidget.init({
    chatbotId: "${chatbotId}"${
      process.env.NEXT_PUBLIC_API_URL
        ? `,\n    apiUrl: "${process.env.NEXT_PUBLIC_API_URL}"`
        : ""
    }
  });
</script>`}</pre>
                </div>
                <Button
                  variant="default"
                  className="mt-3"
                  onClick={async () => {
                    const el = document.getElementById("embed-script");
                    if (!el) return;
                    const text = el.textContent || "";
                    try {
                      await navigator.clipboard.writeText(text);
                      setEmbedCopyStatus("embed-script");
                      setTimeout(() => setEmbedCopyStatus(null), 2000);
                    } catch {
                      const ta = document.createElement("textarea");
                      ta.value = text;
                      document.body.appendChild(ta);
                      ta.select();
                      document.execCommand("copy");
                      setEmbedCopyStatus("embed-script");
                      setTimeout(() => setEmbedCopyStatus(null), 2000);
                      document.body.removeChild(ta);
                    }
                  }}
                >
                  <Code className="h-4 w-4 mr-2" />
                  {embedCopyStatus === "embed-script" ? "Copied!" : "Copy Code"}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Platform-Specific Instructions */}
          <Card>
            <CardHeader>
              <CardTitle>Platform-Specific Instructions</CardTitle>
              <CardDescription>
                Step-by-step guides for popular platforms
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* HTML/Static Websites */}
                <div className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <Globe className="h-5 w-5 text-purple-600" />
                    <h4 className="font-semibold">HTML / Static Websites</h4>
                  </div>
                  <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground ml-7">
                    <li>Open your HTML file in a text editor</li>
                    <li>
                      Find the closing{" "}
                      <code className="bg-muted px-1.5 py-0.5 rounded text-xs">
                        &lt;/body&gt;
                      </code>{" "}
                      tag
                    </li>
                    <li>Paste the JavaScript Widget code just before it</li>
                    <li>Save the file and refresh your browser</li>
                  </ol>
                </div>

                {/* React */}
                <div className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <Code className="h-5 w-5 text-blue-600" />
                    <h4 className="font-semibold">React / Next.js</h4>
                  </div>
                  <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground ml-7">
                    <li>
                      Add the script to your{" "}
                      <code className="bg-muted px-1.5 py-0.5 rounded text-xs">
                        public/index.html
                      </code>{" "}
                      (React) or{" "}
                      <code className="bg-muted px-1.5 py-0.5 rounded text-xs">
                        _document.tsx
                      </code>{" "}
                      (Next.js)
                    </li>
                    <li>
                      Place it in the{" "}
                      <code className="bg-muted px-1.5 py-0.5 rounded text-xs">
                        &lt;body&gt;
                      </code>{" "}
                      section or use{" "}
                      <code className="bg-muted px-1.5 py-0.5 rounded text-xs">
                        useEffect()
                      </code>{" "}
                      to load it dynamically
                    </li>
                    <li>
                      Alternatively, use the iframe method for easier
                      integration
                    </li>
                  </ol>
                </div>

                {/* WordPress */}
                <div className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <Globe className="h-5 w-5 text-blue-500" />
                    <h4 className="font-semibold">WordPress</h4>
                  </div>
                  <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground ml-7">
                    <li>
                      Go to <strong>Appearance → Theme File Editor</strong>
                    </li>
                    <li>
                      Select{" "}
                      <code className="bg-muted px-1.5 py-0.5 rounded text-xs">
                        footer.php
                      </code>{" "}
                      from the right sidebar
                    </li>
                    <li>
                      Paste the code before the{" "}
                      <code className="bg-muted px-1.5 py-0.5 rounded text-xs">
                        &lt;/body&gt;
                      </code>{" "}
                      tag
                    </li>
                    <li>
                      Click <strong>Update File</strong>
                    </li>
                    <li>
                      <em>
                        Or use a plugin like "Insert Headers and Footers" for
                        easier management
                      </em>
                    </li>
                  </ol>
                </div>

                {/* Shopify */}
                <div className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <Globe className="h-5 w-5 text-green-600" />
                    <h4 className="font-semibold">Shopify</h4>
                  </div>
                  <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground ml-7">
                    <li>
                      Go to <strong>Online Store → Themes</strong>
                    </li>
                    <li>
                      Click <strong>Actions → Edit code</strong>
                    </li>
                    <li>
                      Find{" "}
                      <code className="bg-muted px-1.5 py-0.5 rounded text-xs">
                        theme.liquid
                      </code>{" "}
                      under Layout
                    </li>
                    <li>
                      Paste the code before{" "}
                      <code className="bg-muted px-1.5 py-0.5 rounded text-xs">
                        &lt;/body&gt;
                      </code>
                    </li>
                    <li>Save and preview your store</li>
                  </ol>
                </div>

                {/* Wix / Squarespace */}
                <div className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <Globe className="h-5 w-5 text-orange-600" />
                    <h4 className="font-semibold">
                      Wix / Squarespace / Webflow
                    </h4>
                  </div>
                  <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground ml-7">
                    <li>
                      Look for "Custom Code" or "Code Injection" in your site
                      settings
                    </li>
                    <li>
                      Add the script to the <strong>Footer</strong> or{" "}
                      <strong>Body End</strong> section
                    </li>
                    <li>Save and publish your changes</li>
                    <li>
                      <em>
                        Note: Exact steps vary by platform version - check their
                        documentation
                      </em>
                    </li>
                  </ol>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* iframe Alternative */}
          <Card>
            <CardHeader>
              <CardTitle>iframe Embed (Alternative)</CardTitle>
              <CardDescription>
                Use this if you prefer iframe embedding or need to restrict
                JavaScript execution
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-slate-950 text-slate-50 p-4 rounded-md font-mono text-sm overflow-x-auto">
                <pre id="embed-iframe">{`<iframe
  src="${
    process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"
  }/embed/${chatbotId}"
  width="400"
  height="600"
  style="border:0; width:100%; min-width:320px; min-height:420px;"
  title="Chatbot"
></iframe>`}</pre>
              </div>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={async () => {
                    const el = document.getElementById("embed-iframe");
                    if (!el) return;
                    const text = el.textContent || "";
                    try {
                      await navigator.clipboard.writeText(text);
                      setEmbedCopyStatus("embed-iframe");
                      setTimeout(() => setEmbedCopyStatus(null), 2000);
                    } catch {
                      const ta = document.createElement("textarea");
                      ta.value = text;
                      document.body.appendChild(ta);
                      ta.select();
                      document.execCommand("copy");
                      setEmbedCopyStatus("embed-iframe");
                      setTimeout(() => setEmbedCopyStatus(null), 2000);
                      document.body.removeChild(ta);
                    }
                  }}
                >
                  <Code className="h-4 w-4 mr-2" />
                  {embedCopyStatus === "embed-iframe"
                    ? "Copied!"
                    : "Copy iframe Code"}
                </Button>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex gap-2">
                  <HelpCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-blue-900">
                    <strong>Note:</strong> The iframe method displays the
                    chatbot inline on your page, not as a floating widget.
                    Adjust the width and height attributes to fit your layout.
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Testing and Troubleshooting */}
          <Card>
            <CardHeader>
              <CardTitle>Testing & Troubleshooting</CardTitle>
              <CardDescription>
                Verify your installation and fix common issues
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Testing Checklist */}
                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <CheckSquare className="h-4 w-4 text-purple-600" />
                    Testing Checklist
                  </h4>
                  <div className="space-y-2 ml-6">
                    <div className="flex items-start gap-2">
                      <div className="h-5 w-5 rounded border-2 border-muted-foreground flex-shrink-0 mt-0.5" />
                      <p className="text-sm">
                        Widget appears in the bottom corner of your page
                      </p>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="h-5 w-5 rounded border-2 border-muted-foreground flex-shrink-0 mt-0.5" />
                      <p className="text-sm">
                        Clicking the widget opens the chat interface
                      </p>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="h-5 w-5 rounded border-2 border-muted-foreground flex-shrink-0 mt-0.5" />
                      <p className="text-sm">
                        Your welcome message displays correctly
                      </p>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="h-5 w-5 rounded border-2 border-muted-foreground flex-shrink-0 mt-0.5" />
                      <p className="text-sm">Bot responds to test messages</p>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="h-5 w-5 rounded border-2 border-muted-foreground flex-shrink-0 mt-0.5" />
                      <p className="text-sm">Widget works on mobile devices</p>
                    </div>
                  </div>
                </div>

                {/* Common Issues */}
                <div className="border-t pt-6">
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-amber-600" />
                    Common Issues & Solutions
                  </h4>
                  <div className="space-y-4">
                    <div className="bg-muted/50 rounded-lg p-4">
                      <p className="font-medium text-sm mb-1">
                        Widget doesn't appear
                      </p>
                      <ul className="text-sm text-muted-foreground space-y-1 ml-4 list-disc">
                        <li>Check browser console for errors (F12)</li>
                        <li>
                          Verify the code is placed before the{" "}
                          <code className="bg-background px-1 rounded">
                            &lt;/body&gt;
                          </code>{" "}
                          tag
                        </li>
                        <li>Clear browser cache and hard refresh (Ctrl+F5)</li>
                        <li>
                          Ensure your chatbot status is set to "Active" in
                          Settings
                        </li>
                      </ul>
                    </div>

                    <div className="bg-muted/50 rounded-lg p-4">
                      <p className="font-medium text-sm mb-1">
                        Widget appears but doesn't respond
                      </p>
                      <ul className="text-sm text-muted-foreground space-y-1 ml-4 list-disc">
                        <li>
                          Verify you've added knowledge sources in the Knowledge
                          tab
                        </li>
                        <li>Check that your knowledge sources are indexed</li>
                        <li>Look for API errors in the browser console</li>
                      </ul>
                    </div>

                    <div className="bg-muted/50 rounded-lg p-4">
                      <p className="font-medium text-sm mb-1">
                        Widget conflicts with other elements
                      </p>
                      <ul className="text-sm text-muted-foreground space-y-1 ml-4 list-disc">
                        <li>Adjust widget position in the Appearance tab</li>
                        <li>Use offset settings to fine-tune placement</li>
                        <li>Check for CSS conflicts with z-index</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Need Help */}
                <div className="border-t pt-6">
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <div className="flex gap-3">
                      <HelpCircle className="h-5 w-5 text-purple-600 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <h4 className="font-semibold text-sm text-purple-900 mb-1">
                          Still need help?
                        </h4>
                        <p className="text-sm text-purple-800">
                          If you're experiencing issues not covered here, please
                          contact our support team or check our documentation
                          for more detailed guides and API references.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Tabs
            value={settingsSubTab}
            onValueChange={setSettingsSubTab}
            className="w-full"
          >
            <TabsList className="w-full justify-start border-b rounded-none h-auto p-0 bg-transparent mb-6">
              <TabsTrigger
                value="general"
                className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-4 py-2"
              >
                General
              </TabsTrigger>
              <TabsTrigger
                value="team"
                className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-4 py-2"
              >
                Team
              </TabsTrigger>
            </TabsList>
            <TabsContent value="general" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Chatbot Settings</CardTitle>
                  <CardDescription>
                    Update your chatbot&apos;s general information and status
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSettingsSubmit} className="space-y-6">
                    {settingsError && (
                      <div className="p-3 bg-red-50 border border-red-200 text-red-600 rounded-md text-sm">
                        {settingsError}
                      </div>
                    )}
                    {settingsSuccess && (
                      <div className="p-3 bg-green-50 border border-green-200 text-green-600 rounded-md text-sm">
                        {settingsSuccess}
                      </div>
                    )}

                    <div className="space-y-2">
                      <Label htmlFor="chatbot-name">Chatbot Name</Label>
                      <Input
                        id="chatbot-name"
                        name="name"
                        defaultValue={chatbot.name}
                        placeholder="My Awesome Chatbot"
                        required
                        disabled={!canEdit}
                      />
                      <p className="text-xs text-muted-foreground">
                        This is the internal name of your chatbot.
                      </p>
                    </div>

                    <div className="space-y-3">
                      <Label>Chatbot Status</Label>
                      <RadioGroup
                        name="status"
                        defaultValue={
                          chatbot.status === "draft" ? "paused" : chatbot.status
                        }
                        className="grid gap-4 sm:grid-cols-2"
                        disabled={!canEdit}
                      >
                        <div>
                          <RadioGroupItem
                            value="active"
                            id="status-active"
                            className="peer sr-only"
                          />
                          <Label
                            htmlFor="status-active"
                            className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                          >
                            <div className="mb-2 h-4 w-4 rounded-full border border-primary peer-data-[state=checked]:bg-primary" />
                            <span className="text-sm font-semibold">
                              Active
                            </span>
                            <span className="text-xs text-muted-foreground text-center mt-1">
                              Live and responding
                            </span>
                          </Label>
                        </div>
                        <div>
                          <RadioGroupItem
                            value="paused"
                            id="status-paused"
                            className="peer sr-only"
                          />
                          <Label
                            htmlFor="status-paused"
                            className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                          >
                            <div className="mb-2 h-4 w-4 rounded-full border border-primary peer-data-[state=checked]:bg-primary" />
                            <span className="text-sm font-semibold">
                              Paused
                            </span>
                            <span className="text-xs text-muted-foreground text-center mt-1">
                              Temporarily offline
                            </span>
                          </Label>
                        </div>
                      </RadioGroup>
                      {chatbot.status === "draft" && (
                        <p className="text-sm text-yellow-600 font-medium">
                          This chatbot is currently in Draft mode. Change it to
                          Active to make it live.
                        </p>
                      )}
                    </div>

                    <div className="flex justify-end pt-4 border-t">
                      <Button
                        type="submit"
                        disabled={isSavingSettings || !canEdit}
                      >
                        {isSavingSettings ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Saving...
                          </>
                        ) : (
                          <>
                            <Save className="h-4 w-4 mr-2" />
                            Save Settings
                          </>
                        )}
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>

              {["owner", "admin"].includes(chatbot.permission_level) && (
                <Card className="border-red-100">
                  <CardHeader>
                    <CardTitle className="text-red-600">Danger Zone</CardTitle>
                    <CardDescription>
                      Permanently delete this chatbot and all its data
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button
                      variant="destructive"
                      className="bg-red-600 hover:bg-red-700"
                      onClick={handleDeleteChatbot}
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete Chatbot
                    </Button>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
            <TabsContent value="team" className="space-y-6">
              <ChatbotTeamSettings chatbotId={chatbotId} />
            </TabsContent>
          </Tabs>
        </TabsContent>
      </Tabs>

      {/* Widget Preview - Visible in all tabs */}
      <Dialog
        open={isFilePreviewOpen}
        onOpenChange={handleFilePreviewOpenChange}
      >
        <DialogContent className="max-w-5xl w-[95vw] h-[85vh] flex flex-col">
          <DialogHeader>
            <DialogTitle className="truncate">{filePreviewTitle}</DialogTitle>
            <DialogDescription>
              Preview mode.
            </DialogDescription>
          </DialogHeader>
          <div className="flex-1 min-h-0 border rounded-md bg-white">
            {filePreviewType === "image" && filePreviewObjectUrl && (
              <div className="h-full overflow-auto p-4">
                <img
                  src={filePreviewObjectUrl}
                  alt={filePreviewTitle}
                  className="max-w-full h-auto mx-auto"
                />
              </div>
            )}
            {filePreviewType === "pdf" && filePreviewObjectUrl && (
              <iframe
                src={filePreviewObjectUrl}
                title={filePreviewTitle}
                className="w-full h-full"
              />
            )}
            {filePreviewType === "text" && (
              <pre className="h-full overflow-auto p-4 text-sm whitespace-pre-wrap break-words">
                {filePreviewText}
              </pre>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {chatbot && appearance && (
        <ChatbotWidgetPreview
          key={`widget-${chatbotId}`}
          primaryColor={watchedAppearanceValues.primary_color}
          headerText={watchedAppearanceValues.header_text}
          avatarUrl={watchedAppearanceValues.avatar_url}
          position={watchedAppearanceValues.position}
          offsetX={watchedAppearanceValues.offset_x}
          offsetY={watchedAppearanceValues.offset_y}
          welcomeMessage={watchedAppearanceValues.welcome_message}
          initialSuggestions={watchedAppearanceValues.initial_suggestions}
          showBranding={watchedAppearanceValues.show_branding}
          contained={false}
          initialOpen={false}
          readOnly={false}
          chatbotId={chatbotId}
        />
      )}
    </div>
  );
}
