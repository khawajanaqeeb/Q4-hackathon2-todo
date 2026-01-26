/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Turbopack-specific optimizations for development
  experimental: {
    // Memory optimizations for development
    serverExternalPackages: [
      // Add packages that should be externalized to save memory
    ],

    // Optimizations for faster builds
    optimizePackageImports: [
      // Optimize imports for faster startup
    ],
  },

  // Webpack configuration for development memory management
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      // Add plugins for memory monitoring during development
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false, // Don't bundle fs module in client
      };

      // Reduce memory footprint in development
      if (process.env.NODE_ENV === 'development') {
        // Add memory monitoring plugin if available
        config.optimization = {
          ...config.optimization,
          splitChunks: {
            chunks: 'all',
            cacheGroups: {
              // Separate auth-related chunks for easier debugging
              auth: {
                test: /[\\/]src[\\/]lib[\\/]auth/,
                name: 'auth',
                chunks: 'all',
                priority: 10,
              },
              // Vendor chunk for dependencies
              vendor: {
                test: /[\\/]node_modules[\\/]/,
                name: 'vendors',
                chunks: 'all',
                priority: 5,
              }
            }
          }
        };
      }
    }

    return config;
  },

  // Environment-specific settings
  env: {
    NEXT_PUBLIC_DEV_MEMORY_MONITORING: process.env.NODE_ENV === 'development' ? 'true' : 'false',
  },

  // Development-specific optimizations
  // Enable faster refresh - this is now enabled by default in Next.js 14+
  // fastRefresh is deprecated in newer versions
};

module.exports = nextConfig
