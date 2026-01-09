import { useState, useRef, useEffect } from 'preact/hooks'
import type { ChatbotConfig } from '../index'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  suggestions?: string[]
  imagePreview?: string
  timestamp: Date
}

interface ChatbotWidgetProps {
  config: ChatbotConfig
}

// Image compression utility
async function compressImage(file: File, maxSizeKB: number = 1024): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        let { width, height } = img
        
        // Calculate new dimensions (max 1200px)
        const maxDim = 1200
        if (width > maxDim || height > maxDim) {
          if (width > height) {
            height = (height / width) * maxDim
            width = maxDim
          } else {
            width = (width / height) * maxDim
            height = maxDim
          }
        }
        
        canvas.width = width
        canvas.height = height
        
        const ctx = canvas.getContext('2d')!
        ctx.drawImage(img, 0, 0, width, height)
        
        // Try different quality levels
        let quality = 0.9
        const tryCompress = () => {
          canvas.toBlob(
            (blob) => {
              if (!blob) {
                reject(new Error('Failed to compress image'))
                return
              }
              if (blob.size / 1024 > maxSizeKB && quality > 0.1) {
                quality -= 0.1
                tryCompress()
              } else {
                resolve(blob)
              }
            },
            'image/jpeg',
            quality
          )
        }
        tryCompress()
      }
      img.onerror = () => reject(new Error('Failed to load image'))
      img.src = e.target?.result as string
    }
    reader.onerror = () => reject(new Error('Failed to read file'))
    reader.readAsDataURL(file)
  })
}

// Generate unique ID
function generateId(): string {
  return Math.random().toString(36).substring(2, 15)
}

