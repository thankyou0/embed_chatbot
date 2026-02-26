"use client";

import { useRef, useState, useCallback, Suspense } from "react";
import { FloatingParticles } from "./floating-particles";
import {
  motion,
  useInView,
  useMotionValue,
  useSpring,
  useTransform,
} from "framer-motion";
import { Check, Sparkles } from "lucide-react";
import Link from "next/link";
import dynamic from "next/dynamic";

const PricingScene = dynamic(() => import("./3d/pricing-scene"), { ssr: false });

/* ═══════════════════════════════════════════════════════════════
   Plans Data
   ═══════════════════════════════════════════════════════════════ */
const plans = [
  {
    name: "Free",
    description: "Perfect for trying out",
    price: { monthly: "0", yearly: "0" },
    features: [
      "1 chatbot",
      "50 messages / month",
      "Website crawling",
      "Basic customization",
      "Community support",
    ],
    cta: "Get Started",
    href: "/signup",
    popular: false,
    gradient: "from-gray-500/20 to-gray-600/5",
    accentColor: "gray",
  },
  {
    name: "Pro",
    description: "For growing businesses",
    price: { monthly: "29", yearly: "24" },
    features: [
      "5 chatbots",
      "Unlimited messages",
      "All data sources",
      "Full customization",
      "Analytics dashboard",
      "Priority support",
      "Remove branding",
    ],
    cta: "Start Pro Trial",
    href: "/signup",
    popular: true,
    gradient: "from-emerald-500/20 to-teal-500/5",
    accentColor: "emerald",
  },
  {
    name: "Enterprise",
    description: "For large organizations",
    price: { monthly: "Custom", yearly: "Custom" },
    features: [
      "Unlimited chatbots",
      "Unlimited messages",
      "All data sources",
      "Full customization",
      "Advanced analytics",
      "Dedicated support",
      "Custom integrations",
      "Team management",
      "SSO & SAML",
    ],
    cta: "Contact Sales",
    href: "/signup",
    popular: false,
    gradient: "from-violet-500/20 to-purple-500/5",
    accentColor: "violet",
  },
];

/* ═══════════════════════════════════════════════════════════════
   3D Tilt Pricing Card
   ═══════════════════════════════════════════════════════════════ */
function PricingCard({
  plan,
  yearly,
  index,
}: {
  plan: (typeof plans)[0];
  yearly: boolean;
  index: number;
}) {
  const cardRef = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const rotateX = useSpring(useTransform(y, [-0.5, 0.5], [6, -6]), { stiffness: 200, damping: 20 });
  const rotateY = useSpring(useTransform(x, [-0.5, 0.5], [-6, 6]), { stiffness: 200, damping: 20 });

  const handleMouse = useCallback((e: React.MouseEvent) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    x.set((e.clientX - rect.left) / rect.width - 0.5);
    y.set((e.clientY - rect.top) / rect.height - 0.5);
  }, [x, y]);

  const handleLeave = useCallback(() => {
    x.set(0);
    y.set(0);
  }, [x, y]);

  const price = yearly ? plan.price.yearly : plan.price.monthly;
  const isCustom = price === "Custom";

  const borderColor = plan.popular
    ? "border-emerald-500/30"
    : plan.accentColor === "violet"
    ? "border-violet-500/15"
    : "border-white/10";

  return (
    <motion.div
      ref={cardRef}
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * 0.15 }}
      onMouseMove={handleMouse}
      onMouseLeave={handleLeave}
      style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
      className={`relative rounded-2xl border ${borderColor} bg-white/[0.02] backdrop-blur-sm p-6 md:p-8 flex flex-col h-full ${
        plan.popular ? "ring-1 ring-emerald-500/20 shadow-lg shadow-emerald-500/5" : ""
      }`}
    >
      {/* Popular badge */}
      {plan.popular && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5">
          <Sparkles className="w-3 h-3" />
          Most Popular
        </div>
      )}

      {/* Gradient overlay */}
      <div className={`absolute inset-0 rounded-2xl bg-gradient-to-b ${plan.gradient} pointer-events-none`} />

      <div className="relative z-10 flex flex-col h-full">
        {/* Plan name & description */}
        <div className="mb-6">
          <h3 className="text-xl font-bold text-white mb-1">{plan.name}</h3>
          <p className="text-sm text-white/40">{plan.description}</p>
        </div>

        {/* Price */}
        <div className="mb-6">
          {isCustom ? (
            <div className="text-3xl font-bold text-white">Custom</div>
          ) : (
            <div className="flex items-end gap-1">
              <span className="text-4xl font-bold text-white">${price}</span>
              <span className="text-white/40 mb-1">/mo</span>
            </div>
          )}
          {yearly && !isCustom && price !== "0" && (
            <p className="text-xs text-emerald-400 mt-1">Save 17% with yearly billing</p>
          )}
        </div>

        {/* Features */}
        <ul className="space-y-3 mb-8 flex-1">
          {plan.features.map((feature) => (
            <li key={feature} className="flex items-center gap-2.5 text-sm text-white/60">
              <Check className="w-4 h-4 text-emerald-500 flex-shrink-0" />
              {feature}
            </li>
          ))}
        </ul>

        {/* CTA */}
        <Link
          href={plan.href}
          className={`text-center py-3 rounded-xl font-semibold text-sm transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] ${
            plan.popular
              ? "bg-emerald-500 text-white hover:bg-emerald-400 shadow-lg shadow-emerald-500/20"
              : "bg-white/5 text-white/70 hover:bg-white/10 border border-white/10"
          }`}
        >
          {plan.cta}
        </Link>
      </div>
    </motion.div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Main Pricing Section
   ═══════════════════════════════════════════════════════════════ */
