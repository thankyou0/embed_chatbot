"use client";

import { useRef } from "react";
import { motion, useInView, useScroll, useTransform } from "framer-motion";
import { Upload, Wand2, Code2, Rocket } from "lucide-react";

const steps = [
  {
    step: "01",
    icon: Upload,
    title: "Upload Your Data",
    description:
      "Add your knowledge sources — crawl your website, upload PDFs and documents, or add Q&A pairs. The AI processes and understands all of it.",
    color: "emerald",
    visual: (
      <div className="space-y-3">
        {[
          { icon: "📄", name: "product-docs.pdf", detail: "2.4 MB • Processed" },
          { icon: "🌐", name: "yoursite.com/docs", detail: "42 pages crawled" },
          { icon: "💬", name: "Q&A Pairs", detail: "15 pairs added" },
        ].map((item, i) => (
          <motion.div
            key={item.name}
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.3 + i * 0.1 }}
            className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/5 hover:bg-white/[0.08] hover:border-white/10 transition-all duration-200"
          >
            <div className="w-8 h-8 rounded bg-emerald-500/20 flex items-center justify-center text-xs">
              {item.icon}
            </div>
            <div className="flex-1">
              <div className="text-sm text-white/70">{item.name}</div>
              <div className="text-xs text-white/30">{item.detail}</div>
            </div>
            <motion.div
              initial={{ scale: 0 }}
              whileInView={{ scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: 0.6 + i * 0.15, type: "spring" }}
              className="text-xs text-green-400"
            >
              ✓
            </motion.div>
          </motion.div>
        ))}
      </div>
    ),
  },
  {
    step: "02",
    icon: Wand2,
    title: "Customize Your Bot",
    description:
      "Brand it as yours — pick colors, add your logo, set the tone of voice, configure welcome messages, and adjust the chat position.",
    color: "teal",
    visual: (
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <span className="text-xs text-white/40 w-16">Theme</span>
          <div className="flex gap-2">
            {[
              { c: "#10b981", active: true },
              { c: "#14b8a6", active: false },
              { c: "#ec4899", active: false },
              { c: "#f59e0b", active: false },
              { c: "#3b82f6", active: false },
            ].map(({ c, active }) => (
              <motion.div
                key={c}
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.9 }}
                className={`w-6 h-6 rounded-full cursor-pointer transition-all ${
                  active ? "ring-2 ring-white/50 ring-offset-2 ring-offset-[#0a0a0f]" : "hover:ring-1 hover:ring-white/30"
                }`}
                style={{ backgroundColor: c }}
              />
            ))}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-white/40 w-16">Position</span>
          <div className="flex gap-2">
            <div className="px-3 py-1 text-xs rounded bg-emerald-600 text-white">Bottom Right</div>
            <div className="px-3 py-1 text-xs rounded bg-white/5 text-white/50 hover:bg-white/10 transition-colors cursor-pointer">Bottom Left</div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-white/40 w-16">Name</span>
          <div className="px-3 py-1.5 text-sm rounded bg-white/5 border border-white/10 text-white/70 flex-1">AI Assistant</div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-white/40 w-16">Welcome</span>
          <div className="px-3 py-1.5 text-sm rounded bg-white/5 border border-white/10 text-white/70 flex-1">Hi! How can I help you?</div>
        </div>
      </div>
    ),
  },
  {
    step: "03",
    icon: Code2,
    title: "Embed One Script",
    description:
      "Copy the auto-generated embed code and paste it into your website. It's a single script tag — takes 10 seconds.",
    color: "cyan",
    visual: (
      <div className="relative group">
        <div className="p-4 rounded-lg bg-[#0d0d17] border border-white/5 font-mono text-xs group-hover:border-white/10 transition-colors">
          <div className="text-white/30 mb-2">{"<!-- Add to your HTML -->"}</div>
          <div><span className="text-pink-400">{"<script"}</span></div>
          <div className="pl-4">
            <span className="text-cyan-400">src</span><span className="text-white/50">=</span>
            <span className="text-green-400">{'"https://embed.chat/widget.js"'}</span>
          </div>
          <div className="pl-4">
            <span className="text-cyan-400">data-bot-id</span><span className="text-white/50">=</span>
            <span className="text-green-400">{'"your-bot-id"'}</span>
          </div>
          <div><span className="text-pink-400">{"></script>"}</span></div>
        </div>
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="absolute top-2 right-2 px-2 py-1 text-[10px] rounded bg-emerald-600/80 text-white cursor-pointer hover:bg-emerald-500 transition-colors"
        >
          Copy
        </motion.div>
      </div>
    ),
  },
  {
    step: "04",
    icon: Rocket,
    title: "Go Live Instantly",
    description:
      "Your chatbot is live and answering questions from real visitors. Track conversations and improve performance from the dashboard.",
    color: "violet",
    visual: (
      <div className="space-y-3">
        {[
          { label: "Status", value: <span className="flex items-center gap-1.5 text-xs text-green-400"><span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />Live</span> },
          { label: "Conversations Today", value: <span className="text-sm font-semibold text-white">247</span> },
          { label: "Avg. Response Time", value: <span className="text-sm font-semibold text-white">0.8s</span> },
          { label: "Satisfaction Rate", value: <span className="text-sm font-semibold text-white">94%</span> },
        ].map((item, i) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.3, delay: 0.2 + i * 0.1 }}
            className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/[0.08] transition-colors"
          >
            <span className="text-xs text-white/50">{item.label}</span>
            {item.value}
          </motion.div>
        ))}
      </div>
    ),
  },
];