export function ChatbotWidget({ config }: ChatbotWidgetProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [widgetConfig, setWidgetConfig] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const apiUrl = config.apiUrl || 'http://localhost:8000'
  const chatbotId = config.chatbotId

  const position = config.theme?.position || 'bottom-right'
  const positionClasses = {
    'bottom-right': 'ecw-bottom-right',
    'bottom-left': 'ecw-bottom-left',
  }

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Fetch widget config and show welcome message on first open
  useEffect(() => {
    if (isOpen && messages.length === 0 && chatbotId) {
      fetchWidgetConfig()
    }
  }, [isOpen, chatbotId])

  const fetchWidgetConfig = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/v1/chat/${chatbotId}/config`)
      if (response.ok) {
        const data = await response.json()
        setWidgetConfig(data)
        
        // Show welcome message
        const welcomeMsg = data.welcome_message || "Hello! How can I help you today?"
        const initialSuggestions = data.initial_suggestions || [
          "What products do you have?",
          "Tell me about your return policy"
        ]
        
        setMessages([{
          id: generateId(),
          role: 'assistant',
          content: welcomeMsg,
          suggestions: initialSuggestions.slice(0, 2),
          timestamp: new Date()
        }])
      }
    } catch (err) {
      console.error('Failed to fetch widget config:', err)
      // Show default welcome
      setMessages([{
        id: generateId(),
        role: 'assistant',
        content: "Hello! How can I help you today?",
        suggestions: ["What products do you have?", "Tell me about your return policy"],
        timestamp: new Date()
      }])
    }
  }

  const handleImageSelect = (e: Event) => {
    const input = e.target as HTMLInputElement
    const file = input.files?.[0]
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file')
        return
      }
      setSelectedImage(file)
      
      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
      setError(null)
    }
  }

  const removeImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const sendMessage = async (messageText?: string) => {
    const text = messageText || inputValue.trim()
    if (!text && !selectedImage) return
    if (!chatbotId) {
      setError('Chatbot not configured')
      return
    }

    // Add user message to UI
    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: text || '(Image uploaded)',
      imagePreview: imagePreview || undefined,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)
    setError(null)

    try {
      // Build form data
      const formData = new FormData()
      formData.append('message', text || 'What is this?')
      if (sessionId) {
        formData.append('session_id', sessionId)
      }
      
      // Compress and add image if selected
      if (selectedImage) {
        try {
          const compressedBlob = await compressImage(selectedImage, 1024)
          formData.append('image', compressedBlob, 'image.jpg')
        } catch (err) {
          console.error('Image compression failed:', err)
          formData.append('image', selectedImage)
        }
      }

      if (config.isPreview) {
        formData.append('is_preview', 'true')
      }

      const response = await fetch(`${apiUrl}/api/v1/chat/${chatbotId}/message`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()
      
      // Update session ID
      if (data.session_id) {
        setSessionId(data.session_id)
      }

      // Add assistant response
      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: data.message,
        suggestions: data.suggestions?.slice(0, 2) || [],
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMessage])

    } catch (err) {
      console.error('Failed to send message:', err)
      setError('Failed to send message. Please try again.')
      
      // Add error message
      setMessages(prev => [...prev, {
        id: generateId(),
        role: 'assistant',
        content: "I'm sorry, I encountered an error. Please try again.",
        timestamp: new Date()
      }])
    } finally {
      setIsLoading(false)
      removeImage()
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion)
  }

  const handleKeyPress = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const primaryColor = widgetConfig?.primary_color || config.theme?.primaryColor || '#6366f1'

  return (
    <div className={`ecw-widget ${positionClasses[position]}`}>
      {isOpen ? (
        <div className="ecw-window">
          {/* Header */}
          <div className="ecw-header" style={{ backgroundColor: primaryColor }}>
            <div className="ecw-header-info">
              {widgetConfig?.avatar_url && (
                <img src={widgetConfig.avatar_url} alt="" className="ecw-header-avatar" />
              )}
              <div>
                <h3 className="ecw-header-title">{widgetConfig?.display_name || 'Chat Support'}</h3>
                <span className="ecw-header-subtitle">We typically reply instantly</span>
              </div>
            </div>
            <button className="ecw-close-btn" onClick={() => setIsOpen(false)}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Messages */}
          <div className="ecw-messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`ecw-message ecw-message-${msg.role}`}>
                {msg.imagePreview && (
                  <div className="ecw-message-image">
                    <img src={msg.imagePreview} alt="Uploaded" />
                  </div>
                )}
                <div 
                  className="ecw-message-bubble"
                  style={msg.role === 'user' ? { backgroundColor: primaryColor } : {}}
                >
                  {msg.content}
                </div>
                {/* Suggestions */}
                {msg.role === 'assistant' && msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="ecw-suggestions">
                    {msg.suggestions.map((suggestion, idx) => (
                      <button
                        key={idx}
                        className="ecw-suggestion-btn"
                        onClick={() => handleSuggestionClick(suggestion)}
                        style={{ borderColor: primaryColor, color: primaryColor }}
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="ecw-message ecw-message-assistant">
                <div className="ecw-message-bubble ecw-loading">
                  <span className="ecw-dot"></span>
                  <span className="ecw-dot"></span>
                  <span className="ecw-dot"></span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Error display */}
          {error && (
            <div className="ecw-error">
              {error}
              <button onClick={() => setError(null)}>×</button>
            </div>
          )}

          {/* Image preview */}
          {imagePreview && (
            <div className="ecw-image-preview">
              <img src={imagePreview} alt="Selected" />
              <button className="ecw-image-remove" onClick={removeImage}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}

          {/* Input */}
          <div className="ecw-input-area">
            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              onChange={handleImageSelect}
              style={{ display: 'none' }}
            />
            <button 
              className="ecw-image-btn"
              onClick={() => fileInputRef.current?.click()}
              title="Upload image"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
            </button>
            <input
              type="text"
              className="ecw-text-input"
              placeholder="Type your message..."
              value={inputValue}
              onInput={(e) => setInputValue((e.target as HTMLInputElement).value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <button 
              className="ecw-send-btn"
              onClick={() => sendMessage()}
              disabled={isLoading || (!inputValue.trim() && !selectedImage)}
              style={{ backgroundColor: primaryColor }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
              </svg>
            </button>
          </div>
        </div>
      ) : (
        <button
          className="ecw-toggle"
          onClick={() => setIsOpen(true)}
          style={{ backgroundColor: primaryColor }}
        >
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </button>
      )}
    </div>
  )
}
