"use client";

import { useRef, useState, useEffect } from "react";
import { motion, useInView, AnimatePresence } from "framer-motion";
import {
  Upload,
  Globe,
  FileText,
  HelpCircle,
  Code2,
  CheckCircle2,
  Copy,
  MessageSquare,
  BarChart3,
  Users,
  ArrowRight,
  Sparkles,
  Bot,
} from "lucide-react";

/* Step cards for the right side */
const steps = [
  {
    num: "01",
    title: "Upload Your Data",
    desc: "Feed your chatbot PDFs, websites, documents, Q&A pairs — any knowledge source. Our AI processes and understands it all.",
    color: "emerald",
  },
  {
    num: "02",
    title: "Customize Your Bot",
    desc: "Match your brand perfectly. Choose colors, name, tone, position, and behavior. No coding required.",
    color: "teal",
  },
  {
    num: "03",
    title: "Embed One Script",
    desc: "Copy a single line of code. Paste it anywhere — React, WordPress, Shopify, plain HTML. It just works.",
    color: "cyan",
  },
  {
    num: "04",
    title: "Go Live Instantly",
    desc: "Your AI chatbot is live, answering customers 24/7. Monitor analytics, satisfaction, & conversations in real-time.",
    color: "violet",
  },
];

const colorMap: Record<string, { ring: string; text: string; bg: string; glow: string; border: string; hex: string }> = {
  emerald: { ring: "ring-emerald-500", text: "text-emerald-400", bg: "bg-emerald-500/10", glow: "shadow-emerald-500/30", border: "border-emerald-500/40", hex: "#10b981" },
  teal:    { ring: "ring-teal-500",    text: "text-teal-400",    bg: "bg-teal-500/10",    glow: "shadow-teal-500/30",    border: "border-teal-500/40",    hex: "#14b8a6" },
  cyan:    { ring: "ring-cyan-500",    text: "text-cyan-400",    bg: "bg-cyan-500/10",    glow: "shadow-cyan-500/30",    border: "border-cyan-500/40",    hex: "#06b6d4" },
  violet:  { ring: "ring-violet-500",  text: "text-violet-400",  bg: "bg-violet-500/10",  glow: "shadow-violet-500/30",  border: "border-violet-500/40",  hex: "#a855f7" },
};

const STEP_DURATION = 4000; // ms per step

/* ═══════════════════════════════════════ Step visuals ═══════════════════════════════════════ */

