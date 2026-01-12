import { render } from 'preact'
import { App } from './app'
import widgetStyles from './widget.css?inline'

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
    // Add cache-busting query param to always get fresh config
    const cacheBuster = `?t=${Date.now()}`;
    const response = await fetch(`${baseUrl}/api/v1/chat/${chatbotId}/config${cacheBuster}`);
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

function injectStyles() {
  const styleId = 'chatbot-widget-styles';
  if (!document.getElementById(styleId)) {
    const style = document.createElement('style');
    style.id = styleId;
    // In build mode with ?inline, it might be a string or { default: string }
    const cssText = typeof widgetStyles === 'string' ? widgetStyles : (widgetStyles as any).default;
    if (cssText) {
      style.textContent = cssText;
      document.head.appendChild(style);
      console.log('Chatbot widget styles injected');
    } else {
      console.error('Failed to get chatbot widget styles');
    }
  }
}

async function initChatbotWidget(config: ChatbotConfig) {
  // Inject styles immediately
  injectStyles();

  let container = document.getElementById('chatbot-widget-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'chatbot-widget-container';
    document.body.appendChild(container);
  }

  // Always fetch config from API to get latest appearance settings
  // This ensures changes in dashboard are reflected immediately on refresh
  const fetchedConfig = await fetchWidgetConfig(config.chatbotId, config.apiUrl);
  
  if (fetchedConfig) {
    // Merge fetched config with provided config (provided config takes precedence for overrides)
    const mergedConfig: ChatbotConfig = {
      ...config,
      position: config.position ?? fetchedConfig.position,
      offsetX: config.offsetX ?? fetchedConfig.offset_x,
      offsetY: config.offsetY ?? fetchedConfig.offset_y,
      primaryColor: config.primaryColor ?? fetchedConfig.primary_color,
      headerText: config.headerText ?? fetchedConfig.header_text,
      welcomeMessage: config.welcomeMessage ?? (fetchedConfig.welcome_message || undefined),
      initialSuggestions: config.initialSuggestions ?? fetchedConfig.initial_suggestions,
      avatarUrl: config.avatarUrl ?? fetchedConfig.avatar_url,
      showBranding: config.showBranding !== undefined ? config.showBranding : fetchedConfig.show_branding,
    };
    render(<App {...mergedConfig} />, container);
    return;
  }

  // Fallback to provided config or defaults if API fetch fails
  render(<App {...config} />, container);
}

// Expose the init function globally
window.ChatbotWidget = {
  init: initChatbotWidget,
};

