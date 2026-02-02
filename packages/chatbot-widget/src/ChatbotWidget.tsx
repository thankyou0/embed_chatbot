import React, { useState, useRef, useEffect, useMemo } from "react";
import type {
  Message,
  ChatbotWidgetProps,
  ChatbotConfig,
  ProductInfo,
} from "./types";
import { compressImage, generateId } from "./utils";
import { marked } from "marked";
import "./styles.css";

// Configure marked
marked.use({
  breaks: true,
  gfm: true,
  renderer: {
    link({ href, title, text }) {
      return `<a href="${href}" ${title ? `title="${title}"` : ""} target="_blank" rel="noopener noreferrer">${text}</a>`;
    },
  },
});

// Product Carousel Component
function ProductCarousel({ products }: { products: ProductInfo[] }) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  const checkScrollability = () => {
    const container = scrollContainerRef.current;
    if (container) {
      setCanScrollLeft(container.scrollLeft > 0);
      setCanScrollRight(
        container.scrollLeft <
          container.scrollWidth - container.clientWidth - 5,
      );
    }
  };

  useEffect(() => {
    checkScrollability();
    const container = scrollContainerRef.current;
    if (container) {
      container.addEventListener("scroll", checkScrollability);
      return () => container.removeEventListener("scroll", checkScrollability);
    }
  }, [products]);

  const scroll = (direction: "left" | "right") => {
    const container = scrollContainerRef.current;
    if (container) {
      const scrollAmount = 180; // Width of one card + gap
      container.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth",
      });
    }
  };

  const formatPrice = (price?: string | null, currency?: string | null) => {
    if (!price) return null;
    return currency ? `${currency}${price}` : price;
  };

  if (!products || products.length === 0) return null;

  return (
    <div className="product-carousel-wrapper">
      {/* Left Arrow */}
      {canScrollLeft && (
        <button
          className="product-carousel-arrow left"
          onClick={() => scroll("left")}
          aria-label="Scroll left"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
      )}

      {/* Carousel Container */}
      <div ref={scrollContainerRef} className="product-carousel-container">
        {products.map((product, index) => (
          <a
            key={index}
            href={product.url}
            target="_blank"
            rel="noopener noreferrer"
            className="product-card"
          >
            {/* Product Image */}
            {product.image ? (
              <div className="product-card-image">
                <img
                  src={product.image}
                  alt={product.name}
                  loading="lazy"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.style.display = "none";
                    target.parentElement?.classList.add("no-image");
                  }}
                />
              </div>
            ) : (
              <div className="product-card-image no-image">
                <svg
                  width="32"
                  height="32"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                >
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
              </div>
            )}

            {/* Product Info */}
            <div className="product-card-info">
              <h4 className="product-card-name" title={product.name}>
                {product.name}
              </h4>
              {formatPrice(product.price, product.currency) && (
                <p className="product-card-price">
                  {formatPrice(product.price, product.currency)}
                </p>
              )}
              {product.rating && (
                <div className="product-card-rating">
                  <span className="rating-star">★</span>
                  <span>{product.rating.toFixed(1)}</span>
                  {product.review_count && (
                    <span className="review-count">
                      ({product.review_count})
                    </span>
                  )}
                </div>
              )}
            </div>
          </a>
        ))}
      </div>

      {/* Right Arrow */}
      {canScrollRight && (
        <button
          className="product-carousel-arrow right"
          onClick={() => scroll("right")}
          aria-label="Scroll right"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M9 18l6-6-6-6" />
          </svg>
        </button>
      )}
    </div>
  );
}

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
  const [reportedMessages, setReportedMessages] = useState<Set<string>>(
    new Set(),
  );
  const [toast, setToast] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isAtBottomRef = useRef(true);

  const apiUrl = config.apiUrl || "http://localhost:8000";
  const chatbotId = config.chatbotId;

  const isPreview = config.isPreview || false;
  const [isConfigLoading, setIsConfigLoading] = useState(
    !isPreview && !!chatbotId,
  );

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

  const fetchWidgetConfig = async () => {
    if (!chatbotId || isPreview) return;

    try {
      const response = await fetch(`${apiUrl}/api/v1/chat/${chatbotId}/config`);
      if (response.ok) {
        const data = await response.json();
        setWidgetConfig(data);

        // Only set welcome message if we don't have messages yet
        setMessages((prev) => {
          if (prev.length > 0) return prev;

          if (data.is_paused) {
            const pausedMessage = `🚧 ${data.display_name || "This chatbot"} is currently offline for maintenance. Please check back later. We appreciate your patience!`;
            return [
              {
                id: generateId(),
                role: "assistant",
                content: pausedMessage,
                suggestions: [],
                timestamp: new Date(),
              },
            ];
          } else {
            const welcomeMsg =
              data.welcome_message || "Hi! How can I help you today?";
            const initialSugs = data.initial_suggestions || [];
            return [
              {
                id: generateId(),
                role: "assistant",
                content: welcomeMsg,
                suggestions: initialSugs,
                timestamp: new Date(),
              },
            ];
          }
        });
      } else {
        // Fallback to default if load fails
        setWidgetConfig({});
        setMessages((prev) => {
          if (prev.length > 0) return prev;
          return [
            {
              id: generateId(),
              role: "assistant",
              content: "Hi! How can I help you today?",
              suggestions: [],
              timestamp: new Date(),
            },
          ];
        });
      }
    } catch (err) {
      console.error("Failed to fetch widget config:", err);
      setWidgetConfig({});
      setMessages((prev) => {
        if (prev.length > 0) return prev;
        return [
          {
            id: generateId(),
            role: "assistant",
            content: "Hi! How can I help you today?",
            suggestions: [],
            timestamp: new Date(),
          },
        ];
      });
    } finally {
      setIsConfigLoading(false);
    }
  };

  // Pre-fetch widget config on mount to ensure bubble appearance (color, avatar, offsets) is correct
  // even before the user opens the chat.
  const hasInitedFetch = useRef(false);
  useEffect(() => {
    if (!isPreview && chatbotId && !hasInitedFetch.current) {
      hasInitedFetch.current = true;
      fetchWidgetConfig();
    }
  }, [chatbotId, isPreview, apiUrl]);

  // Show welcome message on first open (handles preview mode logic)
  useEffect(() => {
    if (isOpen && messages.length === 0 && isPreview) {
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
    messages.length,
    config.welcomeMessage,
    config.initialSuggestions,
  ]);

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

    // Create placeholder assistant message for streaming
    const assistantMessageId = generateId();
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: "assistant",
      content: "",
      isTyping: true,
      timestamp: new Date(),
    };
    setMessages((prev: Message[]) => [...prev, assistantMessage]);

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

      // Use streaming endpoint
      const response = await fetch(
        `${apiUrl}/api/v1/chat/${chatbotId}/message/stream`,
        {
          method: "POST",
          body: formData,
        },
      );

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      // Process SSE stream
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let streamedContent = "";
      let streamSessionId = sessionId;
      let finalSuggestions: string[] = [];
      let finalProducts: ProductInfo[] = [];

      // ===== PRODUCTION-GRADE 4-STAGE PACING SYSTEM =====

      // Stage A: Sentence-level gating buffer
      let sentenceBuffer = "";
      let displayedContent = "";
      let renderQueue: string[] = []; // Sentence/phrase queue
      let isRendering = false;
      let firstCharShown = false;
      let streamEnded = false;

      // Tunable parameters
      const CHAR_DELAY_MS = 20; // Constant brisk speed (~50 chars/sec)
      const CHAR_VARIANCE = 0; // Uniform speed
      const COMMA_PAUSE_MS = 20;
      const PERIOD_PAUSE_MS = 20;
      const PARAGRAPH_PAUSE_MS = 20;
      const SENTENCE_GATE_TIMEOUT_MS = 50;
      const FIRST_CHAR_DELAY_MS = 20;
      const MAX_BUFFER_CHARS = 500;
      const ADAPTIVE_SPEED_MULTIPLIER = 0.5;

      // Sentence detection regex
      const SENTENCE_END_REGEX =
        /[.!?]\s+|<br\s*\/?>\s*|<\/p>\s*|<\/li>\s*|\n\n/;

      // Stage B: Character-by-character renderer with consistent speed
      const renderCharacters = async (text: string) => {
        if (isRendering) return;
        isRendering = true;

        // Minimum latency before first character
        if (!firstCharShown) {
          await new Promise((r) => setTimeout(r, FIRST_CHAR_DELAY_MS));
          firstCharShown = true;
        }

        for (let i = 0; i < text.length; i++) {
          const char = text[i];
          displayedContent += char;

          setMessages((prev: Message[]) => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage && lastMessage.id === assistantMessageId) {
              lastMessage.content = displayedContent;
            }
            return newMessages;
          });

          // Constant speed (Stage C and variance removed)
          let delay = CHAR_DELAY_MS;

          // Stage D: Adaptive speed when buffer is large
          if (
            renderQueue.length > 2 ||
            sentenceBuffer.length > MAX_BUFFER_CHARS
          ) {
            delay *= ADAPTIVE_SPEED_MULTIPLIER;
          }

          await new Promise((r) => setTimeout(r, delay));
        }

        isRendering = false;
        processRenderQueue(); // Continue with next chunk
      };

      // Stage A+D: Sentence gating and burst handling
      const processRenderQueue = async () => {
        if (isRendering || renderQueue.length === 0) return;

        const nextChunk = renderQueue.shift();
        if (nextChunk) {
          await renderCharacters(nextChunk);
        }
      };

      // Sentence gate timer
      let sentenceGateTimer: NodeJS.Timeout | null = null;

      const flushSentenceBuffer = () => {
        if (sentenceBuffer.trim()) {
          renderQueue.push(sentenceBuffer);
          sentenceBuffer = "";
          processRenderQueue();
        }
        if (sentenceGateTimer) {
          clearTimeout(sentenceGateTimer);
          sentenceGateTimer = null;
        }
      };

      const addToSentenceBuffer = (content: string) => {
        sentenceBuffer += content;
        streamedContent += content;

        // Check if we have a complete sentence
        const match = sentenceBuffer.match(SENTENCE_END_REGEX);
        if (match) {
          flushSentenceBuffer();
        } else {
          // Emergency flush if buffer too large
          if (sentenceBuffer.length > MAX_BUFFER_CHARS) {
            flushSentenceBuffer();
          } else {
            // Reset sentence gate timeout
            if (sentenceGateTimer) clearTimeout(sentenceGateTimer);
            sentenceGateTimer = setTimeout(() => {
              flushSentenceBuffer();
            }, SENTENCE_GATE_TIMEOUT_MS);
          }
        }
      };

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          // Decode chunk and add to buffer
          buffer += decoder.decode(value, { stream: true });

          // Process complete SSE messages
          const lines = buffer.split("\n");
          buffer = lines.pop() || ""; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6);
              try {
                const chunk = JSON.parse(data);

                if (chunk.type === "session") {
                  // Update session ID
                  streamSessionId = chunk.session_id;
                  setSessionId(chunk.session_id);
                } else if (chunk.type === "content") {
                  // Add to sentence buffer for gated rendering
                  addToSentenceBuffer(chunk.content);
                } else if (chunk.type === "done") {
                  // Stream ended - flush any remaining content
                  streamEnded = true;
                  flushSentenceBuffer();

                  // Save final metadata
                  finalSuggestions = chunk.suggestions || [];
                  finalProducts = chunk.products || [];

                  // Wait for all rendering to complete
                  const finishAllRendering = async () => {
                    while (renderQueue.length > 0 || isRendering) {
                      await new Promise((r) => setTimeout(r, 100));
                    }

                    setMessages((prev: Message[]) => {
                      const newMessages = [...prev];
                      const lastMessage = newMessages[newMessages.length - 1];
                      if (
                        lastMessage &&
                        lastMessage.id === assistantMessageId
                      ) {
                        lastMessage.isTyping = false;
                        lastMessage.suggestions = finalSuggestions;
                        lastMessage.products = finalProducts;
                      }
                      return newMessages;
                    });
                  };
                  finishAllRendering();
                } else if (chunk.type === "error") {
                  throw new Error(chunk.error || "Stream error");
                }
              } catch (err) {
                console.error("Failed to parse SSE chunk:", err);
              }
            }
          }
        }
      }

      setIsTyping(false);
      removeImage();
    } catch (err) {
      console.error("Failed to send message:", err);
      setIsTyping(false);
      removeImage();

      // Update assistant message with error
      setMessages((prev: Message[]) => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.id === assistantMessageId) {
          lastMessage.content =
            "I'm sorry, I encountered an error. Please try again.";
          lastMessage.isTyping = false;
        }
        return newMessages;
      });
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (isTyping) return;
    sendMessage(suggestion);
  };

  const handleReportAnswer = async (userMessage: string, messageId: string) => {
    // Allow reporting in preview mode (submit report and show toast)
    if (!chatbotId || !sessionId) {
      setToast("missing fields. can't submit report");
      setTimeout(() => setToast(null), 3000);
      return;
    }

    try {
      await fetch(`${apiUrl}/api/v1/chat/${chatbotId}/report`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          message_content: userMessage,
        }),
      });

      // Mark this message as reported
      setReportedMessages((prev) => new Set(prev).add(messageId));

      // Show toast notification
      setToast("Thank you for your feedback!");
      setTimeout(() => setToast(null), 3000);
    } catch (err) {
      console.error("Failed to report message:", err);
      setToast("Failed to report. Please try again.");
      setTimeout(() => setToast(null), 3000);
    }
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

    // If contained (like in preview or iframe), use absolute positioning
    if (config.isContained) {
      return {
        ...base,
        position: "absolute",
      };
    }

    // Default fixed positioning for floating widget on host site
    return {
      ...base,
      position: "fixed",
    };
  }, [position, offsetX, offsetY, config.isContained]);

  // Helper to render message content as markdown
  const renderMessageContent = (content: string, isTyping?: boolean) => {
    try {
      // Use marked to parse markdown
      // marked.parse returns a string or Promise<string>. In modern versions it is sync unless async: true is set.
      let html = marked.parse(content) as string;

      if (isTyping) {
        // If typing, we want to append the cursor inside the last <p> tag if it exists
        // so it stays inline with the last sentence
        if (html.includes("</p>")) {
          html = html.replace(
            /<\/p>\s*$/,
            '<span class="chatbot-typing-cursor"></span></p>',
          );
        } else {
          html += '<span class="chatbot-typing-cursor"></span>';
        }
      }

      return html;
    } catch (e) {
      console.error("Error parsing markdown:", e);
      return (
        content +
        (isTyping ? '<span class="chatbot-typing-cursor"></span>' : "")
      );
    }
  };

  return (
    <div
      className="chatbot-widget-container"
      style={{
        ...positionStyle,
        // Hide while loading in production to prevent "flash" of default blue settings
        visibility: isConfigLoading ? "hidden" : "visible",
      }}
    >
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
                      <div
                        className="chatbot-message-text"
                        dangerouslySetInnerHTML={{
                          __html: renderMessageContent(
                            msg.content,
                            msg.isTyping,
                          ),
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Product Carousel - show after message when typing is complete */}
                {msg.role === "assistant" &&
                  !msg.isTyping &&
                  msg.products &&
                  msg.products.length > 0 && (
                    <ProductCarousel products={msg.products} />
                  )}

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
                        ),
                      )}
                    </div>
                  )}

                {/* Report button - show for assistant messages (except welcome) */}
                {msg.role === "assistant" &&
                  !msg.isTyping &&
                  messages.indexOf(msg) > 0 &&
                  !reportedMessages.has(msg.id) && (
                    <div className="chatbot-report-container">
                      <button
                        type="button"
                        onClick={() => {
                          // Find the previous user message
                          const msgIndex = messages.indexOf(msg);
                          for (let i = msgIndex - 1; i >= 0; i--) {
                            if (messages[i].role === "user") {
                              handleReportAnswer(messages[i].content, msg.id);
                              break;
                            }
                          }
                        }}
                        className="chatbot-report-button"
                        title="Report this answer"
                        disabled={!chatbotId || !sessionId}
                      >
                        <svg
                          width="14"
                          height="14"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                        >
                          <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17" />
                        </svg>
                        <span>Not helpful</span>
                      </button>
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

          {/* Toast Notification */}
          {toast && <div className="chatbot-toast">{toast}</div>}
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
