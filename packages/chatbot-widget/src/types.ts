export interface ProductInfo {
  name: string;
  url: string;
  price?: string | null;
  currency?: string | null;
  image?: string | null;
  brand?: string | null;
  rating?: number | null;
  review_count?: number | null;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  suggestions?: string[];
  imagePreview?: string;
  isTyping?: boolean;
  isWaitingForContent?: boolean; // True while waiting for first content chunk (shows skeleton)
  isWelcome?: boolean; // True for the initial welcome message (enables typewriter animation)
  timestamp: Date;
  products?: ProductInfo[]; // Product carousel data
}

export interface ChatbotConfig {
  chatbotId: string;
  apiUrl?: string;
  isPreview?: boolean;
  isContained?: boolean; // Whether widget should be positioned absolutely within container
  primaryColor?: string;
  headerText?: string;
  avatarUrl?: string | null;
  position?: "bottom-right" | "bottom-left";
  offsetX?: number;
  offsetY?: number;
  welcomeMessage?: string | null;
  initialSuggestions?: string[];
  showBranding?: boolean;
  // Personality customization
  personalityTone?: "formal" | "casual" | "friendly" | "professional";
  responseLength?: "concise" | "balanced" | "detailed";
  temperature?: number;
  customInstructions?: string | null;
  // Language settings
  language?: "en" | "hi" | "gu";
  languages?: ("en" | "hi" | "gu")[];
  // Server-provided welcome message translations keyed by lang code
  welcomeMessageTranslations?: Record<string, string> | null;
  theme?: {
    primaryColor?: string;
    position?: "bottom-right" | "bottom-left";
  };
}

export interface ChatbotWidgetProps {
  config: ChatbotConfig;
}
