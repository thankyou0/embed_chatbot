"use client";

import Link from "next/link";
import { MessageSquare } from "lucide-react";

const footerLinks = {
  Product: [
    { label: "Features", href: "#features" },
    { label: "Pricing", href: "#pricing" },
    { label: "Demo", href: "#demo" },
    { label: "How It Works", href: "#how-it-works" },
  ],
  Resources: [
    { label: "Documentation", href: "#" },
    { label: "API Reference", href: "#" },
    { label: "Blog", href: "#" },
    { label: "Changelog", href: "#" },
  ],
  Company: [
    { label: "About", href: "#" },
    { label: "Contact", href: "#" },
    { label: "Privacy Policy", href: "#" },
    { label: "Terms of Service", href: "#" },
  ],
  Account: [
    { label: "Sign In", href: "/login" },
    { label: "Sign Up", href: "/signup" },
    { label: "Dashboard", href: "/dashboard/chatbots" },
  ],
};

export function Footer() {
  return (
    <footer className="border-t border-white/5 bg-[#07070b]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8">
          {/* Brand column */}
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <MessageSquare className="h-4 w-4 text-white" />
              </div>
              <span className="text-base font-bold text-white">EmbedChat</span>
            </Link>
            <p className="text-sm text-white/30 leading-relaxed">
              AI-powered chatbot platform. Train on your data, embed anywhere,
              engage visitors 24/7.
            </p>
          </div>

          {/* Link columns */}
          {Object.entries(footerLinks).map(([title, links]) => (
            <div key={title}>
              <h4 className="text-sm font-semibold text-white/60 mb-4">
                {title}
              </h4>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-white/30 hover:text-white/60 transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom */}
        <div className="mt-12 pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-white/20">
            © {new Date().getFullYear()} EmbedChat. All rights reserved.
          </p>
          <div className="flex items-center gap-4">
            <a
              href="#"
              className="text-white/20 hover:text-white/50 transition-colors text-sm"
            >
              Twitter
            </a>
            <a
              href="#"
              className="text-white/20 hover:text-white/50 transition-colors text-sm"
            >
              GitHub
            </a>
            <a
              href="#"
              className="text-white/20 hover:text-white/50 transition-colors text-sm"
            >
              Discord
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
