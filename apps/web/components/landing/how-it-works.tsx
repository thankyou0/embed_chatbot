"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { Upload, Wand2, Code2, Rocket } from "lucide-react";

const steps = [
  {
    step: "01",
    icon: Upload,
    title: "Upload Your Data",
    description:
      "Add your knowledge sources — crawl your website, upload PDFs and documents, or add Q&A pairs. The AI processes and understands all of it.",
    visual: (
      <div className="space-y-3">
        <div className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/5">
          <div className="w-8 h-8 rounded bg-blue-500/20 flex items-center justify-center text-xs">
            📄
          </div>
          <div className="flex-1">
            <div className="text-sm text-white/70">product-docs.pdf</div>
            <div className="text-xs text-white/30">2.4 MB • Processed</div>
          </div>
          <div className="text-xs text-green-400">✓</div>
        </div>
        <div className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/5">
          <div className="w-8 h-8 rounded bg-purple-500/20 flex items-center justify-center text-xs">
            🌐
          </div>
          <div className="flex-1">
            <div className="text-sm text-white/70">yoursite.com/docs</div>
            <div className="text-xs text-white/30">42 pages crawled</div>
          </div>
          <div className="text-xs text-green-400">✓</div>
        </div>
        <div className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/5">
          <div className="w-8 h-8 rounded bg-amber-500/20 flex items-center justify-center text-xs">
            💬
          </div>
          <div className="flex-1">
            <div className="text-sm text-white/70">Q&A Pairs</div>
            <div className="text-xs text-white/30">15 pairs added</div>
          </div>
          <div className="text-xs text-green-400">✓</div>
        </div>
      </div>
    ),
  },
  {
    step: "02",
    icon: Wand2,
    title: "Customize Your Bot",
    description:
      "Brand it as yours — pick colors, add your logo, set the tone of voice, configure welcome messages, and adjust the chat position.",
    visual: (
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <span className="text-xs text-white/40 w-16">Theme</span>
          <div className="flex gap-2">
            {["#6366f1", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981"].map(
              (c) => (
                <div
                  key={c}
                  className="w-6 h-6 rounded-full border-2 border-transparent hover:border-white/50 transition-colors cursor-pointer"
                  style={{ backgroundColor: c }}
                />
              )
            )}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-white/40 w-16">Position</span>
          <div className="flex gap-2">
            <div className="px-3 py-1 text-xs rounded bg-indigo-600 text-white">
              Bottom Right
            </div>
            <div className="px-3 py-1 text-xs rounded bg-white/5 text-white/50">
              Bottom Left
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-white/40 w-16">Name</span>
          <div className="px-3 py-1.5 text-sm rounded bg-white/5 border border-white/10 text-white/70 flex-1">
            AI Assistant
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-white/40 w-16">Welcome</span>
          <div className="px-3 py-1.5 text-sm rounded bg-white/5 border border-white/10 text-white/70 flex-1">
            Hi! How can I help you?
          </div>
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
    visual: (
      <div className="relative">
        <div className="p-4 rounded-lg bg-[#0d0d17] border border-white/5 font-mono text-xs">
          <div className="text-white/30 mb-2">
            {"<!-- Add to your HTML -->"}
          </div>
          <div>
            <span className="text-pink-400">{"<script"}</span>
          </div>
          <div className="pl-4">
            <span className="text-cyan-400">src</span>
            <span className="text-white/50">=</span>
            <span className="text-green-400">
              {'"https://embed.chat/widget.js"'}
            </span>
          </div>
          <div className="pl-4">
            <span className="text-cyan-400">data-bot-id</span>
            <span className="text-white/50">=</span>
            <span className="text-green-400">{'"your-bot-id"'}</span>
          </div>
          <div>
            <span className="text-pink-400">{"></script>"}</span>
          </div>
        </div>
        <div className="absolute top-2 right-2 px-2 py-1 text-[10px] rounded bg-indigo-600/80 text-white cursor-pointer hover:bg-indigo-500/80 transition">
          Copy
        </div>
      </div>
    ),
  },
  {
    step: "04",
    icon: Rocket,
    title: "Go Live Instantly",
    description:
      "Your chatbot is live and answering questions from real visitors. Track conversations and improve performance from the dashboard.",
    visual: (
      <div className="space-y-3">
        <div className="flex items-center justify-between p-3 rounded-lg bg-white/5">
          <span className="text-xs text-white/50">Status</span>
          <span className="flex items-center gap-1.5 text-xs text-green-400">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            Live
          </span>
        </div>
        <div className="flex items-center justify-between p-3 rounded-lg bg-white/5">
          <span className="text-xs text-white/50">Conversations Today</span>
          <span className="text-sm font-semibold text-white">247</span>
        </div>
        <div className="flex items-center justify-between p-3 rounded-lg bg-white/5">
          <span className="text-xs text-white/50">Avg. Response Time</span>
          <span className="text-sm font-semibold text-white">0.8s</span>
        </div>
        <div className="flex items-center justify-between p-3 rounded-lg bg-white/5">
          <span className="text-xs text-white/50">Satisfaction Rate</span>
          <span className="text-sm font-semibold text-white">94%</span>
        </div>
      </div>
    ),
  },
];

export function HowItWorks() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section
      id="how-it-works"
      ref={ref}
      className="relative py-24 lg:py-32 bg-gradient-to-b from-transparent via-indigo-500/[0.03] to-transparent"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16 lg:mb-20"
        >
          <p className="text-sm font-medium text-indigo-400 tracking-wider uppercase mb-3">
            How It Works
          </p>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Live in{" "}
            <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              Four Simple Steps
            </span>
          </h2>
          <p className="text-lg text-white/40 max-w-2xl mx-auto">
            From data upload to live conversations — the entire process takes
            less than 5 minutes.
          </p>
        </motion.div>

        {/* Steps */}
        <div className="space-y-12 lg:space-y-24">
          {steps.map((step, i) => (
            <motion.div
              key={step.step}
              initial={{ opacity: 0, y: 40 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.7, delay: i * 0.15 }}
              className={`flex flex-col ${
                i % 2 === 0 ? "lg:flex-row" : "lg:flex-row-reverse"
              } items-center gap-8 lg:gap-16`}
            >
              {/* Text */}
              <div className="flex-1 text-center lg:text-left">
                <div className="inline-flex items-center gap-3 mb-4">
                  <span className="text-5xl font-bold bg-gradient-to-b from-white/20 to-white/5 bg-clip-text text-transparent">
                    {step.step}
                  </span>
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
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
                <div className="p-6 rounded-2xl border border-white/5 bg-white/[0.02] backdrop-blur-sm">
                  {step.visual}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
