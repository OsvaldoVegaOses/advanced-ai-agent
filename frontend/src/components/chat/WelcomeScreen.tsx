'use client';

import { useState } from 'react';
import { useAppStore } from '@/store/useAppStore';
import { 
  SparklesIcon,
  ChatBubbleLeftRightIcon,
  CogIcon,
  LightBulbIcon,
  RocketLaunchIcon,
  CodeBracketIcon
} from '@heroicons/react/24/outline';
import { Conversation } from '@/types';

const quickStarters = [
  {
    title: "Automatización de procesos",
    description: "Ayúdame a automatizar procesos empresariales",
    icon: RocketLaunchIcon,
    prompt: "Hola, me gustaría explorar cómo puedo automatizar procesos en mi empresa. ¿Podrías ayudarme a identificar oportunidades de mejora?"
  },
  {
    title: "Análisis de datos",
    description: "Analizar y procesar información empresarial",
    icon: SparklesIcon,
    prompt: "Necesito ayuda para analizar datos de mi negocio. ¿Qué métodos recomiendas para obtener insights valiosos?"
  },
  {
    title: "Desarrollo de código",
    description: "Asistencia con programación y desarrollo",
    icon: CodeBracketIcon,
    prompt: "Estoy trabajando en un proyecto de desarrollo. ¿Podrías ayudarme con buenas prácticas y soluciones técnicas?"
  },
  {
    title: "Consultoría estratégica",
    description: "Asesoramiento en decisiones de negocio",
    icon: LightBulbIcon,
    prompt: "Necesito asesoramiento estratégico para mi empresa. ¿Podrías ayudarme a evaluar diferentes opciones y tomar decisiones informadas?"
  }
];

export default function WelcomeScreen() {
  const { setCurrentConversation, addMessage, config } = useAppStore();
  const [selectedStarter, setSelectedStarter] = useState<string | null>(null);

  const handleQuickStart = (starter: typeof quickStarters[0]) => {
    // Crear nueva conversación
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: starter.title,
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    setCurrentConversation(newConversation);

    // Agregar mensaje inicial
    const userMessage = {
      id: `msg-${Date.now()}`,
      content: starter.prompt,
      role: 'user' as const,
      timestamp: new Date(),
    };

    addMessage(userMessage);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Contenido principal */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-6 py-12">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="flex justify-center mb-6">
              <div className="p-4 bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl">
                <ChatBubbleLeftRightIcon className="w-12 h-12 text-white" />
              </div>
            </div>
            <h1 className="text-4xl font-bold text-gradient mb-4">
              Advanced AI Agent
            </h1>
            <p className="text-xl text-secondary-600 max-w-2xl mx-auto">
              Tu asistente inteligente para automatización empresarial, análisis de datos 
              y desarrollo de soluciones innovadoras.
            </p>
          </div>

          {/* Características principales */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="card text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <SparklesIcon className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="font-semibold text-secondary-900 mb-2">
                IA Avanzada
              </h3>
              <p className="text-secondary-600 text-sm">
                Potenciado por modelos de lenguaje de última generación
              </p>
            </div>

            <div className="card text-center">
              <div className="w-12 h-12 bg-accent-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <CogIcon className="w-6 h-6 text-accent-600" />
              </div>
              <h3 className="font-semibold text-secondary-900 mb-2">
                Automatización
              </h3>
              <p className="text-secondary-600 text-sm">
                Optimiza procesos y aumenta la eficiencia operacional
              </p>
            </div>

            <div className="card text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <RocketLaunchIcon className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="font-semibold text-secondary-900 mb-2">
                Escalable
              </h3>
              <p className="text-secondary-600 text-sm">
                Crece con tu negocio y se adapta a tus necesidades
              </p>
            </div>
          </div>

          {/* Quick starters */}
          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-secondary-900 mb-6 text-center">
              ¿Cómo puedo ayudarte hoy?
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              {quickStarters.map((starter, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickStart(starter)}
                  onMouseEnter={() => setSelectedStarter(starter.title)}
                  onMouseLeave={() => setSelectedStarter(null)}
                  className={`
                    p-6 rounded-xl border-2 text-left transition-all duration-200
                    ${selectedStarter === starter.title
                      ? 'border-primary-300 bg-primary-50 shadow-lg scale-105'
                      : 'border-secondary-200 bg-white hover:border-primary-200 hover:shadow-md'
                    }
                  `}
                >
                  <div className="flex items-start space-x-4">
                    <div className={`
                      p-2 rounded-lg transition-colors
                      ${selectedStarter === starter.title
                        ? 'bg-primary-200'
                        : 'bg-secondary-100'
                      }
                    `}>
                      <starter.icon className={`
                        w-5 h-5 transition-colors
                        ${selectedStarter === starter.title
                          ? 'text-primary-700'
                          : 'text-secondary-600'
                        }
                      `} />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-secondary-900 mb-1">
                        {starter.title}
                      </h3>
                      <p className="text-secondary-600 text-sm">
                        {starter.description}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Configuración actual */}
          <div className="card bg-secondary-50 border-secondary-300">
            <div className="flex items-center space-x-3 mb-3">
              <CogIcon className="w-5 h-5 text-secondary-600" />
              <h3 className="font-semibold text-secondary-900">
                Configuración actual
              </h3>
            </div>
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-secondary-600">Modelo:</span>
                <span className="ml-2 font-medium text-secondary-900">
                  {config.model}
                </span>
              </div>
              <div>
                <span className="text-secondary-600">Temperatura:</span>
                <span className="ml-2 font-medium text-secondary-900">
                  {config.temperature}
                </span>
              </div>
              <div>
                <span className="text-secondary-600">Max tokens:</span>
                <span className="ml-2 font-medium text-secondary-900">
                  {config.maxTokens}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}