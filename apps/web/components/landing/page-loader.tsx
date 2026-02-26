"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";

export function PageLoader() {
  const [loading, setLoading] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    // Intercept all anchor clicks that navigate to other pages
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const anchor = target.closest("a");
      if (!anchor) return;

      const href = anchor.getAttribute("href");
      if (!href) return;

      // Only show loader for internal page navigations (not hash links)
      if (
        href.startsWith("/") &&
        !href.startsWith("/#") &&
        href !== pathname
      ) {
        setLoading(true);
      }
    };

    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, [pathname]);

  // Hide loader when path changes (navigation complete)
  useEffect(() => {
    setLoading(false);
  }, [pathname]);

  return (
    <AnimatePresence>
      {loading && (
        <>
          {/* Top loading bar */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed top-0 left-0 right-0 z-[100] h-[3px] bg-[#0a0a0f]/50"
          >
            <motion.div
              initial={{ width: "0%" }}
              animate={{ width: ["0%", "30%", "60%", "80%"] }}
              transition={{
                duration: 2,
                ease: "easeInOut",
                times: [0, 0.3, 0.6, 1],
              }}
              className="h-full bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400 rounded-r-full shadow-[0_0_15px_rgba(16,185,129,0.5)]"
            />
          </motion.div>

          {/* Full-screen overlay with professional spinner */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-[99] bg-[#0a0a0f]/60 backdrop-blur-sm flex items-center justify-center"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              className="flex flex-col items-center gap-4"
            >
              {/* Animated spinner ring */}
              <div className="relative w-12 h-12">
                <div className="absolute inset-0 rounded-full border-2 border-white/10" />
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    ease: "linear",
                  }}
                  className="absolute inset-0 rounded-full border-2 border-transparent border-t-emerald-500 border-r-teal-400"
                />
                <motion.div
                  animate={{ rotate: -360 }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: "linear",
                  }}
                  className="absolute inset-1 rounded-full border-2 border-transparent border-b-cyan-400 border-l-emerald-300"
                />
              </div>

              {/* Loading text */}
              <motion.p
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="text-sm text-white/50 font-medium tracking-wider"
              >
                Loading...
              </motion.p>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
