"use client";

import { useRef, Suspense } from "react";
import { motion, useInView } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import Link from "next/link";
import dynamic from "next/dynamic";

const CTAScene = dynamic(() => import("./3d/cta-scene"), { ssr: false });

export default function CTA3D() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} className="relative py-24 lg:py-32 overflow-hidden">
      {/* 3D Portal Background */}
      <div className="absolute inset-0 z-0">
        <Suspense fallback={null}>
          <CTAScene />
        </Suspense>
      </div>

      {/* Gradient overlays for readability */}
      <div className="absolute inset-0 z-[1] bg-gradient-to-b from-[#0a0a0f] via-transparent to-[#0a0a0f] opacity-60" />
      <div className="absolute inset-0 z-[1] bg-radial-gradient pointer-events-none" style={{
        background: "radial-gradient(ellipse at center, transparent 30%, #0a0a0f 80%)",
      }} />

      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={inView ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-sm text-emerald-400 mb-6"
        >
          <Sparkles className="w-3.5 h-3.5" />
          No credit card required
        </motion.div>

        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.15 }}
          className="text-3xl sm:text-4xl lg:text-6xl font-bold text-white mb-5"
        >
          Ready to Enter{" "}
          <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">
            The Future
          </span>
          ?
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.25 }}
          className="text-lg md:text-xl text-white/60 max-w-xl mx-auto mb-10"
        >
          Join thousands of businesses using EmbedChat to engage visitors,
          answer questions instantly, and convert more leads.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.35 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link
            href="/signup"
            className="group inline-flex items-center gap-2 px-8 py-4 bg-emerald-500 text-white font-semibold rounded-xl hover:bg-emerald-400 transition-all shadow-xl shadow-emerald-500/20 hover:shadow-2xl hover:shadow-emerald-500/30 hover:scale-[1.03] active:scale-[0.98]"
          >
            Get Started Free
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link
            href="/login"
            className="inline-flex items-center gap-2 px-8 py-4 border border-white/20 text-white/80 font-medium rounded-xl hover:bg-white/5 hover:border-white/30 transition-all hover:scale-[1.02] active:scale-[0.98] backdrop-blur-sm"
          >
            Sign In to Dashboard
          </Link>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="mt-8 text-sm text-white/30"
        >
          Free forever plan available · Setup in under 5 minutes · Works on any website
        </motion.p>
      </div>
    </section>
  );
}
