import { render } from 'preact'
import { ChatbotWidget } from './components/ChatbotWidget'
import { widgetStyles } from './styles'

export interface ChatbotConfig {
  apiUrl?: string
  chatbotId?: string
  tenantId?: string // Deprecated, use chatbotId
  isPreview?: boolean
  theme?: {
    primaryColor?: string
    position?: 'bottom-right' | 'bottom-left'
  }
  primaryColor?: string
  headerText?: string
  avatarUrl?: string | null
  welcomeMessage?: string | null
  initialSuggestions?: string[]
  showBranding?: boolean
  position?: 'bottom-right' | 'bottom-left'
  offsetX?: number
  offsetY?: number
}

function injectStyles() {
  const styleId = 'chatbot-widget-styles';
  if (!document.getElementById(styleId)) {
    const style = document.createElement('style');
    style.id = styleId;
    
    if (widgetStyles) {
      style.textContent = widgetStyles;
      document.head.appendChild(style);
      console.log('Chatbot widget styles injected');
    } else {
      console.warn('Failed to get chatbot widget styles');
    }
  }
}

// Store widget root for updates
const widgetRoots = new Map<HTMLElement, any>();

export function initChatbot(config: ChatbotConfig = {}, containerElement?: HTMLElement) {
  // Inject styles immediately
  injectStyles();

  let container = containerElement || document.getElementById('chatbot-widget-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'chatbot-widget-container';
    document.body.appendChild(container);
  }

  // Check if widget already exists in this container
  const existingRoot = widgetRoots.get(container);
  if (existingRoot) {
    // Update existing widget with new config (Preact will handle prop updates)
    render(<ChatbotWidget config={config} />, container, existingRoot);
  } else {
    // Create new widget
    const root = render(<ChatbotWidget config={config} />, container);
    widgetRoots.set(container, root);
  }
}

// Auto-initialize if script has data attributes
if (typeof window !== 'undefined') {
  const script = document.currentScript as HTMLScriptElement
  if (script?.dataset.autoInit === 'true') {
    const config: ChatbotConfig = {
      apiUrl: script.dataset.apiUrl,
      chatbotId: script.dataset.chatbotId || script.dataset.tenantId,
      isPreview: script.dataset.isPreview === 'true'
    }
    initChatbot(config)
  }
}

// Export for manual initialization
if (typeof window !== 'undefined') {
  ;(window as any).ChatbotWidget = { 
    init: (config: ChatbotConfig = {}, containerElement?: HTMLElement) => {
      initChatbot(config, containerElement);
    },
    // Helper to destroy widget instance
    destroy: (containerId?: string) => {
      const container = containerId 
        ? document.getElementById(containerId)
        : document.getElementById('chatbot-widget-container');
      if (container) {
        container.innerHTML = '';
        widgetRoots.delete(container);
      }
    }
  }
}

