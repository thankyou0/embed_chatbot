import { render } from 'preact'
import { ChatbotWidget, type ChatbotConfig } from '@chatbot/chatbot-widget'


// Styles are imported via the shared component's CSS

// Store widget root for updates
const widgetRoots = new Map<HTMLElement, any>();

export function initChatbot(config: Partial<ChatbotConfig> = {}, containerElement?: HTMLElement) {
  // Validate required chatbotId
  if (!config.chatbotId) {
    console.error('ChatbotWidget: chatbotId is required');
    return;
  }

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
    render(<ChatbotWidget config={config as ChatbotConfig} />, container, existingRoot);
  } else {
    // Create new widget
    const root = render(<ChatbotWidget config={config as ChatbotConfig} />, container);
    widgetRoots.set(container, root);
  }
}

// Export for manual initialization
if (typeof window !== 'undefined') {
  ;(window as any).ChatbotWidget = { 
    init: (config: Partial<ChatbotConfig> = {}, containerElement?: HTMLElement) => {
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

