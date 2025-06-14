'use client';

import { useEffect, useState } from 'react';

interface HealthStatus {
  status: string;
  service: string;
  version: string;
}

export default function SimplePage() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      setIsChecking(true);
      const response = await fetch('https://advanced-ai-agent-0003.azurewebsites.net/health');
      
      if (response.ok) {
        const status = await response.json();
        setHealthStatus(status);
      } else {
        throw new Error('Backend not responding');
      }
    } catch (error) {
      setHealthStatus({
        status: 'unhealthy',
        service: 'Advanced AI Agent',
        version: '1.0.0',
      });
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🤖 Advanced AI Agent
          </h1>
          <p className="text-gray-600">
            Sistema de AI inteligente desplegado en Azure
          </p>
        </div>

        <div className="space-y-4">
          {/* Estado de conexión */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <span className="font-medium text-gray-700">Estado del Backend:</span>
            <div className="flex items-center space-x-2">
              {isChecking ? (
                <>
                  <div className="w-3 h-3 bg-yellow-400 rounded-full animate-pulse"></div>
                  <span className="text-sm text-yellow-600">Verificando...</span>
                </>
              ) : healthStatus?.status === 'healthy' ? (
                <>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-green-600">Conectado</span>
                </>
              ) : (
                <>
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span className="text-sm text-red-600">Desconectado</span>
                </>
              )}
            </div>
          </div>

          {/* Información del sistema */}
          {healthStatus && (
            <div className="p-4 bg-blue-50 rounded-lg">
              <h3 className="font-medium text-blue-900 mb-2">Información del Sistema</h3>
              <div className="space-y-1 text-sm">
                <div>
                  <span className="text-blue-700">Servicio:</span>{' '}
                  <span className="text-blue-900 font-medium">{healthStatus.service}</span>
                </div>
                <div>
                  <span className="text-blue-700">Versión:</span>{' '}
                  <span className="text-blue-900 font-medium">{healthStatus.version}</span>
                </div>
                <div>
                  <span className="text-blue-700">Estado:</span>{' '}
                  <span className="text-blue-900 font-medium">{healthStatus.status}</span>
                </div>
              </div>
            </div>
          )}

          {/* Botones de acción */}
          <div className="space-y-3">
            <button
              onClick={checkBackendHealth}
              disabled={isChecking}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-lg transition-colors"
            >
              {isChecking ? 'Verificando...' : 'Reconectar Backend'}
            </button>

            {healthStatus?.status === 'healthy' && (
              <button
                onClick={() => alert('¡Chat interface será implementada próximamente!')}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
              >
                💬 Iniciar Chat con AI
              </button>
            )}
          </div>

          {/* URLs del sistema */}
          <div className="pt-4 border-t border-gray-200">
            <h4 className="font-medium text-gray-700 mb-2">Enlaces del Sistema</h4>
            <div className="space-y-1 text-sm">
              <a 
                href="https://advanced-ai-agent-0003.azurewebsites.net/health" 
                target="_blank"
                rel="noopener noreferrer"
                className="block text-blue-600 hover:text-blue-800 underline"
              >
                🔗 Backend API Health Check
              </a>
              <a 
                href="https://github.com/OsvaldoVegaOses/advanced-ai-agent" 
                target="_blank"
                rel="noopener noreferrer"
                className="block text-blue-600 hover:text-blue-800 underline"
              >
                📂 Código Fuente en GitHub
              </a>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 pt-4 border-t border-gray-200 text-center">
          <p className="text-xs text-gray-500">
            Desplegado en Azure con Microsoft for Startups
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Frontend: Azure Static Web Apps | Backend: Azure App Services
          </p>
        </div>
      </div>
    </div>
  );
}