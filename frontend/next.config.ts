import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  images: {
    unoptimized: false,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
};

export default nextConfig;


