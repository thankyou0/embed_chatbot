import { render } from 'preact'
import { App } from './app'
import './widget.css'

interface ChatbotConfig {
  chatbotId: string;
  apiUrl?: string; // Optional API URL override
  position?: 'bottom-right' | 'bottom-left';
  offsetX?: number;
  offsetY?: number;
  primaryColor?: string;
  headerText?: string;
  welcomeMessage?: string;
  initialSuggestions?: string[];
  avatarUrl?: string | null;
  showBranding?: boolean;
}

interface WidgetConfigResponse {
  primary_color: string;
  header_text: string;
  avatar_url: string | null;
  position: 'bottom-right' | 'bottom-left';
  offset_x: number;
  offset_y: number;
  welcome_message: string | null;
  initial_suggestions: string[];
  show_branding: boolean;
}

declare global {
  interface Window {
    ChatbotWidget: {
      init: (config: ChatbotConfig) => void;
    };
  }
}

const API_BASE_URL = import.meta.env.VITE_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchWidgetConfig(chatbotId: string, apiUrl?: string): Promise<WidgetConfigResponse | null> {
  const baseUrl = apiUrl || API_BASE_URL;
  try {
    const response = await fetch(`${baseUrl}/api/v1/chat/${chatbotId}/config`);
    if (response.ok) {
      return await response.json();
    }
    console.warn('Failed to fetch widget config, using defaults');
    return null;
  } catch (error) {
    console.warn('Error fetching widget config, using defaults:', error);
    return null;
  }
}

async function initChatbotWidget(config: ChatbotConfig) {
  let container = document.getElementById('chatbot-widget-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'chatbot-widget-container';
    document.body.appendChild(container);
  }

  // If only chatbotId is provided, fetch config from API
  // Otherwise, use provided config (for backwards compatibility)
  const hasExplicitConfig = config.position !== undefined || 
                               config.offsetX !== undefined || 
                               config.offsetY !== undefined ||
                               config.primaryColor !== undefined ||
                               config.headerText !== undefined;

  if (!hasExplicitConfig) {
    // Fetch config from API
    const fetchedConfig = await fetchWidgetConfig(config.chatbotId, config.apiUrl);
    if (fetchedConfig) {
      // Merge fetched config with provided config (provided config takes precedence)
      const mergedConfig: ChatbotConfig = {
        ...config,
        position: fetchedConfig.position,
        offsetX: fetchedConfig.offset_x,
        offsetY: fetchedConfig.offset_y,
        primaryColor: fetchedConfig.primary_color,
        headerText: fetchedConfig.header_text,
        welcomeMessage: fetchedConfig.welcome_message || undefined,
        initialSuggestions: fetchedConfig.initial_suggestions,
        avatarUrl: fetchedConfig.avatar_url,
        showBranding: fetchedConfig.show_branding,
      };
      render(<App {...mergedConfig} />, container);
      return;
    }
  }

  // Use provided config or defaults
  render(<App {...config} />, container);
}

// Expose the init function globally
window.ChatbotWidget = {
  init: initChatbotWidget,
};

