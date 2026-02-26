"use client";

import { useRef, useState } from "react";
import { motion, useInView } from "framer-motion";
import { Send, ArrowRight } from "lucide-react";

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

export function DemoSection() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });
  const [activeDemo, setActiveDemo] = useState(0);
  const [showAnswer, setShowAnswer] = useState(true);

  const handleDemoClick = (index: number) => {
    if (index === activeDemo) return;
    setShowAnswer(false);
    setTimeout(() => {
      setActiveDemo(index);
      setShowAnswer(true);
    }, 200);
  };

  return (
    <section id="demo" ref={ref} className="relative py-24 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
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
          animate={inView ? { opacity: 1, y: 0 } : {}}
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
                <button
                  key={i}
                  onClick={() => handleDemoClick(i)}
                  className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
                    activeDemo === i
                      ? "border-emerald-500/40 bg-emerald-500/10 text-white"
                      : "border-white/5 bg-white/[0.02] text-white/50 hover:text-white/70 hover:bg-white/[0.04]"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <Send
                      className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                        activeDemo === i ? "text-emerald-400" : "text-white/20"
                      }`}
                    />
                    <span className="text-sm leading-relaxed">
                      {conv.question}
                    </span>
                  </div>
                </button>
              ))}
            </div>

            {/* Chat window */}
            <div className="lg:col-span-3">
              <div className="rounded-2xl border border-white/10 bg-[#111118] overflow-hidden shadow-2xl shadow-emerald-500/5">
                {/* Chat header */}
                <div className="px-5 py-3.5 bg-gradient-to-r from-emerald-600 to-teal-600 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-sm">
                    🤖
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white">
                      EmbedChat Demo
                    </div>
                    <div className="text-[10px] text-white/70 flex items-center gap-1">
                      <span className="w-1.5 h-1.5 bg-green-400 rounded-full" />
                      Powered by your knowledge base
                    </div>
                  </div>
                </div>

                {/* Messages */}
                <div className="p-5 space-y-4 min-h-[280px]">
                  {/* Bot welcome */}
                  <div className="flex gap-2.5">
                    <div className="w-7 h-7 rounded-full bg-emerald-500/20 flex-shrink-0 flex items-center justify-center text-xs">
                      🤖
                    </div>
                    <div className="px-4 py-2.5 rounded-2xl rounded-tl-sm bg-white/5 text-sm text-white/70 max-w-[80%]">
                      Hi! I&apos;m trained on your knowledge base. Ask me anything!
                    </div>
                  </div>

                  {/* User question */}
                  <div className="flex justify-end">
                    <div className="px-4 py-2.5 rounded-2xl rounded-tr-sm bg-emerald-600 text-sm text-white max-w-[80%]">
                      {demoConversations[activeDemo].question}
                    </div>
                  </div>

                  {/* Bot answer */}
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={
                      showAnswer ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }
                    }
                    transition={{ duration: 0.4 }}
                    className="flex gap-2.5"
                  >
                    <div className="w-7 h-7 rounded-full bg-emerald-500/20 flex-shrink-0 flex items-center justify-center text-xs">
                      🤖
                    </div>
                    <div className="px-4 py-2.5 rounded-2xl rounded-tl-sm bg-white/5 text-sm text-white/70 max-w-[80%] leading-relaxed">
                      {demoConversations[activeDemo].answer}
                    </div>
                  </motion.div>
                </div>

                {/* Input */}
                <div className="px-5 pb-5">
                  <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10">
                    <span className="text-sm text-white/30 flex-1">
                      Type your question...
                    </span>
                    <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center cursor-pointer hover:bg-emerald-500 transition">
                      <ArrowRight className="w-4 h-4 text-white" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