/* Step 1: Data Upload UI mockup */
function UploadVisual() {
  const sources = [
    { icon: Globe, label: "Website", active: true },
    { icon: FileText, label: "File", active: false },
    { icon: HelpCircle, label: "Q&A", active: false },
  ];

  const crawledPages = [
    { url: "example.com/products", status: "done", pages: 24 },
    { url: "example.com/about", status: "done", pages: 3 },
    { url: "example.com/faq", status: "crawling", pages: 12 },
  ];

  return (
    <div className="w-full h-full flex flex-col gap-3 p-1">
      {/* Source selector tabs */}
      <div className="flex gap-2">
        {sources.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 + 0.2 }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              s.active
                ? "bg-emerald-500/20 border border-emerald-500/30 text-emerald-400"
                : "bg-white/[0.03] border border-white/5 text-white/40"
            }`}
          >
            <s.icon className="w-3 h-3" />
            {s.label}
          </motion.div>
        ))}
      </div>

      {/* URL input mock */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="flex gap-2"
      >
        <div className="flex-1 bg-white/[0.03] border border-white/10 rounded-lg px-3 py-2 text-xs text-white/40 flex items-center gap-2">
          <Globe className="w-3 h-3 text-white/20" />
          <span>https://example.com</span>
        </div>
        <div className="px-3 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 rounded-lg text-xs font-medium text-white flex items-center gap-1.5 whitespace-nowrap">
          <Upload className="w-3 h-3" />
          Crawl
        </div>
      </motion.div>

      {/* Crawled pages list */}
      <div className="flex-1 space-y-2 mt-1">
        {crawledPages.map((page, i) => (
          <motion.div
            key={page.url}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 + i * 0.15 }}
            className="flex items-center gap-2 bg-white/[0.02] border border-white/5 rounded-lg px-3 py-2"
          >
            <div className={`w-1.5 h-1.5 rounded-full ${page.status === "done" ? "bg-emerald-400" : "bg-amber-400 animate-pulse"}`} />
            <span className="text-xs text-white/60 flex-1 truncate">{page.url}</span>
            <span className="text-[10px] text-white/30">{page.pages} pages</span>
            {page.status === "done" && <CheckCircle2 className="w-3 h-3 text-emerald-400" />}
            {page.status === "crawling" && (
              <div className="w-3 h-3 border border-amber-400/60 border-t-amber-400 rounded-full animate-spin" />
            )}
          </motion.div>
        ))}
      </div>

      {/* Stats bar */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.1 }}
        className="flex items-center justify-between pt-2 border-t border-white/5"
      >
        <div className="flex items-center gap-3">
          <span className="text-[10px] text-white/30">39 pages crawled</span>
          <span className="text-[10px] text-emerald-400">● Processing</span>
        </div>
        <div className="h-1.5 w-20 bg-white/5 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full"
            initial={{ width: "0%" }}
            animate={{ width: "78%" }}
            transition={{ delay: 1.2, duration: 1.5, ease: "easeOut" }}
          />
        </div>
      </motion.div>
    </div>
  );
}

/* Step 2: Bot Customization UI mockup */
function CustomizeVisual() {
  const colors = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];

  return (
    <div className="w-full h-full flex flex-col gap-3 p-1">
      {/* Bot name input */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="space-y-1.5"
      >
        <label className="text-[10px] text-white/40 uppercase tracking-wider font-medium">Bot Name</label>
        <div className="bg-white/[0.03] border border-white/10 rounded-lg px-3 py-2 text-xs text-white/70">
          My Store Assistant
        </div>
      </motion.div>

      {/* Color picker */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35 }}
        className="space-y-1.5"
      >
        <label className="text-[10px] text-white/40 uppercase tracking-wider font-medium">Primary Color</label>
        <div className="flex items-center gap-2">
          {colors.map((color, i) => (
            <div
              key={color}
              className={`w-6 h-6 rounded-lg transition-all ${i === 0 ? "ring-2 ring-white/40 scale-110" : "ring-1 ring-white/10"}`}
              style={{ backgroundColor: color }}
            />
          ))}
          <div className="ml-auto text-[10px] text-white/30 font-mono">#10b981</div>
        </div>
      </motion.div>

      {/* Tone selector */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="space-y-1.5"
      >
        <label className="text-[10px] text-white/40 uppercase tracking-wider font-medium">Conversation Tone</label>
        <div className="grid grid-cols-2 gap-1.5">
          {["Friendly & Warm", "Professional", "Casual", "Formal"].map((tone, i) => (
            <div
              key={tone}
              className={`px-2 py-1.5 rounded-lg text-[10px] text-center transition-all ${
                i === 0
                  ? "bg-emerald-500/15 border border-emerald-500/30 text-emerald-400"
                  : "bg-white/[0.02] border border-white/5 text-white/30"
              }`}
            >
              {tone}
            </div>
          ))}
        </div>
      </motion.div>

      {/* Position selector */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.65 }}
        className="space-y-1.5"
      >
        <label className="text-[10px] text-white/40 uppercase tracking-wider font-medium">Widget Position</label>
        <div className="flex gap-2">
          {["Bottom Left", "Bottom Right"].map((pos, i) => (
            <div
              key={pos}
              className={`flex-1 px-2 py-1.5 rounded-lg text-[10px] text-center transition-all ${
                i === 1
                  ? "bg-teal-500/15 border border-teal-500/30 text-teal-400"
                  : "bg-white/[0.02] border border-white/5 text-white/30"
              }`}
            >
              {pos}
            </div>
          ))}
        </div>
      </motion.div>

      {/* Languages */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="space-y-1.5"
      >
        <label className="text-[10px] text-white/40 uppercase tracking-wider font-medium">Languages</label>
        <div className="flex gap-1.5">
          {["English", "Hindi", "Gujarati"].map((lang, i) => (
            <div
              key={lang}
              className={`px-2.5 py-1 rounded-lg text-[10px] transition-all ${
                i < 2
                  ? "bg-emerald-500/15 border border-emerald-500/30 text-emerald-400"
                  : "bg-white/[0.02] border border-white/5 text-white/30"
              }`}
            >
              {lang}
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

/* Step 3: Embed Script UI mockup */
function EmbedVisual() {
  return (
    <div className="w-full h-full flex flex-col gap-3 p-1">
      {/* Quick start guide header */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-gradient-to-r from-emerald-500/10 to-teal-500/5 border border-emerald-500/20 rounded-xl p-3"
      >
        <div className="flex items-center gap-2 mb-2">
          <div className="w-5 h-5 rounded-full bg-gradient-to-br from-emerald-600 to-teal-600 flex items-center justify-center">
            <Sparkles className="w-3 h-3 text-white" />
          </div>
          <span className="text-xs font-semibold text-white">Quick Start Guide</span>
        </div>
        <div className="space-y-1.5">
          {["Copy the script below", "Paste before </body>", "That\u2019s it \u2014 you\u2019re live!"].map((step, i) => (
            <div key={step} className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-gradient-to-br from-emerald-600 to-teal-600 flex items-center justify-center text-[8px] font-bold text-white">
                {i + 1}
              </div>
              <span className="text-[10px] text-white/50">{step}</span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Code block */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="flex-1 relative"
      >
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center gap-1.5">
            <Code2 className="w-3 h-3 text-cyan-400" />
            <span className="text-[10px] text-white/40 font-medium">JavaScript Widget</span>
          </div>
          <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">Recommended</span>
        </div>
        <div className="bg-[#0d1117] border border-white/5 rounded-lg p-3 font-mono text-[10px] leading-relaxed overflow-hidden">
          <div className="text-white/30">&lt;!-- EmbedChat Widget --&gt;</div>
          <div>
            <span className="text-cyan-400">&lt;script </span>
            <span className="text-violet-400">src</span>
            <span className="text-white/50">=</span>
            <span className="text-emerald-400">&quot;embedchat.js&quot;</span>
            <span className="text-cyan-400">&gt;&lt;/script&gt;</span>
          </div>
          <div>
            <span className="text-cyan-400">&lt;script&gt;</span>
          </div>
          <div className="pl-3">
            <span className="text-violet-400">EmbedChat</span>
            <span className="text-white/60">.init({`{`}</span>
          </div>
          <div className="pl-6">
            <span className="text-blue-400">id</span>
            <span className="text-white/40">: </span>
            <span className="text-emerald-400">&quot;bot_abc123&quot;</span>
          </div>
          <div className="pl-3">
            <span className="text-white/60">{`}`})</span>
          </div>
          <div>
            <span className="text-cyan-400">&lt;/script&gt;</span>
          </div>
        </div>

        {/* Copy button */}
        <div className="absolute top-7 right-2 p-1.5 rounded-md bg-white/5 hover:bg-white/10 transition-colors cursor-pointer">
          <Copy className="w-3 h-3 text-white/30" />
        </div>
      </motion.div>

      {/* Platform chips */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="flex flex-wrap gap-1.5"
      >
        {["HTML", "React", "WordPress", "Shopify", "Wix"].map((p) => (
          <span key={p} className="text-[9px] px-2 py-0.5 rounded-md bg-white/[0.03] border border-white/5 text-white/30">
            {p}
          </span>
        ))}
      </motion.div>
    </div>
  );
}

/* Step 4: Go Live — Analytics Dashboard mockup */
function GoLiveVisual() {
  const stats = [
    { label: "Sessions", value: "1,247", icon: Users, color: "text-emerald-400", change: "+12%" },
    { label: "Messages", value: "4,892", icon: MessageSquare, color: "text-blue-400", change: "+24%" },
    { label: "Satisfaction", value: "94%", icon: BarChart3, color: "text-teal-400", change: "+3%" },
  ];

  return (
    <div className="w-full h-full flex flex-col gap-3 p-1">
      {/* Status badge */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2, type: "spring" }}
        className="flex items-center gap-2"
      >
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/25">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[10px] font-medium text-emerald-400">Live</span>
        </div>
        <span className="text-[10px] text-white/30">Bot is active on example.com</span>
      </motion.div>

      {/* Stats cards */}
      <div className="grid grid-cols-3 gap-2">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 + i * 0.1 }}
            className="bg-white/[0.02] border border-white/5 rounded-lg p-2.5"
          >
            <div className="flex items-center justify-between mb-1">
              <stat.icon className={`w-3 h-3 ${stat.color}`} />
              <span className="text-[8px] text-emerald-400 font-medium">{stat.change}</span>
            </div>
            <div className="text-sm font-bold text-white">{stat.value}</div>
            <div className="text-[9px] text-white/30">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Mini chat conversation */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="flex-1 bg-white/[0.02] border border-white/5 rounded-lg p-2.5 space-y-2"
      >
        <div className="flex items-center gap-2 mb-1.5">
          <div className="w-4 h-4 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
            <Bot className="w-2.5 h-2.5 text-white" />
          </div>
          <span className="text-[10px] text-white/50 font-medium">Recent conversation</span>
        </div>
        {/* User message */}
        <div className="flex justify-end">
          <div className="bg-emerald-500/20 border border-emerald-500/20 rounded-lg rounded-br-sm px-2.5 py-1.5 max-w-[85%]">
            <span className="text-[10px] text-white/70">Do you have wireless headphones?</span>
          </div>
        </div>
        {/* Bot reply */}
        <div className="flex justify-start">
          <div className="bg-white/[0.04] border border-white/5 rounded-lg rounded-bl-sm px-2.5 py-1.5 max-w-[85%]">
            <span className="text-[10px] text-white/60">{"Yes! We have 3 wireless headphone models starting from $49.99 🎧"}</span>
          </div>
        </div>
        {/* Suggestions */}
        <div className="flex gap-1 flex-wrap">
          {["View all headphones", "Compare models"].map((s) => (
            <span key={s} className="text-[8px] px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/15 text-emerald-400/70">
              {s}
            </span>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

/* Visual component map */
const StepVisuals = [UploadVisual, CustomizeVisual, EmbedVisual, GoLiveVisual];

/* ═══════════════════════════════════════ Main Component ═══════════════════════════════════════ */

export default function HowItWorks3D() {
  const containerRef = useRef<HTMLDivElement>(null);
  const inView = useInView(containerRef, { once: false, margin: "-100px" });
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    if (!inView) return;
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % steps.length);
    }, STEP_DURATION);
    return () => clearInterval(interval);
  }, [inView]);

  const ActiveVisual = StepVisuals[activeStep];
  const activeColor = colorMap[steps[activeStep].color];

  return (
    <section
      ref={containerRef}
      id="how-it-works"
      className="relative py-24 md:py-36 overflow-hidden"
      style={{ background: "linear-gradient(180deg, #0a0a0f 0%, #0d0d17 50%, #0a0a0f 100%)" }}
    >
      {/* Section header */}
      <div className="relative z-10 max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8 mb-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-sm text-emerald-400 mb-4">
            🚀 Ready in 5 Minutes
          </span>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4">
            How It{" "}
            <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">
              Works
            </span>
          </h2>
          <p className="text-lg text-white/50 max-w-2xl mx-auto">
            Four simple steps from zero to a fully deployed AI chatbot on your website.
          </p>
        </motion.div>
      </div>

      {/* Main content */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          {/* Left: Interactive UI mockup */}
          <motion.div
            className="relative w-full"
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
          >
            {/* Glow ring */}
            <div
              className="absolute -inset-4 rounded-3xl opacity-30 blur-xl transition-colors duration-700"
              style={{ background: `radial-gradient(ellipse at center, ${activeColor.hex}20, transparent 70%)` }}
            />

            {/* Dashboard mockup frame */}
            <div className="relative bg-[#0c0c18] border border-white/[0.08] rounded-2xl overflow-hidden shadow-2xl">
              {/* Window chrome bar */}
              <div className="flex items-center gap-2 px-4 py-2.5 border-b border-white/5 bg-white/[0.02]">
                <div className="flex gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
                  <div className="w-2.5 h-2.5 rounded-full bg-amber-500/50" />
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/50" />
                </div>
                <div className="flex-1 flex justify-center">
                  <div className="px-3 py-0.5 rounded-md bg-white/[0.04] text-[10px] text-white/20 font-mono">
                    app.embedchat.io/dashboard
                  </div>
                </div>
              </div>

              {/* Content area */}
              <div>
                {/* Main panel */}
                <div className="p-4 sm:p-5 min-h-[320px] sm:min-h-[380px]">
                  {/* Panel header */}
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="text-sm font-semibold text-white">{steps[activeStep].title}</h4>
                      <p className="text-[10px] text-white/30 mt-0.5">Step {steps[activeStep].num} of 04</p>
                    </div>
                    <div
                      className="px-2 py-1 rounded-md text-[9px] font-medium"
                      style={{
                        backgroundColor: `${activeColor.hex}15`,
                        color: activeColor.hex,
                        border: `1px solid ${activeColor.hex}30`,
                      }}
                    >
                      {activeStep < 3 ? "In Progress" : "Complete \u2713"}
                    </div>
                  </div>

                  {/* Animated visual swap */}
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={activeStep}
                      initial={{ opacity: 0, y: 20, filter: "blur(4px)" }}
                      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                      exit={{ opacity: 0, y: -15, filter: "blur(4px)" }}
                      transition={{ duration: 0.4 }}
                      className="h-[220px] sm:h-[260px]"
                    >
                      <ActiveVisual />
                    </motion.div>
                  </AnimatePresence>
                </div>
              </div>
            </div>

            {/* Floating particles around the frame */}
            {[...Array(6)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 rounded-full"
                style={{
                  backgroundColor: activeColor.hex,
                  top: `${15 + i * 15}%`,
                  left: i % 2 === 0 ? "-2%" : "102%",
                  opacity: 0.3,
                }}
                animate={{
                  y: [0, -10, 0],
                  opacity: [0.1, 0.4, 0.1],
                }}
                transition={{
                  duration: 2 + i * 0.5,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: i * 0.3,
                }}
              />
            ))}
          </motion.div>

          {/* Right: Step cards */}
          <div className="space-y-3 sm:space-y-4">
            {steps.map((step, i) => {
              const c = colorMap[step.color];
              const isActive = i === activeStep;
              return (
                <motion.div
                  key={step.num}
                  initial={{ opacity: 0, x: 40 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.12 }}
                  onClick={() => setActiveStep(i)}
                  className={`group relative rounded-2xl border backdrop-blur-sm p-5 cursor-pointer transition-all duration-500 ${
                    isActive
                      ? `${c.border} bg-white/[0.04] shadow-lg ${c.glow} scale-[1.02]`
                      : "border-white/5 bg-white/[0.01] hover:border-white/10 hover:bg-white/[0.02]"
                  }`}
                >
                  {/* Progress bar */}
                  {isActive && (
                    <div className="absolute top-0 left-0 right-0 h-[2px] rounded-t-2xl overflow-hidden">
                      <motion.div
                        className="h-full"
                        initial={{ width: "0%" }}
                        animate={{ width: "100%" }}
                        transition={{ duration: STEP_DURATION / 1000, ease: "linear" }}
                        key={`bar-${activeStep}`}
                        style={{
                          background: `linear-gradient(90deg, transparent, ${c.hex})`,
                        }}
                      />
                    </div>
                  )}

                  <div className="flex items-start gap-4">
                    {/* Step number */}
                    <div
                      className={`flex-shrink-0 w-10 h-10 rounded-xl ${c.bg} ring-1 ${c.ring} flex items-center justify-center transition-all duration-300 ${
                        isActive ? "ring-2 scale-110" : "opacity-50"
                      }`}
                    >
                      <span className={`text-sm font-bold ${c.text}`}>{step.num}</span>
                    </div>
                    {/* Text */}
                    <div className="flex-1">
                      <h3
                        className={`text-lg font-semibold mb-1 transition-colors duration-300 ${
                          isActive ? "text-white" : "text-white/40"
                        }`}
                      >
                        {step.title}
                      </h3>
                      <p
                        className={`text-sm leading-relaxed transition-colors duration-300 ${
                          isActive ? "text-white/60" : "text-white/25"
                        }`}
                      >
                        {step.desc}
                      </p>
                    </div>
                    {/* Arrow indicator */}
                    {isActive && (
                      <motion.div
                        initial={{ opacity: 0, x: -5 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex-shrink-0 mt-1"
                      >
                        <ArrowRight className={`w-4 h-4 ${c.text}`} />
                      </motion.div>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Ambient background glows */}
      <div className="absolute top-1/3 left-1/4 w-96 h-96 bg-emerald-500/[0.03] rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-cyan-500/[0.03] rounded-full blur-[100px] pointer-events-none" />
    </section>
  );
}
