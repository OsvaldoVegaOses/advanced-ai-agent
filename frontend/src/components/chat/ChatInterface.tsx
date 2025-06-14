'use client';

import { useEffect, useRef } from 'react';
import { useAppStore } from '../../store/useAppStore';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';
import { useChat } from '../../hooks/useChat';

export default function ChatInterface() {
  const { chat } = useAppStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { sendMessage, isLoading, isTyping } = useChat();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chat.currentConversation?.messages, isTyping]);

  const handleSendMessage = async (content: string) => {
    await sendMessage(content);
  };

  if (!chat.currentConversation) {
    return null;
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header de la conversación */}
      <div className="bg-white border-b border-secondary-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-secondary-900">
              {chat.currentConversation.title}
            </h2>
            <p className="text-sm text-secondary-500">
              {chat.currentConversation.messages.length} mensajes
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            {isLoading && (
              <div className="flex items-center space-x-2 text-secondary-500">
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
                <span className="text-sm">Procesando...</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Área de mensajes */}
      <div className="flex-1 overflow-y-auto bg-secondary-50">
        <div className="max-w-4xl mx-auto">
          {chat.currentConversation.messages.length === 0 ? (
            <div className="flex items-center justify-center h-full py-12">
              <div className="text-center">
                <div className="w-16 h-16 bg-secondary-200 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">💬</span>
                </div>
                <h3 className="text-lg font-medium text-secondary-900 mb-2">
                  Inicia la conversación
                </h3>
                <p className="text-secondary-600">
                  Escribe tu mensaje para comenzar a chatear con el agente AI
                </p>
              </div>
            </div>
          ) : (
            <div className="py-6 space-y-6">
              {chat.currentConversation.messages.map((message, index) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  isLast={index === chat.currentConversation!.messages.length - 1}
                />
              ))}
              
              {isTyping && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input de chat */}
      <div className="bg-white border-t border-secondary-200">
        <div className="max-w-4xl mx-auto">
          <ChatInput
            onSend={handleSendMessage}
            disabled={isLoading}
            placeholder="Escribe tu mensaje..."
          />
        </div>
      </div>
    </div>
  );
}