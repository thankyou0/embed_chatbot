"use client";

import { useRef, useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { motion, useInView, useMotionValue, useSpring, useTransform } from "framer-motion";
import { ArrowRight, Sparkles, MessageSquare } from "lucide-react";
import { Hero3DCanvas } from "./3d/hero-canvas";

/* ────────── Animated counter ────────── */
function AnimatedCounter({ target, suffix = "", duration = 2000 }: { target: number; suffix?: string; duration?: number }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const inView = useInView(ref, { once: true });

  useEffect(() => {
    if (!inView) return;
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= target) {
        setCount(target);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [inView, target, duration]);

  return (
    <span ref={ref}>
      {count.toLocaleString()}{suffix}
    </span>
  );
}

/* ────────── Floating 3D geometric shape (2D fallback) ────────── */
function FloatingShape({
  className,
  delay = 0,
  children,
}: {
  className?: string;
  delay?: number;
  children: React.ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 1.2, delay, ease: "easeOut" }}
      className={`absolute preserve-3d ${className}`}
    >
      {children}
    </motion.div>
  );
}

/* ────────── Particle ────────── */
function Particle({ size, left, top, delay, duration }: { size: number; left: string; top: string; delay: number; duration: number }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: [0, 0.5, 0] }}
      transition={{ duration, repeat: Infinity, delay, ease: "easeInOut" }}
      className="absolute rounded-full bg-emerald-400/30 blur-[1px]"
      style={{ width: size, height: size, left, top }}
    />
  );
}

/* ────────── Main Hero ────────── */
export function HeroSection() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true });

  return (
    <section
      ref={ref}
      className="relative min-h-screen flex flex-col items-center justify-start pt-20 overflow-hidden"
    >
      {/* ── 3D Scene as background layer ── */}
      <div className="absolute inset-0 z-0">
        <Hero3DCanvas />
      </div>

      {/* ── Gradient overlay for text readability ── */}
      <div className="absolute inset-0 z-[1] bg-gradient-to-b from-[#0a0a0f]/70 via-[#0a0a0f]/40 to-[#0a0a0f]/80 pointer-events-none" />

      {/* ── Floating particles (on top of 3D, behind text) ── */}
      <Particle size={4} left="15%" top="30%" delay={0} duration={6} />
      <Particle size={3} left="75%" top="20%" delay={1} duration={7} />
      <Particle size={5} left="85%" top="60%" delay={2} duration={5} />
      <Particle size={3} left="25%" top="70%" delay={1.5} duration={8} />
      <Particle size={4} left="60%" top="80%" delay={0.5} duration={6} />
      <Particle size={3} left="40%" top="15%" delay={2.5} duration={7} />

      {/* ── Main content (text + CTAs) ── */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center pt-8 sm:pt-14">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.9 }}
          animate={inView ? { opacity: 1, y: 0, scale: 1 } : {}}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 text-sm mb-8 animate-glow-pulse"
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
          <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent animate-gradient-shift">
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

        {/* CTAs with hover effects */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link
            href="/signup"
            className="group relative inline-flex items-center gap-2 px-8 py-4 text-base font-semibold bg-gradient-to-r from-emerald-500 to-teal-600 rounded-xl hover:from-emerald-400 hover:to-teal-500 transition-all duration-300 shadow-2xl shadow-emerald-500/25 hover:shadow-emerald-500/50 hover:scale-[1.02] active:scale-[0.98]"
          >
            <span className="absolute inset-0 rounded-xl bg-white/0 hover:bg-white/10 transition-colors" />
            Start for Free
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
          <a
            href="#demo"
            className="group inline-flex items-center gap-2 px-8 py-4 text-base font-medium border border-white/10 rounded-xl hover:bg-white/5 hover:border-white/20 transition-all duration-300 text-white/70 hover:text-white hover:scale-[1.02] active:scale-[0.98]"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-500 group-hover:animate-pulse" />
            See Live Demo
          </a>
        </motion.div>
      </div>

      {/* ── The 3D laptop scene occupies the lower area ── */}
      {/* It's rendered inside the Hero3DCanvas above — the camera is positioned
          so the laptop sits naturally below the text content */}

      {/* ── Animated Stats (below the 3D scene) ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.8, delay: 0.8 }}
        className="relative z-10 mt-auto pb-16 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-3xl mx-auto w-full px-4"
      >
        {[
          { value: 10000, suffix: "+", label: "Chatbots Created" },
          { value: 50, suffix: "M+", label: "Messages Handled" },
          { value: 99.9, suffix: "%", label: "Uptime" },
          { value: 1, suffix: "s", prefix: "<", label: "Response Time" },
        ].map((stat) => (
          <motion.div
            key={stat.label}
            whileHover={{ scale: 1.05, y: -2 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className="text-center group cursor-default"
          >
            <div className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent group-hover:from-emerald-300 group-hover:to-cyan-300 transition-all">
              {stat.prefix || ""}
              {typeof stat.value === "number" && stat.value >= 100 ? (
                <AnimatedCounter target={stat.value} suffix={stat.suffix} />
              ) : (
                `${stat.value}${stat.suffix}`
              )}
            </div>
            <div className="text-sm text-white/40 mt-1 group-hover:text-white/60 transition-colors">
              {stat.label}
            </div>
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
}
