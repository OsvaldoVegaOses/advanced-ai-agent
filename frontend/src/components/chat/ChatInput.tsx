'use client';

import { useState, useRef, KeyboardEvent } from 'react';
import { ChatInputProps } from '@/types';
import { PaperAirplaneIcon, StopIcon } from '@heroicons/react/24/outline';

export default function ChatInput({ 
  onSend, 
  disabled = false, 
  placeholder = "Escribe tu mensaje...",
  maxLength = 4000 
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage && !disabled) {
      onSend(trimmedMessage);
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    if (value.length <= maxLength) {
      setMessage(value);
      
      // Auto-resize textarea
      const textarea = e.target;
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  };

  const remainingChars = maxLength - message.length;
  const isNearLimit = remainingChars < 100;

  return (
    <div className="p-4">
      <div className="relative">
        {/* Textarea container */}
        <div className="relative border border-secondary-300 rounded-lg bg-white focus-within:border-primary-500 focus-within:ring-1 focus-within:ring-primary-500">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onCompositionStart={() => setIsComposing(true)}
            onCompositionEnd={() => setIsComposing(false)}
            placeholder={placeholder}
            disabled={disabled}
            className="w-full px-4 py-3 pr-12 border-0 resize-none focus:outline-none bg-transparent"
            style={{ 
              minHeight: '52px',
              maxHeight: '120px'
            }}
          />
          
          {/* Send button */}
          <div className="absolute bottom-2 right-2">
            <button
              onClick={handleSubmit}
              disabled={!message.trim() || disabled}
              className={`
                p-2 rounded-lg transition-all duration-200
                ${!message.trim() || disabled
                  ? 'bg-secondary-100 text-secondary-400 cursor-not-allowed'
                  : 'bg-primary-600 hover:bg-primary-700 text-white shadow-sm hover:shadow-md'
                }
              `}
              title={disabled ? 'Esperando respuesta...' : 'Enviar mensaje (Enter)'}
            >
              {disabled ? (
                <StopIcon className="w-4 h-4" />
              ) : (
                <PaperAirplaneIcon className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>

        {/* Character counter */}
        {(isNearLimit || message.length > 0) && (
          <div className="flex justify-between items-center mt-2 px-1">
            <div className="text-xs text-secondary-500">
              Shift + Enter para nueva línea
            </div>
            <div className={`
              text-xs
              ${isNearLimit ? 'text-amber-600' : 'text-secondary-500'}
              ${remainingChars < 0 ? 'text-red-600' : ''}
            `}>
              {remainingChars} caracteres restantes
            </div>
          </div>
        )}

        {/* Suggestions (opcional) */}
        {message.length === 0 && !disabled && (
          <div className="mt-3 flex flex-wrap gap-2">
            {[
              'Explícame sobre...',
              'Ayúdame con...',
              'Analiza estos datos...',
              'Crea un plan para...'
            ].map((suggestion, index) => (
              <button
                key={index}
                onClick={() => setMessage(suggestion)}
                className="px-3 py-1 text-xs bg-secondary-100 hover:bg-secondary-200 text-secondary-700 rounded-full transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}