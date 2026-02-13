/** @type {import('next').NextConfig} */

const nextConfig = {
  reactStrictMode: true,

  // Enable standalone output for Docker production builds
  output: "standalone",

  // Disable x-powered-by header for security
  poweredByHeader: false,

  // Disable ESLint during builds (for production deployment)
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },

  // Optional: Also disable TypeScript errors during build if needed
  typescript: {
    // Warning: This allows production builds to successfully complete even if
    // your project has type errors.
    // ignoreBuildErrors: true, // Uncomment if you have TypeScript errors
  },
  experimental: {
    instrumentationHook: true,
  },
};

// Conditionally apply Sentry config if available
let finalConfig = nextConfig;
try {
  const { withSentryConfig } = require("@sentry/nextjs");
  finalConfig = withSentryConfig(
    nextConfig,
    {
      silent: true,
    },
    {
      disableLogger: true,
    },
  );
} catch (e) {
  // Sentry not installed, continue without it
  console.log("Sentry not available, continuing without monitoring");
}

module.exports = finalConfig;