export default function Pricing3D() {
  const [yearly, setYearly] = useState(false);

  return (
    <section
      id="pricing"
      className="relative py-24 md:py-36 overflow-hidden"
      style={{ background: "linear-gradient(180deg, #0a0a0f 0%, #0d0d17 50%, #0a0a0f 100%)" }}
    >
      {/* 3D Background Scene */}
      <div className="absolute inset-0 z-0 opacity-40">
        <Suspense fallback={null}>
          <PricingScene />
        </Suspense>
      </div>

      {/* Floating particles */}
      <FloatingParticles count={8} color="#a855f7" color2="#10b981" sizeRange={[1, 2]} speed={0.6} />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-sm text-emerald-400 mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            Simple Pricing
          </span>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4">
            Choose Your{" "}
            <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">
              Plan
            </span>
          </h2>
          <p className="text-lg text-white/50 max-w-2xl mx-auto mb-8">
            Start free, upgrade when you need more. No hidden fees.
          </p>

          {/* Toggle */}
          <div className="inline-flex items-center gap-3 p-1.5 rounded-full bg-white/[0.03] border border-white/10">
            <button
              onClick={() => setYearly(false)}
              className={`relative px-5 py-2 rounded-full text-sm font-medium transition-all ${
                !yearly ? "text-white" : "text-white/40 hover:text-white/60"
              }`}
            >
              {!yearly && (
                <motion.div
                  layoutId="pricingToggle3d"
                  className="absolute inset-0 rounded-full bg-emerald-500/20 border border-emerald-500/30"
                />
              )}
              <span className="relative z-10">Monthly</span>
            </button>
            <button
              onClick={() => setYearly(true)}
              className={`relative px-5 py-2 rounded-full text-sm font-medium transition-all ${
                yearly ? "text-white" : "text-white/40 hover:text-white/60"
              }`}
            >
              {yearly && (
                <motion.div
                  layoutId="pricingToggle3d"
                  className="absolute inset-0 rounded-full bg-emerald-500/20 border border-emerald-500/30"
                />
              )}
              <span className="relative z-10">
                Yearly <span className="text-emerald-400 text-xs">-17%</span>
              </span>
            </button>
          </div>
        </motion.div>

        {/* Cards grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 max-w-5xl mx-auto">
          {plans.map((plan, i) => (
            <PricingCard key={plan.name} plan={plan} yearly={yearly} index={i} />
          ))}
        </div>
      </div>

      {/* Ambient glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/[0.02] rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-violet-500/[0.02] rounded-full blur-[100px] pointer-events-none" />
    </section>
  );
}
