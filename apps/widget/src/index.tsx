import { render } from 'preact'
import { ChatbotWidget, type ChatbotConfig } from '@chatbot/chatbot-widget'

// Re-export ChatbotConfig for backward compatibility
export type { ChatbotConfig }

// Styles are imported via the shared component's CSS

// Store widget root for updates
const widgetRoots = new Map<HTMLElement, any>();

export function initChatbot(config: ChatbotConfig = {}, containerElement?: HTMLElement) {
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

