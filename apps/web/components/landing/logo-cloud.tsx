"use client";

import { motion, useInView } from "framer-motion";
import { useRef } from "react";

const logos = [
  { name: "React", icon: "⚛️" },
  { name: "WordPress", icon: "📝" },
  { name: "Shopify", icon: "🛍️" },
  { name: "Webflow", icon: "🌊" },
  { name: "Wix", icon: "✨" },
  { name: "Squarespace", icon: "◻️" },
  { name: "HTML/JS", icon: "🌐" },
  { name: "Next.js", icon: "▲" },
];

export function LogoCloud() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} className="relative py-16 border-y border-white/5 overflow-hidden">
      <motion.div
        initial={{ opacity: 0 }}
        animate={inView ? { opacity: 1 } : {}}
        transition={{ duration: 0.8 }}
      >
        <p className="text-center text-sm text-white/30 mb-8 uppercase tracking-widest">
          Works with every platform
        </p>

        {/* Infinite scrolling marquee */}
        <div className="relative">
          {/* Fade edges */}
          <div className="absolute left-0 top-0 bottom-0 w-24 bg-gradient-to-r from-[#0a0a0f] to-transparent z-10 pointer-events-none" />
          <div className="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-[#0a0a0f] to-transparent z-10 pointer-events-none" />

          <motion.div
            animate={{ x: ["0%", "-50%"] }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="flex gap-12 items-center w-max"
          >
            {/* Duplicate logos for seamless loop */}
            {[...logos, ...logos].map((logo, i) => (
              <div
                key={`${logo.name}-${i}`}
                className="flex items-center gap-2.5 text-white/30 hover:text-white/70 transition-colors duration-300 cursor-default flex-shrink-0 px-2"
              >
                <span className="text-2xl">{logo.icon}</span>
                <span className="text-sm font-medium whitespace-nowrap">{logo.name}</span>
              </div>
            ))}
          </motion.div>
        </div>
      </motion.div>
    </section>
  );
}
