'use client'

// Type declarations to suppress IDE errors (dependencies available in Docker)
declare const process: {
  env: {
    NEXT_PUBLIC_API_URL?: string
  }
}

import { ChatbotWidget, type ChatbotConfig } from '@chatbot/chatbot-widget'

interface WidgetPreviewProps {
  primaryColor: string
  headerText: string
  avatarUrl: string | null
  position: 'bottom-right' | 'bottom-left'
  offsetX?: number
  offsetY?: number
  welcomeMessage: string | null
  initialSuggestions: string[]
  showBranding: boolean
  embedded?: boolean
  initialOpen?: boolean
  readOnly?: boolean
  contained?: boolean
  chatbotId?: string
}

export function ChatbotWidgetPreview({
  primaryColor,
  headerText,
  avatarUrl,
  position,
  offsetX = 0,
  offsetY = 0,
  welcomeMessage,
  initialSuggestions,
  showBranding,
  embedded = false,
  initialOpen = false,
  readOnly = false,
  contained = false,
  chatbotId,
}: WidgetPreviewProps) {
  const apiUrl = process?.env?.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const config: ChatbotConfig = {
    chatbotId: chatbotId || 'preview',
    apiUrl: apiUrl,
    isPreview: true,
    primaryColor: primaryColor,
    headerText: headerText,
    avatarUrl: avatarUrl,
    position: position,
    offsetX: offsetX,
    offsetY: offsetY,
    welcomeMessage: welcomeMessage,
    initialSuggestions: initialSuggestions,
    showBranding: showBranding,
  }

  // Container styles for contained mode
  const containerStyle: React.CSSProperties = contained
    ? {
        width: '100%',
        height: '100%',
        position: 'relative',
        minHeight: '600px',
      }
    : {
        position: 'relative',
      }

  return (
    <div style={containerStyle}>
      <ChatbotWidget config={config} />
    </div>
  )
}
