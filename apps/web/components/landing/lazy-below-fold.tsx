"use client";

import dynamic from "next/dynamic";

// Lazy-load heavy 3D sections — JS chunks are only fetched
// when the browser is idle or the user scrolls near them.
const HowItWorks3D = dynamic(
  () => import("@/components/landing/how-it-works-3d"),
  { ssr: false, loading: () => <SectionPlaceholder /> },
);

const Demo3D = dynamic(() => import("@/components/landing/demo-3d"), {
  ssr: false,
  loading: () => <SectionPlaceholder />,
});

const Pricing3D = dynamic(() => import("@/components/landing/pricing-3d"), {
  ssr: false,
  loading: () => <SectionPlaceholder />,
});

const CTA3D = dynamic(() => import("@/components/landing/cta-3d"), {
  ssr: false,
  loading: () => <SectionPlaceholder />,
});

function SectionPlaceholder() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent" />
    </div>
  );
}

export function LazyBelowFold() {
  return (
    <>
      <HowItWorks3D />
      <Demo3D />
      <Pricing3D />
      <CTA3D />
    </>
  );
}
