/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Enable standalone output for Docker production builds
  output: 'standalone',

  // Disable x-powered-by header for security
  poweredByHeader: false,
}

module.exports = nextConfig