export function HowItWorks() {
  const sectionRef = useRef(null);
  const inView = useInView(sectionRef, { once: true, margin: "-100px" });

  // Scroll-driven timeline progress
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });
  const lineHeight = useTransform(scrollYProgress, [0.1, 0.8], ["0%", "100%"]);

  return (
    <section
      id="how-it-works"
      ref={sectionRef}
      className="relative py-24 lg:py-32 bg-gradient-to-b from-transparent via-emerald-500/[0.03] to-transparent"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16 lg:mb-20"
        >
          <p className="text-sm font-medium text-emerald-400 tracking-wider uppercase mb-3">
            How It Works
          </p>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Live in{" "}
            <span className="bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
              Four Simple Steps
            </span>
          </h2>
          <p className="text-lg text-white/40 max-w-2xl mx-auto">
            From data upload to live conversations — the entire process takes
            less than 5 minutes.
          </p>
        </motion.div>

        {/* Steps with animated timeline */}
        <div className="relative">
          {/* Vertical timeline line (desktop only) */}
          <div className="absolute left-1/2 top-0 bottom-0 w-px bg-white/5 hidden lg:block -translate-x-1/2" />
          <motion.div
            style={{ height: lineHeight }}
            className="absolute left-1/2 top-0 w-px bg-gradient-to-b from-emerald-500 via-teal-500 to-cyan-500 hidden lg:block -translate-x-1/2"
          />

          <div className="space-y-12 lg:space-y-24">
            {steps.map((step, i) => (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.7, delay: 0.1 }}
                className={`relative flex flex-col ${
                  i % 2 === 0 ? "lg:flex-row" : "lg:flex-row-reverse"
                } items-center gap-8 lg:gap-16`}
              >
                {/* Timeline dot (desktop) */}
                <div className="absolute left-1/2 -translate-x-1/2 hidden lg:flex z-10">
                  <motion.div
                    initial={{ scale: 0 }}
                    whileInView={{ scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: 0.3, type: "spring" }}
                    className="w-12 h-12 rounded-full bg-[#0a0a0f] border-2 border-emerald-500/50 flex items-center justify-center"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/30">
                      <step.icon className="w-4 h-4 text-white" />
                    </div>
                  </motion.div>
                </div>

                {/* Text */}
                <div className="flex-1 text-center lg:text-left">
                  <div className="inline-flex items-center gap-3 mb-4">
                    <motion.span
                      initial={{ opacity: 0, scale: 0.5 }}
                      whileInView={{ opacity: 1, scale: 1 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.5, type: "spring" }}
                      className="text-5xl font-bold bg-gradient-to-b from-white/20 to-white/5 bg-clip-text text-transparent"
                    >
                      {step.step}
                    </motion.span>
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center lg:hidden shadow-lg shadow-emerald-500/25">
                      <step.icon className="w-5 h-5 text-white" />
                    </div>
                  </div>
                  <h3 className="text-2xl lg:text-3xl font-bold text-white mb-3">
                    {step.title}
                  </h3>
                  <p className="text-white/40 text-base lg:text-lg leading-relaxed max-w-md mx-auto lg:mx-0">
                    {step.description}
                  </p>
                </div>

                {/* Visual */}
                <div className="flex-1 w-full max-w-md">
                  <motion.div
                    whileHover={{ scale: 1.02, y: -4 }}
                    transition={{ type: "spring", stiffness: 300, damping: 20 }}
                    className="p-6 rounded-2xl border border-white/5 bg-white/[0.02] backdrop-blur-sm hover:border-white/10 hover:bg-white/[0.04] transition-all duration-300"
                  >
                    {step.visual}
                  </motion.div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
