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
    <section ref={ref} className="relative py-16 border-y border-white/5">
      <motion.div
        initial={{ opacity: 0 }}
        animate={inView ? { opacity: 1 } : {}}
        transition={{ duration: 0.8 }}
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
      >
        <p className="text-center text-sm text-white/30 mb-8 uppercase tracking-widest">
          Works with every platform
        </p>
        <div className="flex flex-wrap justify-center items-center gap-8 md:gap-12">
          {logos.map((logo, i) => (
            <motion.div
              key={logo.name}
              initial={{ opacity: 0, y: 10 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.05 }}
              className="flex items-center gap-2 text-white/30 hover:text-white/60 transition-colors"
            >
              <span className="text-xl">{logo.icon}</span>
              <span className="text-sm font-medium">{logo.name}</span>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </section>
  );
}
