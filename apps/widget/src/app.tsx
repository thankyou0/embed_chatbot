import { useState, useEffect, useRef } from 'preact/hooks'
import { MessageSquare, X } from 'lucide-preact' // Using lucide-preact for icons

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
}

const DEFAULT_API_BASE_URL = import.meta.env.VITE_PUBLIC_API_URL || 'http://localhost:8000';

export function App(config: ChatbotConfig) {
  const API_BASE_URL = config.apiUrl || DEFAULT_API_BASE_URL;
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const effectivePosition = config.position || 'bottom-right';
  const effectiveOffsetX = config.offsetX || 20;
  const effectiveOffsetY = config.offsetY || 20;
  const effectivePrimaryColor = config.primaryColor || '#1a73e8';
  const effectiveHeaderText = config.headerText || 'Chat with us';
  const effectiveWelcomeMessage = config.welcomeMessage || 'Hi! How can I help you today?';
  const effectiveInitialSuggestions = config.initialSuggestions || [];
  const effectiveAvatarUrl = config.avatarUrl || 'https://i.pravatar.cc/300'; // Default avatar
  const effectiveShowBranding = config.showBranding !== false; // Default to true

  useEffect(() => {
    // Load session ID from sessionStorage on component mount
    const storedSessionId = sessionStorage.getItem(`chatbot_session_id_${config.chatbotId}`);
    if (storedSessionId) {
      setSessionId(storedSessionId);
    }

    // Add welcome message if chat is opened for the first time in a session
    if (isOpen && messages.length === 0) {
      setMessages([{ text: effectiveWelcomeMessage, isUser: false }]);
      if (effectiveInitialSuggestions.length > 0) {
        setMessages(prev => [...prev, { text: "", isUser: false, suggestions: effectiveInitialSuggestions }]);
      }
    }
  }, [isOpen]);

  useEffect(() => {
    // Scroll to the latest message
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const toggleChat = () => {
    setIsOpen(prev => !prev);
  };

  const handleSendMessage = async (text?: string) => {
    const messageText = text || inputValue;
    if (!messageText.trim()) return;

    const userMessage = { text: messageText, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    if (!text) setInputValue('');

    setIsTyping(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/${config.chatbotId}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageText,
          session_id: sessionId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        sessionStorage.setItem(`chatbot_session_id_${config.chatbotId}`, data.session_id);

        setMessages(prev => [
          ...prev,
          { text: data.message, isUser: false, suggestions: data.suggestions },
        ]);
      } else {
        console.error('Error fetching chat response:', response.statusText);
        setMessages(prev => [
          ...prev,
          { text: 'Oops! Something went wrong. Please try again later.', isUser: false },
        ]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [
        ...prev,
        { text: 'Oops! Could not connect to the chatbot. Please try again later.', isUser: false },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const containerClasses = [
    'chatbot-widget-container',
    effectivePosition,
  ].join(' ');

  const containerStyle = {
    [effectivePosition.includes('right') ? 'right' : 'left']: `${effectiveOffsetX}px`,
    [effectivePosition.includes('bottom') ? 'bottom' : 'top']: `${effectiveOffsetY}px`,
    // Ensure the container is not visible until Preact renders
    visibility: 'visible',
  };

  useEffect(() => {
    if (isOpen) {
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          toggleChat();
        }
      };
      document.addEventListener('keydown', handleKeyDown);
      return () => {
        document.removeEventListener('keydown', handleKeyDown);
      };
    }
  }, [isOpen]);

  return (
    <div className={containerClasses} style={containerStyle} role="complementary" aria-label="Chatbot widget">
      {!isOpen && (
        <button
          className="chatbot-bubble"
          onClick={toggleChat}
          style={{ backgroundColor: effectivePrimaryColor }}
          aria-label={`Open ${effectiveHeaderText}`}
          aria-expanded="false"
        >
          <MessageSquare size={30} />
          <span className="chatbot-sr-only">Open chat window</span>
        </button>
      )}

      {isOpen && (
        <div 
          className={`chatbot-window ${effectivePosition}`}
          role="dialog"
          aria-label={effectiveHeaderText}
          aria-modal="true"
        >
          <div className="chatbot-header" style={{ backgroundColor: effectivePrimaryColor }}>
            <h3 id="chatbot-header-title">{effectiveHeaderText}</h3>
            <button 
              onClick={toggleChat}
              aria-label="Close chat window"
              aria-expanded="true"
            >
              <X size={20} />
              <span className="chatbot-sr-only">Close chat</span>
            </button>
          </div>
          <div 
            className="chatbot-messages"
            role="log"
            aria-live="polite"
            aria-atomic="false"
            aria-label="Chat messages"
          >
            {messages.map((msg, index) => (
              <div 
                key={index} 
                className={`chatbot-message ${msg.isUser ? 'user' : 'bot'}`}
              >
                {!msg.isUser && effectiveAvatarUrl && (
                  <img 
                    src={effectiveAvatarUrl} 
                    alt="Bot Avatar" 
                    className="chatbot-avatar"
                    aria-hidden="true"
                  />
                )}
                <div className="chatbot-message-bubble">
                  {msg.text}
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="chatbot-message bot" role="status" aria-live="polite">
                 {effectiveAvatarUrl && (
                  <img 
                    src={effectiveAvatarUrl} 
                    alt="Bot Avatar" 
                    className="chatbot-avatar"
                    aria-hidden="true"
                  />
                )}
                <div className="chatbot-message-bubble typing-indicator" aria-label="Bot is typing">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} aria-hidden="true" />
          </div>
          {(() => {
            const lastMessage = messages[messages.length - 1];
            if (messages.length > 0 && lastMessage?.suggestions && lastMessage.suggestions.length > 0) {
              return (
                <div className="chatbot-suggestions" role="group" aria-label="Suggested questions">
                  {lastMessage.suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      type="button"
                      className="chatbot-suggestion-item"
                      onClick={() => handleSendMessage(suggestion)}
                      aria-label={`Send suggestion: ${suggestion}`}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              );
            }
            return null;
          })()}
          <div className="chatbot-input-area" role="form" aria-label="Message input">
            <label htmlFor="chatbot-input" className="chatbot-sr-only">
              Type your message
            </label>
            <input
              id="chatbot-input"
              type="text"
              placeholder="Type your message..."
              value={inputValue}
              onInput={(e) => setInputValue((e.target as HTMLInputElement).value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSendMessage();
                }
              }}
              disabled={isTyping}
              aria-label="Message input"
              aria-describedby="chatbot-header-title"
            />
            <button 
              onClick={() => handleSendMessage()} 
              disabled={isTyping || !inputValue.trim()} 
              style={{ backgroundColor: effectivePrimaryColor }}
              aria-label="Send message"
            >
              Send
            </button>
          </div>
          {effectiveShowBranding && (
            <div className="chatbot-footer" role="contentinfo">
              Powered by YourBrand
            </div>
          )}
        </div>
      )}
    </div>
  );
}
