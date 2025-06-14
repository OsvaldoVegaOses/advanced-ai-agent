import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AppStore, User, Conversation, Message, Notification, AgentConfig, UserPreferences } from '@/types';

const defaultConfig: AgentConfig = {
  name: 'Advanced AI Agent',
  description: 'Agente inteligente para automatización de procesos empresariales',
  model: 'gpt-4',
  systemPrompt: 'Eres un asistente AI avanzado especializado en automatización empresarial. Proporciona respuestas precisas, útiles y profesionales.',
  temperature: 0.7,
  maxTokens: 2048,
  tools: [
    { name: 'web_search', description: 'Búsqueda en web', enabled: true },
    { name: 'code_analysis', description: 'Análisis de código', enabled: true },
    { name: 'data_processing', description: 'Procesamiento de datos', enabled: true },
  ]
};

const defaultPreferences: UserPreferences = {
  theme: 'light',
  language: 'es',
  aiModel: 'gpt-4',
  maxTokens: 2048,
  temperature: 0.7,
  streamResponses: true,
};

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      // Estado inicial
      user: null,
      chat: {
        conversations: [],
        currentConversation: null,
        isLoading: false,
        isTyping: false,
        error: null,
      },
      ui: {
        sidebarOpen: true,
        theme: 'light',
        notifications: [],
      },
      config: defaultConfig,

      // User Actions
      setUser: (user) => set({ user }),
      
      updatePreferences: (preferences) =>
        set((state) => ({
          user: state.user ? {
            ...state.user,
            preferences: { ...state.user.preferences, ...preferences }
          } : null
        })),

      // Chat Actions
      setCurrentConversation: (conversation) =>
        set((state) => ({
          chat: { ...state.chat, currentConversation: conversation }
        })),

      addMessage: (message) =>
        set((state) => {
          const currentConversation = state.chat.currentConversation;
          if (!currentConversation) return state;

          const updatedConversation = {
            ...currentConversation,
            messages: [...currentConversation.messages, message],
            updatedAt: new Date(),
          };

          const conversationIndex = state.chat.conversations.findIndex(
            (conv) => conv.id === currentConversation.id
          );

          const updatedConversations = [...state.chat.conversations];
          if (conversationIndex >= 0) {
            updatedConversations[conversationIndex] = updatedConversation;
          } else {
            updatedConversations.push(updatedConversation);
          }

          return {
            chat: {
              ...state.chat,
              currentConversation: updatedConversation,
              conversations: updatedConversations,
            }
          };
        }),

      updateMessage: (messageId, updates) =>
        set((state) => {
          const currentConversation = state.chat.currentConversation;
          if (!currentConversation) return state;

          const updatedMessages = currentConversation.messages.map((msg) =>
            msg.id === messageId ? { ...msg, ...updates } : msg
          );

          const updatedConversation = {
            ...currentConversation,
            messages: updatedMessages,
            updatedAt: new Date(),
          };

          return {
            chat: {
              ...state.chat,
              currentConversation: updatedConversation,
            }
          };
        }),

      deleteMessage: (messageId) =>
        set((state) => {
          const currentConversation = state.chat.currentConversation;
          if (!currentConversation) return state;

          const updatedMessages = currentConversation.messages.filter(
            (msg) => msg.id !== messageId
          );

          const updatedConversation = {
            ...currentConversation,
            messages: updatedMessages,
            updatedAt: new Date(),
          };

          return {
            chat: {
              ...state.chat,
              currentConversation: updatedConversation,
            }
          };
        }),

      setLoading: (isLoading) =>
        set((state) => ({
          chat: { ...state.chat, isLoading }
        })),

      setTyping: (isTyping) =>
        set((state) => ({
          chat: { ...state.chat, isTyping }
        })),

      setError: (error) =>
        set((state) => ({
          chat: { ...state.chat, error }
        })),

      // UI Actions
      toggleSidebar: () =>
        set((state) => ({
          ui: { ...state.ui, sidebarOpen: !state.ui.sidebarOpen }
        })),

      setTheme: (theme) =>
        set((state) => ({
          ui: { ...state.ui, theme }
        })),

      addNotification: (notification) =>
        set((state) => ({
          ui: {
            ...state.ui,
            notifications: [
              ...state.ui.notifications,
              { ...notification, id: Date.now().toString() }
            ]
          }
        })),

      removeNotification: (id) =>
        set((state) => ({
          ui: {
            ...state.ui,
            notifications: state.ui.notifications.filter((n) => n.id !== id)
          }
        })),

      // Config Actions
      updateConfig: (configUpdates) =>
        set((state) => ({
          config: { ...state.config, ...configUpdates }
        })),
    }),
    {
      name: 'advanced-ai-agent-store',
      partialize: (state) => ({
        user: state.user,
        ui: { theme: state.ui.theme, sidebarOpen: state.ui.sidebarOpen },
        config: state.config,
      }),
    }
  )
);