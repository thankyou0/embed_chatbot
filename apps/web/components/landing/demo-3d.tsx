"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

/* ═══════════════════════════ Demo conversations ═══════════════════════════ */

interface Product {
  name: string;
  price: string;
  image?: string;
}

interface Message {
  role: "user" | "bot";
  text: string;
  products?: Product[];
  suggestions?: string[];
}

interface DemoConvo {
  question: string;
  tag: string;
  color: "emerald" | "teal" | "cyan";
  messages: Message[];
}

const demoConversations: DemoConvo[] = [
  {
    question: "Hi there! What can you help me with?",
    tag: "👋 Greeting",
    color: "emerald",
    messages: [
      { role: "bot", text: "Hi! Welcome to TechStore 👋 I'm your AI shopping assistant. I can help you find products, answer questions about our store, check pricing, and much more!" },
      { role: "user", text: "Hi there! What can you help me with?" },
      {
        role: "bot",
        text: "I can help you with:\n• **Browse & search** our product catalog\n• **Compare** products and find the best deals\n• **Check availability** and shipping info\n• **Answer questions** about our policies",
        suggestions: ["Show me your best sellers", "What's your return policy?", "Do you offer free shipping?"],
      },
    ],
  },
  {
    question: "What are your shipping options?",
    tag: "📦 Non-Product",
    color: "teal",
    messages: [
      { role: "bot", text: "Hi! Welcome to TechStore 👋 How can I help you today?" },
      { role: "user", text: "What are your shipping options?" },
      {
        role: "bot",
        text: "We offer several shipping options:\n\n**Standard Shipping** — Free on orders over ₹999, 5-7 business days\n**Express Shipping** — ₹149, 2-3 business days\n**Same Day Delivery** — ₹299, available in select cities\n\nAll orders include tracking and insurance.",
        suggestions: ["Which cities have same-day delivery?", "How do I track my order?", "What's your return policy?"],
      },
    ],
  },
  {
    question: "Show me wireless headphones under ₹5000",
    tag: "🎧 Product",
    color: "cyan",
    messages: [
      { role: "bot", text: "Hi! Welcome to TechStore 👋 How can I help you today?" },
      { role: "user", text: "Show me wireless headphones under ₹5000" },
      {
        role: "bot",
        text: "Here are our best wireless headphones under ₹5,000:",
        products: [
          { name: "SoundMax Pro Wireless", price: "₹3,499" },
          { name: "BassBoost ANC 200", price: "₹4,299" },
          { name: "FlexBuds Ultra Lite", price: "₹2,999" },
          { name: "ZenAudio Studio X", price: "₹4,799" },
        ],
        suggestions: ["Compare top 2 options", "Which has best battery life?", "Any ongoing offers?"],
      },
    ],
  },
];

const colorClasses: Record<string, { border: string; bg: string; text: string }> = {
  emerald: { border: "border-emerald-500/30", bg: "bg-emerald-500/10", text: "text-emerald-400" },
  teal:    { border: "border-teal-500/30",    bg: "bg-teal-500/10",    text: "text-teal-400" },
  cyan:    { border: "border-cyan-500/30",     bg: "bg-cyan-500/10",    text: "text-cyan-400" },
};

/* ═══════════════════════════ Widget mockup ═══════════════════════════ */

