'use client'

import { useEffect } from 'react'
import { useParams } from 'next/navigation'

export default function EmbedPage() {
  const params = useParams()
  const chatbotId = params.chatbotId as string

  useEffect(() => {
    // Load widget script from port 3001 (or your widget URL)
    const script = document.createElement('script')
    script.src = `${process.env.NEXT_PUBLIC_WIDGET_URL || 'http://localhost:3001'}/widget.umd.js`
    script.async = true
    script.onload = () => {
      if (window.ChatbotWidget) {
        window.ChatbotWidget.init({
          chatbotId: chatbotId,
          apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        })
      }
    }
    document.head.appendChild(script)

    return () => {
      const existingScript = document.querySelector('script[src*="widget.umd.js"]')
      if (existingScript) {
        existingScript.remove()
      }
    }
  }, [chatbotId])

  return (
    <div style={{ 
      width: '100%', 
      height: '100vh', 
      margin: 0, 
      padding: 0,
      overflow: 'hidden',
      position: 'relative',
      background: 'transparent'
    }}>
      {/* Widget will be injected here by the script */}
    </div>
  )
}

declare global {
  interface Window {
    ChatbotWidget?: {
      init: (config: any, containerElement?: HTMLElement) => void
      destroy?: (containerId?: string) => void
    }
  }
}