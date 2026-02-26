"use client";

import { useRef, useState, useCallback } from "react";
import {
  motion,
  useInView,
  useMotionValue,
  useSpring,
  useTransform,
  AnimatePresence,
} from "framer-motion";
import { Send, ArrowRight, MessageSquare } from "lucide-react";

const demoConversations = [
  {
    question: "What are your pricing plans?",
    answer:
      "We offer three plans: Free (1 chatbot, 50 messages/mo), Pro ($29/mo, 5 chatbots, unlimited messages), and Enterprise (custom pricing, unlimited everything). All plans include analytics and customization.",
  },
  {
    question: "How do I embed the chatbot?",
    answer:
      'Simply copy the script tag from your dashboard and paste it before the closing </body> tag on your website. It works with any platform — WordPress, Shopify, React, or plain HTML. It\'s literally one line of code!',
  },
  {
    question: "What data sources can I use?",
    answer:
      "You can train your chatbot using: website crawling (we'll scrape your pages), PDF/document uploads, manual Q&A pairs, and raw text input. All sources are processed and indexed automatically.",
  },
];

/* ── 3D tilt wrapper for the chat window ── */
function TiltChatWindow({ children }: { children: React.ReactNode }) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotateX = useSpring(useTransform(y, [-0.5, 0.5], [4, -4]), {
    stiffness: 200,
    damping: 20,
  });
  const rotateY = useSpring(useTransform(x, [-0.5, 0.5], [-4, 4]), {
    stiffness: 200,
    damping: 20,
  });

  const onMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      const rect = e.currentTarget.getBoundingClientRect();
      x.set((e.clientX - rect.left) / rect.width - 0.5);
      y.set((e.clientY - rect.top) / rect.height - 0.5);
    },
    [x, y]
  );

  const onLeave = useCallback(() => {
    x.set(0);
    y.set(0);
  }, [x, y]);

  return (
    <div className="perspective-1000">
      <motion.div
        style={{ rotateX, rotateY }}
        className="preserve-3d"
        onMouseMove={onMove}
        onMouseLeave={onLeave}
      >
        {children}
      </motion.div>
    </div>
  );
}

/* ── Typing dots animation ── */
function TypingDots() {
  return (
    <div className="flex gap-2.5">
      <div className="w-7 h-7 rounded-full bg-emerald-500/20 flex-shrink-0 flex items-center justify-center text-xs">
        <MessageSquare className="w-3.5 h-3.5 text-emerald-400" />
      </div>
      <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-white/5 flex items-center gap-1">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            animate={{ opacity: [0.3, 1, 0.3], y: [0, -3, 0] }}
            transition={{
              duration: 0.8,
              repeat: Infinity,
              delay: i * 0.15,
            }}
            className="w-1.5 h-1.5 rounded-full bg-emerald-400/60"
          />
        ))}
      </div>
    </div>
  );
}

