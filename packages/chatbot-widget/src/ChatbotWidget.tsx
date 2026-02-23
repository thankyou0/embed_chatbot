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
    link(token: any) {
      const href = token.href as string;
      const title = token.title as string | null;
      const text = token.text as string;
      return `<a class="chatbot-message-link" href="${href}" ${title ? `title="${title}"` : ""} target="_blank" rel="noopener noreferrer">${text}</a>`;
    },
  },
});

const USER_SAFE_RESPONSE_ERROR =
  "I'm sorry, I can't respond right now. Please try again in a few minutes.";

const sanitizeAssistantErrorMessage = (rawMessage?: string) => {
  const text = (rawMessage || "").trim();
  if (!text) return USER_SAFE_RESPONSE_ERROR;

  const lowered = text.toLowerCase();
  const technicalTokens = [
    "traceback",
    "exception",
    "stack",
    "http",
    "status",
    "api",
    "groq",
    "llama",
    "rate limit",
    "tokens per day",
    "tpd",
    "org_",
    "service tier",
    "model",
  ];

  if (technicalTokens.some((token) => lowered.includes(token))) {
    return USER_SAFE_RESPONSE_ERROR;
  }

  if (text.length > 220) {
    return USER_SAFE_RESPONSE_ERROR;
  }

  return text;
};

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

    // Normalize currency codes/names to proper symbols
    const currencyMap: Record<string, string> = {
      inr: "₹",
      INR: "₹",
      "₹": "₹",
      rs: "₹",
      "rs.": "₹",
      rupee: "₹",
      rupees: "₹",
      usd: "$",
      USD: "$",
      $: "$",
      dollar: "$",
      dollars: "$",
      eur: "€",
      EUR: "€",
      "€": "€",
      gbp: "£",
      GBP: "£",
      "£": "£",
    };

    const trimmed = (currency || "").trim();
    let symbol = currencyMap[trimmed] || currencyMap[trimmed.toLowerCase()] || trimmed;
    
    // If no currency field, try to detect from the price string itself
    if (!symbol) {
      if (price.includes("₹")) symbol = "₹";
      else if (price.includes("$")) symbol = "$";
      else if (price.includes("€")) symbol = "€";
      else if (price.includes("£")) symbol = "£";
    }

    // Format number with commas (Indian style for ₹, Western for others)
    // Safety: strip any currency symbols that may still be embedded in the price string
    const cleanPrice = price.replace(/[₹$€£]/g, "").replace(/,/g, "").trim();
    const numericPrice = parseFloat(cleanPrice);
    let formatted: string;
    if (!isNaN(numericPrice)) {
      if (symbol === "₹") {
        // Indian numbering: 1,00,000
        formatted = numericPrice.toLocaleString("en-IN", {
          maximumFractionDigits: 2,
          minimumFractionDigits: numericPrice % 1 === 0 ? 0 : 2,
        });
      } else {
        formatted = numericPrice.toLocaleString("en-US", {
          maximumFractionDigits: 2,
          minimumFractionDigits: numericPrice % 1 === 0 ? 0 : 2,
        });
      }
    } else {
      formatted = price;
    }

    return symbol ? `${symbol}${formatted}` : formatted;
  };

  // Handle image drag start - allows dragging product images to chatbot input
  const handleImageDragStart = (
    e: React.DragEvent<HTMLImageElement>,
    imageUrl: string,
  ) => {
    e.stopPropagation(); // Prevent parent link from interfering
    // Set the image URL as drag data
    e.dataTransfer.setData("text/plain", imageUrl);
    e.dataTransfer.effectAllowed = "copy";
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
        {products.map((product, index) => {
          // Validate product URL — skip link wrapper for empty/invalid/internal URLs
          const hasValidUrl =
            product.url &&
            product.url.startsWith("http") &&
            !product.url.includes("localhost") &&
            !product.url.includes("/dashboard/") &&
            !product.url.includes("undefined");

          const CardWrapper = hasValidUrl ? "a" : "div";
          const linkProps = hasValidUrl
            ? {
                href: product.url,
                target: "_blank" as const,
                rel: "noopener noreferrer",
              }
            : {};

          return (
          <CardWrapper
            key={index}
            {...linkProps}
            className="product-card"
            onDragStart={(e: React.DragEvent) => {
              // Prevent the entire link from being dragged
              e.preventDefault();
            }}
          >
            {/* Product Image */}
            {product.image ? (
              <div className="product-card-image">
                <img
                  src={product.image}
                  alt={product.name}
                  loading="lazy"
                  draggable="true"
                  onDragStart={(e) => handleImageDragStart(e, product.image!)}
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
          </CardWrapper>
          );
        })}
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

// --- Welcome Typewriter Animation Component ---
// Cycles through multi-language greetings with a typing → deleting animation
function WelcomeTypewriter({
  greetings,
  staticContent,
}: {
  greetings: string[];
  staticContent: string;
}) {
  const [displayText, setDisplayText] = useState("");
  const [greetingIndex, setGreetingIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  const [charIndex, setCharIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    if (greetings.length <= 1) {
      // Single language — just show static content, no animation
      setDisplayText(greetings[0] || staticContent);
      return;
    }

    const currentGreeting = greetings[greetingIndex];

    if (isPaused) {
      // Pause after fully typed before starting to delete
      const pauseTimer = setTimeout(() => {
        setIsPaused(false);
        setIsDeleting(true);
      }, 1800);
      return () => clearTimeout(pauseTimer);
    }

    if (!isDeleting) {
      // Typing forward
      if (charIndex < currentGreeting.length) {
        const timer = setTimeout(() => {
          setDisplayText(currentGreeting.slice(0, charIndex + 1));
          setCharIndex(charIndex + 1);
        }, 30); // typing speed
        return () => clearTimeout(timer);
      } else {
        // Finished typing — pause before deleting
        setIsPaused(true);
      }
    } else {
      // Deleting backward
      if (charIndex > 0) {
        const timer = setTimeout(() => {
          setDisplayText(currentGreeting.slice(0, charIndex - 1));
          setCharIndex(charIndex - 1);
        }, 16); // deleting speed (faster than typing)
        return () => clearTimeout(timer);
      } else {
        // Finished deleting — move to next greeting
        setIsDeleting(false);
        setGreetingIndex((prev) => (prev + 1) % greetings.length);
      }
    }
  }, [charIndex, isDeleting, isPaused, greetingIndex, greetings, staticContent]);

  return (
    <span>
      {displayText}
      <span className="typewriter-cursor">|</span>
    </span>
  );
}

// --- Thinking Indicator Component ---
// Shows real-time backend status while the bot is processing.
// Falls back to a timed cycle if no status events arrive.
const FALLBACK_THINKING = "Thinking...";

function ThinkingIndicator({ status }: { status?: string | null }) {
  const [fallbackText, setFallbackText] = useState(FALLBACK_THINKING);
  const [visible, setVisible] = useState(true);

  // Fallback cycle only when no backend status has been received
  useEffect(() => {
    if (status) return;              // backend is driving the text
    const cycle = ["Thinking...", "Searching knowledge base...", "Crafting a response..."];
    let idx = 0;
    const timer = setInterval(() => {
      setVisible(false);
      const swap = setTimeout(() => {
        idx = (idx + 1) % cycle.length;
        setFallbackText(cycle[idx]);
        setVisible(true);
      }, 300);
      return () => clearTimeout(swap);
    }, 2200);
    return () => clearInterval(timer);
  }, [status]);

  // Animate when backend status changes
  useEffect(() => {
    if (!status) return;
    setVisible(false);
    const t = setTimeout(() => setVisible(true), 120);
    return () => clearTimeout(t);
  }, [status]);

  const displayText = status || fallbackText;

  return (
    <div className="thinking-indicator">
      <div className="thinking-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
      <span className={`thinking-text${visible ? " visible" : ""}`}>
        {displayText}
      </span>
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
  const [isDragging, setIsDragging] = useState(false);
  const [widgetConfig, setWidgetConfig] = useState<any>(null);
  const [thinkingStatus, setThinkingStatus] = useState<string | null>(null);
  const [_error, setError] = useState<string | null>(null);
  const [reportedMessages, setReportedMessages] = useState<Set<string>>(
    new Set(),
  );
  const [toast, setToast] = useState<string | null>(null);
  // Dark mode state — auto-detect from host page / OS preference, allow manual override
  const [isDarkMode, setIsDarkMode] = useState(() => {
    try {
      // 1. Check if user previously made an explicit override choice
      const stored = localStorage.getItem('chatbot-dark-mode');
      if (stored !== null) return stored === 'true';
    } catch {}
    // 2. Check host page <html> or <body> for 'dark' class (Tailwind convention)
    if (document.documentElement.classList.contains('dark') || document.body.classList.contains('dark')) return true;
    // 3. Detect OS/browser preference via media query
    if (typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: dark)').matches) return true;
    return false;
  });
  // Track whether user has manually overridden (so we stop auto-syncing)
  const [darkModeOverridden, setDarkModeOverridden] = useState(() => {
    try { return localStorage.getItem('chatbot-dark-mode') !== null; } catch { return false; }
  });
  // Voice input state
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [speechLangIdx, setSpeechLangIdx] = useState(0);
  const [speechLangChosen, setSpeechLangChosen] = useState(false); // true once user picks a language this conversation
  const [showLangPicker, setShowLangPicker] = useState(false); // language picker popup visibility
  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const windowRef = useRef<HTMLDivElement>(null);
  const isAtBottomRef = useRef(true);
  const abortControllerRef = useRef<AbortController | null>(null);

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

  // Language-aware default texts
  // Support both singular 'language' (preview/config) and plural 'languages' (API response)
  const configLanguagesRaw: string[] = isPreview
    ? (config.languages || (config.language ? [config.language] : ["en"]))
    : (widgetConfig?.languages || (widgetConfig?.language ? [widgetConfig.language] : ["en"]));
  // Memoize by *content* (not reference) so downstream useMemos/effects don't re-trigger on every render
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const configLanguages = useMemo(() => configLanguagesRaw, [configLanguagesRaw.join(",")]);
  const lang = configLanguages[0] || "en";

  // Speech recognition language options — one per base language (Latn variants share base lang recognition)
  const speechLangOptions = useMemo(() => {
    const speechMap: Record<string, { code: string; label: string }> = {
      en: { code: "en-US", label: "EN" },
      hi: { code: "hi-IN", label: "हि" },
      gu: { code: "gu-IN", label: "ગુ" },
    };
    return configLanguages.filter((l) => speechMap[l]).map((l) => speechMap[l]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [configLanguages]);

  // Multi-language welcome greetings — fallback when server translations aren't available
  const welcomeGreetingsFallback: Record<string, string> = {
    en: "Hi! How can I help you today?",
    hi: "नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ?",
    gu: "નમસ્તે! હું તમને કેવી રીતે મદદ કરી શકું?",
  };

  const defaultWelcome = welcomeGreetingsFallback[lang] || welcomeGreetingsFallback.en;

  // Compute the actual welcome message (needed before greetingsArray so it can be included)
  const welcomeMessage = isPreview
    ? config.welcomeMessage || defaultWelcome
    : widgetConfig?.welcome_message || config.welcomeMessage || defaultWelcome;

  // Server-provided translations of the welcome message (keyed by lang code)
  const serverTranslations: Record<string, string> | null = isPreview
    ? config.welcomeMessageTranslations || null
    : widgetConfig?.welcome_message_translations || null;

  // Build the sequence of greetings for the typewriter animation:
  // User's configured welcome message → translated variants for each enabled language.
  // Uses real LLM translations from the server when available, otherwise falls back
  // to generic native-script greetings.
  const greetingsArray = useMemo(() => {
    const hasGu = configLanguages.includes("gu");
    const hasHi = configLanguages.includes("hi");

    // Only animate if at least one non-English language is allowed
    if (!hasGu && !hasHi) return [welcomeMessage].filter(Boolean);

    const seq: string[] = [];

    // 1. User's configured welcome message (always first)
    seq.push(welcomeMessage);

    // 2. Translated variants — prefer server translations, fall back to fixed greetings
    if (hasGu) {
      const guText = serverTranslations?.gu || welcomeGreetingsFallback.gu;
      if (welcomeMessage !== guText) seq.push(guText);
    }
    if (hasHi) {
      const hiText = serverTranslations?.hi || welcomeGreetingsFallback.hi;
      if (welcomeMessage !== hiText) seq.push(hiText);
    }

    return seq.filter(Boolean);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [configLanguages, welcomeMessage, serverTranslations]);

  const defaultPlaceholder =
    lang === "hi"
      ? "अपना संदेश लिखें..."
      : lang === "gu"
        ? "તમારો સંદેશ લખો..."
        : "Type your message...";

  // listeningText based on primary configured language
  const listeningText =
    lang === "hi"
      ? "सुन रहा हूँ..."
      : lang === "gu"
        ? "સાંભળી રહ્યું છે..."
        : "Listening...";

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
      const welcomeMsg = config.welcomeMessage || defaultWelcome;
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
            const welcomeMsg = data.welcome_message || defaultWelcome;
            const initialSugs = data.initial_suggestions || [];
            return [
              {
                id: generateId(),
                role: "assistant",
                content: welcomeMsg,
                suggestions: initialSugs,
                timestamp: new Date(),
                isWelcome: true,
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
              content: defaultWelcome,
              suggestions: [],
              timestamp: new Date(),
              isWelcome: true,
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
            content: defaultWelcome,
            suggestions: [],
            timestamp: new Date(),
            isWelcome: true,
          },
        ];
      });
    } finally {
      setIsConfigLoading(false);
    }
  };

  // Pre-fetch widget config on mount to ensure bubble appearance (color, avatar, offsets) is correct
  // This runs immediately and synchronously to prevent any flash of default colors
  const hasInitedFetch = useRef(false);
  useEffect(() => {
    if (!isPreview && chatbotId && !hasInitedFetch.current) {
      hasInitedFetch.current = true;
      // Start fetch immediately - don't delay
      fetchWidgetConfig();
    }
  }, [chatbotId, isPreview, apiUrl]);

  // Initialize Web Speech API ONCE on mount – never recreate the recognition
  // object, so ongoing recordings aren't aborted by React re-renders.
  useEffect(() => {
    const SR =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;
    if (!SR) {
      setSpeechSupported(false);
      return;
    }
    setSpeechSupported(true);
    const rec = new SR();
    rec.continuous = false;
    rec.interimResults = true;
    rec.lang = "en-US"; // initial default; updated by the lang-sync effect below

    rec.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((r: any) => r[0])
        .map((r: any) => r.transcript)
        .join("");
      setInputValue(transcript);
    };

    rec.onend = () => {
      setIsListening(false);
    };

    rec.onerror = (event: any) => {
      console.error("Speech recognition error:", event.error);
      setIsListening(false);
      if (event.error === "not-allowed") {
        setToast("Microphone access denied. Please allow microphone access.");
        setTimeout(() => setToast(null), 3000);
      }
    };

    recognitionRef.current = rec;

    return () => {
      rec.abort();
      recognitionRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // mount-only — object is reused across lang changes

  // Keep recognition.lang synced with the user-selected language index.
  // Each language has its own BCP-47 code so the Web Speech API outputs the
  // correct script (English → Latin, Gujarati → ગુજરાતી, Hindi → हिन्दी).
  useEffect(() => {
    if (recognitionRef.current && !isListening) {
      const code = speechLangOptions[speechLangIdx]?.code || "en-US";
      recognitionRef.current.lang = code;
    }
  }, [speechLangOptions, speechLangIdx, isListening]);

  // Persist dark mode preference
  useEffect(() => {
    try { localStorage.setItem('chatbot-dark-mode', String(isDarkMode)); } catch {}
  }, [isDarkMode]);

  // Auto-sync dark mode from host page (MutationObserver on <html> class)
  // and OS preference changes — only if user hasn't manually overridden
  useEffect(() => {
    if (darkModeOverridden) return; // user toggled manually, respect their choice

    // Watch for host page <html> class changes (e.g. Tailwind dark mode toggle)
    const observer = new MutationObserver(() => {
      const hostDark = document.documentElement.classList.contains('dark') || document.body.classList.contains('dark');
      setIsDarkMode(hostDark);
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });

    // Watch for OS/browser preference changes
    const mediaQuery = window.matchMedia?.('(prefers-color-scheme: dark)');
    const handleMediaChange = (e: MediaQueryListEvent) => setIsDarkMode(e.matches);
    mediaQuery?.addEventListener?.('change', handleMediaChange);

    return () => {
      observer.disconnect();
      mediaQuery?.removeEventListener?.('change', handleMediaChange);
    };
  }, [darkModeOverridden]);

  // Close language picker when clicking outside
  useEffect(() => {
    if (!showLangPicker) return;
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.chatbot-action-button-wrapper')) {
        setShowLangPicker(false);
      }
    };
    document.addEventListener('click', handleClick, true);
    return () => document.removeEventListener('click', handleClick, true);
  }, [showLangPicker]);

  // Cycle to next speech language (called separately from start/stop)
  // (kept for single-language fallback but not used in multi-language UI)

  // Start speech recognition with the currently selected language
  // Accepts an optional index override for cases where React state hasn't updated yet
  const startListening = (langIdxOverride?: number) => {
    if (!recognitionRef.current) return;
    const idx = langIdxOverride !== undefined ? langIdxOverride : speechLangIdx;
    const code = speechLangOptions[idx]?.code || "en-US";
    recognitionRef.current.lang = code;
    try {
      recognitionRef.current.start();
      setIsListening(true);
    } catch (error) {
      console.error("Failed to start speech recognition:", error);
      setIsListening(false);
    }
  };

  // Stop speech recognition
  const stopListening = () => {
    if (!recognitionRef.current) return;
    recognitionRef.current.stop();
    setIsListening(false);
  };

  // Handle mic button click — show lang picker or start/stop listening
  const handleMicClick = () => {
    if (!recognitionRef.current) return;
    if (isListening) {
      stopListening();
      return;
    }
    // If only one language or already chosen → start directly
    if (speechLangOptions.length <= 1 || speechLangChosen) {
      startListening();
    } else {
      // Show language picker popup
      setShowLangPicker(true);
    }
  };

  // Handle language selection from picker popup
  const handleLangSelect = (idx: number) => {
    setSpeechLangIdx(idx);
    setSpeechLangChosen(true);
    setShowLangPicker(false);
    // Start listening immediately with the selected index (don't rely on state)
    setTimeout(() => startListening(idx), 50);
  };

  // Show welcome message on first open (handles preview mode logic)
  useEffect(() => {
    if (isOpen && messages.length === 0 && isPreview) {
      // In preview mode, use config prop directly
      const welcomeMsg = config.welcomeMessage || defaultWelcome;
      const initialSugs = config.initialSuggestions || [];

      setMessages([
        {
          id: generateId(),
          role: "assistant",
          content: welcomeMsg,
          suggestions: initialSugs,
          timestamp: new Date(),
          isWelcome: true,
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
      processImageFile(file);
    }
  };

  const processImageFile = (file: File) => {
    // Validate file type - support all common image formats
    const validImageTypes = [
      "image/jpeg",
      "image/jpg",
      "image/png",
      "image/gif",
      "image/webp",
      "image/svg+xml",
      "image/bmp",
      "image/tiff",
    ];

    if (
      !validImageTypes.includes(file.type) &&
      !file.type.startsWith("image/")
    ) {
      // Fix #3: Show toast for unsupported file types
      const fileExt = file.name.split(".").pop()?.toUpperCase() || "file";
      setToast(
        `❌ ${fileExt} files are not supported. Please upload an image file (JPG, PNG, GIF, WebP, SVG, etc.)`,
      );
      setTimeout(() => setToast(null), 4000);
      return;
    }

    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError("Image size must be less than 10MB");
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
  };

  // Handle drag and drop
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    // Only set dragging to false when leaving the entire chatbot window
    // relatedTarget will be null when mouse leaves the window or moves to outside elements
    const relatedTarget = e.relatedTarget as HTMLElement | null;
    if (relatedTarget === null || !windowRef.current?.contains(relatedTarget)) {
      setIsDragging(false);
    }
  };

  // Handle clipboard paste — extract images from Ctrl+V
  const handlePaste = (e: React.ClipboardEvent) => {
    const items = e.clipboardData?.items;
    if (!items) return;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.startsWith("image/")) {
        e.preventDefault(); // prevent pasting the image as text
        const file = items[i].getAsFile();
        if (file) {
          processImageFile(file); // replaces any existing image (single image only)
        }
        return; // only process the first image
      }
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    // Check for file drops FIRST (higher priority - user uploading from their device)
    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type.startsWith("image/")) {
        processImageFile(file);
        return;
      }
    }

    // Check for image URL from drag (e.g., from product carousel)
    const imageUrl = e.dataTransfer?.getData("text/plain");
    if (
      imageUrl &&
      (imageUrl.startsWith("http://") || imageUrl.startsWith("https://"))
    ) {
      // Check if it's an image URL - match various patterns
      // Common image patterns: .jpg, .png, /image/, image_256, /web/image/, etc.
      const isImageUrl =
        imageUrl.match(/\.(jpg|jpeg|png|gif|webp|svg|bmp|tiff?)(\?.*)?$/i) ||
        imageUrl.includes("/image/") ||
        imageUrl.includes("/images/") ||
        imageUrl.includes("/image_") ||
        imageUrl.includes("/img/") ||
        imageUrl.includes("/media/") ||
        imageUrl.includes("/uploads/") ||
        imageUrl.includes("/product/") ||
        imageUrl.includes("/cdn/");

      if (isImageUrl) {
        console.log("Attempting to load image from URL:", imageUrl);

        // Show loading toast
        setToast("🔄 Loading image...");

        // Try using an Image element first to validate and get the image
        const img = new Image();
        img.crossOrigin = "anonymous";

        img.onload = () => {
          // Create a canvas to convert the image to blob
          const canvas = document.createElement("canvas");
          canvas.width = img.naturalWidth;
          canvas.height = img.naturalHeight;
          const ctx = canvas.getContext("2d");

          if (ctx) {
            try {
              ctx.drawImage(img, 0, 0);
              canvas.toBlob(
                (blob) => {
                  setToast(null); // Clear loading toast
                  if (blob) {
                    const file = new File([blob], "product-image.jpg", {
                      type: "image/jpeg",
                    });
                    processImageFile(file);
                  } else {
                    setToast(
                      "❌ Failed to process image. Try saving it first, then upload.",
                    );
                    setTimeout(() => setToast(null), 4000);
                  }
                },
                "image/jpeg",
                0.9,
              );
            } catch (canvasError) {
              // Canvas tainted by CORS - can't extract image data
              console.error("Canvas tainted by CORS:", canvasError);
              setToast(
                "❌ Can't load this image due to website security. Right-click → Save Image, then drag the file.",
              );
              setTimeout(() => setToast(null), 5000);
            }
          }
        };

        img.onerror = () => {
          console.error("Failed to load image with CORS");
          // Show user-friendly error - CORS prevents loading external images
          setToast(
            "❌ Can't load this image directly. Right-click the image → Save Image As, then drag the saved file here.",
          );
          setTimeout(() => setToast(null), 5000);
        };

        img.src = imageUrl;
        return;
      } else {
        // URL is not an image - show helpful feedback
        console.log("Dropped URL is not an image:", imageUrl);
        setToast(
          "💡 That's a link, not an image. To analyze a product, drag its image directly or click the 📎 to upload.",
        );
        setTimeout(() => setToast(null), 4000);
        return;
      }
    }
  };

  // Prevent browser from navigating when dropping URLs anywhere on the document
  useEffect(() => {
    const preventBrowserDrop = (e: DragEvent) => {
      // Prevent default only if we're dropping a URL that could cause navigation
      const url = e.dataTransfer?.getData("text/plain") || "";
      if (url.startsWith("http://") || url.startsWith("https://")) {
        e.preventDefault();
      }
    };

    const preventDragOver = (e: DragEvent) => {
      // Prevent dragover to allow drop
      e.preventDefault();
    };

    // Only attach when chatbot is open to avoid interfering with other page functionality
    if (isOpen) {
      document.addEventListener("drop", preventBrowserDrop);
      document.addEventListener("dragover", preventDragOver);
    }

    return () => {
      document.removeEventListener("drop", preventBrowserDrop);
      document.removeEventListener("dragover", preventDragOver);
    };
  }, [isOpen]);

  // Add Escape key handler to clear dragging state
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isDragging) {
        setIsDragging(false);
      }
    };

    if (isDragging) {
      window.addEventListener("keydown", handleKeyDown);
    }

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isDragging]);

  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const sendMessage = async (messageText?: string) => {
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

    // Stop the welcome typewriter animation on first user message
    setMessages((prev: Message[]) => {
      if (prev.length > 0 && prev[0].isWelcome) {
        const updated = [...prev];
        updated[0] = { ...updated[0], isWelcome: false, content: welcomeMessage };
        return updated;
      }
      return prev;
    });

    // If a previous stream is still running, abort it and finalize that message
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    // Finalize any in-progress assistant message
    setMessages((prev: Message[]) => {
      const newMessages = [...prev];
      const lastMsg = newMessages[newMessages.length - 1];
      if (lastMsg && lastMsg.role === "assistant" && lastMsg.isTyping) {
        lastMsg.isTyping = false;
        lastMsg.isWaitingForContent = false;
        if (!lastMsg.content) {
          lastMsg.content = "_(interrupted)_";
        }
      }
      return newMessages;
    });

    // Store image data before clearing
    const currentImagePreview = imagePreview;
    const currentSelectedImage = selectedImage;

    // Add user message to UI
    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: text || "(Image uploaded)",
      imagePreview: currentImagePreview || undefined,
      timestamp: new Date(),
    };
    setMessages((prev: Message[]) => [...prev, userMessage]);
    if (!messageText) setInputValue("");

    // Fix #5: Clear image selection immediately after adding user message
    removeImage();

    setIsTyping(true);
    setThinkingStatus(null);
    setError(null);

    // Fix #1: Scroll to bottom immediately when user sends message
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 50);

    // Create placeholder assistant message for streaming
    const assistantMessageId = generateId();
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: "assistant",
      content: "",
      isTyping: true,
      isWaitingForContent: true, // Fix #3: Show skeleton while waiting for first content
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
      if (isPreview) {
        formData.append("is_preview", "true");
      }

      // Compress and add image if selected (use stored reference since state is cleared)
      if (currentSelectedImage) {
        try {
          const compressedBlob = await compressImage(
            currentSelectedImage,
            1024,
          );
          formData.append("image", compressedBlob, "image.jpg");
        } catch (err) {
          console.error("Image compression failed:", err);
          formData.append("image", currentSelectedImage);
        }
      }

      // Use streaming endpoint
      const controller = new AbortController();
      abortControllerRef.current = controller;
      const response = await fetch(
        `${apiUrl}/api/v1/chat/${chatbotId}/message/stream`,
        {
          method: "POST",
          body: formData,
          signal: controller.signal,
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
      let streamErrorMessage: string | null = null;

      // Fix #3: Track if we're still waiting for first content
      let hasReceivedFirstContent = false;

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

      // Fix #2: Markdown tag buffering - collect content until tag is complete
      let tagBuffer = "";
      const INCOMPLETE_TAG_REGEX = /<[^>]*$/; // Matches incomplete HTML tags at end
      const COMPLETE_TAG_PAIRS = [
        { open: /<strong>/, close: /<\/strong>/ },
        { open: /<em>/, close: /<\/em>/ },
        { open: /<ul>/, close: /<\/ul>/ },
        { open: /<ol>/, close: /<\/ol>/ },
        { open: /<li>/, close: /<\/li>/ },
        { open: /<p>/, close: /<\/p>/ },
        { open: /<br\s*\/?>/, close: null }, // Self-closing
      ];

      // Sentence detection regex
      const SENTENCE_END_REGEX =
        /[.!?]\s+|<br\s*\/?>\s*|<\/p>\s*|<\/li>\s*|\n\n/;

      // Stage B: Character-by-character renderer with consistent speed
      // Fix #2: Enhanced with markdown tag buffering to prevent showing raw tags
      const renderCharacters = async (text: string) => {
        if (isRendering) return;
        isRendering = true;

        // Minimum latency before first character
        if (!firstCharShown) {
          await new Promise((r) => setTimeout(r, FIRST_CHAR_DELAY_MS));
          firstCharShown = true;

          // Fix #3: Mark that we have content now (hide skeleton)
          hasReceivedFirstContent = true;
          setMessages((prev: Message[]) => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage && lastMessage.id === assistantMessageId) {
              lastMessage.isWaitingForContent = false;
            }
            return newMessages;
          });
        }

        // Fix #2: Combine with any buffered incomplete tags
        let fullText = tagBuffer + text;
        tagBuffer = "";

        // Check for incomplete HTML tags at the end
        const incompleteMatch = fullText.match(INCOMPLETE_TAG_REGEX);
        if (incompleteMatch) {
          // Buffer the incomplete tag for next chunk
          tagBuffer = incompleteMatch[0];
          fullText = fullText.slice(0, -tagBuffer.length);
        }

        // Also buffer if we're in the middle of a tag (between < and >)
        // This handles cases where tags come character by character
        let safeToRender = "";
        let pendingTagContent = "";
        let inTag = false;

        for (let i = 0; i < fullText.length; i++) {
          const char = fullText[i];
          if (char === "<") {
            inTag = true;
            pendingTagContent += char;
          } else if (char === ">" && inTag) {
            inTag = false;
            pendingTagContent += char;
            // Complete tag found - render it all at once
            safeToRender += pendingTagContent;
            pendingTagContent = "";
          } else if (inTag) {
            pendingTagContent += char;
          } else {
            safeToRender += char;
          }
        }

        // If we ended inside a tag, buffer it
        if (pendingTagContent) {
          tagBuffer = pendingTagContent + tagBuffer;
        }

        // Render the safe content character by character
        // But render complete HTML tags instantly
        let i = 0;
        while (i < safeToRender.length) {
          // Check if we're at the start of an HTML tag
          if (safeToRender[i] === "<") {
            // Find the end of this tag and render it all at once
            const tagEnd = safeToRender.indexOf(">", i);
            if (tagEnd !== -1) {
              const fullTag = safeToRender.slice(i, tagEnd + 1);
              displayedContent += fullTag;
              i = tagEnd + 1;

              setMessages((prev: Message[]) => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                if (lastMessage && lastMessage.id === assistantMessageId) {
                  lastMessage.content = displayedContent;
                }
                return newMessages;
              });
              continue;
            }
          }

          const char = safeToRender[i];
          displayedContent += char;
          i++;

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

      const processSseLine = (line: string): "continue" | "break" => {
        if (!line.startsWith("data: ")) {
          return "continue";
        }
        const data = line.slice(6).trim();
        if (!data) {
          return "continue";
        }
        try {
          const chunk = JSON.parse(data);

          if (chunk.type === "session") {
            // Update session ID
            streamSessionId = chunk.session_id;
            setSessionId(chunk.session_id);
          } else if (chunk.type === "status") {
            // Backend is reporting its current processing stage
            setThinkingStatus(chunk.status || null);
          } else if (chunk.type === "content") {
            // First content arrives — clear thinking status
            setThinkingStatus(null);
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
                if (lastMessage && lastMessage.id === assistantMessageId) {
                  lastMessage.isTyping = false;
                  lastMessage.suggestions = finalSuggestions;
                  lastMessage.products = finalProducts;
                }
                return newMessages;
              });
            };
            finishAllRendering();
          } else if (chunk.type === "error") {
            streamErrorMessage = sanitizeAssistantErrorMessage(
              chunk.error || "Stream error",
            );
            return "break";
          }
        } catch (parseError) {
          console.error("Failed to parse SSE chunk:", parseError);
        }

        return "continue";
      };

      if (reader) {
        streamLoop: while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          // Decode chunk and add to buffer
          buffer += decoder.decode(value, { stream: true });

          // Process complete SSE messages
          const lines = buffer.split("\n");
          buffer = lines.pop() || ""; // Keep incomplete line in buffer

          for (const line of lines) {
            const action = processSseLine(line);
            if (action === "break") {
              break streamLoop;
            }
          }
        }

        // Process any trailing buffer line to avoid missing a final error/done chunk
        if (buffer.trim()) {
          const action = processSseLine(buffer.trim());
          if (action === "break") {
            streamErrorMessage = streamErrorMessage || USER_SAFE_RESPONSE_ERROR;
          }
        }
      } else {
        streamErrorMessage = USER_SAFE_RESPONSE_ERROR;
      }

      if (streamErrorMessage) {
        throw new Error(streamErrorMessage);
      }

      // If stream ended without explicit done/error, fail gracefully and stop loader.
      if (!streamEnded) {
        throw new Error(USER_SAFE_RESPONSE_ERROR);
      }

      abortControllerRef.current = null;
      setIsTyping(false);
      // Image already cleared at start of sendMessage
    } catch (err: any) {
      // If the request was aborted (user sent a new message), don't show error
      if (err?.name === "AbortError") {
        return;
      }
      console.error("Failed to send message:", err);
      abortControllerRef.current = null;
      setIsTyping(false);
      // Image already cleared at start of sendMessage

      // Update assistant message with error
      const userSafeError = sanitizeAssistantErrorMessage(err?.message);
      setMessages((prev: Message[]) => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.id === assistantMessageId) {
          lastMessage.content = userSafeError;
          lastMessage.isTyping = false;
          lastMessage.isWaitingForContent = false;
          lastMessage.suggestions = [];
          lastMessage.products = [];
        }
        return newMessages;
      });
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    // Allow sending even while typing - previous stream will be aborted
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
          isWelcome: true,
        },
      ]);
      setSessionId(null);
      removeImage();
      setSpeechLangChosen(false);
      setShowLangPicker(false);
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
        // Hide while loading config in production to prevent "flash" of default settings
        // Show immediately in preview mode or when config is loaded
        opacity: isConfigLoading ? 0 : 1,
        pointerEvents: isConfigLoading ? "none" : "auto",
        transition: "opacity 0.2s ease-in-out",
      }}
    >
      {isOpen ? (
        <div
          ref={windowRef}
          className={`chatbot-window${isDarkMode ? " dark" : ""}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {/* Fix #2: Drag overlay at window level for full coverage */}
          {isDragging && (
            <div className="chatbot-drag-overlay-fullscreen">
              <div className="chatbot-drag-overlay-content">
                <svg
                  width="64"
                  height="64"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  className="chatbot-drag-icon"
                >
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
                <p className="chatbot-drag-text">Drop your image here</p>
                <p className="chatbot-drag-subtext">We'll analyze it for you</p>
              </div>
            </div>
          )}
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
              {/* Dark mode toggle */}
              <button
                type="button"
                onClick={() => {
                  setIsDarkMode((prev) => !prev);
                  setDarkModeOverridden(true);
                }}
                title={isDarkMode ? "Light mode" : "Dark mode"}
                className="chatbot-header-button"
              >
                {isDarkMode ? (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="5" />
                    <line x1="12" y1="1" x2="12" y2="3" />
                    <line x1="12" y1="21" x2="12" y2="23" />
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                    <line x1="1" y1="12" x2="3" y2="12" />
                    <line x1="21" y1="12" x2="23" y2="12" />
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                  </svg>
                ) : (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                  </svg>
                )}
              </button>
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
                      {/* Contextual thinking animation while waiting for response */}
                      {msg.isWaitingForContent ? (
                        <ThinkingIndicator status={thinkingStatus} />
                      ) : msg.isWelcome && greetingsArray.length > 1 ? (
                        <div className="chatbot-message-text">
                          <WelcomeTypewriter
                            key={welcomeMessage}
                            greetings={greetingsArray}
                            staticContent={welcomeMessage}
                          />
                        </div>
                      ) : (
                        <div
                          className="chatbot-message-text"
                          dangerouslySetInnerHTML={{
                            __html: renderMessageContent(
                              msg.content,
                              msg.isTyping && !msg.isWaitingForContent,
                            ),
                          }}
                        />
                      )}
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
          <div
            className={`chatbot-input-area ${isDragging ? "drag-active" : ""}`}
          >
            {/* Image Preview — compact thumbnail with top-left remove button */}
            {imagePreview && (
              <div className="chatbot-image-preview">
                <div className="chatbot-image-preview-thumb">
                  <img
                    src={imagePreview}
                    alt="Selected"
                    className="chatbot-image-preview-img"
                  />
                  <button
                    type="button"
                    onClick={removeImage}
                    className="chatbot-image-preview-remove"
                    title="Remove image"
                  >
                    <svg
                      width="10"
                      height="10"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                    >
                      <path d="M18 6L6 18M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            )}

            <div className="chatbot-input-row">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/gif,image/webp,image/svg+xml,image/bmp,image/tiff,image/*"
                onChange={handleImageSelect}
                className="chatbot-file-input"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={!isPreview && widgetConfig?.is_paused}
                className="chatbot-image-button chatbot-image-button-sm"
                title="Upload image"
              >
                <svg
                  width="14"
                  height="14"
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
                  isListening
                    ? listeningText
                    : !isPreview && widgetConfig?.is_paused
                      ? "Chat is temporarily unavailable"
                      : defaultPlaceholder
                }
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                onPaste={handlePaste}
                disabled={!isPreview && widgetConfig?.is_paused}
              />
              {/* Unified action button: Send / Mic / Stop — based on current state */}
              <div className="chatbot-action-button-wrapper">
                {/* Language picker popup — shown above the action button */}
                {showLangPicker && (
                  <div className="chatbot-lang-picker">
                    <div className="chatbot-lang-picker-title">Select language</div>
                    {speechLangOptions.map((opt, idx) => (
                      <button
                        key={opt.code}
                        type="button"
                        className="chatbot-lang-picker-option"
                        onClick={() => handleLangSelect(idx)}
                      >
                        <span className="chatbot-lang-picker-label">{opt.label}</span>
                        <span className="chatbot-lang-picker-code">{opt.code}</span>
                      </button>
                    ))}
                  </div>
                )}
                {inputValue.trim() || selectedImage ? (
                  /* SEND button — when there is text or image */
                  <button
                    type="button"
                    disabled={!isPreview && widgetConfig?.is_paused}
                    onClick={() => sendMessage()}
                    className="chatbot-send-button"
                    style={{ backgroundColor: primaryColor }}
                    title="Send message"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
                    </svg>
                  </button>
                ) : isListening ? (
                  /* STOP button — while listening */
                  <button
                    type="button"
                    onClick={handleMicClick}
                    className="chatbot-send-button chatbot-stop-button"
                    title="Stop listening"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="6" y="6" width="12" height="12" rx="1" />
                    </svg>
                  </button>
                ) : speechSupported ? (
                  /* MIC button — when textbox is empty and not listening */
                  <button
                    type="button"
                    onClick={handleMicClick}
                    disabled={!isPreview && widgetConfig?.is_paused}
                    className="chatbot-send-button chatbot-mic-button"
                    style={{ backgroundColor: primaryColor }}
                    title="Voice input"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                      <line x1="12" y1="19" x2="12" y2="23" />
                      <line x1="8" y1="23" x2="16" y2="23" />
                    </svg>
                  </button>
                ) : (
                  /* Fallback SEND button — when no speech support */
                  <button
                    type="button"
                    disabled
                    className="chatbot-send-button"
                    style={{ backgroundColor: primaryColor }}
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
                    </svg>
                  </button>
                )}
              </div>
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
