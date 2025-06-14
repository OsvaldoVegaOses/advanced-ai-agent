/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://advanced-ai-agent-0003.azurewebsites.net',
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
        ],
      },
    ]
  },
  // Para Azure Static Web Apps, usar output estático
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  // Optimizaciones para Azure
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  experimental: {
    optimizePackageImports: ['@heroicons/react']
  }
}

module.exports = nextConfig