/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL: process.env.NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL,
    NEXT_PUBLIC_OPENAI_DOMAIN_KEY: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY,
  },
};

module.exports = nextConfig;