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

export function initChatbot(config: ChatbotConfig = {}) {
  // Inject styles immediately
  injectStyles();

  let container = document.getElementById('chatbot-widget-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'chatbot-widget-container';
    document.body.appendChild(container);
  }

  render(<ChatbotWidget config={config} />, container);
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
  ;(window as any).ChatbotWidget = { init: initChatbot }
}

