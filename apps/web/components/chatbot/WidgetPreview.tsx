'use client'

// Type declarations to suppress IDE errors (dependencies available in Docker)
declare const process: {
  env: {
    NEXT_PUBLIC_API_URL?: string
    NEXT_PUBLIC_WIDGET_URL?: string
  }
}

declare global {
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any
    }
  }
}

// @ts-ignore - Dependencies available in Docker
import { useEffect, useRef, useState } from 'react'

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
  const containerRef = useRef<HTMLDivElement>(null)
  const scriptRef = useRef<HTMLScriptElement | null>(null)
  const previewContainerRef = useRef<HTMLDivElement | null>(null)
  const widgetInstanceRef = useRef<any>(null)
  const [isLoaded, setIsLoaded] = useState(false)
  const widgetUrl = process?.env?.NEXT_PUBLIC_WIDGET_URL || 'http://localhost:3001'
  const apiUrl = process?.env?.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  // Initialize widget once
  useEffect(() => {
    if (!containerRef.current) return

    // Load widget script
    const loadWidget = () => {
      // Check if script is already loaded
      // @ts-ignore - ChatbotWidget available after script loads
      if ((window as any).ChatbotWidget) {
        initializeWidget()
        return
      }

      // Create and load script
      const script = document.createElement('script')
      script.src = `${widgetUrl}/widget.umd.js`
      script.async = true
      script.onload = () => {
        setIsLoaded(true)
        // Small delay to ensure ChatbotWidget is available
        setTimeout(initializeWidget, 100)
      }
      script.onerror = () => {
        console.error('Failed to load widget script')
      }
      
      scriptRef.current = script
      document.head.appendChild(script)
    }

    // Initialize widget with current props (only once)
    const initializeWidget = () => {
      // @ts-ignore - ChatbotWidget available after script loads
      const ChatbotWidget = (window as any).ChatbotWidget
      if (!ChatbotWidget || !containerRef.current || previewContainerRef.current) return

      // Create a unique container for this preview instance
      const previewContainer = document.createElement('div')
      const containerId = `chatbot-widget-preview-${Date.now()}`
      previewContainer.id = containerId
      previewContainer.style.position = contained ? 'relative' : 'fixed'
      previewContainer.style.bottom = contained ? 'auto' : `${16 + offsetY}px`
      previewContainer.style[position === 'bottom-right' ? 'right' : 'left'] = contained ? 'auto' : `${16 + offsetX}px`
      previewContainer.style.zIndex = '9999'
      
      if (contained) {
        previewContainer.style.width = '100%'
        previewContainer.style.height = '100%'
      }

      containerRef.current.appendChild(previewContainer)
      previewContainerRef.current = previewContainer

      // Initialize widget with config and pass the container
      const widgetConfig = {
        chatbotId: chatbotId || 'preview',
        apiUrl: apiUrl,
        theme: {
          primaryColor: primaryColor,
          position: position,
        },
        primaryColor: primaryColor,
        headerText: headerText,
        avatarUrl: avatarUrl,
        welcomeMessage: welcomeMessage,
        initialSuggestions: initialSuggestions,
        showBranding: showBranding,
        position: position,
        offsetX: offsetX,
        offsetY: offsetY,
        isPreview: true,
      }

      try {
        // Pass the container element directly to initChatbot
        ChatbotWidget.init(widgetConfig, previewContainer)
        widgetInstanceRef.current = { config: widgetConfig, container: previewContainer }
      } catch (error) {
        console.error('Failed to initialize widget:', error)
      }
    }

    // Load widget script
    loadWidget()

    // Cleanup on unmount only
    return () => {
      if (previewContainerRef.current && previewContainerRef.current.parentNode) {
        previewContainerRef.current.parentNode.removeChild(previewContainerRef.current)
        previewContainerRef.current = null
      }
      widgetInstanceRef.current = null
    }
  }, [contained, chatbotId, widgetUrl, apiUrl]) // Only re-init if these change

  // Update widget config when appearance props change (without re-initializing)
  useEffect(() => {
    // Only update if widget is already initialized
    if (!previewContainerRef.current || !isLoaded) return

    // @ts-ignore - ChatbotWidget available after script loads
    const ChatbotWidget = (window as any).ChatbotWidget
    if (!ChatbotWidget) return

    // Update container position if needed
    if (previewContainerRef.current) {
      previewContainerRef.current.style.bottom = contained ? 'auto' : `${16 + offsetY}px`
      previewContainerRef.current.style[position === 'bottom-right' ? 'right' : 'left'] = contained ? 'auto' : `${16 + offsetX}px`
    }

    // Update widget config - init will update existing widget without destroying state
    const widgetConfig = {
      chatbotId: chatbotId || 'preview',
      apiUrl: apiUrl,
      theme: {
        primaryColor: primaryColor,
        position: position,
      },
      primaryColor: primaryColor,
      headerText: headerText,
      avatarUrl: avatarUrl,
      welcomeMessage: welcomeMessage,
      initialSuggestions: initialSuggestions,
      showBranding: showBranding,
      position: position,
      offsetX: offsetX,
      offsetY: offsetY,
      isPreview: true,
    }

    try {
      // Call init with existing container - Preact will update the component with new props
      ChatbotWidget.init(widgetConfig, previewContainerRef.current)
      widgetInstanceRef.current = { config: widgetConfig, container: previewContainerRef.current }
    } catch (error) {
      console.error('Failed to update widget config:', error)
    }
  }, [
    primaryColor,
    headerText,
    avatarUrl,
    position,
    offsetX,
    offsetY,
    welcomeMessage,
    initialSuggestions,
    showBranding,
    chatbotId,
    apiUrl,
    contained,
    isLoaded, // Only update after widget is loaded
  ])

  // Container styles for contained mode
  const containerStyle: any = contained
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
    <div ref={containerRef} style={containerStyle}>
      {!isLoaded && (
        <div className="flex items-center justify-center h-full min-h-[600px] text-gray-400">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-400 mx-auto mb-2"></div>
            <p>Loading widget preview...</p>
          </div>
        </div>
      )}
    </div>
  )
}
