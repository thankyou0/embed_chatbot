"use client";

import { useRef } from "react";
import dynamic from "next/dynamic";
import { Suspense } from "react";
import { motion, useInView } from "framer-motion";

const LogoCloudScene = dynamic(() => import("./3d/logo-cloud-scene"), {
  ssr: false,
  loading: () => null,
});

const platforms = [
  { name: "React", icon: "⚛️", color: "#61dafb" },
  { name: "WordPress", icon: "📝", color: "#21759b" },
  { name: "Shopify", icon: "🛍️", color: "#96bf48" },
  { name: "Webflow", icon: "🌊", color: "#4353ff" },
  { name: "Wix", icon: "✨", color: "#faad4d" },
  { name: "Squarespace", icon: "◼️", color: "#ffffff" },
  { name: "HTML/JS", icon: "🌐", color: "#f06529" },
  { name: "Next.js", icon: "▲", color: "#ffffff" },
  { name: "Vue", icon: "💚", color: "#42b883" },
  { name: "Angular", icon: "🔺", color: "#dd0031" },
];

const stats = [
  { value: "10+", label: "Platforms" },
  { value: "<30s", label: "Setup Time" },
  { value: "1 Line", label: "of Code" },
];

export function LogoCloud() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-50px" });

  return (
    <section
      ref={ref}
      className="relative py-16 md:py-28 border-y border-white/5 overflow-hidden"
      style={{ background: "linear-gradient(180deg, #0a0a0f 0%, #0d0d1a 50%, #0a0a0f 100%)" }}
    >
      <motion.div
        initial={{ opacity: 0 }}
        animate={inView ? { opacity: 1 } : {}}
        transition={{ duration: 0.8 }}
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
      >
        {/* Header */}
        <div className="text-center mb-4">
          <motion.span
            initial={{ opacity: 0, y: 10 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-sm text-emerald-400 mb-4"
          >
            🔌 Universal Integration
          </motion.span>
          <motion.h3
            initial={{ opacity: 0, y: 10 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-3"
          >
            Works with{" "}
            <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">
              Every Platform
            </span>
          </motion.h3>
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-base text-white/40 max-w-xl mx-auto"
          >
            One embed script. Every framework, CMS, and website builder. Hover over the nodes to explore.
          </motion.p>
        </div>

        {/* Stats row */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex justify-center gap-6 sm:gap-10 mb-6"
        >
          {stats.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={inView ? { opacity: 1, scale: 1 } : {}}
              transition={{ delay: 0.4 + i * 0.1, type: "spring" }}
              className="text-center"
            >
              <div className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
                {stat.value}
              </div>
              <div className="text-[11px] text-white/30 mt-0.5">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>

        {/* 3D Integration Galaxy — enhanced container */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={inView ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 1, delay: 0.3 }}
          className="relative w-full"
        >
          {/* Decorative ring behind canvas */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] sm:w-[400px] sm:h-[400px] md:w-[500px] md:h-[500px] rounded-full border border-emerald-500/[0.06] pointer-events-none" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[200px] h-[200px] sm:w-[280px] sm:h-[280px] md:w-[340px] md:h-[340px] rounded-full border border-teal-500/[0.04] pointer-events-none" />

          {/* Canvas area */}
          <div className="w-full h-[280px] sm:h-[360px] md:h-[450px] relative">
            <Suspense
              fallback={
                <div className="w-full h-full flex items-center justify-center">
                  <div className="w-8 h-8 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
                </div>
              }
            >
              <LogoCloudScene />
            </Suspense>
          </div>
        </motion.div>

        {/* Platform chip bar below the galaxy */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="flex flex-wrap justify-center gap-2 mt-6"
        >
          {platforms.map((p, i) => (
            <motion.div
              key={p.name}
              initial={{ opacity: 0, y: 10 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.9 + i * 0.05 }}
              className="group flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.06] hover:border-white/[0.12] transition-all duration-300 cursor-default"
            >
              <span className="text-xs">{p.icon}</span>
              <span className="text-[11px] text-white/40 font-medium group-hover:text-white/70 transition-colors">
                {p.name}
              </span>
              <div
                className="w-1 h-1 rounded-full opacity-40 group-hover:opacity-100 transition-opacity"
                style={{ backgroundColor: p.color }}
              />
            </motion.div>
          ))}
        </motion.div>

        {/* Bottom tagline */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 1.2, duration: 0.6 }}
          className="text-center mt-6"
        >
          <p className="text-xs text-white/20">
            ...and any website that supports a <span className="text-white/40 font-mono">&lt;script&gt;</span> tag
          </p>
        </motion.div>
      </motion.div>

      {/* Ambient background glows */}
      <div className="absolute top-1/3 left-1/4 w-80 h-80 bg-emerald-500/[0.03] rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/3 right-1/4 w-64 h-64 bg-cyan-500/[0.02] rounded-full blur-[80px] pointer-events-none" />
    </section>
  );
}
