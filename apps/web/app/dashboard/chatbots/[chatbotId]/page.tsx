"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { toast } from "@/lib/notify-toast";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  ChevronRight,
  ChevronDown,
  Settings,
  Database,
  Palette,
  Code,
  BarChart3,
  Check,
  FileText,
  Download,
} from "lucide-react";
import { PageLoader } from "@/components/ui/loading";
import { SkeletonChatbotPage } from "@/components/ui/skeleton";
import { ErrorBoundary } from "@/components/ui/error-boundary";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiRequestWithAuth } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { useHeaderContent } from "@/contexts/HeaderContext";
import { ChatbotWidgetPreview } from "@/components/chatbot/WidgetPreview";
import { AnimatePresence, motion } from "framer-motion";

import {
  OverviewTab,
  KnowledgeTab,
  AppearanceTab,
  InstallTab,
  SettingsTab,
} from "./tabs";

import {
  type ChatbotDetail,
  type KnowledgeSource,
  type QAPair,
  type ChatbotStats,
  type RecentActivity,
  type RecentActivityListResponse,
  type AppearanceData,
  type AppearanceFormData,
  appearanceSchema,
} from "./types";

// ─── Component ─────────────────────────────────────────────
export default function ChatbotDetailPage() {
  const params = useParams();
  const router = useRouter();
  const chatbotId = params.chatbotId as string;
  const { isAdmin, isOrgOwner } = useAuth();
  const { setContent } = useHeaderContent();

  // ── Chatbot Switcher ──
  const [allChatbots, setAllChatbots] = useState<
    { id: string; name: string; status: string }[]
  >([]);
  const [isSwitcherOpen, setIsSwitcherOpen] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const switcherRef = useRef<HTMLDivElement>(null);
  const prevChatbotIdRef = useRef<string>(chatbotId);

  // ── Core State ──
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

  // ── Knowledge Base State ──
  const [isAddKnowledgeOpen, setIsAddKnowledgeOpen] = useState(false);
  const [knowledgeType, setKnowledgeType] = useState<"url" | "file" | "qa">(
    "url",
  );
  const [newUrl, setNewUrl] = useState("");
  const [isCrawling, setIsCrawling] = useState(false);
  const [uploadFiles, setUploadFiles] = useState<FileList | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  // ── Selection State ──
  const [selectedPages, setSelectedPages] = useState<string[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [selectedQAs, setSelectedQAs] = useState<string[]>([]);
  const [isBulkDeleting, setIsBulkDeleting] = useState(false);
  const [deletingFileId, setDeletingFileId] = useState<string | null>(null);

  // ── File Preview State ──
  const [previewFile, setPreviewFile] = useState<{
    filename: string;
    content: string;
    type: string;
    url?: string;
    mode?: "text" | "iframe" | "download";
  } | null>(null);
  const [loadingPreviewFileId, setLoadingPreviewFileId] = useState<
    string | null
  >(null);

  // ── QA State ──
  const [newQA, setNewQA] = useState({ question: "", answer: "" });
  const [editingQA, setEditingQA] = useState<QAPair | null>(null);
  const [isQAOpen, setIsQAOpen] = useState(false);
  const [qaXlsx, setQaXlsx] = useState<File | null>(null);

  // ── Appearance State ──
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

  // ── Settings State ──
  const [settingsSubTab, setSettingsSubTab] = useState("general");
  const [isSavingSettings, setIsSavingSettings] = useState(false);
  const [settingsSuccess, setSettingsSuccess] = useState<string | null>(null);
  const [settingsError, setSettingsError] = useState<string | null>(null);

  // ── Crawl Scheduling State ──
  const [isCrawlScheduleOpen, setIsCrawlScheduleOpen] = useState(false);
  const [selectedCrawlSource, setSelectedCrawlSource] = useState<any | null>(
    null,
  );

  // ── Polling State ──
  const [isPolling, setIsPolling] = useState(false);
  const [pollingStartTime, setPollingStartTime] = useState<number | null>(null);
  const MAX_POLLING_DURATION = 5 * 60 * 1000;
  const [manuallyStartedCrawl, setManuallyStartedCrawl] = useState(false);
  const [pollingTimedOut, setPollingTimedOut] = useState(false);

  // ── Crawl Notification Refs ──
  const previousKnowledgeSourcesRef = useRef<KnowledgeSource[]>([]);
  const lastFetchTimeRef = useRef<number>(0);
  const autoDeletedSourcesRef = useRef<Set<string>>(new Set());
  const eventSourceRef = useRef<EventSource | null>(null);

  // ── Persistent Crawl Notifications ──
  const [crawlNotifications, setCrawlNotifications] = useState<
    {
      id: string;
      notification_type: string;
      message: string;
      severity: "info" | "warning" | "error";
      is_read: boolean;
      created_at: string;
    }[]
  >([]);

  // ── Appearance Form ──
  const form = useForm<AppearanceFormData>({
    resolver: zodResolver(appearanceSchema),
    mode: "onChange",
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
      personality_tone: "friendly",
      response_length: "balanced",
      temperature: 0.7,
      custom_instructions: null,
      languages: ["en"],
    },
  });

  const { watch, setValue, control, formState: { isDirty: isAppearanceDirty } } = form;

  const watchedPrimaryColor = useWatch({ control, name: "primary_color", defaultValue: "#3B82F6" });
  const watchedHeaderText = useWatch({ control, name: "header_text", defaultValue: "Chat Support" });
  const watchedWelcomeMessage = useWatch({ control, name: "welcome_message", defaultValue: null });
  const watchedAvatarUrl = useWatch({ control, name: "avatar_url", defaultValue: null });
  const watchedPosition = useWatch({ control, name: "position", defaultValue: "bottom-right" });
  const watchedOffsetX = useWatch({ control, name: "offset_x", defaultValue: 0 });
  const watchedOffsetY = useWatch({ control, name: "offset_y", defaultValue: 0 });
  const watchedInitialSuggestions = useWatch({ control, name: "initial_suggestions", defaultValue: [] });
  const watchedShowBranding = useWatch({ control, name: "show_branding", defaultValue: true });
  const watchedPersonalityTone = useWatch({ control, name: "personality_tone", defaultValue: "friendly" });
  const watchedResponseLength = useWatch({ control, name: "response_length", defaultValue: "balanced" });
  const watchedTemperature = useWatch({ control, name: "temperature", defaultValue: 0.7 });
  const watchedLanguages = useWatch({ control, name: "languages", defaultValue: ["en"] });

  const watchedAppearanceValues = {
    primary_color: watchedPrimaryColor ?? "#3B82F6",
    header_text: watchedHeaderText ?? "Chat Support",
    welcome_message: watchedWelcomeMessage ?? null,
    avatar_url: watchedAvatarUrl ?? null,
    position: watchedPosition ?? "bottom-right",
    offset_x: watchedOffsetX ?? 0,
    offset_y: watchedOffsetY ?? 0,
    initial_suggestions: watchedInitialSuggestions ?? [],
    show_branding: watchedShowBranding !== undefined ? watchedShowBranding : true,
    personality_tone: watchedPersonalityTone ?? "friendly",
    response_length: watchedResponseLength ?? "balanced",
    temperature: watchedTemperature ?? 0.7,
    language: watchedLanguages?.[0] ?? "en",
  };

  const formData = watch();

  // ── Unsaved changes guard (browser beforeunload) ──
  useEffect(() => {
    if (!isAppearanceDirty) return;
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      // Modern browsers show a generic message; returnValue is required for legacy
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [isAppearanceDirty]);

  // ── Tab-switch guard when appearance form is dirty ──
  const [pendingTab, setPendingTab] = useState<string | null>(null);
  const [showUnsavedDialog, setShowUnsavedDialog] = useState(false);

  const handleTabChange = useCallback(
    (value: string) => {
      // If leaving appearance tab with unsaved changes, confirm first
      if (activeTab === "appearance" && isAppearanceDirty && value !== "appearance") {
        setPendingTab(value);
        setShowUnsavedDialog(true);
        return;
      }
      setActiveTab(value);
      if (value === "knowledge" && !hasLoadedKnowledge) fetchKnowledgeSources();
      if (value === "appearance" && !hasLoadedAppearance) fetchAppearance();
      if (value === "overview") {
        fetchChatbotStats();
        fetchRecentActivity(recentActivityPage);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [activeTab, isAppearanceDirty, hasLoadedKnowledge, hasLoadedAppearance, recentActivityPage],
  );

  // ═══════════════════════════════════════════════════════════
  // Effects
  // ═══════════════════════════════════════════════════════════

  // Smooth data swap when switching chatbots
  useEffect(() => {
    if (prevChatbotIdRef.current !== chatbotId) {
      prevChatbotIdRef.current = chatbotId;
      setIsTransitioning(true);
      setHasLoadedKnowledge(false);
      setHasLoadedAppearance(false);
      setCrawlNotifications([]);
    }
  }, [chatbotId]);

  // Main initializer
  useEffect(() => {
    const isSwitching = isTransitioning;
    const initializePage = async () => {
      await fetchChatbotDetails(!isSwitching);
      setIsTransitioning(false);
      fetchChatbotStats();
      fetchRecentActivity(1);
      fetchAppearance();
      setTimeout(() => {
        if (!hasLoadedKnowledge) fetchKnowledgeSources();
      }, 1000);
    };
    initializePage();
  }, [chatbotId]);

  // Fetch all chatbots for the switcher (once)
  useEffect(() => {
    const fetchAllChatbots = async () => {
      try {
        const token = getAccessToken();
        if (!token) return;
        const res = await apiRequestWithAuth<{
          chatbots: { id: string; name: string; status: string }[];
        }>("/api/v1/chatbots", token, { method: "GET" });
        setAllChatbots(res.chatbots || []);
      } catch {
        // non-fatal
      }
    };
    fetchAllChatbots();
  }, []);

  // Close switcher on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        switcherRef.current &&
        !switcherRef.current.contains(e.target as Node)
      ) {
        setIsSwitcherOpen(false);
      }
    };
    if (isSwitcherOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () =>
        document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isSwitcherOpen]);

  // Fetch persistent crawl notifications
  useEffect(() => {
    fetchCrawlNotifications();
  }, [chatbotId]);

  // Polling controller — detect status changes, show toasts, auto-delete failed empty sources
  useEffect(() => {
    const hasCrawlingSources = knowledgeSources.some((s) => {
      const status = s.status?.toLowerCase();
      return status === "crawling" || status === "pending";
    });

    if (previousKnowledgeSourcesRef.current.length > 0) {
      knowledgeSources.forEach((current) => {
        const previous = previousKnowledgeSourcesRef.current.find(
          (p) => p.id === current.id,
        );
        if (previous && previous.status !== current.status) {
          const getSourceDisplayName = (source: KnowledgeSource) => {
            if (source.source_type === "crawled_url") return source.source_url;
            if (
              source.source_type === "uploaded_file" &&
              source.files &&
              source.files.length > 0
            )
              return source.files[0].filename;
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
            if (
              current.error_message &&
              current.error_message.toLowerCase().includes("quota")
            ) {
              toast.info(current.error_message);
            } else {
              toast.success(`${verb} completed for ${displayName}`);
            }
            fetchCrawlNotifications();
          } else if (current.status === "failed") {
            toast.error(
              current.error_message || `${verb} failed for ${displayName}`,
            );
            fetchCrawlNotifications();
          }
          fetchChatbotStats();
        }
      });

      // Auto-cleanup failed empty crawl sources
      knowledgeSources.forEach((s) => {
        if (
          s.source_type === "crawled_url" &&
          s.status === "failed" &&
          (s.pages_found === 0 || !s.pages || s.pages.length === 0) &&
          !autoDeletedSourcesRef.current.has(s.id)
        ) {
          autoDeletedSourcesRef.current.add(s.id);
          toast.error(s.error_message || `Crawl failed for ${s.source_url}`);
          handleDeleteSource(s.id, undefined, true);
        }
      });
    }
    previousKnowledgeSourcesRef.current = knowledgeSources;

    if (!hasCrawlingSources && isPolling) {
      setIsPolling(false);
      setPollingStartTime(null);
      setManuallyStartedCrawl(false);
      fetchKnowledgeSources(false);
      fetchChatbotStats();
      return;
    }

    if (!isPolling && hasCrawlingSources && !pollingTimedOut) {
      setIsPolling(true);
      setPollingStartTime(Date.now());
    }
  }, [knowledgeSources, manuallyStartedCrawl, isPolling, pollingTimedOut]);

  // Adaptive polling timer
  useEffect(() => {
    if (!isPolling) return;

    let timeoutId: ReturnType<typeof setTimeout>;
    let stopped = false;

    const getPollingInterval = () => {
      if (!pollingStartTime) return 2000;
      const elapsed = Date.now() - pollingStartTime;
      if (elapsed < 15000) return 2000;
      if (elapsed < 60000) return 5000;
      return 10000;
    };

    const poll = async () => {
      if (stopped) return;
      await fetchKnowledgeSources(false);
      await fetchChatbotStats();

      if (
        pollingStartTime &&
        Date.now() - pollingStartTime > MAX_POLLING_DURATION
      ) {
        setIsPolling(false);
        setPollingStartTime(null);
        setPollingTimedOut(true);
        toast.info(
          "Your content is still being processed. Auto-refresh has been paused — click the refresh button to check for updates.",
        );
        return;
      }

      if (!stopped) {
        timeoutId = setTimeout(poll, getPollingInterval());
      }
    };

    timeoutId = setTimeout(poll, getPollingInterval());

    return () => {
      stopped = true;
      clearTimeout(timeoutId);
    };
  }, [isPolling, pollingStartTime]);

  // SSE subscription for processing phase
  useEffect(() => {
    const hasProcessingSources = knowledgeSources.some(
      (s) => s.status?.toLowerCase() === "processing",
    );
    const hasCrawlingOrPending = knowledgeSources.some((s) => {
      const st = s.status?.toLowerCase();
      return st === "crawling" || st === "pending";
    });

    if (
      hasProcessingSources &&
      !hasCrawlingOrPending &&
      !eventSourceRef.current
    ) {
      const token = getAccessToken();
      if (!token) return;

      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const url = `${API_URL}/api/v1/chatbots/${chatbotId}/knowledge-sources/status-stream?token=${encodeURIComponent(token)}`;

      const es = new EventSource(url);
      let doneHandled = false;

      es.onmessage = (e) => {
        try {
          const sources = JSON.parse(e.data);
          if (Array.isArray(sources)) {
            setKnowledgeSources((prev) =>
              prev.map((p) => {
                const updated = sources.find((s: any) => s.id === p.id);
                if (!updated) return p;
                return {
                  ...p,
                  status: updated.status,
                  pages_found: updated.pages_found ?? p.pages_found,
                  error_message: updated.error_message ?? p.error_message,
                  updated_at: updated.updated_at ?? p.updated_at,
                  crawl_progress: updated.crawl_progress ?? p.crawl_progress,
                };
              }),
            );
          }
        } catch {
          // ignore parse errors
        }
      };

      es.addEventListener("done", () => {
        doneHandled = true;
        es.close();
        eventSourceRef.current = null;
        fetchKnowledgeSources(false);
        fetchChatbotStats();
      });

      es.addEventListener("timeout", () => {
        doneHandled = true;
        es.close();
        eventSourceRef.current = null;
        fetchKnowledgeSources(false);
        fetchChatbotStats();
      });

      es.onerror = () => {
        if (!doneHandled) {
          console.error(
            "Processing SSE closed unexpectedly — fallback fetch",
          );
          es.close();
          eventSourceRef.current = null;
          fetchKnowledgeSources(false);
          fetchChatbotStats();
        }
      };

      eventSourceRef.current = es;
    }

    if (!hasProcessingSources && eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, [knowledgeSources, chatbotId]);

  // ═══════════════════════════════════════════════════════════
  // Handlers & Fetchers
  // ═══════════════════════════════════════════════════════════

  const handleSwitchChatbot = (targetId: string) => {
    if (targetId === chatbotId) {
      setIsSwitcherOpen(false);
      return;
    }
    setIsSwitcherOpen(false);
    setIsTransitioning(true);
    setTimeout(() => {
      router.push(`/dashboard/chatbots/${targetId}`);
    }, 200);
  };

  const fetchCrawlNotifications = async () => {
    try {
      const token = getAccessToken();
      if (!token) return;
      const res = await apiRequestWithAuth<
        {
          id: string;
          notification_type: string;
          message: string;
          severity: "info" | "warning" | "error";
          is_read: boolean;
          created_at: string;
        }[]
      >(`/chatbots/${chatbotId}/notifications?unread_only=true`, { token });
      setCrawlNotifications(res || []);
    } catch {
      // non-fatal
    }
  };

  const dismissNotification = async (notificationId: string) => {
    try {
      const token = getAccessToken();
      if (!token) return;
      await apiRequestWithAuth(
        `/chatbots/${chatbotId}/notifications/mark-read`,
        {
          token,
          method: "POST",
          body: { notification_ids: [notificationId] },
        },
      );
      setCrawlNotifications((prev) =>
        prev.filter((n) => n.id !== notificationId),
      );
    } catch {
      // non-fatal
    }
  };

  const dismissAllNotifications = async () => {
    try {
      const token = getAccessToken();
      if (!token) return;
      await apiRequestWithAuth(
        `/chatbots/${chatbotId}/notifications/mark-read`,
        {
          token,
          method: "POST",
          body: { mark_all: true },
        },
      );
      setCrawlNotifications([]);
    } catch {
      // non-fatal
    }
  };

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
        { method: "GET", cache: "no-store" as RequestCache },
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
        { method: "GET", cache: "no-store" as RequestCache },
      );
      setStats(response);
      fetchRecentActivity(recentActivityPage, false);
    } catch (err) {
      console.error("Failed to fetch stats:", err);
    }
  };

  const fetchChatbotDetails = async (showLoading = true) => {
    try {
      if (showLoading) setIsLoading(true);
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
      if (err.message?.includes("404") || err.message?.includes("403")) {
        setTimeout(() => router.push("/dashboard/chatbots"), 2000);
      }
    } finally {
      if (showLoading) setIsLoading(false);
    }
  };

  const fetchKnowledgeSources = async (
    showLoading = true,
  ): Promise<KnowledgeSource[] | null> => {
    try {
      if (showLoading) setIsLoadingKnowledge(true);
      const token = getAccessToken();
      if (!token) return null;

      const timestamp = new Date().getTime();
      const requestTimestamp = timestamp;
      lastFetchTimeRef.current = Math.max(
        lastFetchTimeRef.current,
        requestTimestamp,
      );

      const response = await apiRequestWithAuth<KnowledgeSource[]>(
        `/api/v1/chatbots/${chatbotId}/knowledge-sources?t=${timestamp}`,
        token,
        { method: "GET", cache: "no-store" as RequestCache },
      );

      if (requestTimestamp < lastFetchTimeRef.current) return null;

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

      const cacheBust = `_t=${Date.now()}`;
      const response = await apiRequestWithAuth<AppearanceData>(
        `/api/v1/chatbots/${chatbotId}/appearance?${cacheBust}`,
        token,
        { method: "GET" },
      );

      setAppearance(response);
      setHasLoadedAppearance(true);

      Object.keys(response).forEach((key) => {
        if (
          key !== "id" &&
          key !== "chatbot_id" &&
          key !== "created_at" &&
          key !== "updated_at" &&
          key !== "welcome_message_translations"
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
      if (!token) return;

      const newSource = await apiRequestWithAuth<KnowledgeSource>(
        `/api/v1/chatbots/${chatbotId}/crawl`,
        token,
        { method: "POST", body: JSON.stringify({ base_url: newUrl }) },
      );

      setKnowledgeSources((prev) => {
        const exists = prev.some((s) => s.id === newSource.id);
        if (exists) return prev.map((s) => (s.id === newSource.id ? newSource : s));
        return [...prev, newSource];
      });

      setNewUrl("");
      setIsAddKnowledgeOpen(false);
      await fetchKnowledgeSources();
      await fetchChatbotStats();

      setPollingTimedOut(false);
      setManuallyStartedCrawl(true);
      setIsPolling(true);
      setPollingStartTime(Date.now());
    } catch (err: any) {
      toast.error(err.message || "Failed to start crawl");
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

      for (let i = 0; i < uploadFiles.length; i++) {
        const file = uploadFiles[i];
        const fd = new FormData();
        fd.append("file", file);

        const response = await fetch(
          `${API_URL}/api/v1/chatbots/${chatbotId}/upload`,
          {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
            body: fd,
          },
        );

        if (!response.ok) {
          const errData = await response.json();
          throw new Error(
            `Failed to upload ${file.name}: ${errData.detail || "Unknown error"}`,
          );
        }
      }

      setUploadFiles(null);
      setIsAddKnowledgeOpen(false);
      await fetchKnowledgeSources(false);
      await fetchChatbotStats();

      setPollingTimedOut(false);
      setManuallyStartedCrawl(true);
      setIsPolling(true);
      setPollingStartTime(Date.now());
    } catch (err: any) {
      toast.error(err.message || "Failed to upload files");
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
      fetchChatbotStats();
      toast.success(
        editingQA ? "QA pair updated" : "QA pair added successfully",
      );
    } catch (err: any) {
      toast.error(err.message || "Failed to save QA pair");
    }
  };

  const handleQAXlsxUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!qaXlsx) return;
    try {
      const token = getAccessToken();
      if (!token) return;

      const fd = new FormData();
      fd.append("file", qaXlsx);

      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${API_URL}/api/v1/chatbots/${chatbotId}/qa/upload`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: fd,
        },
      );

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Upload failed");
      }

      setQaXlsx(null);
      await fetchKnowledgeSources();
      await fetchChatbotStats();

      setPollingTimedOut(false);
      setManuallyStartedCrawl(true);
      setIsPolling(true);
      setPollingStartTime(Date.now());
    } catch (err: any) {
      toast.error(err.message || "Failed to upload XLSX");
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
      fetchChatbotStats();
    } catch (err: any) {
      toast.error(err.message || "Failed to delete QA");
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
      setDeletingFileId(sourceId);

      await apiRequestWithAuth(
        `/api/v1/chatbots/knowledge-sources/${sourceId}`,
        token,
        { method: "DELETE" },
      );

      await fetchKnowledgeSources();
      fetchChatbotStats();
    } catch (err: any) {
      toast.error(err.message || "Failed to delete source");
    } finally {
      setDeletingFileId(null);
    }
  };

  const handleStopCrawl = async (sourceId: string) => {
    try {
      const token = getAccessToken();
      if (!token) return;

      await apiRequestWithAuth(
        `/api/v1/chatbots/knowledge-sources/${sourceId}/stop`,
        token,
        { method: "POST" },
      );

      setKnowledgeSources((prev) =>
        prev.map((s) =>
          s.id === sourceId ? { ...s, status: "processing" as const } : s,
        ),
      );

      toast.success("Crawl stopped. Processing crawled pages...");
      setTimeout(() => fetchKnowledgeSources(false), 2000);
    } catch (err: any) {
      toast.error(err.message || "Failed to stop crawl");
    }
  };

  const handlePreviewFile = async (file: any) => {
    if (!file?.files?.[0]) return;
    const uploadedFile = file.files[0];
    const filename = uploadedFile.filename;
    const fileExtension = filename.split(".").pop()?.toLowerCase();

    try {
      const token = getAccessToken();
      if (!token) return;

      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const fileUrl = `${API_URL}/api/v1/chatbots/files/${uploadedFile.id}/preview?token=${token}`;

      const textFormats = [
        "txt", "md", "csv", "json", "xml", "html", "htm", "yaml", "yml",
        "log", "ini", "cfg", "conf", "env", "sh", "bat", "py", "js", "ts",
        "css", "sql",
      ];
      if (fileExtension && textFormats.includes(fileExtension)) {
        setLoadingPreviewFileId(uploadedFile.id);
        try {
          const response = await fetch(fileUrl);
          if (!response.ok) throw new Error("Failed to fetch file");
          const text = await response.text();
          setPreviewFile({ filename, content: text, type: fileExtension, mode: "text" });
        } finally {
          setLoadingPreviewFileId(null);
        }
        return;
      }

      if (fileExtension === "pdf") {
        window.open(fileUrl, "_blank");
        return;
      }

      const officeFormats = ["docx", "doc", "pptx", "ppt", "xlsx", "xls"];
      if (fileExtension && officeFormats.includes(fileExtension)) {
        setPreviewFile({
          filename,
          content: `This ${fileExtension.toUpperCase()} file cannot be previewed in the browser. Click below to download and view it in the appropriate application.`,
          type: fileExtension,
          url: fileUrl,
          mode: "download",
        });
        return;
      }

      const imageFormats = ["png", "jpg", "jpeg", "gif", "webp", "svg", "bmp"];
      if (fileExtension && imageFormats.includes(fileExtension)) {
        setPreviewFile({
          filename, content: "", type: fileExtension, url: fileUrl, mode: "iframe",
        });
        return;
      }

      setPreviewFile({
        filename,
        content: `This file type (.${fileExtension}) cannot be previewed in the browser.`,
        type: fileExtension || "unknown",
        url: fileUrl,
        mode: "download",
      });
    } catch (err: any) {
      toast.error(err.message || "Failed to open file preview");
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

      const updatedSources = await fetchKnowledgeSources();
      if (updatedSources) {
        const emptyCrawlSources = updatedSources
          .filter((s) => s.source_type === "crawled_url")
          .filter((source) => !source.pages || source.pages.length === 0);

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
          await fetchKnowledgeSources();
        }
      }
      fetchChatbotStats();
    } catch (err: any) {
      toast.error(err.message || "Failed to delete page");
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

      if (type === "pages") setSelectedPages([]);
      else if (type === "files") setSelectedFiles([]);
      else if (type === "qa") setSelectedQAs([]);

      const updatedSources = await fetchKnowledgeSources();

      if (type === "pages" && updatedSources) {
        const emptyCrawlSources = updatedSources
          .filter((s) => s.source_type === "crawled_url")
          .filter((source) => !source.pages || source.pages.length === 0);

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
          await fetchKnowledgeSources();
        }
      }
      fetchChatbotStats();
    } catch (err: any) {
      toast.error(err.message || "Bulk delete failed");
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
      toast.error(err.message || "Failed to delete chatbot");
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
          headers: { Authorization: `Bearer ${token}` },
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
      toast.error(err.message || "Failed to export activity");
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
    for (let page = start; page <= end; page += 1) items.push(page);
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

      const fd = new FormData(e.currentTarget);
      const name = fd.get("name") as string;
      const status = fd.get("status") as "draft" | "active" | "paused";

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

      const updated = await apiRequestWithAuth<AppearanceData>(
        `/api/v1/chatbots/${chatbotId}/appearance`,
        token,
        { method: "PATCH", body: JSON.stringify(data) },
      );

      if (updated && updated.id) setAppearance(updated);

      setAppearanceSuccessMessage("Appearance settings saved successfully!");
      setTimeout(() => setAppearanceSuccessMessage(null), 3000);

      await fetchAppearance();

      // Reset form dirty state so isDirty becomes false after successful save
      form.reset(form.getValues());
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

  // ── Set header bar content ──
  useEffect(() => {
    if (chatbot) {
      const roleLabel =
        chatbot.permission_level.charAt(0).toUpperCase() +
        chatbot.permission_level.slice(1);
      setContent({
        title: (
          <>
            <Link
              href="/dashboard/chatbots"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Chatbots
            </Link>
            <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="inline-flex items-center gap-1 bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 to-teal-600 hover:opacity-80 transition-opacity focus:outline-none">
                  {chatbot.name}
                  <ChevronDown className="h-3 w-3 text-emerald-600 opacity-60" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-56 max-h-64 overflow-y-auto">
                {allChatbots.map((bot) => (
                  <DropdownMenuItem
                    key={bot.id}
                    onClick={() => {
                      if (bot.id !== chatbotId) router.push(`/dashboard/chatbots/${bot.id}`);
                    }}
                    className={cn(
                      "cursor-pointer",
                      bot.id === chatbotId && "bg-accent font-medium"
                    )}
                  >
                    <span className="truncate">{bot.name}</span>
                    {bot.id === chatbotId && (
                      <Check className="h-3.5 w-3.5 ml-auto shrink-0 text-emerald-600" />
                    )}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
            <Badge
              variant={
                chatbot.status === "active"
                  ? "active"
                  : chatbot.status === "paused"
                    ? "paused"
                    : "draft"
              }
              className="text-[10px] ml-1"
            >
              {chatbot.status.charAt(0).toUpperCase() + chatbot.status.slice(1)}
            </Badge>
            <Badge variant="outline" className="text-[10px]">
              {roleLabel}
            </Badge>
          </>
        ),
      });
    } else {
      setContent({ title: "Chatbots" });
    }
    return () => setContent(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chatbot, allChatbots, chatbotId, router, setContent]);

  // ═══════════════════════════════════════════════════════════
  // Early Returns
  // ═══════════════════════════════════════════════════════════

  if (isLoading && !chatbot) {
    return <SkeletonChatbotPage />;
  }

  if (error || !chatbot) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-foreground mb-2">
            {error?.includes("404") ? "Chatbot Not Found" : "Access Denied"}
          </h2>
          <p className="text-muted-foreground mb-4">
            {error || "You don't have permission to view this chatbot."}
          </p>
          <Button onClick={() => router.push("/dashboard/chatbots")}>
            Back to Chatbots
          </Button>
        </div>
      </div>
    );
  }

  // ── Derived Values ──
  const canEdit = ["owner", "admin", "editor"].includes(
    chatbot.permission_level,
  );

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

  const qaPairs: QAPair[] = knowledgeSources
    .filter((s) => s.source_type === "qa_pair" && s.qa_pairs)
    .flatMap((s) => s.qa_pairs || []);

  const crawlSources = knowledgeSources.filter(
    (s) => s.source_type === "crawled_url",
  );
  const fileSources = knowledgeSources.filter(
    (s) => s.source_type === "uploaded_file",
  );
  const allCrawledPages = crawlSources.flatMap((s) =>
    (s.pages || []).map((p) => ({
      ...p,
      status: s.status,
      source_url: s.source_url,
    })),
  );
  const crawlSourcesWithPages = crawlSources;

  // ═══════════════════════════════════════════════════════════
  // Render
  // ═══════════════════════════════════════════════════════════

  return (
    <>
    <div
      className={cn(
        "space-y-6 transition-all duration-300 ease-in-out",
        isTransitioning
          ? "opacity-0 translate-y-1"
          : "opacity-100 translate-y-0",
      )}
    >

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={handleTabChange}
        className="w-full"
      >
        {(() => {
          const visibleTabs = [
            true,
            canViewKnowledge,
            canViewAppearance,
            true,
            canViewSettings,
          ].filter(Boolean).length;

          return (
            <TabsList
              className="grid w-full lg:w-auto"
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
                  <span className="hidden sm:inline">
                    Appearance & Behavior
                  </span>
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

        {/* ── Overview Tab ── */}
        <TabsContent value="overview" className="space-y-6">
          <ErrorBoundary compact>
          <OverviewTab
            chatbotId={chatbotId}
            stats={stats}
            recentActivity={recentActivity}
            recentActivityPage={recentActivityPage}
            recentActivityTotal={recentActivityTotal}
            recentActivityTotalPages={recentActivityTotalPages}
            isLoadingRecentActivity={isLoadingRecentActivity}
            isExportingRecentActivity={isExportingRecentActivity}
            navigationTarget={navigationTarget}
            setNavigationTarget={setNavigationTarget}
            setActiveTab={setActiveTab}
            fetchRecentActivity={fetchRecentActivity}
            handleExportRecentActivity={handleExportRecentActivity}
            getActivityPaginationItems={getActivityPaginationItems}
          />
          </ErrorBoundary>
        </TabsContent>

        {/* ── Knowledge Tab ── */}
        <TabsContent value="knowledge" className="space-y-6">
          <ErrorBoundary compact>
          <KnowledgeTab
            chatbotId={chatbotId}
            canEdit={canEdit}
            knowledgeSources={knowledgeSources}
            isLoadingKnowledge={isLoadingKnowledge}
            isAddKnowledgeOpen={isAddKnowledgeOpen}
            setIsAddKnowledgeOpen={setIsAddKnowledgeOpen}
            knowledgeType={knowledgeType}
            setKnowledgeType={setKnowledgeType}
            newUrl={newUrl}
            setNewUrl={setNewUrl}
            isCrawling={isCrawling}
            handleCrawl={handleCrawl}
            uploadFiles={uploadFiles}
            setUploadFiles={setUploadFiles}
            isUploading={isUploading}
            handleFileUpload={handleFileUpload}
            newQA={newQA}
            setNewQA={setNewQA}
            editingQA={editingQA}
            setEditingQA={setEditingQA}
            handleQASubmit={handleQASubmit}
            qaXlsx={qaXlsx}
            setQaXlsx={setQaXlsx}
            handleQAXlsxUpload={handleQAXlsxUpload}
            handleDeleteQA={handleDeleteQA}
            handleDeleteSource={handleDeleteSource}
            handleStopCrawl={handleStopCrawl}
            handlePreviewFile={handlePreviewFile}
            selectedPages={selectedPages}
            setSelectedPages={setSelectedPages}
            selectedFiles={selectedFiles}
            setSelectedFiles={setSelectedFiles}
            selectedQAs={selectedQAs}
            setSelectedQAs={setSelectedQAs}
            isBulkDeleting={isBulkDeleting}
            handleBulkDelete={handleBulkDelete}
            deletingFileId={deletingFileId}
            loadingPreviewFileId={loadingPreviewFileId}
            knowledgeTab={knowledgeTab}
            setKnowledgeTab={setKnowledgeTab}
            crawlSources={crawlSources}
            fileSources={fileSources}
            qaPairs={qaPairs}
            allCrawledPages={allCrawledPages}
            crawlSourcesWithPages={crawlSourcesWithPages}
            crawlNotifications={crawlNotifications}
            dismissNotification={dismissNotification}
            dismissAllNotifications={dismissAllNotifications}
            isCrawlScheduleOpen={isCrawlScheduleOpen}
            setIsCrawlScheduleOpen={setIsCrawlScheduleOpen}
            selectedCrawlSource={selectedCrawlSource}
            setSelectedCrawlSource={setSelectedCrawlSource}
            onSyncTriggered={() => {
              fetchKnowledgeSources(false);
              fetchChatbotStats();
            }}
          />
          </ErrorBoundary>
        </TabsContent>

        {/* ── Appearance Tab ── */}
        <TabsContent value="appearance" className="space-y-6">
          <ErrorBoundary compact>
          <AppearanceTab
            chatbotId={chatbotId}
            appearanceError={appearanceError}
            appearanceSuccessMessage={appearanceSuccessMessage}
            isSavingAppearance={isSavingAppearance}
            newSuggestion={newSuggestion}
            setNewSuggestion={setNewSuggestion}
            handleAddSuggestion={handleAddSuggestion}
            handleRemoveSuggestion={handleRemoveSuggestion}
            handleAppearanceSubmit={handleAppearanceSubmit}
            fetchAppearance={fetchAppearance}
            setAppearanceSuccessMessage={setAppearanceSuccessMessage}
            setAppearanceError={setAppearanceError}
            avatarInputRef={avatarInputRef}
            form={form}
            watchedPrimaryColor={watchedPrimaryColor ?? "#3B82F6"}
            watchedLanguages={(watchedLanguages || ["en"]) as string[]}
          />
          </ErrorBoundary>
        </TabsContent>

        {/* ── Install Tab ── */}
        <TabsContent value="install" className="space-y-6">
          <ErrorBoundary compact>
          <InstallTab
            chatbotId={chatbotId}
            embedCopyStatus={embedCopyStatus}
            setEmbedCopyStatus={setEmbedCopyStatus}
          />
          </ErrorBoundary>
        </TabsContent>

        {/* ── Settings Tab ── */}
        <TabsContent value="settings" className="space-y-6">
          <ErrorBoundary compact>
          <SettingsTab
            chatbot={chatbot}
            chatbotId={chatbotId}
            canEdit={canEdit}
            settingsSubTab={settingsSubTab}
            setSettingsSubTab={setSettingsSubTab}
            isSavingSettings={isSavingSettings}
            settingsSuccess={settingsSuccess}
            settingsError={settingsError}
            handleSettingsSubmit={handleSettingsSubmit}
            handleDeleteChatbot={handleDeleteChatbot}
          />
          </ErrorBoundary>
        </TabsContent>
      </Tabs>

      {/* File Preview Dialog */}
      <Dialog open={!!previewFile} onOpenChange={() => setPreviewFile(null)}>
        <DialogContent className="sm:max-w-4xl max-h-[80vh] flex flex-col">
          {previewFile && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-primary" />
                  {previewFile.filename}
                  <Badge variant="secondary" className="text-xs">
                    {previewFile.type.toUpperCase()}
                  </Badge>
                </DialogTitle>
              </DialogHeader>

              <div className="flex-1 overflow-auto">
                {previewFile.mode === "text" && (
                  <pre className="text-sm whitespace-pre-wrap font-mono bg-muted p-4 rounded-lg border">
                    {previewFile.content}
                  </pre>
                )}
                {previewFile.mode === "iframe" &&
                  previewFile.url &&
                  (["png", "jpg", "jpeg", "gif", "webp", "svg", "bmp"].includes(
                    previewFile.type,
                  ) ? (
                    <div className="flex items-center justify-center">
                      <img
                        src={previewFile.url}
                        alt={previewFile.filename}
                        className="max-w-full max-h-[60vh] object-contain rounded"
                      />
                    </div>
                  ) : (
                    <iframe
                      src={previewFile.url}
                      className="w-full h-[60vh] rounded border"
                      title={previewFile.filename}
                    />
                  ))}
                {previewFile.mode === "download" && (
                  <div className="flex flex-col items-center justify-center gap-4 py-12">
                    <FileText className="h-16 w-16 text-muted-foreground" />
                    <p className="text-muted-foreground text-center">
                      {previewFile.content}
                    </p>
                    {previewFile.url && (
                      <a
                        href={previewFile.url}
                        download={previewFile.filename}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                      >
                        <Download className="h-4 w-4" />
                        Download File
                      </a>
                    )}
                  </div>
                )}
              </div>

              <div className="pt-4 border-t bg-muted/50 flex justify-end gap-2 -mx-6 -mb-6 px-6 py-4 rounded-b-lg">
                {previewFile.mode === "text" && (
                  <Button
                    variant="outline"
                    onClick={() => {
                      navigator.clipboard.writeText(previewFile.content);
                      toast.success("Content copied to clipboard!");
                    }}
                  >
                    Copy to Clipboard
                  </Button>
                )}
                <Button onClick={() => setPreviewFile(null)}>Close</Button>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Unsaved Changes Confirmation Dialog */}
      <Dialog open={showUnsavedDialog} onOpenChange={setShowUnsavedDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Unsaved Changes</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            You have unsaved changes in the Appearance tab. Are you sure you want to leave? Your changes will be lost.
          </p>
          <div className="flex justify-end gap-2 pt-4">
            <Button
              variant="outline"
              onClick={() => {
                setShowUnsavedDialog(false);
                setPendingTab(null);
              }}
            >
              Stay
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                setShowUnsavedDialog(false);
                form.reset();
                if (pendingTab) {
                  setActiveTab(pendingTab);
                  if (pendingTab === "knowledge" && !hasLoadedKnowledge) fetchKnowledgeSources();
                  if (pendingTab === "overview") {
                    fetchChatbotStats();
                    fetchRecentActivity(recentActivityPage);
                  }
                  setPendingTab(null);
                }
              }}
            >
              Discard Changes
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>

    {/* Widget Preview — rendered outside transition container so position:fixed works */}
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
        language={watchedAppearanceValues.language as "en" | "hi" | "gu"}
        languages={(watchedLanguages || ["en"]) as ("en" | "hi" | "gu")[]}
        welcomeMessageTranslations={
          appearance?.welcome_message_translations || null
        }
        contained={false}
        initialOpen={false}
        readOnly={false}
        chatbotId={chatbotId}
      />
    )}
    </>
  );
}
