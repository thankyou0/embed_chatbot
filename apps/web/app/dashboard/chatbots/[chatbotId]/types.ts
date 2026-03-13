import * as z from "zod";

// ── Chatbot ────────────────────────────────────────────────
export interface ChatbotDetail {
  id: string;
  tenant_id: number;
  name: string;
  description: string | null;
  status: "draft" | "active" | "paused";
  created_by: number;
  created_at: string;
  updated_at: string;
  permission_level: "owner" | "admin" | "editor" | "viewer";
  can_manage_knowledge: boolean;
  can_manage_appearance: boolean;
  can_resolve_queries: boolean;
  can_view_analytics_billing: boolean;
}

// ── Knowledge Sources ──────────────────────────────────────
export interface KnowledgeSource {
  id: string;
  chatbot_id: string;
  source_type: "crawled_url" | "uploaded_file" | "qa_pair";
  source_url: string | null;
  status: "pending" | "processing" | "crawling" | "completed" | "failed";
  pages_found: number;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  crawl_progress?: {
    pages_crawled: number;
    urls_in_queue: number;
    crawl_speed: number;
    started_at: string;
    estimated_remaining_seconds: number | null;
  } | null;
  files?: {
    id: string;
    filename: string;
    file_size: number;
    mime_type: string;
  }[];
  qa_pairs?: QAPair[];
  pages?: CrawledPage[];
}

export interface CrawledPage {
  id: string;
  knowledge_source_id: string;
  url: string;
  title: string | null;
  is_product?: boolean;
  created_at: string;
}

export interface QAPair {
  id: string;
  question: string;
  answer: string;
  created_at: string;
  updated_at: string;
}

// ── Stats & Activity ───────────────────────────────────────
export interface RecentActivity {
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

export interface KnowledgeSourceBreakdown {
  total_crawled_urls: number;
  total_uploaded_files: number;
  total_qa_pairs: number;
  total_crawled_pages: number;
  total_file_size: number;
  total_qa_count: number;
}

export interface ChatbotStats {
  total_conversations: number;
  total_knowledge_sources: number;
  active_knowledge_sources: number;
  total_kb_size: number;
  knowledge_breakdown: KnowledgeSourceBreakdown;
}

export interface RecentActivityListResponse {
  activities: RecentActivity[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ── Notifications ──────────────────────────────────────────
export interface CrawlNotification {
  id: string;
  notification_type: string;
  message: string;
  severity: "info" | "warning" | "error";
  is_read: boolean;
  created_at: string;
}

// ── Appearance ─────────────────────────────────────────────
export const appearanceSchema = z.object({
  primary_color: z.string().regex(/^#[0-9A-Fa-f]{6}$/, "Invalid hex color"),
  header_text: z.string().min(1, "Header text is required").max(255),
  avatar_url: z.string().nullable(),
  position: z.enum(["bottom-right", "bottom-left"]),
  offset_x: z.number().int().optional().default(0),
  offset_y: z.number().int().optional().default(0),
  welcome_message: z.string().nullable(),
  initial_suggestions: z.array(z.string()),
  show_branding: z.boolean(),
  personality_tone: z
    .enum(["formal", "casual", "friendly", "professional"])
    .default("friendly"),
  response_length: z
    .enum(["concise", "balanced", "detailed"])
    .default("balanced"),
  temperature: z.number().min(0).max(1).default(0.7),
  custom_instructions: z.string().nullable().optional(),
  languages: z
    .array(z.enum(["en", "hi", "gu"]))
    .min(1, "At least one language must be selected")
    .default(["en"]),
});

export type AppearanceFormData = z.infer<typeof appearanceSchema>;

export interface AppearanceData extends AppearanceFormData {
  id: string;
  chatbot_id: string;
  welcome_message_translations?: Record<string, string> | null;
  created_at: string;
  updated_at: string;
}

// ── File preview ───────────────────────────────────────────
export interface FilePreviewData {
  filename: string;
  content: string;
  type: string;
  url?: string;
  mode?: "text" | "iframe" | "download";
}
