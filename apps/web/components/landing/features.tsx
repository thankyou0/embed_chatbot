"use client";

import { useRef, useCallback } from "react";
import { motion, useInView, useMotionValue, useSpring, useTransform } from "framer-motion";
import {
  MessageSquare,
  Brain,
  Palette,
  Code2,
  BarChart3,
  Shield,
  Globe,
  Zap,
  Database,
} from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "Train on Your Data",
    description:
      "Upload PDFs, crawl websites, add Q&A pairs, or paste text. Your chatbot learns your business inside-out.",
    gradient: "from-blue-500 to-cyan-500",
    glow: "shadow-blue-500/20",
  },
  {
    icon: Code2,
    title: "Embed in One Line",
    description:
      "Copy a single script tag and paste it into any website. Works with React, WordPress, Shopify, or plain HTML.",
    gradient: "from-emerald-500 to-teal-500",
    glow: "shadow-emerald-500/20",
  },
  {
    icon: Palette,
    title: "Fully Customizable",
    description:
      "Match your brand — custom colors, logo, welcome messages, position, and more. Make it yours.",
    gradient: "from-violet-500 to-purple-500",
    glow: "shadow-violet-500/20",
  },
  {
    icon: MessageSquare,
    title: "Smart Conversations",
    description:
      "Powered by advanced LLMs with context awareness. Delivers accurate, helpful responses every time.",
    gradient: "from-pink-500 to-rose-500",
    glow: "shadow-pink-500/20",
  },
  {
    icon: BarChart3,
    title: "Analytics & Insights",
    description:
      "Track conversations, popular questions, satisfaction rates, and user engagement in real-time.",
    gradient: "from-orange-500 to-amber-500",
    glow: "shadow-orange-500/20",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description:
      "Enterprise-grade security with data encryption, access controls, and team permissions.",
    gradient: "from-green-500 to-emerald-500",
    glow: "shadow-green-500/20",
  },
  {
    icon: Database,
    title: "Knowledge Sources",
    description:
      "Connect multiple data sources — website crawling, file uploads, raw text, and structured Q&A pairs.",
    gradient: "from-teal-500 to-cyan-500",
    glow: "shadow-teal-500/20",
  },
  {
    icon: Globe,
    title: "Multi-Bot Management",
    description:
      "Create and manage multiple chatbots from a single dashboard. Different bots for different purposes.",
    gradient: "from-indigo-500 to-blue-500",
    glow: "shadow-indigo-500/20",
  },
  {
    icon: Zap,
    title: "Instant Deployment",
    description:
      "Go live in minutes. No complex setup, no server management. Create, train, and deploy — that's it.",
    gradient: "from-amber-500 to-yellow-500",
    glow: "shadow-amber-500/20",
  },
];

/* ────────── 3D Tilt Feature Card ────────── */
function FeatureCard({
  feature,
  index,
  inView,
}: {
  feature: (typeof features)[0];
  index: number;
  inView: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const rotateX = useSpring(useTransform(y, [-0.5, 0.5], [10, -10]), {
    stiffness: 200,
    damping: 25,
  });
  const rotateY = useSpring(useTransform(x, [-0.5, 0.5], [-10, 10]), {
    stiffness: 200,
    damping: 25,
  });
  const glowX = useSpring(useTransform(x, [-0.5, 0.5], [0, 100]), {
    stiffness: 200,
    damping: 25,
  });
  const glowY = useSpring(useTransform(y, [-0.5, 0.5], [0, 100]), {
    stiffness: 200,
    damping: 25,
  });

  const handleMouse = useCallback(
    (e: React.MouseEvent) => {
      if (!ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      x.set((e.clientX - rect.left) / rect.width - 0.5);
      y.set((e.clientY - rect.top) / rect.height - 0.5);
    },
    [x, y]
  );

  const handleLeave = useCallback(() => {
    x.set(0);
    y.set(0);
  }, [x, y]);

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay: index * 0.07 }}
      onMouseMove={handleMouse}
      onMouseLeave={handleLeave}
      style={{
        rotateX,
        rotateY,
        transformPerspective: 800,
      }}
      className="group relative preserve-3d"
    >
      <div className="relative p-6 lg:p-8 rounded-2xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.05] hover:border-white/10 transition-all duration-300 overflow-hidden h-full">
        {/* Mouse-follow glow */}
        <motion.div
          style={{
            left: glowX,
            top: glowY,
          }}
          className="absolute w-40 h-40 -translate-x-1/2 -translate-y-1/2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
        >
          <div className={`w-full h-full rounded-full bg-gradient-to-br ${feature.gradient} blur-3xl opacity-20`} />
        </motion.div>

        {/* Icon */}
        <div
          className={`relative w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-5 shadow-lg ${feature.glow} group-hover:scale-110 group-hover:shadow-xl transition-all duration-300`}
        >
          <feature.icon className="w-6 h-6 text-white" />
        </div>

        <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-white transition-colors">
          {feature.title}
        </h3>
        <p className="text-sm text-white/40 leading-relaxed group-hover:text-white/55 transition-colors">
          {feature.description}
        </p>

        {/* Bottom gradient line */}
        <div
          className={`absolute bottom-0 left-6 right-6 h-[2px] rounded-full bg-gradient-to-r ${feature.gradient} opacity-0 group-hover:opacity-40 transition-opacity duration-300`}
        />
      </div>
    </motion.div>
  );
}

export function FeaturesSection() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="features" ref={ref} className="relative py-24 lg:py-32">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[2px] bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16 lg:mb-20"
        >
          <motion.p
            initial={{ opacity: 0, scale: 0.9 }}
            animate={inView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.5 }}
            className="text-sm font-medium text-emerald-400 tracking-wider uppercase mb-3"
          >
            Features
          </motion.p>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Everything You Need to{" "}
            <span className="bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
              Engage Visitors
            </span>
          </h2>
          <p className="text-lg text-white/40 max-w-2xl mx-auto">
            A complete platform to build, customize, and deploy AI chatbots that
            actually understand your business.
          </p>
        </motion.div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <FeatureCard
              key={feature.title}
              feature={feature}
              index={i}
              inView={inView}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
