"use client";

import { useRef, useState, useCallback } from "react";
import {
  motion,
  useInView,
  useMotionValue,
  useSpring,
  useTransform,
  AnimatePresence,
} from "framer-motion";
import { Check, Sparkles } from "lucide-react";
import Link from "next/link";

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
  },
];

/* ── 3D hover tilt for pricing cards ── */
function PricingCard({
  plan,
  yearly,
  index,
}: {
  plan: (typeof plans)[number];
  yearly: boolean;
  index: number;
}) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotateX = useSpring(useTransform(y, [-0.5, 0.5], [6, -6]), {
    stiffness: 200,
    damping: 20,
  });
  const rotateY = useSpring(useTransform(x, [-0.5, 0.5], [-6, 6]), {
    stiffness: 200,
    damping: 20,
  });

  const onMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      const rect = e.currentTarget.getBoundingClientRect();
      x.set((e.clientX - rect.left) / rect.width - 0.5);
      y.set((e.clientY - rect.top) / rect.height - 0.5);
    },
    [x, y]
  );
  const onLeave = useCallback(() => {
    x.set(0);
    y.set(0);
  }, [x, y]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay: index * 0.12 }}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      style={{ rotateX, rotateY }}
      className={`perspective-1000 preserve-3d relative p-6 lg:p-8 rounded-2xl border transition-all duration-300 ${
        plan.popular
          ? "border-emerald-500/40 bg-emerald-500/[0.08] shadow-xl shadow-emerald-500/10"
          : "border-white/5 bg-white/[0.02] hover:border-white/10 hover:shadow-lg hover:shadow-emerald-500/5"
      }`}
    >
      {plan.popular && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4, type: "spring" }}
          className="absolute -top-3 left-1/2 -translate-x-1/2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gradient-to-r from-emerald-500 to-teal-600 text-xs font-medium text-white"
        >
          <Sparkles className="w-3 h-3" />
          Most Popular
        </motion.div>
      )}

      <div className="mb-6">
        <h3 className="text-xl font-bold text-white mb-1">{plan.name}</h3>
        <p className="text-sm text-white/40">{plan.description}</p>
      </div>

      <div className="mb-6">
        {plan.price.monthly === "Custom" ? (
          <div className="text-3xl font-bold text-white">Custom</div>
        ) : (
          <div className="flex items-baseline gap-1">
            <AnimatePresence mode="wait">
              <motion.span
                key={yearly ? "y" : "m"}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                transition={{ duration: 0.25 }}
                className="text-4xl font-bold text-white"
              >
                ${yearly ? plan.price.yearly : plan.price.monthly}
              </motion.span>
            </AnimatePresence>
            <span className="text-white/30 text-sm">/mo</span>
          </div>
        )}
      </div>

      <ul className="space-y-3 mb-8">
        {plan.features.map((f, fi) => (
          <motion.li
            key={f}
            initial={{ opacity: 0, x: -10 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.1 + fi * 0.04 }}
            className="flex items-start gap-2.5"
          >
            <Check className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
            <span className="text-sm text-white/60">{f}</span>
          </motion.li>
        ))}
      </ul>

      <Link
        href={plan.href}
        className={`block w-full text-center py-3 rounded-xl text-sm font-medium transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] ${
          plan.popular
            ? "bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40"
            : "border border-white/10 text-white/70 hover:bg-white/5 hover:text-white"
        }`}
      >
        {plan.cta}
      </Link>
    </motion.div>
  );
}

export function PricingSection() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });
  const [yearly, setYearly] = useState(false);

  return (
    <section
      id="pricing"
      ref={ref}
      className="relative py-24 lg:py-32 bg-gradient-to-b from-transparent via-emerald-500/[0.03] to-transparent"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <p className="text-sm font-medium text-emerald-400 tracking-wider uppercase mb-3">
            Pricing
          </p>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Simple,{" "}
            <span className="bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
              Transparent
            </span>{" "}
            Pricing
          </h2>
          <p className="text-lg text-white/40 max-w-xl mx-auto mb-8">
            Start free. Upgrade when you need more.
          </p>

          {/* Toggle */}
          <div className="inline-flex items-center gap-3 p-1 rounded-full border border-white/10 bg-white/5">
            <button
              onClick={() => setYearly(false)}
              className={`relative px-4 py-2 text-sm rounded-full transition-all ${
                !yearly ? "text-white" : "text-white/50 hover:text-white/70"
              }`}
            >
              {!yearly && (
                <motion.div
                  layoutId="pricingToggle"
                  className="absolute inset-0 bg-emerald-600 rounded-full shadow-lg"
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
              <span className="relative z-10">Monthly</span>
            </button>
            <button
              onClick={() => setYearly(true)}
              className={`relative px-4 py-2 text-sm rounded-full transition-all flex items-center gap-1.5 ${
                yearly ? "text-white" : "text-white/50 hover:text-white/70"
              }`}
            >
              {yearly && (
                <motion.div
                  layoutId="pricingToggle"
                  className="absolute inset-0 bg-emerald-600 rounded-full shadow-lg"
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
              <span className="relative z-10 flex items-center gap-1.5">
                Yearly
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-green-500/20 text-green-400">
                  -20%
                </span>
              </span>
            </button>
          </div>
        </motion.div>

        {/* Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto items-start">
          {plans.map((plan, i) => (
            <PricingCard key={plan.name} plan={plan} yearly={yearly} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