export function DemoSection() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });
  const [activeDemo, setActiveDemo] = useState(0);
  const [phase, setPhase] = useState<"answer" | "typing" | "hidden">("answer");

  const handleDemoClick = (index: number) => {
    if (index === activeDemo) return;
    setPhase("hidden");
    setTimeout(() => {
      setActiveDemo(index);
      setPhase("typing");
    }, 200);
    setTimeout(() => {
      setPhase("answer");
    }, 1000);
  };

  return (
    <section id="demo" ref={ref} className="relative py-24 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <p className="text-sm font-medium text-emerald-400 tracking-wider uppercase mb-3">
            Live Demo
          </p>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            See It{" "}
            <span className="bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
              in Action
            </span>
          </h2>
          <p className="text-lg text-white/40 max-w-2xl mx-auto">
            Ask a question and see how the chatbot responds with context-aware,
            accurate answers from your knowledge base.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="max-w-4xl mx-auto"
        >
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
            {/* Questions sidebar */}
            <div className="lg:col-span-2 space-y-3">
              <p className="text-xs text-white/30 uppercase tracking-wider mb-4 font-medium">
                Try a question
              </p>
              {demoConversations.map((conv, i) => (
                <motion.button
                  key={i}
                  onClick={() => handleDemoClick(i)}
                  whileHover={{ x: 4 }}
                  whileTap={{ scale: 0.98 }}
                  className={`w-full text-left p-4 rounded-xl border transition-all duration-300 ${
                    activeDemo === i
                      ? "border-emerald-500/40 bg-emerald-500/10 text-white shadow-lg shadow-emerald-500/5"
                      : "border-white/5 bg-white/[0.02] text-white/50 hover:text-white/70 hover:bg-white/[0.04] hover:border-white/10"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <Send
                      className={`w-4 h-4 mt-0.5 flex-shrink-0 transition-colors ${
                        activeDemo === i ? "text-emerald-400" : "text-white/20"
                      }`}
                    />
                    <span className="text-sm leading-relaxed">
                      {conv.question}
                    </span>
                  </div>
                </motion.button>
              ))}
            </div>

            {/* Chat window with 3D tilt */}
            <div className="lg:col-span-3">
              <TiltChatWindow>
                <div className="rounded-2xl border border-white/10 bg-[#111118] overflow-hidden shadow-2xl shadow-emerald-500/5">
                  {/* Chat header */}
                  <div className="px-5 py-3.5 bg-gradient-to-r from-emerald-600 to-teal-600 flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                      <MessageSquare className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-white">
                        EmbedChat Demo
                      </div>
                      <div className="text-[10px] text-white/70 flex items-center gap-1">
                        <motion.span
                          animate={{ scale: [1, 1.3, 1] }}
                          transition={{ duration: 2, repeat: Infinity }}
                          className="w-1.5 h-1.5 bg-green-400 rounded-full inline-block"
                        />
                        Powered by your knowledge base
                      </div>
                    </div>
                  </div>

                  {/* Messages */}
                  <div className="p-5 space-y-4 min-h-[280px]">
                    {/* Bot welcome */}
                    <div className="flex gap-2.5">
                      <div className="w-7 h-7 rounded-full bg-emerald-500/20 flex-shrink-0 flex items-center justify-center text-xs">
                        <MessageSquare className="w-3.5 h-3.5 text-emerald-400" />
                      </div>
                      <div className="px-4 py-2.5 rounded-2xl rounded-tl-sm bg-white/5 text-sm text-white/70 max-w-[80%]">
                        Hi! I&apos;m trained on your knowledge base. Ask me anything!
                      </div>
                    </div>

                    {/* User question */}
                    <AnimatePresence mode="wait">
                      <motion.div
                        key={`q-${activeDemo}`}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.3 }}
                        className="flex justify-end"
                      >
                        <div className="px-4 py-2.5 rounded-2xl rounded-tr-sm bg-emerald-600 text-sm text-white max-w-[80%]">
                          {demoConversations[activeDemo].question}
                        </div>
                      </motion.div>
                    </AnimatePresence>

                    {/* Typing indicator or bot answer */}
                    <AnimatePresence mode="wait">
                      {phase === "typing" && (
                        <motion.div
                          key="typing"
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                          transition={{ duration: 0.2 }}
                        >
                          <TypingDots />
                        </motion.div>
                      )}
                      {phase === "answer" && (
                        <motion.div
                          key={`a-${activeDemo}`}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: 10 }}
                          transition={{ duration: 0.4 }}
                          className="flex gap-2.5"
                        >
                          <div className="w-7 h-7 rounded-full bg-emerald-500/20 flex-shrink-0 flex items-center justify-center text-xs">
                            <MessageSquare className="w-3.5 h-3.5 text-emerald-400" />
                          </div>
                          <div className="px-4 py-2.5 rounded-2xl rounded-tl-sm bg-white/5 text-sm text-white/70 max-w-[80%] leading-relaxed">
                            {demoConversations[activeDemo].answer}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>

                  {/* Input */}
                  <div className="px-5 pb-5">
                    <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 transition-colors hover:border-white/20">
                      <span className="text-sm text-white/30 flex-1">
                        Type your question...
                      </span>
                      <motion.div
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center cursor-pointer hover:bg-emerald-500 transition"
                      >
                        <ArrowRight className="w-4 h-4 text-white" />
                      </motion.div>
                    </div>
                  </div>
                </div>
              </TiltChatWindow>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
