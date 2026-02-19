"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
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
  },
  {
    icon: Code2,
    title: "Embed in One Line",
    description:
      "Copy a single script tag and paste it into any website. Works with React, WordPress, Shopify, or plain HTML.",
    gradient: "from-indigo-500 to-purple-500",
  },
  {
    icon: Palette,
    title: "Fully Customizable",
    description:
      "Match your brand — custom colors, logo, welcome messages, position, and more. Make it yours.",
    gradient: "from-purple-500 to-pink-500",
  },
  {
    icon: MessageSquare,
    title: "Smart Conversations",
    description:
      "Powered by advanced LLMs with context awareness. Delivers accurate, helpful responses every time.",
    gradient: "from-pink-500 to-rose-500",
  },
  {
    icon: BarChart3,
    title: "Analytics & Insights",
    description:
      "Track conversations, popular questions, satisfaction rates, and user engagement in real-time.",
    gradient: "from-orange-500 to-amber-500",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description:
      "Enterprise-grade security with data encryption, access controls, and team permissions.",
    gradient: "from-green-500 to-emerald-500",
  },
  {
    icon: Database,
    title: "Knowledge Sources",
    description:
      "Connect multiple data sources — website crawling, file uploads, raw text, and structured Q&A pairs.",
    gradient: "from-teal-500 to-cyan-500",
  },
  {
    icon: Globe,
    title: "Multi-Bot Management",
    description:
      "Create and manage multiple chatbots from a single dashboard. Different bots for different purposes.",
    gradient: "from-violet-500 to-indigo-500",
  },
  {
    icon: Zap,
    title: "Instant Deployment",
    description:
      "Go live in minutes. No complex setup, no server management. Create, train, and deploy — that's it.",
    gradient: "from-amber-500 to-yellow-500",
  },
];

export function FeaturesSection() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="features" ref={ref} className="relative py-24 lg:py-32">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[2px] bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16 lg:mb-20"
        >
          <p className="text-sm font-medium text-indigo-400 tracking-wider uppercase mb-3">
            Features
          </p>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Everything You Need to{" "}
            <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
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
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.07 }}
              className="group relative p-6 lg:p-8 rounded-2xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.05] hover:border-white/10 transition-all duration-300"
            >
              {/* Icon */}
              <div
                className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-5 shadow-lg group-hover:scale-110 transition-transform duration-300`}
              >
                <feature.icon className="w-6 h-6 text-white" />
              </div>

              <h3 className="text-lg font-semibold text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-white/40 leading-relaxed">
                {feature.description}
              </p>

              {/* Hover gradient line */}
              <div
                className={`absolute bottom-0 left-6 right-6 h-[2px] rounded-full bg-gradient-to-r ${feature.gradient} opacity-0 group-hover:opacity-30 transition-opacity duration-300`}
              />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
