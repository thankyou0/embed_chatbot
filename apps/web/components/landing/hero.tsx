"use client";

import { useRef } from "react";
import Link from "next/link";
import { motion, useInView } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";

export function HeroSection() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true });

  return (
    <section
      ref={ref}
      className="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden"
    >
      {/* Animated background gradients */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 -left-1/4 w-[600px] h-[600px] bg-indigo-500/20 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-1/4 -right-1/4 w-[500px] h-[500px] bg-purple-500/20 rounded-full blur-[120px] animate-pulse [animation-delay:1s]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-cyan-500/10 rounded-full blur-[100px] animate-pulse [animation-delay:2s]" />
      </div>

      {/* Grid overlay */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-sm mb-8"
        >
          <Sparkles className="w-4 h-4" />
          <span>AI-Powered Chatbot Platform</span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, delay: 0.1 }}
          className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.1] mb-6"
        >
          <span className="text-white">Embed an AI Chatbot</span>
          <br />
          <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
            on Any Website
          </span>
          <br />
          <span className="text-white">in Minutes</span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="text-lg sm:text-xl text-white/50 max-w-2xl mx-auto mb-10 leading-relaxed"
        >
          Train your chatbot on your own data — docs, websites, PDFs — and embed
          it anywhere with a single line of code. Engage visitors 24/7 with
          intelligent, on-brand conversations.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link
            href="/signup"
            className="group inline-flex items-center gap-2 px-8 py-4 text-base font-semibold bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl hover:from-indigo-400 hover:to-purple-500 transition-all shadow-2xl shadow-indigo-500/25 hover:shadow-indigo-500/40"
          >
            Start for Free
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
          <a
            href="#demo"
            className="inline-flex items-center gap-2 px-8 py-4 text-base font-medium border border-white/10 rounded-xl hover:bg-white/5 transition-all text-white/70 hover:text-white"
          >
            See Live Demo
          </a>
        </motion.div>

        {/* 3D Spline Scene */}
        <motion.div
          initial={{ opacity: 0, y: 60, scale: 0.95 }}
          animate={inView ? { opacity: 1, y: 0, scale: 1 } : {}}
          transition={{ duration: 1, delay: 0.5, ease: "easeOut" }}
          className="relative mt-16 lg:mt-20 mx-auto max-w-5xl"
        >
          {/* Glow effect behind the mockup */}
          <div className="absolute -inset-4 bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-cyan-500/20 rounded-3xl blur-3xl" />

          {/* Browser mockup */}
          <div className="relative rounded-2xl border border-white/10 bg-[#111118] overflow-hidden shadow-2xl">
            {/* Browser chrome */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5 bg-[#0d0d14]">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/60" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
                <div className="w-3 h-3 rounded-full bg-green-500/60" />
              </div>
              <div className="flex-1 mx-4">
                <div className="max-w-sm mx-auto px-3 py-1 rounded-md bg-white/5 text-white/30 text-xs text-center">
                  yourwebsite.com
                </div>
              </div>
            </div>

            {/* Page content with embedded widget mockup */}
            <div className="relative p-4 sm:p-8 min-h-[400px] bg-gradient-to-br from-[#111118] to-[#0d0d17]">
              {/* Fake website content */}
              <div className="space-y-4 max-w-md">
                <div className="h-4 bg-white/5 rounded w-3/4" />
                <div className="h-4 bg-white/5 rounded w-1/2" />
                <div className="h-3 bg-white/[0.03] rounded w-full" />
                <div className="h-3 bg-white/[0.03] rounded w-5/6" />
                <div className="h-3 bg-white/[0.03] rounded w-4/6" />
                <div className="mt-6 h-32 bg-white/[0.02] rounded-lg border border-white/5" />
                <div className="h-3 bg-white/[0.03] rounded w-full" />
                <div className="h-3 bg-white/[0.03] rounded w-3/4" />
              </div>

              {/* Chat Widget Mockup - floating in bottom-right */}
              <div className="absolute bottom-4 right-4 sm:bottom-8 sm:right-8">
                {/* Chat bubble trigger */}
                <motion.div
                  animate={{ y: [0, -6, 0] }}
                  transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                  className="relative"
                >
                  {/* Notification badge */}
                  <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-[10px] font-bold z-10">
                    1
                  </div>

                  {/* Chat popup */}
                  <div className="w-[280px] sm:w-[320px] rounded-2xl border border-white/10 bg-[#1a1a2e] shadow-2xl shadow-indigo-500/10 overflow-hidden mb-3">
                    {/* Chat header */}
                    <div className="px-4 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-sm">
                        🤖
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-white">
                          AI Assistant
                        </div>
                        <div className="text-[10px] text-white/70 flex items-center gap-1">
                          <span className="w-1.5 h-1.5 bg-green-400 rounded-full" />
                          Online
                        </div>
                      </div>
                    </div>

                    {/* Chat messages */}
                    <div className="p-4 space-y-3">
                      <div className="flex gap-2">
                        <div className="w-6 h-6 rounded-full bg-indigo-500/20 flex-shrink-0 flex items-center justify-center text-[10px]">
                          🤖
                        </div>
                        <div className="px-3 py-2 rounded-xl rounded-tl-sm bg-white/5 text-sm text-white/80 max-w-[220px]">
                          Hi! 👋 How can I help you today?
                        </div>
                      </div>
                      <div className="flex justify-end">
                        <div className="px-3 py-2 rounded-xl rounded-tr-sm bg-indigo-600 text-sm text-white max-w-[220px]">
                          What are your pricing plans?
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <div className="w-6 h-6 rounded-full bg-indigo-500/20 flex-shrink-0 flex items-center justify-center text-[10px]">
                          🤖
                        </div>
                        <div className="px-3 py-2 rounded-xl rounded-tl-sm bg-white/5 text-sm text-white/80 max-w-[220px]">
                          <TypingIndicator />
                        </div>
                      </div>
                    </div>

                    {/* Chat input */}
                    <div className="px-4 pb-4">
                      <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 border border-white/10">
                        <span className="text-sm text-white/30 flex-1">
                          Type a message...
                        </span>
                        <div className="w-6 h-6 rounded-md bg-indigo-600 flex items-center justify-center">
                          <ArrowRight className="w-3 h-3 text-white" />
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-3xl mx-auto"
        >
          {[
            { value: "10K+", label: "Chatbots Created" },
            { value: "50M+", label: "Messages Handled" },
            { value: "99.9%", label: "Uptime" },
            { value: "<1s", label: "Response Time" },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                {stat.value}
              </div>
              <div className="text-sm text-white/40 mt-1">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 py-1 px-1">
      <motion.div
        animate={{ opacity: [0.3, 1, 0.3] }}
        transition={{ duration: 1.2, repeat: Infinity, delay: 0 }}
        className="w-1.5 h-1.5 bg-white/50 rounded-full"
      />
      <motion.div
        animate={{ opacity: [0.3, 1, 0.3] }}
        transition={{ duration: 1.2, repeat: Infinity, delay: 0.2 }}
        className="w-1.5 h-1.5 bg-white/50 rounded-full"
      />
      <motion.div
        animate={{ opacity: [0.3, 1, 0.3] }}
        transition={{ duration: 1.2, repeat: Infinity, delay: 0.4 }}
        className="w-1.5 h-1.5 bg-white/50 rounded-full"
      />
    </div>
  );
}
