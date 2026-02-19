"use client";

import { useRef, useState } from "react";
import { motion, useInView } from "framer-motion";
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

export function PricingSection() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });
  const [yearly, setYearly] = useState(false);

  return (
    <section
      id="pricing"
      ref={ref}
      className="relative py-24 lg:py-32 bg-gradient-to-b from-transparent via-indigo-500/[0.03] to-transparent"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <p className="text-sm font-medium text-indigo-400 tracking-wider uppercase mb-3">
            Pricing
          </p>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Simple,{" "}
            <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
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
              className={`px-4 py-2 text-sm rounded-full transition-all ${
                !yearly
                  ? "bg-indigo-600 text-white shadow-lg"
                  : "text-white/50 hover:text-white/70"
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setYearly(true)}
              className={`px-4 py-2 text-sm rounded-full transition-all flex items-center gap-1.5 ${
                yearly
                  ? "bg-indigo-600 text-white shadow-lg"
                  : "text-white/50 hover:text-white/70"
              }`}
            >
              Yearly
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-green-500/20 text-green-400">
                -20%
              </span>
            </button>
          </div>
        </motion.div>

        {/* Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: i * 0.1 }}
              className={`relative p-6 lg:p-8 rounded-2xl border transition-all ${
                plan.popular
                  ? "border-indigo-500/40 bg-indigo-500/[0.08] scale-[1.02] shadow-xl shadow-indigo-500/10"
                  : "border-white/5 bg-white/[0.02] hover:border-white/10"
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 text-xs font-medium text-white">
                  <Sparkles className="w-3 h-3" />
                  Most Popular
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-xl font-bold text-white mb-1">
                  {plan.name}
                </h3>
                <p className="text-sm text-white/40">{plan.description}</p>
              </div>

              <div className="mb-6">
                {plan.price.monthly === "Custom" ? (
                  <div className="text-3xl font-bold text-white">Custom</div>
                ) : (
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold text-white">
                      ${yearly ? plan.price.yearly : plan.price.monthly}
                    </span>
                    <span className="text-white/30 text-sm">/mo</span>
                  </div>
                )}
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2.5">
                    <Check className="w-4 h-4 text-indigo-400 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-white/60">{f}</span>
                  </li>
                ))}
              </ul>

              <Link
                href={plan.href}
                className={`block w-full text-center py-3 rounded-xl text-sm font-medium transition-all ${
                  plan.popular
                    ? "bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40"
                    : "border border-white/10 text-white/70 hover:bg-white/5 hover:text-white"
                }`}
              >
                {plan.cta}
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
