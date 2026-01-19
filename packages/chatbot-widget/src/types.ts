export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  suggestions?: string[];
  imagePreview?: string;
  isTyping?: boolean;
  timestamp: Date;
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
  theme?: {
    primaryColor?: string;
    position?: "bottom-right" | "bottom-left";
  };
}

export interface ChatbotWidgetProps {
  config: ChatbotConfig;
}
