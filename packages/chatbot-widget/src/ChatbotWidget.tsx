import React, { useState, useRef, useEffect, useMemo } from "react";
import type { Message, ChatbotWidgetProps, ChatbotConfig } from "./types";
import { compressImage, generateId } from "./utils";
import "./styles.css";

export function ChatbotWidget({ config }: ChatbotWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [widgetConfig, setWidgetConfig] = useState<any>(null);
  const [_error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isAtBottomRef = useRef(true);

  const apiUrl = config.apiUrl || "http://localhost:8000";
  const chatbotId = config.chatbotId;

  // In preview mode, prioritize config prop over widgetConfig from API for real-time updates
  // In production, use widgetConfig from API (fetched once)
  const isPreview = config.isPreview || false;

  const position = isPreview
    ? config.position || config.theme?.position || "bottom-right"
    : widgetConfig?.position || config.theme?.position || "bottom-right";

  const primaryColor = useMemo(() => {
    const color = isPreview
      ? config.primaryColor || config.theme?.primaryColor || "#2563eb"
      : widgetConfig?.primary_color || config.theme?.primaryColor || "#2563eb";
    if (color && /^#[0-9A-Fa-f]{6}$/.test(color)) {
      return color;
    }
    return "#2563eb";
  }, [
    isPreview,
    widgetConfig?.primary_color,
    config.primaryColor,
    config.theme?.primaryColor,
  ]);

  const headerText = isPreview
    ? config.headerText || "Chat with us"
    : widgetConfig?.header_text || config.headerText || "Chat with us";

  const avatarUrl = isPreview
    ? config.avatarUrl || null
    : widgetConfig?.avatar_url || config.avatarUrl || null;

  const welcomeMessage = isPreview
    ? config.welcomeMessage || "Hi! How can I help you today?"
    : widgetConfig?.welcome_message ||
      config.welcomeMessage ||
      "Hi! How can I help you today?";

  const initialSuggestions = isPreview
    ? config.initialSuggestions || []
    : widgetConfig?.initial_suggestions || config.initialSuggestions || [];

  const showBranding = isPreview
    ? config.showBranding !== undefined
      ? config.showBranding
      : true
    : widgetConfig?.show_branding !== false;

  const offsetX = isPreview
    ? (config.offsetX ?? 0)
    : (widgetConfig?.offset_x ?? config.offsetX ?? 0);

  const offsetY = isPreview
    ? (config.offsetY ?? 0)
    : (widgetConfig?.offset_y ?? config.offsetY ?? 0);

  // Update welcome message and suggestions when config changes in preview mode
  useEffect(() => {
    if (isPreview && isOpen && messages.length > 0) {
      // Update welcome message if it changed
      const welcomeMsg =
        config.welcomeMessage || "Hi! How can I help you today?";
      const initialSugs = config.initialSuggestions || [];

      setMessages((prev: Message[]) => {
        // Update first message if it's the welcome message
        if (prev.length > 0 && prev[0].role === "assistant") {
          const updated = [...prev];
          updated[0] = {
            ...updated[0],
            content: welcomeMsg,
            suggestions: initialSugs,
          };
          return updated;
        }
        return prev;
      });
    }
  }, [
    isPreview,
    isOpen,
    config.welcomeMessage,
    config.initialSuggestions,
    messages.length,
  ]);

  // Smart scroll logic - matches preview behavior
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const lastMessage = messages[messages.length - 1];
    if (lastMessage?.role === "user") {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      isAtBottomRef.current = true;
      return;
    }

    if (isAtBottomRef.current) {
      messagesEndRef.current?.scrollIntoView({
        behavior: isTyping ? "auto" : "smooth",
      });
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

  // Fetch widget config and show welcome message on first open
  // Skip API fetch in preview mode - use config prop directly
  useEffect(() => {
    if (isOpen && messages.length === 0 && chatbotId && !isPreview) {
      fetchWidgetConfig();
    } else if (isOpen && messages.length === 0 && isPreview) {
      // In preview mode, use config prop directly
      const welcomeMsg =
        config.welcomeMessage || "Hi! How can I help you today?";
      const initialSugs = config.initialSuggestions || [];

      setMessages([
        {
          id: generateId(),
          role: "assistant",
          content: welcomeMsg,
          suggestions: initialSugs,
          timestamp: new Date(),
        },
      ]);
    }
  }, [
    isOpen,
    chatbotId,
    isPreview,
    config.welcomeMessage,
    config.initialSuggestions,
  ]);

  const fetchWidgetConfig = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/v1/chat/${chatbotId}/config`);
      if (response.ok) {
        const data = await response.json();
        setWidgetConfig(data);

        // Check if chatbot is paused
        if (data.is_paused) {
          const pausedMessage = `🚧 ${data.display_name || "This chatbot"} is currently offline for maintenance. Please check back later. We appreciate your patience!`;
          setMessages([
            {
              id: generateId(),
              role: "assistant",
              content: pausedMessage,
              suggestions: [],
              timestamp: new Date(),
            },
          ]);
        } else {
          // Show welcome message
          const welcomeMsg =
            data.welcome_message || "Hi! How can I help you today?";
          const initialSugs = data.initial_suggestions || [];

          setMessages([
            {
              id: generateId(),
              role: "assistant",
              content: welcomeMsg,
              suggestions: initialSugs,
              timestamp: new Date(),
            },
          ]);
        }
      } else {
        // Fallback to default
        setMessages([
          {
            id: generateId(),
            role: "assistant",
            content: "Hi! How can I help you today?",
            suggestions: [],
            timestamp: new Date(),
          },
        ]);
      }
    } catch (err) {
      console.error("Failed to fetch widget config:", err);
      // Show default welcome
      setMessages([
        {
          id: generateId(),
          role: "assistant",
          content: "Hi! How can I help you today?",
          suggestions: [],
          timestamp: new Date(),
        },
      ]);
    }
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const input = e.target;
    const file = input.files?.[0];
    if (file) {
      if (!file.type.startsWith("image/")) {
        setError("Please select an image file");
        return;
      }
      setSelectedImage(file);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
      setError(null);
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Type message character by character (matches preview)
  const typeMessage = (fullText: string, suggestions?: string[]) => {
    let currentIndex = 0;
    const typingMessage: Message = {
      id: generateId(),
      role: "assistant",
      content: "",
      isTyping: true,
      suggestions,
      timestamp: new Date(),
    };

    setMessages((prev: Message[]) => [...prev, typingMessage]);

    const typingInterval = setInterval(() => {
      currentIndex++;
      const partialText = fullText.slice(0, currentIndex);

      setMessages((prev: Message[]) => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.isTyping) {
          lastMessage.content = partialText;
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
    }, 20); // 20ms per character
  };

  const sendMessage = async (messageText?: string) => {
    if (isTyping) return;

    // Check if chatbot is paused (only for non-preview mode)
    if (!isPreview && widgetConfig?.is_paused) {
      return; // Do nothing if chatbot is paused
    }

    const text = messageText || inputValue.trim();
    if (!text && !selectedImage) return;
    if (!chatbotId) {
      setError("Chatbot not configured");
      return;
    }

    // Add user message to UI
    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: text || "(Image uploaded)",
      imagePreview: imagePreview || undefined,
      timestamp: new Date(),
    };
    setMessages((prev: Message[]) => [...prev, userMessage]);
    if (!messageText) setInputValue("");
    setIsTyping(true);
    setError(null);

    try {
      // Build form data
      const formData = new FormData();
      formData.append("message", text || "What is this?");
      if (sessionId) {
        formData.append("session_id", sessionId);
      }

      // Compress and add image if selected
      if (selectedImage) {
        try {
          const compressedBlob = await compressImage(selectedImage, 1024);
          formData.append("image", compressedBlob, "image.jpg");
        } catch (err) {
          console.error("Image compression failed:", err);
          formData.append("image", selectedImage);
        }
      }

      const response = await fetch(
        `${apiUrl}/api/v1/chat/${chatbotId}/message`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();

      // Update session ID
      if (data.session_id) {
        setSessionId(data.session_id);
      }

      setIsTyping(false);
      removeImage();

      // Use typing effect to show response
      typeMessage(data.message, data.suggestions);
    } catch (err) {
      console.error("Failed to send message:", err);
      setIsTyping(false);
      removeImage();
      typeMessage("I'm sorry, I encountered an error. Please try again.");
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (isTyping) return;
    sendMessage(suggestion);
  };

  const handleClose = () => {
    setIsOpen(false);
    setTimeout(() => {
      setMessages([
        {
          id: generateId(),
          role: "assistant",
          content: welcomeMessage,
          suggestions: initialSuggestions,
          timestamp: new Date(),
        },
      ]);
      setSessionId(null);
      removeImage();
    }, 300);
  };

  const handleMinimize = () => {
    setIsOpen(false);
  };

  // Recalculate position style when offsets or position change
  const positionStyle: React.CSSProperties = useMemo(() => {
    const base = {
      bottom: `${16 + offsetY}px`,
      [position === "bottom-right" ? "right" : "left"]: `${16 + offsetX}px`,
    };

    // If contained (like in preview), use absolute positioning
    if (config.isContained) {
      return {
        ...base,
        position: "absolute",
      };
    }

    // Default fixed positioning for floating widget
    return base;
  }, [position, offsetX, offsetY, config.isContained]);

  return (
    <div className="chatbot-widget-container" style={positionStyle}>
      {isOpen ? (
        <div className="chatbot-window">
          {/* Header */}
          <div
            className="chatbot-header"
            style={{ backgroundColor: primaryColor }}
          >
            <div className="chatbot-header-content">
              {avatarUrl ? (
                <img
                  src={avatarUrl}
                  alt="Bot Avatar"
                  className="chatbot-header-avatar"
                />
              ) : (
                <div className="chatbot-header-avatar-placeholder">
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                </div>
              )}
              <div>
                <h3 className="chatbot-header-title">{headerText}</h3>
              </div>
            </div>
            <div className="chatbot-header-actions">
              <button
                type="button"
                onClick={handleMinimize}
                title="Minimize"
                className="chatbot-header-button"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3" />
                </svg>
              </button>
              <button
                type="button"
                onClick={handleClose}
                title="Close and Reset"
                className="chatbot-header-button"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Messages */}
          <div
            ref={messagesContainerRef}
            className="chatbot-messages"
            onScroll={handleScroll}
          >
            {messages.map((msg: Message) => (
              <div key={msg.id} className="chatbot-message-wrapper">
                <div
                  className={`chatbot-message ${msg.role === "user" ? "user" : "bot"}`}
                >
                  {msg.role === "assistant" && (
                    <div className="chatbot-message-avatar">
                      {avatarUrl ? (
                        <img
                          src={avatarUrl}
                          alt="Bot"
                          className="chatbot-avatar-small"
                        />
                      ) : (
                        <div className="chatbot-avatar-placeholder">
                          <svg
                            width="12"
                            height="12"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                          >
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                          </svg>
                        </div>
                      )}
                    </div>
                  )}
                  <div
                    className={`chatbot-message-content ${msg.role === "user" ? "user" : "bot"}`}
                  >
                    {msg.imagePreview && (
                      <img
                        src={msg.imagePreview}
                        alt="Uploaded"
                        className="chatbot-message-image"
                      />
                    )}
                    <div
                      className={`chatbot-message-bubble ${msg.role === "user" ? "user" : "bot"}`}
                      style={
                        msg.role === "user"
                          ? { backgroundColor: primaryColor }
                          : {}
                      }
                    >
                      <p className="chatbot-message-text">
                        {msg.content}
                        {msg.isTyping && (
                          <span className="chatbot-typing-cursor">|</span>
                        )}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Suggestions for this message - only show when typing is complete */}
                {msg.role === "assistant" &&
                  !msg.isTyping &&
                  msg.suggestions &&
                  msg.suggestions.length > 0 && (
                    <div className="chatbot-suggestions-inline">
                      {msg.suggestions.map(
                        (suggestion: string, idx: number) => (
                          <button
                            key={idx}
                            type="button"
                            disabled={isTyping}
                            onClick={() => handleSuggestionClick(suggestion)}
                            className="chatbot-suggestion-button"
                          >
                            {suggestion}
                          </button>
                        )
                      )}
                    </div>
                  )}
              </div>
            ))}

            {isTyping && !messages.some((m: Message) => m.isTyping) && (
              <div className="chatbot-typing-indicator">
                <div>
                  <span className="chatbot-typing-dot"></span>
                  <span
                    className="chatbot-typing-dot"
                    style={{ animationDelay: "0.2s" }}
                  ></span>
                  <span
                    className="chatbot-typing-dot"
                    style={{ animationDelay: "0.4s" }}
                  ></span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
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
                <span className="chatbot-image-preview-text">
                  Image selected
                </span>
                <button
                  type="button"
                  onClick={removeImage}
                  className="chatbot-image-preview-remove"
                >
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path d="M18 6L6 18M6 6l12 12" />
                  </svg>
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
                disabled={isTyping || (!isPreview && widgetConfig?.is_paused)}
                className="chatbot-image-button"
                title="Upload image"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
              </button>
              <input
                type="text"
                className="chatbot-input"
                placeholder={
                  !isPreview && widgetConfig?.is_paused
                    ? "Chat is temporarily unavailable"
                    : "Type your message..."
                }
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !isTyping) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                disabled={isTyping || (!isPreview && widgetConfig?.is_paused)}
              />
              <button
                type="button"
                disabled={
                  isTyping ||
                  (!inputValue.trim() && !selectedImage) ||
                  (!isPreview && widgetConfig?.is_paused)
                }
                onClick={() => sendMessage()}
                className="chatbot-send-button"
                style={{ backgroundColor: primaryColor }}
              >
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
                </svg>
              </button>
            </div>

            {showBranding && (
              <p className="chatbot-branding">Powered by ChatBot</p>
            )}
          </div>
        </div>
      ) : (
        /* Minimized Button / Bubble */
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="chatbot-bubble"
          style={{ backgroundColor: primaryColor }}
        >
          {avatarUrl ? (
            <img src={avatarUrl} alt="Bot" className="chatbot-bubble-avatar" />
          ) : (
            <svg
              width="28"
              height="28"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          )}
        </button>
      )}
    </div>
  );
}
