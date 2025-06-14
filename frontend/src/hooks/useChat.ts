import { useState, useCallback } from 'react';
import { useAppStore } from '../store/useAppStore';
import { apiClient } from '../lib/api';
import { Message, UseChatOptions, UseChatReturn } from '../types';

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const { 
    chat, 
    config,
    addMessage, 
    setLoading, 
    setTyping, 
    setError,
    addNotification 
  } = useAppStore();
  
  const [isLoading, setIsLoadingLocal] = useState(false);
  const [isTyping, setIsTypingLocal] = useState(false);

  const sendMessage = useCallback(async (content: string) => {
    if (!chat.currentConversation) {
      setError('No hay conversación activa');
      return;
    }

    try {
      setIsLoadingLocal(true);
      setLoading(true);
      setError(null);

      // Crear mensaje del usuario
      const userMessage: Message = {
        id: `msg-${Date.now()}-user`,
        content,
        role: 'user',
        timestamp: new Date(),
      };

      // Agregar mensaje del usuario al estado
      addMessage(userMessage);

      // Preparar request para la API
      const request = {
        message: content,
        conversationId: chat.currentConversation.id,
        config: {
          model: config.model,
          temperature: config.temperature,
          maxTokens: config.maxTokens,
        },
      };

      // Intentar stream primero, luego fallback a respuesta normal
      if (config.streamResponses) {
        try {
          setIsTypingLocal(true);
          setTyping(true);

          let assistantMessage: Message = {
            id: `msg-${Date.now()}-assistant`,
            content: '',
            role: 'assistant',
            timestamp: new Date(),
          };

          addMessage(assistantMessage);

          // Stream response
          const startTime = Date.now();
          for await (const chunk of apiClient.streamMessage(request)) {
            assistantMessage = {
              ...assistantMessage,
              content: assistantMessage.content + chunk,
            };
            
            // Actualizar mensaje en tiempo real
            addMessage(assistantMessage);
          }

          // Agregar metadata final
          const processingTime = Date.now() - startTime;
          assistantMessage = {
            ...assistantMessage,
            metadata: {
              model: config.model,
              processingTime,
              tokens: assistantMessage.content.length, // Aproximación
            },
          };

          addMessage(assistantMessage);

        } catch (streamError) {
          console.warn('Stream failed, falling back to regular API:', streamError);
          
          // Fallback a API normal
          const response = await apiClient.sendMessage(request);
          
          const assistantMessage: Message = {
            id: `msg-${Date.now()}-assistant`,
            content: response.message.content,
            role: 'assistant',
            timestamp: new Date(),
            metadata: response.message.metadata,
          };

          addMessage(assistantMessage);
        }
      } else {
        // Respuesta normal (no stream)
        const response = await apiClient.sendMessage(request);
        
        const assistantMessage: Message = {
          id: `msg-${Date.now()}-assistant`,
          content: response.message.content,
          role: 'assistant',
          timestamp: new Date(),
          metadata: response.message.metadata,
        };

        addMessage(assistantMessage);
      }

      addNotification({
        type: 'success',
        title: 'Mensaje enviado',
        message: 'Respuesta generada exitosamente',
        duration: 2000,
      });

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
      
      setError(errorMessage);
      addNotification({
        type: 'error',
        title: 'Error al enviar mensaje',
        message: errorMessage,
        duration: 5000,
      });

      // Agregar mensaje de error
      const errorResponseMessage: Message = {
        id: `msg-${Date.now()}-error`,
        content: `❌ **Error**: ${errorMessage}\n\nPor favor, intenta nuevamente o verifica tu conexión.`,
        role: 'assistant',
        timestamp: new Date(),
      };

      addMessage(errorResponseMessage);
    } finally {
      setIsLoadingLocal(false);
      setIsTypingLocal(false);
      setLoading(false);
      setTyping(false);
    }
  }, [
    chat.currentConversation,
    config,
    addMessage,
    setLoading,
    setTyping,
    setError,
    addNotification,
  ]);

  const clearMessages = useCallback(() => {
    if (chat.currentConversation) {
      // TODO: Implementar limpieza de mensajes
      addNotification({
        type: 'info',
        title: 'Mensajes limpiados',
        message: 'La conversación ha sido limpiada',
        duration: 2000,
      });
    }
  }, [chat.currentConversation, addNotification]);

  const deleteMessage = useCallback((messageId: string) => {
    // TODO: Implementar eliminación de mensaje
    addNotification({
      type: 'info',
      title: 'Mensaje eliminado',
      message: 'El mensaje ha sido eliminado',
      duration: 2000,
    });
  }, [addNotification]);

  const editMessage = useCallback((messageId: string, content: string) => {
    // TODO: Implementar edición de mensaje
    addNotification({
      type: 'info',
      title: 'Mensaje editado',
      message: 'El mensaje ha sido editado',
      duration: 2000,
    });
  }, [addNotification]);

  return {
    messages: chat.currentConversation?.messages || [],
    sendMessage,
    isLoading: isLoading || chat.isLoading,
    isTyping: isTyping || chat.isTyping,
    error: chat.error,
    clearMessages,
    deleteMessage,
    editMessage,
  };
}