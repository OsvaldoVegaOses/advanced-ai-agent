/**
 * API Service - Gestión de comunicación con el backend
 */
class ApiService {
  constructor() {
    // Usar directamente el backend para evitar problemas de proxy
    this.baseUrl = 'https://advanced-ai-agent-0003.azurewebsites.net';
    this.endpoints = {
      chat: '/chat',
      health: '/health'
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

      // Verificar si la respuesta es JSON o HTML
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json();
        return { success: true, data };
      } else if (contentType && contentType.includes('text/html')) {
        // Si recibimos HTML, significa que Azure no está redirigiendo correctamente
        console.warn(`Received HTML instead of JSON for ${endpoint} - API route not configured`);
        return { 
          success: false, 
          error: 'API route not configured correctly',
          status: 'route_error'
        };
      } else {
        // Intentar parsear como JSON por defecto
        const data = await response.json();
        return { success: true, data };
      }
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