"use client";

import React, { useRef, useState, useEffect, Suspense } from "react";
import dynamic from "next/dynamic";
import { motion, useInView, useScroll, useTransform } from "framer-motion";
import { FloatingParticles } from "./floating-particles";

const FeaturesScene = dynamic(() => import("./3d/features-scene"), {
  ssr: false,
  loading: () => null,
});

export function FeaturesSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const inView = useInView(sectionRef, { once: true, margin: "-100px" });

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });

  return (
    <section
      id="features"
      ref={sectionRef}
      className="relative py-24 lg:py-32 min-h-screen"
    >
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[2px] bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent" />
      </div>

      {/* Floating particles */}
      <FloatingParticles count={10} color="#10b981" color2="#06b6d4" sizeRange={[1, 2.5]} speed={0.7} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-8 lg:mb-12"
        >
          <motion.p
            initial={{ opacity: 0, scale: 0.9 }}
            animate={inView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.5 }}
            className="text-sm font-medium text-emerald-400 tracking-wider uppercase mb-3"
          >
            Features
          </motion.p>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Everything You Need to{" "}
            <span className="bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
              Engage Visitors
            </span>
          </h2>
          <p className="text-base md:text-lg text-white/40 max-w-2xl mx-auto">
            A complete platform to build, customize, and deploy AI chatbots that
            actually understand your business.
          </p>
        </motion.div>

        {/* 3D Feature Constellation */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={inView ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 1, delay: 0.3 }}
          className="w-full h-[350px] sm:h-[450px] md:h-[600px] relative"
        >
          <ScrollDrivenScene scrollYProgress={scrollYProgress} />
        </motion.div>

        {/* Hover hint */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 1.5, duration: 0.5 }}
          className="text-center text-xs text-white/20 mt-4"
        >
          Hover nodes for details
        </motion.p>
      </div>
    </section>
  );
}

/**
 * Bridge component that converts Framer Motion MotionValue into
 * a numeric prop for the R3F canvas.
 */
function ScrollDrivenScene({
  scrollYProgress,
}: {
  scrollYProgress: ReturnType<typeof useScroll>["scrollYProgress"];
}) {
  const progressValue = useTransform(scrollYProgress, [0.1, 0.8], [0, 1]);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const unsub = progressValue.on("change", (v: number) => {
      setProgress(Math.max(0, Math.min(1, v)));
    });
    return unsub;
  }, [progressValue]);

  return (
    <Suspense
      fallback={
        <div className="w-full h-full flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
        </div>
      }
    >
      <FeaturesScene scrollProgress={progress} />
    </Suspense>
  );
}
