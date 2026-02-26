"use client";

import { LandingNavbar } from "@/components/landing/navbar";
import { HeroSection } from "@/components/landing/hero-3d";
import { LogoCloud } from "@/components/landing/logo-cloud-3d";
import { FeaturesSection } from "@/components/landing/features-3d";
import HowItWorks3D from "@/components/landing/how-it-works-3d";
import Demo3D from "@/components/landing/demo-3d";
import Pricing3D from "@/components/landing/pricing-3d";
import { FAQSection } from "@/components/landing/faq";
import CTA3D from "@/components/landing/cta-3d";
import { Footer } from "@/components/landing/footer";
import { PageLoader } from "@/components/landing/page-loader";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white overflow-x-hidden">
      <PageLoader />
      <LandingNavbar />
      <HeroSection />
      <LogoCloud />
      <FeaturesSection />
      <HowItWorks3D />
      <Demo3D />
      <Pricing3D />
      <FAQSection />
      <CTA3D />
      <Footer />
    </div>
  );
}
