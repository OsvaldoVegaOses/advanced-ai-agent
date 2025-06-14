'use client';

import { useState } from 'react';
import { MessageProps } from '@/types';
import { 
  UserIcon, 
  SparklesIcon,
  ClipboardDocumentIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

export default function ChatMessage({ message, isLast, onEdit, onDelete }: MessageProps) {
  const [showActions, setShowActions] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Error copying to clipboard:', error);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const isUser = message.role === 'user';

  return (
    <div
      className={`chat-message ${isUser ? 'user' : 'assistant'}`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <div className="flex space-x-4">
        {/* Avatar */}
        <div className={`
          flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
          ${isUser 
            ? 'bg-primary-100 text-primary-600' 
            : 'bg-gradient-to-br from-accent-500 to-primary-500 text-white'
          }
        `}>
          {isUser ? (
            <UserIcon className="w-5 h-5" />
          ) : (
            <SparklesIcon className="w-5 h-5" />
          )}
        </div>

        {/* Contenido del mensaje */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-sm font-medium text-secondary-900">
              {isUser ? 'Tú' : 'Advanced AI Agent'}
            </span>
            <span className="text-xs text-secondary-500">
              {formatTime(message.timestamp)}
            </span>
            {message.metadata?.processingTime && (
              <span className="text-xs text-secondary-400">
                • {message.metadata.processingTime}ms
              </span>
            )}
          </div>

          {/* Contenido */}
          <div className={`
            prose prose-sm max-w-none
            ${isUser ? 'prose-primary' : 'prose-secondary'}
          `}>
            {isUser ? (
              <p className="text-secondary-900 whitespace-pre-wrap">
                {message.content}
              </p>
            ) : (
              <ReactMarkdown
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    const language = match ? match[1] : '';
                    
                    return !inline && language ? (
                      <SyntaxHighlighter
                        style={tomorrow}
                        language={language}
                        PreTag="div"
                        className="rounded-lg"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    );
                  },
                }}
              >
                {message.content}
              </ReactMarkdown>
            )}
          </div>

          {/* Metadata */}
          {message.metadata && (
            <div className="mt-2 flex items-center space-x-4 text-xs text-secondary-500">
              {message.metadata.model && (
                <span>Modelo: {message.metadata.model}</span>
              )}
              {message.metadata.tokens && (
                <span>Tokens: {message.metadata.tokens}</span>
              )}
            </div>
          )}

          {/* Acciones */}
          <div className={`
            mt-2 flex items-center space-x-2 transition-opacity
            ${showActions ? 'opacity-100' : 'opacity-0'}
          `}>
            <button
              onClick={handleCopy}
              className="p-1 rounded hover:bg-secondary-100 transition-colors"
              title="Copiar mensaje"
            >
              <ClipboardDocumentIcon className="w-4 h-4 text-secondary-500" />
            </button>
            
            {copied && (
              <span className="text-xs text-green-600 animate-fade-in">
                ¡Copiado!
              </span>
            )}

            {onEdit && (
              <button
                onClick={() => onEdit(message.content)}
                className="p-1 rounded hover:bg-secondary-100 transition-colors"
                title="Editar mensaje"
              >
                <PencilIcon className="w-4 h-4 text-secondary-500" />
              </button>
            )}

            {onDelete && (
              <button
                onClick={onDelete}
                className="p-1 rounded hover:bg-red-100 transition-colors"
                title="Eliminar mensaje"
              >
                <TrashIcon className="w-4 h-4 text-red-500" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}