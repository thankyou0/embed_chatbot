/** @type {import('next').NextConfig} */

const nextConfig = {
  reactStrictMode: true,

  // Enable standalone output for Docker production builds
  output: "standalone",

  // Disable x-powered-by header for security
  poweredByHeader: false,

  // Transpile Three.js packages for Next.js compatibility
  transpilePackages: ["three", "@react-three/fiber", "@react-three/drei"],

  // Disable ESLint during builds (for production deployment)
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Disable TypeScript checking during builds (saves memory)
  typescript: {
    ignoreBuildErrors: true,
  },

  // Reduce memory usage during dev compilation
  experimental: {
    // Use lighter-weight page compilation — only compile pages on demand
    workerThreads: false,
    cpus: 1,
  },

  // Webpack: controlled file-watching for Docker bind-mounts (Windows 9P).
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        // Ignore heavy/irrelevant trees so Watchpack doesn't scandir them
        ignored: ["**/node_modules/**", "**/.git/**", "**/.next/**"],
        // Batch rapid changes into one recompilation
        aggregateTimeout: 800,
      };
      // Reduce parallel compilation to save memory
      config.parallelism = 5;
    }
    return config;
  },
};

module.exports = nextConfig;
