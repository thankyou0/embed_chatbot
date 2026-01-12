import { useState, useEffect, useRef, useMemo } from 'preact/hooks'
import { MessageCircle, X, Send, Minimize2, Image as ImageIcon } from 'lucide-preact'

interface ChatbotConfig {
  chatbotId: string;
  apiUrl?: string;
  position?: 'bottom-right' | 'bottom-left';
  offsetX?: number;
  offsetY?: number;
  primaryColor?: string;
  headerText?: string;
  welcomeMessage?: string;
  initialSuggestions?: string[];
  avatarUrl?: string | null;
  showBranding?: boolean;
}

interface Message {
  text: string;
  isUser: boolean;
  suggestions?: string[];
  isTyping?: boolean;
  imagePreview?: string;
}

const DEFAULT_API_BASE_URL = import.meta.env.VITE_PUBLIC_API_URL || 'http://localhost:8000';

export function App(config: ChatbotConfig) {
  const API_BASE_URL = config.apiUrl || DEFAULT_API_BASE_URL;
  
  // Normalize primary color - ensure it's always a valid hex color
  const normalizedPrimaryColor = useMemo(() => {
    if (config.primaryColor && /^#[0-9A-Fa-f]{6}$/.test(config.primaryColor)) {
      return config.primaryColor;
    }
    return config.primaryColor || '#2563eb';
  }, [config.primaryColor]);

  const [isOpen, setIsOpen] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const isAtBottomRef = useRef(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const effectivePosition = config.position || 'bottom-right';
  const effectiveOffsetX = config.offsetX || 20;
  const effectiveOffsetY = config.offsetY || 20;
  const effectiveHeaderText = config.headerText || 'Chat with us';
  const effectiveWelcomeMessage = config.welcomeMessage || 'Hi! How can I help you today?';
  const effectiveInitialSuggestions = config.initialSuggestions || [];
  const effectiveAvatarUrl = config.avatarUrl || null;
  const effectiveShowBranding = config.showBranding !== false;

  const initialMessage = { text: effectiveWelcomeMessage, isUser: false };
  const [messages, setMessages] = useState<Message[]>([initialMessage]);
  const [inputValue, setInputValue] = useState('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  // Load session ID from sessionStorage on component mount
  useEffect(() => {
    const storedSessionId = sessionStorage.getItem(`chatbot_session_id_${config.chatbotId}`);
    if (storedSessionId) {
      setSessionId(storedSessionId);
    }
  }, [config.chatbotId]);

  // Smart scroll logic
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    // Logic:
    // 1. If user message, always scroll (and reset stickiness).
    const lastMessage = messages[messages.length - 1];
    if (lastMessage?.isUser) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      return;
    }

    // 2. If bot message, scroll ONLY if we were previously at the bottom (sticky)
    if (isAtBottomRef.current) {
      messagesEndRef.current?.scrollIntoView({ behavior: isTyping ? 'auto' : 'smooth' });
    }
  }, [messages, isTyping]);

  const handleScroll = () => {
    const container = messagesContainerRef.current;
    if (!container) return;
    
    const threshold = 20;
    const position = container.scrollTop + container.clientHeight;
    const height = container.scrollHeight;
    const isAtBottom = height - position <= threshold;
    
    isAtBottomRef.current = isAtBottom;
  };

  // Function to type out message character by character
  const typeMessage = (fullText: string, suggestions?: string[]) => {
    let currentIndex = 0;
    const typingMessage = { text: '', isUser: false, isTyping: true, suggestions };
    
    // Add empty typing message first
    setMessages((prev) => [...prev, typingMessage]);
    
    const typingInterval = setInterval(() => {
      currentIndex++;
      const partialText = fullText.slice(0, currentIndex);
      
      setMessages((prev) => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.isTyping) {
          lastMessage.text = partialText;
          if (currentIndex >= fullText.length) {
            lastMessage.isTyping = false;
            clearInterval(typingInterval);
          }
        }
        return newMessages;
      });
      
      if (currentIndex >= fullText.length) {
        clearInterval(typingInterval);
      }
    }, 20); // 20ms per character for smooth typing effect
  };

  const handleImageSelect = (e: Event) => {
    const target = e.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Handle Close (X) - Reset messages and close
  const handleClose = () => {
    setIsOpen(false);
    // Small delay to reset messages after the window starts closing
    setTimeout(() => {
      setMessages([initialMessage]);
      setSessionId(null);
      removeImage();
    }, 300);
  };

  // Handle Minimize - Just close window, keep messages
  const handleMinimize = () => {
    setIsOpen(false);
  };

  const handleSendMessage = async (text?: string) => {
    if (isTyping) return;
    const messageText = text || inputValue;
    if (!messageText.trim() && !selectedImage) return;

    const userMessage = { 
      text: messageText || '(Image uploaded)', 
      isUser: true,
      imagePreview: imagePreview || undefined
    };
    setMessages((prev) => [...prev, userMessage]);
    if (!text) setInputValue('');
    
    setIsTyping(true);

    try {
      // Build FormData for multipart/form-data
      const formData = new FormData();
      formData.append('message', messageText || 'What is this?');
      if (sessionId) {
        formData.append('session_id', sessionId);
      }
      if (selectedImage) {
        formData.append('image', selectedImage);
      }
      formData.append('is_preview', 'false');

      const response = await fetch(`${API_BASE_URL}/api/v1/chat/${config.chatbotId}/message`, {
        method: 'POST',
        body: formData, // No Content-Type header - browser sets it automatically with boundary
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        sessionStorage.setItem(`chatbot_session_id_${config.chatbotId}`, data.session_id);
        setIsTyping(false);
        removeImage();
        // Use typing effect to show response
        typeMessage(data.message, data.suggestions);
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('API error:', errorData);
        setIsTyping(false);
        removeImage();
        typeMessage(`Sorry, I encountered an error: ${errorData.detail || 'Please try again.'}`);
      }
    } catch (error) {
      console.error('Error fetching chat response:', error);
      setIsTyping(false);
      removeImage();
      typeMessage('Sorry, I encountered an error. Please try again.');
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (isTyping) return;
    handleSendMessage(suggestion);
  };

  const containerClasses = 'chatbot-widget-container';
  const containerStyle: Record<string, string> = {
    position: 'fixed',
    zIndex: '10000',
    [effectivePosition.includes('right') ? 'right' : 'left']: `${effectiveOffsetX}px`,
    [effectivePosition.includes('bottom') ? 'bottom' : 'top']: `${effectiveOffsetY}px`,
  };

  return (
    <div className={containerClasses} style={containerStyle}>
      {isOpen ? (
        <div className="chatbot-window">
          {/* Header */}
          <div
            className="chatbot-header"
            style={{ backgroundColor: normalizedPrimaryColor }}
          >
            <div className="chatbot-header-content">
              {effectiveAvatarUrl ? (
                <img
                  src={effectiveAvatarUrl}
                  alt="Bot Avatar"
                  className="chatbot-header-avatar"
                />
              ) : (
                <div className="chatbot-header-avatar-placeholder">
                  <MessageCircle size={20} />
                </div>
              )}
              <div>
                <h3 className="chatbot-header-title">{effectiveHeaderText}</h3>
                <div className="chatbot-online-indicator">
                  <span className="chatbot-online-dot"></span>
                  <p className="chatbot-online-text">Online</p>
                </div>
              </div>
            </div>
            <div className="chatbot-header-actions">
              <button
                type="button"
                onClick={handleMinimize}
                title="Minimize"
                className="chatbot-header-button"
              >
                <Minimize2 size={16} />
              </button>
              <button
                type="button"
                onClick={handleClose}
                title="Close and Reset"
                className="chatbot-header-button"
              >
                <X size={16} />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div 
            ref={messagesContainerRef}
            className="chatbot-messages"
            onScroll={handleScroll}
          >
            {messages.map((message, index) => (
              <div key={index} className="chatbot-message-wrapper">
                <div
                  className={`chatbot-message ${message.isUser ? 'user' : 'bot'}`}
                >
                  {!message.isUser && (
                    <div className="chatbot-message-avatar">
                      {effectiveAvatarUrl ? (
                        <img
                          src={effectiveAvatarUrl}
                          alt="Bot"
                          className="chatbot-avatar-small"
                        />
                      ) : (
                        <div className="chatbot-avatar-placeholder">
                          <MessageCircle size={12} />
                        </div>
                      )}
                    </div>
                  )}
                  <div className={`chatbot-message-content ${message.isUser ? 'user' : 'bot'}`}>
                    {message.imagePreview && (
                      <img 
                        src={message.imagePreview} 
                        alt="Uploaded" 
                        className="chatbot-message-image"
                      />
                    )}
                    <div
                      className="chatbot-message-bubble"
                      style={message.isUser ? { backgroundColor: normalizedPrimaryColor } : {}}
                    >
                      <p className="chatbot-message-text">
                        {message.text}
                        {message.isTyping && <span className="chatbot-typing-cursor">|</span>}
                      </p>
                    </div>
                  </div>
                </div>
                
                {/* Suggestions for this message - only show when typing is complete */}
                {!message.isUser && !message.isTyping && message.suggestions && message.suggestions.length > 0 && (
                  <div className="chatbot-suggestions-inline">
                    {message.suggestions.map((suggestion, sIndex) => (
                      <button
                        key={sIndex}
                        type="button"
                        disabled={isTyping}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="chatbot-suggestion-button"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {isTyping && !messages.some(m => m.isTyping) && (
              <div className="chatbot-typing-indicator">
                <div>
                  <span className="chatbot-typing-dot"></span>
                  <span className="chatbot-typing-dot" style={{ animationDelay: '0.2s' }}></span>
                  <span className="chatbot-typing-dot" style={{ animationDelay: '0.4s' }}></span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />

            {/* Initial Suggestions */}
            {messages.length === 1 && effectiveInitialSuggestions.length > 0 && (
              <div className="chatbot-initial-suggestions">
                <p className="chatbot-suggestions-label">Suggested</p>
                <div className="chatbot-suggestions-list">
                  {effectiveInitialSuggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      type="button"
                      disabled={isTyping}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="chatbot-suggestion-button"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="chatbot-input-area">
            {/* Image Preview */}
            {imagePreview && (
              <div className="chatbot-image-preview">
                <img 
                  src={imagePreview} 
                  alt="Selected" 
                  className="chatbot-image-preview-img"
                />
                <span className="chatbot-image-preview-text">Image selected</span>
                <button
                  type="button"
                  onClick={removeImage}
                  className="chatbot-image-preview-remove"
                >
                  <X size={16} />
                </button>
              </div>
            )}
            
            <div className="chatbot-input-row">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="chatbot-file-input"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isTyping}
                className="chatbot-image-button"
              >
                <ImageIcon size={16} />
              </button>
              <input
                type="text"
                value={inputValue}
                onInput={(e) => setInputValue((e.target as HTMLInputElement).value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !isTyping) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                disabled={isTyping}
                placeholder="Type your message..."
                className="chatbot-input"
              />
              <button
                type="button"
                disabled={isTyping || (!inputValue.trim() && !selectedImage)}
                onClick={() => handleSendMessage()}
                className="chatbot-send-button"
                style={{ backgroundColor: normalizedPrimaryColor }}
              >
                <Send size={14} />
              </button>
            </div>
            
            {effectiveShowBranding && (
              <p className="chatbot-branding">
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
          className="chatbot-bubble"
          style={{ backgroundColor: normalizedPrimaryColor }}
        >
          {effectiveAvatarUrl ? (
            <img
              src={effectiveAvatarUrl}
              alt="Bot"
              className="chatbot-bubble-avatar"
            />
          ) : (
            <MessageCircle size={28} />
          )}
        </button>
      )}
    </div>
  );
}
