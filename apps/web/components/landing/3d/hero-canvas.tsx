"use client";

import dynamic from "next/dynamic";
import { Suspense } from "react";

// Dynamically import the 3D scene to avoid SSR issues with Three.js
const HeroScene = dynamic(() => import("./hero-scene"), {
  ssr: false,
  loading: () => null,
});

/**
 * Wrapper that lazy-loads the 3D hero scene.
 * Falls back to nothing (the existing 2D hero remains visible underneath).
 */
export function Hero3DCanvas() {
  return (
    <Suspense fallback={null}>
      <HeroScene />
    </Suspense>
  );
}
