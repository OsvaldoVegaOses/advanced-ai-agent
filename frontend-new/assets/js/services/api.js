/**
 * API Service - Gestión de comunicación con el backend
 */
class ApiService {
  constructor() {
    this.baseUrl = window.location.origin;
    this.endpoints = {
      chat: '/api/chat',
      health: '/api/health'
    };
  }

  /**
   * Realizar petición HTTP con manejo de errores
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      return { 
        success: false, 
        error: error.message,
        status: error.status || 'network_error'
      };
    }
  }

  /**
   * Enviar mensaje al chat
   */
  async sendMessage(message, sessionId = 'default') {
    return await this.request(this.endpoints.chat, {
      method: 'POST',
      body: JSON.stringify({
        message,
        session_id: sessionId,
        context: {},
        stream: false
      })
    });
  }

  /**
   * Verificar estado del backend
   */
  async checkHealth() {
    return await this.request(this.endpoints.health, {
      method: 'GET'
    });
  }
}

// Instancia global
window.apiService = new ApiService();