function WidgetMockup({ messages, isTyping }: { messages: Message[]; isTyping: boolean }) {
  const PRIMARY = "#2563eb";

  return (
    <div
      className="w-[350px] h-[500px] rounded-lg overflow-hidden flex flex-col"
      style={{
        border: "1px solid #e5e7eb",
        boxShadow: "0 25px 50px -12px rgba(0,0,0,0.25)",
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        fontSize: "14px",
        background: "#ffffff",
        color: "#1f2937",
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-3 py-3 flex-shrink-0"
        style={{ backgroundColor: PRIMARY, color: "white" }}
      >
        <div className="flex items-center gap-2">
          {/* Avatar placeholder */}
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center"
            style={{ background: "rgba(255,255,255,0.2)" }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <div>
            <div className="text-sm font-semibold leading-tight">TechStore Assistant</div>
            <div className="flex items-center gap-1">
              <div className="w-1.5 h-1.5 rounded-full" style={{ background: "#4ade80" }} />
              <span className="text-[10px]" style={{ opacity: 0.9 }}>Online</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {/* Dark mode toggle */}
          <button className="p-1 rounded" style={{ background: "rgba(255,255,255,0)" }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          </button>
          {/* Minimize */}
          <button className="p-1 rounded" style={{ background: "rgba(255,255,255,0)" }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3" />
            </svg>
          </button>
          {/* Close */}
          <button className="p-1 rounded" style={{ background: "rgba(255,255,255,0)" }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages area */}
      <div
        className="flex-1 overflow-y-auto px-4 py-4"
        style={{ background: "rgba(249,250,251,0.5)" }}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={messages.map((m) => m.text).join("|")}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-4"
          >
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.15, duration: 0.3 }}
              >
                {msg.role === "user" ? (
                  /* User message */
                  <div className="flex justify-end">
                    <div
                      className="rounded-lg px-3 py-2 max-w-[90%]"
                      style={{
                        background: PRIMARY,
                        color: "white",
                        fontSize: "12px",
                        lineHeight: "1.625",
                        boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
                      }}
                    >
                      {msg.text}
                    </div>
                  </div>
                ) : (
                  /* Bot message */
                  <div>
                    <div className="flex items-end gap-2">
                      {/* Bot avatar */}
                      <div
                        className="w-6 h-6 rounded-full flex-shrink-0 flex items-center justify-center"
                        style={{ background: "#e5e7eb" }}
                      >
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                        </svg>
                      </div>
                      <div
                        className="rounded-lg px-3 py-2 max-w-[90%]"
                        style={{
                          background: "white",
                          border: "1px solid #e5e7eb",
                          fontSize: "12px",
                          lineHeight: "1.625",
                          boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
                        }}
                      >
                        {/* Render text with basic markdown-like formatting */}
                        {msg.text.split("\n").map((line, li) => (
                          <div key={li} className={li > 0 ? "mt-1" : ""}>
                            {line.startsWith("•") || line.startsWith("**") ? (
                              <span
                                dangerouslySetInnerHTML={{
                                  __html: line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"),
                                }}
                              />
                            ) : (
                              <span
                                dangerouslySetInnerHTML={{
                                  __html: line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"),
                                }}
                              />
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Product carousel */}
                    {msg.products && msg.products.length > 0 && (
                      <div className="mt-2 ml-8" style={{ width: "calc(100% - 32px)" }}>
                        <div className="flex gap-2 overflow-x-auto" style={{ scrollSnapType: "x mandatory" }}>
                          {msg.products.map((product, pi) => (
                            <motion.div
                              key={pi}
                              initial={{ opacity: 0, x: 20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: 0.4 + pi * 0.1 }}
                              className="flex-shrink-0 rounded-lg overflow-hidden"
                              style={{
                                width: "140px",
                                background: "white",
                                border: "1px solid #e5e7eb",
                                boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
                                scrollSnapAlign: "start",
                              }}
                            >
                              {/* Product image placeholder */}
                              <div
                                className="flex items-center justify-center"
                                style={{ width: "100%", height: "80px", background: "#f3f4f6" }}
                              >
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                                  <circle cx="8.5" cy="8.5" r="1.5" />
                                  <path d="M21 15l-5-5L5 21" />
                                </svg>
                              </div>
                              {/* Product info */}
                              <div className="p-2">
                                <div
                                  className="font-semibold"
                                  style={{
                                    fontSize: "11px",
                                    color: "#1f2937",
                                    lineHeight: "1.3",
                                    display: "-webkit-box",
                                    WebkitLineClamp: 2,
                                    WebkitBoxOrient: "vertical",
                                    overflow: "hidden",
                                  }}
                                >
                                  {product.name}
                                </div>
                                <div style={{ fontSize: "12px", fontWeight: 700, color: "#059669", marginTop: "2px" }}>
                                  {product.price}
                                </div>
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Suggestions */}
                    {msg.suggestions && msg.suggestions.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2 ml-8">
                        {msg.suggestions.map((suggestion, si) => (
                          <motion.span
                            key={si}
                            initial={{ opacity: 0, y: 5 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.5 + si * 0.08 }}
                            className="rounded-full cursor-pointer"
                            style={{
                              padding: "4px 12px",
                              background: "white",
                              border: "1px solid #e5e7eb",
                              fontSize: "10px",
                              fontWeight: 500,
                              color: "#4b5563",
                              boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
                            }}
                          >
                            {suggestion}
                          </motion.span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </motion.div>
            ))}

            {/* Typing indicator */}
            {isTyping && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-end gap-2"
              >
                <div
                  className="w-6 h-6 rounded-full flex-shrink-0 flex items-center justify-center"
                  style={{ background: "#e5e7eb" }}
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                </div>
                <div
                  className="rounded-lg px-3 py-3 flex gap-1"
                  style={{ background: "rgba(37,99,235,0.06)", border: "1px solid rgba(37,99,235,0.08)" }}
                >
                  {[0, 1, 2].map((d) => (
                    <motion.div
                      key={d}
                      className="w-1.5 h-1.5 rounded-full"
                      style={{ background: "#9ca3af" }}
                      animate={{ scale: [1, 1.4, 1] }}
                      transition={{ duration: 1.4, repeat: Infinity, delay: d * 0.2 }}
                    />
                  ))}
                </div>
              </motion.div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Input area */}
      <div
        className="flex-shrink-0 px-3 py-3"
        style={{ background: "white", borderTop: "1px solid #f3f4f6" }}
      >
        <div className="flex items-center gap-2">
          {/* Image button */}
          <div
            className="flex items-center justify-center flex-shrink-0 rounded-md"
            style={{ width: "30px", height: "30px", background: "white", border: "1px solid #e5e7eb" }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4b5563" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <path d="M21 15l-5-5L5 21" />
            </svg>
          </div>
          {/* Input */}
          <div
            className="flex-1 rounded-md px-3"
            style={{
              height: "36px",
              border: "1px solid #e5e7eb",
              display: "flex",
              alignItems: "center",
              fontSize: "12px",
              color: "#9ca3af",
            }}
          >
            Type your message...
          </div>
          {/* Send button */}
          <div
            className="flex items-center justify-center flex-shrink-0 rounded-md"
            style={{
              width: "36px",
              height: "36px",
              background: PRIMARY,
              color: "white",
              boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
            }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
            </svg>
          </div>
        </div>
        {/* Branding */}
        <div className="text-center mt-2" style={{ fontSize: "10px", color: "#9ca3af", fontWeight: 500 }}>
          Powered by EmbedChat
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════ Main section ═══════════════════════════ */

export default function Demo3D() {
  const [activeConvo, setActiveConvo] = useState(0);
  const [isTyping, setIsTyping] = useState(false);
  const autoPlayRef = useRef<ReturnType<typeof setInterval>>();

  const startAutoPlay = useCallback(() => {
    if (autoPlayRef.current) clearInterval(autoPlayRef.current);
    autoPlayRef.current = setInterval(() => {
      setIsTyping(true);
      setTimeout(() => {
        setActiveConvo((prev) => (prev + 1) % demoConversations.length);
        setIsTyping(false);
      }, 800);
    }, 6000);
  }, []);

  useEffect(() => {
    startAutoPlay();
    return () => {
      if (autoPlayRef.current) clearInterval(autoPlayRef.current);
    };
  }, [startAutoPlay]);

  const handleClick = (idx: number) => {
    setIsTyping(true);
    setTimeout(() => {
      setActiveConvo(idx);
      setIsTyping(false);
    }, 600);
    startAutoPlay();
  };

  const convo = demoConversations[activeConvo];

  return (
    <section
      id="demo"
      className="relative py-24 md:py-36 overflow-hidden"
      style={{ background: "linear-gradient(180deg, #0a0a0f 0%, #0f0f1a 50%, #0a0a0f 100%)" }}
    >
      {/* Header */}
      <div className="relative z-10 max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8 mb-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-teal-500/10 border border-teal-500/20 text-sm text-teal-400 mb-4">
            ✨ Interactive Demo
          </span>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4">
            See It in{" "}
            <span className="bg-gradient-to-r from-teal-400 via-cyan-400 to-blue-400 bg-clip-text text-transparent">
              Action
            </span>
          </h2>
          <p className="text-lg text-white/50 max-w-2xl mx-auto">
            Click a question below and watch the AI respond in real time.
          </p>
        </motion.div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Question selector pills */}
        <div className="flex flex-wrap justify-center gap-3 mb-10 relative z-10">
          {demoConversations.map((q, i) => {
            const c = colorClasses[q.color];
            const isActive = activeConvo === i;
            return (
              <motion.button
                key={i}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => handleClick(i)}
                className={`
                  relative px-5 py-3 rounded-xl border transition-all duration-300
                  ${isActive
                    ? `${c.border} ${c.bg} shadow-lg`
                    : "border-white/10 bg-white/[0.02] hover:bg-white/[0.04]"
                  }
                `}
              >
                <span className="text-xs text-white/30 block mb-0.5">{q.tag}</span>
                <span className={`text-sm font-medium ${isActive ? c.text : "text-white/60"}`}>
                  {q.question}
                </span>
                {isActive && (
                  <motion.div
                    layoutId="demoActiveIndicator"
                    className="absolute -bottom-0.5 left-4 right-4 h-0.5 rounded-full"
                    style={{
                      background: i === 0 ? "#10b981" : i === 1 ? "#14b8a6" : "#06b6d4",
                    }}
                  />
                )}
              </motion.button>
            );
          })}
        </div>

        {/* Laptop / Website mockup */}
        <motion.div
          className="relative max-w-4xl mx-auto"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          {/* Glow behind the laptop */}
          <div
            className="absolute -inset-8 rounded-3xl opacity-20 blur-2xl pointer-events-none"
            style={{ background: "radial-gradient(ellipse at center, #2563eb15, transparent 70%)" }}
          />

          {/* Browser window */}
          <div className="relative bg-[#0c0c18] border border-white/[0.08] rounded-2xl overflow-hidden shadow-2xl">
            {/* Browser chrome */}
            <div className="flex items-center gap-2 px-4 py-2.5 border-b border-white/5 bg-white/[0.02]">
              <div className="flex gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
                <div className="w-2.5 h-2.5 rounded-full bg-amber-500/50" />
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/50" />
              </div>
              <div className="flex-1 flex justify-center">
                <div className="px-4 py-0.5 rounded-md bg-white/[0.04] text-[11px] text-white/20 font-mono">
                  www.techstore.com
                </div>
              </div>
            </div>

            {/* Website content area */}
            <div className="relative flex" style={{ minHeight: "540px" }}>
              {/* Fake website background */}
              <div className="flex-1 p-6 sm:p-8">
                {/* Nav mock */}
                <div className="flex items-center justify-between mb-8">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded bg-blue-500/30" />
                    <span className="text-white/30 text-sm font-semibold">TechStore</span>
                  </div>
                  <div className="hidden sm:flex items-center gap-4">
                    {["Products", "Deals", "Support"].map((n) => (
                      <span key={n} className="text-white/15 text-xs">{n}</span>
                    ))}
                  </div>
                </div>

                {/* Hero area mock */}
                <div className="mb-6">
                  <div className="h-3 w-48 bg-white/[0.06] rounded mb-2" />
                  <div className="h-2 w-64 bg-white/[0.03] rounded mb-1" />
                  <div className="h-2 w-56 bg-white/[0.03] rounded" />
                </div>

                {/* Product grid mock */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 max-w-md">
                  {[...Array(6)].map((_, i) => (
                    <div
                      key={i}
                      className="rounded-lg overflow-hidden"
                      style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.04)" }}
                    >
                      <div className="aspect-square bg-white/[0.02] flex items-center justify-center">
                        <div className="w-6 h-6 rounded bg-white/[0.04]" />
                      </div>
                      <div className="p-2">
                        <div className="h-1.5 w-full bg-white/[0.04] rounded mb-1" />
                        <div className="h-1.5 w-10 bg-white/[0.06] rounded" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Chat widget positioned bottom-right */}
              <div className="absolute bottom-4 right-4 z-20">
                <WidgetMockup
                  messages={convo.messages}
                  isTyping={isTyping}
                />
              </div>
            </div>
          </div>

          {/* Floating particles */}
          {[...Array(4)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 rounded-full bg-blue-500"
              style={{
                top: `${20 + i * 20}%`,
                left: i % 2 === 0 ? "-1%" : "101%",
                opacity: 0.2,
              }}
              animate={{ y: [0, -8, 0], opacity: [0.1, 0.3, 0.1] }}
              transition={{
                duration: 2.5 + i * 0.5,
                repeat: Infinity,
                ease: "easeInOut",
                delay: i * 0.4,
              }}
            />
          ))}
        </motion.div>

        {/* Bottom hint */}
        <div className="text-center mt-8">
          <AnimatePresence mode="wait">
            <motion.p
              key={activeConvo}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-sm text-white/30"
            >
              Showing: <span className="text-white/50 font-medium">{convo.tag}</span> — {
                activeConvo === 0 ? "Greeting & capabilities overview" :
                activeConvo === 1 ? "Non-product info query" :
                "Product search with carousel results"
              }
            </motion.p>
          </AnimatePresence>
        </div>
      </div>

      {/* Ambient glows */}
      <div className="absolute top-1/3 left-1/3 w-96 h-96 bg-blue-500/[0.02] rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-cyan-500/[0.02] rounded-full blur-[100px] pointer-events-none" />
    </section>
  );
}
