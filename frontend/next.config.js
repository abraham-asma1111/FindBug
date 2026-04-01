/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8001',
    NEXT_PUBLIC_SIMULATION_API_URL: process.env.NEXT_PUBLIC_SIMULATION_API_URL || 'http://127.0.0.1:8001',
  },
  images: {
    domains: ['localhost'],
  },
}

module.exports = nextConfig
