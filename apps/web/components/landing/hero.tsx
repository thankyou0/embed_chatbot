"use client";

import { useRef, useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { motion, useInView, useMotionValue, useSpring, useTransform } from "framer-motion";
import { ArrowRight, Sparkles, MessageSquare } from "lucide-react";

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

/* ────────── 3D floating shape ────────── */
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

/* ────────── 3D Tilt Card for browser mockup ────────── */
function TiltCard({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const rotateX = useSpring(useTransform(y, [-0.5, 0.5], [8, -8]), { stiffness: 150, damping: 20 });
  const rotateY = useSpring(useTransform(x, [-0.5, 0.5], [-8, 8]), { stiffness: 150, damping: 20 });

  const handleMouse = useCallback(
    (e: React.MouseEvent) => {
      if (!ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      const px = (e.clientX - rect.left) / rect.width - 0.5;
      const py = (e.clientY - rect.top) / rect.height - 0.5;
      x.set(px);
      y.set(py);
    },
    [x, y]
  );

  const handleLeave = useCallback(() => {
    x.set(0);
    y.set(0);
  }, [x, y]);

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouse}
      onMouseLeave={handleLeave}
      style={{ rotateX, rotateY, transformPerspective: 1200 }}
      className="preserve-3d"
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
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      setMousePos({
        x: (e.clientX / window.innerWidth - 0.5) * 2,
        y: (e.clientY / window.innerHeight - 0.5) * 2,
      });
    };
    window.addEventListener("mousemove", handleMove);
    return () => window.removeEventListener("mousemove", handleMove);
  }, []);

  return (
    <section
      ref={ref}
      className="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden perspective-1500"
    >
      {/* ── Animated background gradients with parallax ── */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          animate={{
            x: mousePos.x * 30,
            y: mousePos.y * 20,
          }}
          transition={{ type: "spring", stiffness: 50, damping: 30 }}
          className="absolute top-1/4 -left-1/4 w-[600px] h-[600px] bg-emerald-500/20 rounded-full blur-[120px]"
        />
        <motion.div
          animate={{
            x: mousePos.x * -20,
            y: mousePos.y * -15,
          }}
          transition={{ type: "spring", stiffness: 50, damping: 30 }}
          className="absolute bottom-1/4 -right-1/4 w-[500px] h-[500px] bg-teal-500/20 rounded-full blur-[120px]"
        />
        <motion.div
          animate={{
            x: mousePos.x * 15,
            y: mousePos.y * 25,
          }}
          transition={{ type: "spring", stiffness: 50, damping: 30 }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-cyan-500/10 rounded-full blur-[100px]"
        />
      </div>

      {/* ── Grid overlay ── */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      {/* ── Floating 3D geometric shapes ── */}
      <FloatingShape className="top-[15%] left-[8%] hidden lg:block" delay={0.5}>
        <div className="w-16 h-16 animate-float-slow">
          <div className="w-full h-full rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/20 backdrop-blur-sm rotate-12 shadow-lg shadow-emerald-500/10" />
        </div>
      </FloatingShape>

      <FloatingShape className="top-[20%] right-[10%] hidden lg:block" delay={0.8}>
        <div className="w-12 h-12 animate-float-medium [animation-delay:1s]">
          <div className="w-full h-full rounded-full bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/20 backdrop-blur-sm shadow-lg shadow-cyan-500/10" />
        </div>
      </FloatingShape>

      <FloatingShape className="bottom-[25%] left-[5%] hidden lg:block" delay={1.0}>
        <div className="w-10 h-10 animate-float-medium [animation-delay:2s]">
          <div className="w-full h-full bg-gradient-to-br from-teal-500/20 to-emerald-500/20 border border-teal-500/20 backdrop-blur-sm shadow-lg shadow-teal-500/10"
            style={{ clipPath: "polygon(50% 0%, 100% 100%, 0% 100%)" }}
          />
        </div>
      </FloatingShape>

      <FloatingShape className="top-[40%] right-[5%] hidden lg:block" delay={1.2}>
        <div className="w-8 h-8 animate-spin-slow">
          <div className="w-full h-full rounded-sm bg-gradient-to-br from-pink-500/15 to-rose-500/15 border border-pink-500/15 backdrop-blur-sm rotate-45 shadow-lg shadow-pink-500/10" />
        </div>
      </FloatingShape>

      <FloatingShape className="bottom-[35%] right-[15%] hidden lg:block" delay={1.4}>
        <div className="w-14 h-14 animate-float-slow [animation-delay:3s]">
          <div className="w-full h-full rounded-2xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/15 backdrop-blur-sm -rotate-12 shadow-lg shadow-amber-500/10" />
        </div>
      </FloatingShape>

      {/* ── 3D Orbiting ring ── */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] hidden lg:block pointer-events-none">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
          className="w-full h-full rounded-full border border-emerald-500/5"
        />
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
          className="absolute inset-8 rounded-full border border-teal-500/5"
        />
      </div>

      {/* ── Floating particles ── */}
      <Particle size={4} left="15%" top="30%" delay={0} duration={6} />
      <Particle size={3} left="75%" top="20%" delay={1} duration={7} />
      <Particle size={5} left="85%" top="60%" delay={2} duration={5} />
      <Particle size={3} left="25%" top="70%" delay={1.5} duration={8} />
      <Particle size={4} left="60%" top="80%" delay={0.5} duration={6} />
      <Particle size={3} left="40%" top="15%" delay={2.5} duration={7} />

      {/* ── Main content ── */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
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

        {/* ── 3D Tilt Browser Mockup ── */}
        <motion.div
          initial={{ opacity: 0, y: 60, scale: 0.95 }}
          animate={inView ? { opacity: 1, y: 0, scale: 1 } : {}}
          transition={{ duration: 1, delay: 0.5, ease: "easeOut" }}
          className="relative mt-16 lg:mt-20 mx-auto max-w-5xl"
        >
          {/* Glow effect behind the mockup */}
          <div className="absolute -inset-4 bg-gradient-to-r from-emerald-500/20 via-teal-500/20 to-cyan-500/20 rounded-3xl blur-3xl animate-pulse [animation-duration:4s]" />

          <TiltCard>
            {/* Browser mockup */}
            <div className="relative rounded-2xl border border-white/10 bg-[#111118] overflow-hidden shadow-2xl shadow-emerald-500/10">
              {/* Browser chrome */}
              <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5 bg-[#0d0d14]">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/60 hover:bg-red-500 transition-colors cursor-pointer" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/60 hover:bg-yellow-500 transition-colors cursor-pointer" />
                  <div className="w-3 h-3 rounded-full bg-green-500/60 hover:bg-green-500 transition-colors cursor-pointer" />
                </div>
                <div className="flex-1 mx-4">
                  <div className="max-w-sm mx-auto px-3 py-1 rounded-md bg-white/5 text-white/30 text-xs text-center flex items-center justify-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500/60 flex items-center justify-center">
                      <span className="text-[6px]">🔒</span>
                    </div>
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
                  <motion.div
                    animate={{ y: [0, -6, 0] }}
                    transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                    className="relative"
                  >
                    {/* Notification badge */}
                    <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-[10px] font-bold z-10 animate-bounce [animation-duration:2s]">
                      1
                    </div>

                    {/* Chat popup */}
                    <div className="w-[280px] sm:w-[320px] rounded-2xl border border-white/10 bg-[#1a1a2e] shadow-2xl shadow-emerald-500/10 overflow-hidden mb-3">
                      {/* Chat header */}
                      <div className="px-4 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                          <MessageSquare className="w-4 h-4 text-white" />
                        </div>
                        <div>
                          <div className="text-sm font-semibold text-white">AI Assistant</div>
                          <div className="text-[10px] text-white/70 flex items-center gap-1">
                            <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
                            Online
                          </div>
                        </div>
                      </div>

                      {/* Chat messages */}
                      <div className="p-4 space-y-3">
                        <div className="flex gap-2">
                          <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex-shrink-0 flex items-center justify-center">
                            <MessageSquare className="w-3 h-3 text-emerald-400" />
                          </div>
                          <div className="px-3 py-2 rounded-xl rounded-tl-sm bg-white/5 text-sm text-white/80 max-w-[220px]">
                            Hi! 👋 How can I help you today?
                          </div>
                        </div>
                        <div className="flex justify-end">
                          <div className="px-3 py-2 rounded-xl rounded-tr-sm bg-emerald-600 text-sm text-white max-w-[220px]">
                            What are your pricing plans?
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex-shrink-0 flex items-center justify-center">
                            <MessageSquare className="w-3 h-3 text-emerald-400" />
                          </div>
                          <div className="px-3 py-2 rounded-xl rounded-tl-sm bg-white/5 text-sm text-white/80 max-w-[220px]">
                            <TypingIndicator />
                          </div>
                        </div>
                      </div>

                      {/* Chat input */}
                      <div className="px-4 pb-4">
                        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 border border-white/10">
                          <span className="text-sm text-white/30 flex-1">Type a message...</span>
                          <div className="w-6 h-6 rounded-md bg-emerald-600 flex items-center justify-center hover:bg-emerald-500 transition-colors cursor-pointer">
                            <ArrowRight className="w-3 h-3 text-white" />
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </div>
            </div>
          </TiltCard>
        </motion.div>

        {/* ── Animated Stats ── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-3xl mx-auto"
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
      </div>
    </section>
  );
}

/* ────────── Typing dots ────────── */
function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 py-1 px-1">
      {[0, 0.2, 0.4].map((delay) => (
        <motion.div
          key={delay}
          animate={{ opacity: [0.3, 1, 0.3], scale: [0.8, 1, 0.8] }}
          transition={{ duration: 1.2, repeat: Infinity, delay }}
          className="w-1.5 h-1.5 bg-emerald-400/60 rounded-full"
        />
      ))}
    </div>
  );
}
