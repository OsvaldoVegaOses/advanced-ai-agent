'use client';

import { SparklesIcon } from '@heroicons/react/24/outline';

export default function TypingIndicator() {
  return (
    <div className="chat-message assistant">
      <div className="flex space-x-4">
        {/* Avatar */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-accent-500 to-primary-500 text-white flex items-center justify-center">
          <SparklesIcon className="w-5 h-5" />
        </div>

        {/* Contenido */}
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-sm font-medium text-secondary-900">
              Advanced AI Agent
            </span>
            <span className="text-xs text-secondary-500">
              escribiendo...
            </span>
          </div>

          {/* Indicador de escritura */}
          <div className="typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot" style={{ animationDelay: '0.2s' }}></div>
            <div className="typing-dot" style={{ animationDelay: '0.4s' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}