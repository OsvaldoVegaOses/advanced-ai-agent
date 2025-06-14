/**
 * API Service - Gestión de comunicación con el backend
 */
class ApiService {
  constructor() {
    // Configuración de URLs con fallback
    this.config = {
      production: {
        baseUrl: 'https://advanced-ai-agent-0003.azurewebsites.net',
        corsProxy: '/api'
      },
      fallback: {
        baseUrl: 'https://advanced-ai-agent-0003.azurewebsites.net',
        corsProxy: null
      }
    };
    
    this.currentConfig = this.config.production;
    this.endpoints = {
      chat: '/chat',
      health: '/health'
    };
    
    this.corsRetryAttempted = false;
  }

  /**
   * Construir URL con configuración actual
   */
  buildUrl(endpoint) {
    if (this.currentConfig.corsProxy) {
      return `${this.currentConfig.corsProxy}${endpoint}`;
    }
    return `${this.currentConfig.baseUrl}${endpoint}`;
  }

  /**
   * Realizar petición HTTP con manejo de errores y fallback CORS
   */
  async request(endpoint, options = {}) {
    const url = this.buildUrl(endpoint);
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
      mode: 'cors',
      credentials: 'omit'
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
      
      // Si es un error CORS y no hemos intentado el fallback
      if (error.message.includes('CORS') && !this.corsRetryAttempted) {
        console.warn('CORS error detected, switching to fallback configuration');
        this.corsRetryAttempted = true;
        this.currentConfig = this.config.fallback;
        
        // Reintentar con configuración fallback
        return await this.request(endpoint, options);
      }
      
      return { 
        success: false, 
        error: error.message,
        status: error.name === 'TypeError' ? 'cors_error' : 'network_error'
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
        conversation_id: sessionId,
        temperature: 0.7,
        max_tokens: 1000,
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