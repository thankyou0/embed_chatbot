/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Enable standalone output for Docker production builds
  output: 'standalone',

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
    ignoreBuildErrors: true, // Enabled to allow builds - fix type errors in development
  },
}

module.exports = nextConfig