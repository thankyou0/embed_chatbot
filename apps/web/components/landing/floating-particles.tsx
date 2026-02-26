"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";

interface FloatingParticlesProps {
  /** Number of particles (keep low for performance — 8-20 recommended) */
  count?: number;
  /** Primary color in hex */
  color?: string;
  /** Optional secondary color */
  color2?: string;
  /** Particle size range [min, max] in px */
  sizeRange?: [number, number];
  /** Animation speed multiplier (1 = default) */
  speed?: number;
  /** Additional class names for the container */
  className?: string;
}

/**
 * Lightweight CSS-animated floating particles.
 * Pure CSS animations — no JS frame loop, no layout thrash.
 * Usage: <FloatingParticles count={12} color="#10b981" />
 */
export function FloatingParticles({
  count = 12,
  color = "#10b981",
  color2,
  sizeRange = [1, 3],
  speed = 1,
  className = "",
}: FloatingParticlesProps) {
  const particles = useMemo(() => {
    return Array.from({ length: count }, (_, i) => {
      const size = sizeRange[0] + Math.random() * (sizeRange[1] - sizeRange[0]);
      const useSecondary = color2 && Math.random() > 0.5;
      return {
        id: i,
        size,
        x: Math.random() * 100,
        y: Math.random() * 100,
        duration: (3 + Math.random() * 4) / speed,
        delay: Math.random() * 3,
        color: useSecondary ? color2 : color,
        opacity: 0.1 + Math.random() * 0.25,
        drift: (Math.random() - 0.5) * 30,
      };
    });
  }, [count, color, color2, sizeRange, speed]);

  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full"
          style={{
            width: p.size,
            height: p.size,
            left: `${p.x}%`,
            top: `${p.y}%`,
            backgroundColor: p.color,
            opacity: 0,
          }}
          animate={{
            y: [0, -40 - Math.random() * 60, 0],
            x: [0, p.drift, 0],
            opacity: [0, p.opacity, 0],
            scale: [0.5, 1, 0.5],
          }}
          transition={{
            duration: p.duration,
            delay: p.delay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}
