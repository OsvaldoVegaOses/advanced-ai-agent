// Tipos principales para el Advanced AI Agent

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: Date;
  metadata?: {
    model?: string;
    tokens?: number;
    processingTime?: number;
  };
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  summary?: string;
  tags?: string[];
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  aiModel: string;
  maxTokens: number;
  temperature: number;
  streamResponses: boolean;
}

export interface AgentConfig {
  name: string;
  description: string;
  model: string;
  systemPrompt: string;
  temperature: number;
  maxTokens: number;
  tools: Tool[];
}

export interface Tool {
  name: string;
  description: string;
  enabled: boolean;
  config?: Record<string, any>;
}

// API Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ChatRequest {
  message: string;
  conversationId?: string;
  config?: Partial<AgentConfig>;
}

export interface ChatResponse {
  message: Message;
  conversationId: string;
  suggestions?: string[];
}

export interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  service: string;
  version: string;
  timestamp?: string;
}

// UI Types
export interface ChatState {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  isLoading: boolean;
  isTyping: boolean;
  error: string | null;
}

export interface UiState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  notifications: Notification[];
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  actions?: NotificationAction[];
}

export interface NotificationAction {
  label: string;
  onClick: () => void;
}

// Form Types
export interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

export interface MessageProps {
  message: Message;
  isLast?: boolean;
  onEdit?: (content: string) => void;
  onDelete?: () => void;
}

// Hook Types
export interface UseChatOptions {
  conversationId?: string;
  autoSave?: boolean;
  maxMessages?: number;
}

export interface UseChatReturn {
  messages: Message[];
  sendMessage: (content: string) => Promise<void>;
  isLoading: boolean;
  isTyping: boolean;
  error: string | null;
  clearMessages: () => void;
  deleteMessage: (messageId: string) => void;
  editMessage: (messageId: string, content: string) => void;
}

// Store Types
export interface AppStore {
  user: User | null;
  chat: ChatState;
  ui: UiState;
  config: AgentConfig;
  
  // Actions
  setUser: (user: User | null) => void;
  updatePreferences: (preferences: Partial<UserPreferences>) => void;
  
  // Chat actions
  setCurrentConversation: (conversation: Conversation | null) => void;
  addMessage: (message: Message) => void;
  updateMessage: (messageId: string, updates: Partial<Message>) => void;
  deleteMessage: (messageId: string) => void;
  setLoading: (loading: boolean) => void;
  setTyping: (typing: boolean) => void;
  setError: (error: string | null) => void;
  
  // UI actions
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
  
  // Config actions
  updateConfig: (config: Partial<AgentConfig>) => void;
}