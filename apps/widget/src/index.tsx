import { render } from 'preact'
import { ChatbotWidget } from './components/ChatbotWidget'
import './styles.css'

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

export function initChatbot(config: ChatbotConfig = {}) {
  const container = document.createElement('div')
  container.id = 'chatbot-widget-container'
  document.body.appendChild(container)

  render(<ChatbotWidget config={config} />, container)
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

