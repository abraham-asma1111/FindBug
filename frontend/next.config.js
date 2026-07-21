/** @type {import('next').NextConfig} */
const labPort = process.env.SIMULATION_LAB_PORT || '5050'

const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8002',
    NEXT_PUBLIC_SIMULATION_API_URL: process.env.NEXT_PUBLIC_SIMULATION_API_URL || 'http://127.0.0.1:8002',
  },
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/lab-sandbox/:path*',
        destination: `http://127.0.0.1:${labPort}/:path*`,
      },
      // Lab iframe HTML references /static/* on port 3000 — proxy to academy-lab
      {
        source: '/static/:path*',
        destination: `http://127.0.0.1:${labPort}/static/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
