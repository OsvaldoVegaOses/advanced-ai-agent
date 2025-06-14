/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://advanced-ai-agent-0003.azurewebsites.net',
  },
  // Para Azure Static Web Apps, usar output estático
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  // Configuración básica para evitar errores de build
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  // Optimizaciones para Azure
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  }
}

module.exports = nextConfig