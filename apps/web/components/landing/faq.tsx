"use client";

import { useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, HelpCircle } from "lucide-react";
import { FloatingParticles } from "./floating-particles";

const faqs = [
  {
    q: "How does the chatbot learn from my data?",
    a: "When you upload documents, crawl a website, or add Q&A pairs, our system processes the content into vector embeddings. The chatbot uses these embeddings along with a large language model to generate accurate, context-aware responses based specifically on your data.",
  },
  {
    q: "What types of data sources are supported?",
    a: "We support four types of knowledge sources: website crawling (automatically scrapes your pages), PDF and document uploads, manual Q&A pairs for precise answers, and raw text input. You can combine multiple sources for comprehensive coverage.",
  },
  {
    q: "Can I customize the look and feel of the widget?",
    a: "Absolutely! You can customize colors, position (bottom-left or bottom-right), chat header, bot name, welcome message, avatar, and more. The widget automatically adapts to match your brand identity.",
  },
  {
    q: "How do I embed the chatbot on my website?",
    a: "It's a single script tag. Go to your chatbot's settings in the dashboard, copy the embed code, and paste it into your website's HTML before the closing </body> tag. It works with any website builder — WordPress, Shopify, Webflow, React, or plain HTML.",
  },
  {
    q: "Is there a limit on conversations?",
    a: "The Free plan includes 50 messages per month. Pro plans offer unlimited messages, and Enterprise plans include unlimited everything with custom rate limits and dedicated infrastructure.",
  },
  {
    q: "Can I manage multiple chatbots?",
    a: "Yes! Depending on your plan, you can create multiple chatbots — each with different data sources, appearances, and configurations. Perfect for different products, departments, or use cases.",
  },
  {
    q: "Do you offer team collaboration?",
    a: "Yes, our Pro and Enterprise plans support team management with role-based permissions. You can invite team members, assign roles (admin, member), and control access to different chatbots and features.",
  },
  {
    q: "Is my data secure?",
    a: "Security is a top priority. All data is encrypted in transit and at rest. We use secure infrastructure with access controls, and your chatbot data is isolated per account. We never use your data to train our models.",
  },
];

export function FAQSection() {
  const ref = useRef(null);
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section id="faq" ref={ref} className="relative py-24 lg:py-32 overflow-hidden">
      {/* Floating particles */}
      <FloatingParticles count={8} color="#14b8a6" color2="#10b981" sizeRange={[1, 2]} speed={0.5} />

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <motion.div
            initial={{ scale: 0 }}
            whileInView={{ scale: 1 }}
            viewport={{ once: true }}
            transition={{ type: "spring", delay: 0.1 }}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 mb-4"
          >
            <HelpCircle className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-sm font-medium text-emerald-400 tracking-wider uppercase">
              FAQ
            </span>
          </motion.div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Frequently Asked{" "}
            <span className="bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
              Questions
            </span>
          </h2>
        </motion.div>

        {/* Accordion */}
        <div className="space-y-3">
          {faqs.map((faq, i) => {
            const isOpen = openIndex === i;
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.05 }}
                whileHover={{ scale: isOpen ? 1 : 1.005 }}
                className={`rounded-xl border transition-all duration-300 ${
                  isOpen
                    ? "border-emerald-500/20 bg-emerald-500/[0.04] shadow-lg shadow-emerald-500/5"
                    : "border-white/5 bg-white/[0.01] hover:bg-white/[0.03] hover:border-white/10"
                }`}
              >
                <button
                  onClick={() => setOpenIndex(isOpen ? null : i)}
                  className="w-full text-left px-5 py-4 flex items-center justify-between gap-4"
                >
                  <span
                    className={`text-sm font-medium transition-colors duration-200 ${
                      isOpen ? "text-white" : "text-white/60"
                    }`}
                  >
                    {faq.q}
                  </span>
                  <motion.div
                    animate={{ rotate: isOpen ? 180 : 0 }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                  >
                    <ChevronDown
                      className={`w-4 h-4 flex-shrink-0 transition-colors duration-200 ${
                        isOpen ? "text-emerald-400" : "text-white/30"
                      }`}
                    />
                  </motion.div>
                </button>
                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{
                        height: { duration: 0.3, ease: "easeInOut" },
                        opacity: { duration: 0.25, delay: 0.05 },
                      }}
                      className="overflow-hidden"
                    >
                      <div className="px-5 pb-4 text-sm text-white/40 leading-relaxed">
                        {faq.a}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
