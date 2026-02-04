/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Turbopack configuration for Next.js 16.1.1
  turbopack: {},

  // Next.js 16.1.1 compatible configuration
  experimental: {
    optimizePackageImports: [
      // Optimize imports for faster startup
    ],
  },

  // Webpack configuration (only used when NOT using Turbopack)
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false, // Don't bundle fs module in client
      };
    }

    return config;
  },

  // Environment-specific settings
  env: {
    NEXT_PUBLIC_DEV_MEMORY_MONITORING: process.env.NODE_ENV === 'development' ? 'true' : 'false',
  },
};

module.exports = nextConfig
