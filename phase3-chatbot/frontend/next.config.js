/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Next.js 16.1.1 and Turbopack compatible configuration
  experimental: {
    // Memory optimizations for development
    serverExternalPackages: [
      // Add packages that should be externalized to save memory
    ],

    // Optimizations for faster builds
    optimizePackageImports: [
      // Optimize imports for faster startup
    ],

    // Turbopack-specific features
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
  },

  // Turbopack-compatible configuration
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      // Add plugins for memory monitoring during development
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
