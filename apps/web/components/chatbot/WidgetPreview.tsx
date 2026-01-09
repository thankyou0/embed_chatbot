'use client'

import { useState, useEffect, useRef, useMemo } from 'react'
import { MessageCircle, X, Send, Minimize2, Image as ImageIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

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
  // Normalize primary color - ensure it's always a valid hex color
  // Use useMemo to ensure it updates when primaryColor prop changes
  const normalizedPrimaryColor = useMemo(() => {
    if (primaryColor && /^#[0-9A-Fa-f]{6}$/.test(primaryColor)) {
      return primaryColor
    }
    return '#2563eb'
  }, [primaryColor])
  const [isOpen, setIsOpen] = useState(embedded || initialOpen) 
  const [isTyping, setIsTyping] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)
  
  // Force open if embedded
  if (embedded && !isOpen) {
    setIsOpen(true)
  }

  const initialMessage = { text: welcomeMessage || 'Hi! How can I help you today?', isUser: false }
  const [messages, setMessages] = useState<Array<{ text: string; isUser: boolean; suggestions?: string[]; isTyping?: boolean; imagePreview?: string }>>([initialMessage])
  const [inputValue, setInputValue] = useState('')
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight
    }
  }, [messages, isTyping])

  // Function to type out message character by character
  const typeMessage = (fullText: string, suggestions?: string[]) => {
    let currentIndex = 0
    const typingMessage = { text: '', isUser: false, isTyping: true, suggestions }
    
    // Add empty typing message first
    setMessages((prev) => [...prev, typingMessage])
    
    const typingInterval = setInterval(() => {
      currentIndex++
      const partialText = fullText.slice(0, currentIndex)
      
      setMessages((prev) => {
        const newMessages = [...prev]
        const lastMessage = newMessages[newMessages.length - 1]
        if (lastMessage && lastMessage.isTyping) {
          lastMessage.text = partialText
          if (currentIndex >= fullText.length) {
            lastMessage.isTyping = false
            clearInterval(typingInterval)
          }
        }
        return newMessages
      })
      
      if (currentIndex >= fullText.length) {
        clearInterval(typingInterval)
      }
    }, 20) // 20ms per character for smooth typing effect
  }

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const removeImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // Handle Close (X) - Reset messages and close
  const handleClose = () => {
    setIsOpen(false)
    // Small delay to reset messages after the window starts closing
    setTimeout(() => {
      setMessages([initialMessage])
      setSessionId(null)
      removeImage()
    }, 300)
  }

  // Handle Minimize - Just close window, keep messages
  const handleMinimize = () => {
    setIsOpen(false)
  }

  const handleSendMessage = async (text?: string) => {
    if (readOnly) return
    const messageText = text || inputValue
    if (!messageText.trim() && !selectedImage) return

    const userMessage = { 
      text: messageText || '(Image uploaded)', 
      isUser: true,
      imagePreview: imagePreview || undefined
    }
    setMessages((prev) => [...prev, userMessage])
    if (!text) setInputValue('')
    
    setIsTyping(true)

    // If we have a chatbotId, try to get a real response
    if (chatbotId) {
      try {
        // Build FormData for multipart/form-data
        const formData = new FormData()
        formData.append('message', messageText || 'What is this?')
        if (sessionId) {
          formData.append('session_id', sessionId)
        }
        if (selectedImage) {
          formData.append('image', selectedImage)
        }
        formData.append('is_preview', 'true')

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/chat/${chatbotId}/message`, {
          method: 'POST',
          body: formData, // No Content-Type header - browser sets it automatically with boundary
        })

        if (response.ok) {
          const data = await response.json()
          setSessionId(data.session_id)
          setIsTyping(false)
          removeImage()
          // Use typing effect to show response
          typeMessage(data.message, data.suggestions)
          return
        } else {
          const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
          console.error('API error:', errorData)
          setIsTyping(false)
          removeImage()
          typeMessage(`Sorry, I encountered an error: ${errorData.detail || 'Please try again.'}`)
          return
        }
      } catch (error) {
        console.error('Error fetching chat response:', error)
        setIsTyping(false)
        removeImage()
        typeMessage('Sorry, I encountered an error. Please try again.')
        return
      }
    } else {
      // Fallback to mock response
      setTimeout(() => {
        setIsTyping(false)
        removeImage()
        typeMessage('Thanks for your message! This is a preview.')
      }, 1000)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    if (readOnly) return
    handleSendMessage(suggestion)
  }

  const positionClasses = embedded 
    ? 'relative flex justify-center items-center h-full w-full' 
    : `${contained ? 'absolute' : 'fixed'} z-50`

  const style: React.CSSProperties = embedded ? {} : {
    bottom: 16 + offsetY,
    [position === 'bottom-right' ? 'right' : 'left']: 16 + offsetX,
  }

  return (
    <div className={positionClasses} style={style}>
      {/* Chat Widget */}
      {isOpen ? (
        <div className={`bg-white rounded-lg shadow-2xl w-[350px] flex flex-col overflow-hidden border border-gray-200 ${embedded ? 'h-full' : 'h-[500px]'}`}>
          {/* Header */}
          <div
            className="p-3 text-white flex items-center justify-between"
            style={{ backgroundColor: normalizedPrimaryColor }}
          >
            <div className="flex items-center gap-2">
              {avatarUrl ? (
                <img
                  src={avatarUrl}
                  alt="Bot Avatar"
                  className="w-8 h-8 rounded-full border-2 border-white object-cover"
                />
              ) : (
                <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                  <MessageCircle className="h-5 w-5" />
                </div>
              )}
              <div>
                <h3 className="font-semibold text-sm leading-tight">{headerText}</h3>
                <div className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
                  <p className="text-[10px] opacity-90">Online</p>
                </div>
              </div>
            </div>
            {!embedded && (
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={handleMinimize}
                  title="Minimize"
                  className="hover:bg-white/20 p-1 rounded transition-colors"
                >
                  <Minimize2 className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  onClick={handleClose}
                  title="Close and Reset"
                  className="hover:bg-white/20 p-1 rounded transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}
          </div>

          {/* Messages */}
          <div 
            ref={messagesContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50"
          >
            {messages.map((message, index) => (
              <div key={index} className="space-y-2">
                <div
                  className={`flex items-end gap-2 ${message.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  {!message.isUser && (
                    <div className="flex-shrink-0 mb-1">
                      {avatarUrl ? (
                        <img
                          src={avatarUrl}
                          alt="Bot"
                          className="w-6 h-6 rounded-full object-cover border border-gray-200"
                        />
                      ) : (
                        <div className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center">
                          <MessageCircle className="h-3 w-3 text-gray-500" />
                        </div>
                      )}
                    </div>
                  )}
                  <div className={`max-w-[75%] ${message.isUser ? 'flex flex-col items-end gap-1' : ''}`}>
                    {message.imagePreview && (
                      <img 
                        src={message.imagePreview} 
                        alt="Uploaded" 
                        className="max-w-[150px] max-h-[100px] rounded-lg object-cover border border-gray-200"
                      />
                    )}
                    <div
                      className={`rounded-lg px-3 py-2 ${
                        message.isUser
                          ? 'text-white shadow-sm'
                          : 'bg-white text-gray-800 border border-gray-200 shadow-sm'
                      }`}
                      style={message.isUser ? { backgroundColor: normalizedPrimaryColor } : {}}
                    >
                      <p className="text-xs leading-relaxed">
                        {message.text}
                        {message.isTyping && <span className="inline-block w-1 h-3 bg-gray-400 ml-1 animate-pulse">|</span>}
                      </p>
                    </div>
                  </div>
                </div>
                
                {/* Suggestions for this message - only show when typing is complete */}
                {!message.isUser && !message.isTyping && message.suggestions && message.suggestions.length > 0 && (
                  <div className="flex flex-wrap gap-2 ml-8">
                    {message.suggestions.map((suggestion, sIndex) => (
                      <button
                        key={sIndex}
                        type="button"
                        disabled={readOnly || isTyping}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="text-left px-3 py-1 bg-white border border-gray-200 rounded-full hover:border-gray-400 transition-colors text-[10px] font-medium text-gray-600 shadow-sm disabled:opacity-50"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {isTyping && !messages.some(m => m.isTyping) && (
              <div className="flex items-center gap-2 ml-8">
                <div className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce"></span>
                  <span className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                  <span className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />

            {/* Initial Suggestions */}
            {messages.length === 1 && initialSuggestions.length > 0 && (
              <div className="space-y-2 ml-8">
                <p className="text-[10px] text-gray-400 font-medium uppercase tracking-wider">Suggested</p>
                <div className="flex flex-wrap gap-2">
                  {initialSuggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      type="button"
                      disabled={readOnly || isTyping}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="text-left px-3 py-1.5 bg-white border border-gray-200 rounded-full hover:border-gray-400 transition-colors text-[10px] font-medium text-gray-600 shadow-sm disabled:opacity-50"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-3 bg-white border-t border-gray-100">
            {/* Image Preview */}
            {imagePreview && (
              <div className="mb-2 flex items-center gap-2 p-2 bg-gray-50 rounded-lg border border-gray-200">
                <img 
                  src={imagePreview} 
                  alt="Selected" 
                  className="w-12 h-12 rounded object-cover"
                />
                <span className="text-xs text-gray-600 flex-1">Image selected</span>
                <button
                  type="button"
                  onClick={removeImage}
                  className="text-gray-400 hover:text-gray-600 p-1"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}
            
            <div className="flex gap-2">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="hidden"
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={() => fileInputRef.current?.click()}
                disabled={readOnly || isTyping}
                className="h-9 w-9 shrink-0"
              >
                <ImageIcon className="h-4 w-4" />
              </Button>
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !readOnly && !isTyping) {
                    e.preventDefault()
                    handleSendMessage()
                  }
                }}
                disabled={readOnly || isTyping}
                placeholder={readOnly ? "Testing disabled in site preview" : "Type your message..."}
                className="flex-1 h-9 text-xs"
              />
              <Button
                type="button"
                disabled={readOnly || isTyping || (!inputValue.trim() && !selectedImage)}
                onClick={() => handleSendMessage()}
                size="icon"
                style={{ backgroundColor: normalizedPrimaryColor }}
                className="text-white hover:opacity-90 h-9 w-9 shrink-0 shadow-sm disabled:opacity-50"
              >
                <Send className="h-3 w-3" />
              </Button>
            </div>
            
            {showBranding && (
              <p className="text-[10px] text-gray-400 text-center mt-2 font-medium">
                Powered by ChatBot
              </p>
            )}
          </div>
        </div>
      ) : (
        /* Minimized Button / Bubble */
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="w-14 h-14 rounded-full text-white shadow-xl flex items-center justify-center hover:scale-105 transition-all duration-300 active:scale-95"
          style={{ backgroundColor: normalizedPrimaryColor }}
        >
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt="Bot"
              className="w-full h-full rounded-full object-cover border-2 border-white"
            />
          ) : (
            <MessageCircle className="h-7 w-7" />
          )}
        </button>
      )}
    </div>
  )
}

