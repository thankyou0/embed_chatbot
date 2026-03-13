import { LandingNavbar } from "@/components/landing/navbar";
import { HeroSection } from "@/components/landing/hero-3d";
import { LogoCloud } from "@/components/landing/logo-cloud-3d";
import { FeaturesSection } from "@/components/landing/features-3d";
import { FAQSection } from "@/components/landing/faq";
import { Footer } from "@/components/landing/footer";
import { PageLoader } from "@/components/landing/page-loader";
import { LazyBelowFold } from "@/components/landing/lazy-below-fold";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white overflow-x-hidden">
      <PageLoader />
      <LandingNavbar />
      <HeroSection />
      <LogoCloud />
      <FeaturesSection />
      {/* Below-the-fold 3D sections lazy-loaded for faster initial paint */}
      <LazyBelowFold />
      <FAQSection />
      <Footer />
    </div>
  );
}
