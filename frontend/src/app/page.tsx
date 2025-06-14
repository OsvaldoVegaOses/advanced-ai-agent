'use client';

import { useEffect, useState } from 'react';
import { useAppStore } from '@/store/useAppStore';
import ChatLayout from '@/components/layout/ChatLayout';
import WelcomeScreen from '@/components/chat/WelcomeScreen';
import ChatInterface from '@/components/chat/ChatInterface';
import { apiClient } from '@/lib/api';
import { HealthStatus } from '@/types';

export default function HomePage() {
  const { chat, addNotification } = useAppStore();
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      setIsChecking(true);
      const status = await apiClient.checkHealth();
      setHealthStatus(status);
      
      if (status.status === 'healthy') {
        addNotification({
          type: 'success',
          title: 'Conexión establecida',
          message: `Conectado a ${status.service} v${status.version}`,
          duration: 3000,
        });
      }
    } catch (error) {
      setHealthStatus({
        status: 'unhealthy',
        service: 'Advanced AI Agent',
        version: '1.0.0',
      });
      
      addNotification({
        type: 'error',
        title: 'Error de conexión',
        message: 'No se pudo conectar con el backend. Verificando...',
        duration: 5000,
      });
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <ChatLayout>
      <div className="flex-1 flex flex-col h-full">
        {/* Header con estado de conexión */}
        <div className="bg-white border-b border-secondary-200 px-6 py-3">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold text-secondary-900">
              Advanced AI Agent
            </h1>
            
            <div className="flex items-center space-x-2">
              {isChecking ? (
                <div className="flex items-center space-x-2 text-secondary-500">
                  <div className="w-2 h-2 bg-secondary-400 rounded-full animate-pulse"></div>
                  <span className="text-sm">Verificando conexión...</span>
                </div>
              ) : healthStatus?.status === 'healthy' ? (
                <div className="flex items-center space-x-2 text-green-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm">Conectado</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2 text-red-600">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span className="text-sm">Desconectado</span>
                  <button
                    onClick={checkBackendHealth}
                    className="text-xs text-primary-600 hover:text-primary-700 underline"
                  >
                    Reintentar
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Contenido principal */}
        <div className="flex-1 overflow-hidden">
          {chat.currentConversation ? (
            <ChatInterface />
          ) : (
            <WelcomeScreen />
          )}
        </div>
      </div>
    </ChatLayout>
  );
}