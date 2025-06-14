'use client';

import { useState } from 'react';
import { useAppStore } from '../../store/useAppStore';
import { 
  PlusIcon,
  ChatBubbleLeftIcon,
  Cog6ToothIcon,
  XMarkIcon,
  TrashIcon,
  PencilIcon
} from '@heroicons/react/24/outline';
import { Conversation } from '../types';

export default function Sidebar() {
  const { 
    chat, 
    ui, 
    toggleSidebar, 
    setCurrentConversation,
    addNotification 
  } = useAppStore();
  
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const handleNewChat = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'Nueva conversación',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    setCurrentConversation(newConversation);
    addNotification({
      type: 'success',
      title: 'Nueva conversación',
      message: 'Conversación creada exitosamente',
      duration: 2000,
    });
  };

  const handleEditTitle = (conversation: Conversation) => {
    setEditingId(conversation.id);
    setEditTitle(conversation.title);
  };

  const handleSaveTitle = () => {
    if (editingId && editTitle.trim()) {
      // TODO: Actualizar título en el store
      addNotification({
        type: 'success',
        title: 'Título actualizado',
        message: 'El título de la conversación ha sido actualizado',
        duration: 2000,
      });
    }
    setEditingId(null);
    setEditTitle('');
  };

  const handleDeleteConversation = (conversationId: string) => {
    // TODO: Implementar eliminación
    addNotification({
      type: 'success',
      title: 'Conversación eliminada',
      message: 'La conversación ha sido eliminada',
      duration: 2000,
    });
  };

  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Hoy';
    if (days === 1) return 'Ayer';
    if (days < 7) return `Hace ${days} días`;
    return date.toLocaleDateString('es-ES', { 
      month: 'short', 
      day: 'numeric' 
    });
  };

  return (
    <div className="h-full bg-white border-r border-secondary-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-secondary-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-secondary-900">
            Conversaciones
          </h2>
          <button
            onClick={toggleSidebar}
            className="p-1 rounded-lg hover:bg-secondary-100 transition-colors md:hidden"
          >
            <XMarkIcon className="w-5 h-5 text-secondary-500" />
          </button>
        </div>

        {/* Botón nueva conversación */}
        <button
          onClick={handleNewChat}
          className="w-full flex items-center space-x-2 px-3 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
        >
          <PlusIcon className="w-4 h-4" />
          <span>Nueva conversación</span>
        </button>
      </div>

      {/* Lista de conversaciones */}
      <div className="flex-1 overflow-y-auto p-2">
        {chat.conversations.length === 0 ? (
          <div className="text-center py-8 text-secondary-500">
            <ChatBubbleLeftIcon className="w-12 h-12 mx-auto mb-3 text-secondary-300" />
            <p className="text-sm">No hay conversaciones aún</p>
            <p className="text-xs mt-1">Inicia una nueva conversación</p>
          </div>
        ) : (
          <div className="space-y-1">
            {chat.conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`
                  group relative p-3 rounded-lg cursor-pointer transition-colors
                  ${chat.currentConversation?.id === conversation.id
                    ? 'bg-primary-50 border border-primary-200'
                    : 'hover:bg-secondary-50'
                  }
                `}
                onClick={() => setCurrentConversation(conversation)}
              >
                {editingId === conversation.id ? (
                  <div className="space-y-2">
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="w-full px-2 py-1 text-sm border border-secondary-300 rounded focus:outline-none focus:ring-1 focus:ring-primary-500"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSaveTitle();
                        if (e.key === 'Escape') setEditingId(null);
                      }}
                      autoFocus
                    />
                    <div className="flex space-x-1">
                      <button
                        onClick={handleSaveTitle}
                        className="px-2 py-1 text-xs bg-primary-600 text-white rounded hover:bg-primary-700"
                      >
                        Guardar
                      </button>
                      <button
                        onClick={() => setEditingId(null)}
                        className="px-2 py-1 text-xs bg-secondary-200 text-secondary-700 rounded hover:bg-secondary-300"
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-secondary-900 truncate">
                          {conversation.title}
                        </h3>
                        <p className="text-xs text-secondary-500 mt-1">
                          {formatDate(conversation.updatedAt)}
                        </p>
                        {conversation.messages.length > 0 && (
                          <p className="text-xs text-secondary-400 mt-1 truncate">
                            {conversation.messages[conversation.messages.length - 1]?.content}
                          </p>
                        )}
                      </div>
                      
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity flex space-x-1 ml-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEditTitle(conversation);
                          }}
                          className="p-1 rounded hover:bg-secondary-200 transition-colors"
                        >
                          <PencilIcon className="w-3 h-3 text-secondary-500" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteConversation(conversation.id);
                          }}
                          className="p-1 rounded hover:bg-red-100 transition-colors"
                        >
                          <TrashIcon className="w-3 h-3 text-red-500" />
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-secondary-200">
        <button className="w-full flex items-center space-x-2 px-3 py-2 text-secondary-600 hover:bg-secondary-50 rounded-lg transition-colors">
          <Cog6ToothIcon className="w-4 h-4" />
          <span className="text-sm">Configuración</span>
        </button>
      </div>
    </div>
  );
}