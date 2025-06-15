/**
 * CHAT CONNECTOR MODULE
 * Módulo independiente para manejar la conexión específica con el endpoint de chat
 */
class ChatConnector {
  constructor(connectionTester) {
    this.connectionTester = connectionTester;
    this.connectionMethod = null;
    this.isInitialized = false;
    this.requestHistory = [];
    this.maxHistorySize = 50;
  }

  /**
   * Inicializar con el método de conexión detectado
   */
  async initialize() {
    console.log('💬 Initializing ChatConnector...');
    
    if (!this.connectionTester) {
      throw new Error('ConnectionTester is required');
    }

    // Obtener método de conexión ya probado
    this.connectionMethod = this.connectionTester.getBestConnectionMethod();
    
    if (this.connectionMethod.method === 'none') {
      console.error('❌ No working connection method available for chat');
      return false;
    }

    // Probar endpoint específico de chat
    const chatTest = await this.testChatEndpoint();
    
    if (!chatTest.success) {
      console.error('❌ Chat endpoint test failed:', chatTest.error);
      return false;
    }

    this.isInitialized = true;
    console.log('✅ ChatConnector initialized successfully');
    return true;
  }

  /**
   * Probar el endpoint de chat específicamente
   */
  async testChatEndpoint() {
    const url = this.buildChatUrl();
    console.log(`🧪 Testing chat endpoint: ${url}`);

    try {
      // Test con payload mínimo
      const testPayload = {
        message: "test",
        conversation_id: "test-connection",
        temperature: 0.7,
        max_tokens: 10,
        stream: false
      };

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        mode: this.connectionMethod.method === 'direct' ? 'cors' : 'same-origin',
        credentials: 'omit',
        body: JSON.stringify(testPayload)
      });

      const contentType = response.headers.get('content-type');
      
      if (!response.ok) {
        return {
          success: false,
          error: `HTTP ${response.status}: ${response.statusText}`,
          details: { url, method: 'POST', contentType }
        };
      }

      if (!contentType || !contentType.includes('application/json')) {
        return {
          success: false,
          error: 'Chat endpoint returns HTML instead of JSON',
          details: { url, contentType }
        };
      }

      const data = await response.json();
      
      return {
        success: true,
        data: data,
        details: { url, method: 'POST', contentType }
      };

    } catch (error) {
      return {
        success: false,
        error: error.message,
        details: { url, method: 'POST', errorType: error.name }
      };
    }
  }

  /**
   * Enviar mensaje de chat
   */
  async sendMessage(message, options = {}) {
    if (!this.isInitialized) {
      throw new Error('ChatConnector not initialized. Call initialize() first.');
    }

    const requestId = this.generateRequestId();
    const startTime = Date.now();

    console.log(`💬 [${requestId}] Sending chat message:`, { message, options });

    try {
      const payload = {
        message: message,
        conversation_id: options.conversationId || 'default',
        temperature: options.temperature || 0.7,
        max_tokens: options.maxTokens || 1000,
        stream: options.stream || false
      };

      const url = this.buildChatUrl();
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        mode: this.connectionMethod.method === 'direct' ? 'cors' : 'same-origin',
        credentials: 'omit',
        body: JSON.stringify(payload)
      });

      const endTime = Date.now();
      const duration = endTime - startTime;

      if (!response.ok) {
        const errorResult = {
          success: false,
          error: `HTTP ${response.status}: ${response.statusText}`,
          requestId,
          duration,
          timestamp: new Date().toISOString()
        };

        this.addToHistory(requestId, payload, errorResult, duration);
        console.log(`❌ [${requestId}] Chat request failed:`, errorResult);
        return errorResult;
      }

      const contentType = response.headers.get('content-type');
      
      if (!contentType || !contentType.includes('application/json')) {
        const errorResult = {
          success: false,
          error: 'Chat endpoint returned HTML instead of JSON',
          details: { contentType, status: response.status },
          requestId,
          duration,
          timestamp: new Date().toISOString()
        };

        this.addToHistory(requestId, payload, errorResult, duration);
        console.log(`❌ [${requestId}] Invalid content type:`, errorResult);
        return errorResult;
      }

      const data = await response.json();
      
      const successResult = {
        success: true,
        data: data,
        requestId,
        duration,
        timestamp: new Date().toISOString()
      };

      this.addToHistory(requestId, payload, successResult, duration);
      console.log(`✅ [${requestId}] Chat request successful:`, successResult);
      
      return successResult;

    } catch (error) {
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      const errorResult = {
        success: false,
        error: error.message,
        errorType: error.name,
        requestId,
        duration,
        timestamp: new Date().toISOString()
      };

      this.addToHistory(requestId, { message }, errorResult, duration);
      console.log(`❌ [${requestId}] Chat request exception:`, errorResult);
      
      return errorResult;
    }
  }

  /**
   * Construir URL para chat
   */
  buildChatUrl() {
    if (this.connectionMethod.method === 'linked-backend') {
      return '/api/chat';
    } else if (this.connectionMethod.method === 'proxy') {
      return '/api/chat';
    } else if (this.connectionMethod.method === 'direct') {
      return `${this.connectionMethod.baseUrl}/chat`;
    }
    throw new Error('Invalid connection method');
  }

  /**
   * Generar ID único para request
   */
  generateRequestId() {
    return `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Agregar request al historial
   */
  addToHistory(requestId, payload, result, duration) {
    this.requestHistory.unshift({
      requestId,
      payload,
      result,
      duration,
      timestamp: new Date().toISOString()
    });

    // Mantener tamaño máximo del historial
    if (this.requestHistory.length > this.maxHistorySize) {
      this.requestHistory = this.requestHistory.slice(0, this.maxHistorySize);
    }
  }

  /**
   * Obtener historial de requests
   */
  getRequestHistory(limit = 10) {
    return this.requestHistory.slice(0, limit);
  }

  /**
   * Obtener estadísticas de performance
   */
  getPerformanceStats() {
    if (this.requestHistory.length === 0) {
      return {
        totalRequests: 0,
        successRate: 0,
        averageResponseTime: 0,
        lastRequest: null
      };
    }

    const successful = this.requestHistory.filter(req => req.result.success);
    const totalRequests = this.requestHistory.length;
    const successRate = (successful.length / totalRequests) * 100;
    
    const durations = this.requestHistory.map(req => req.duration);
    const averageResponseTime = durations.reduce((a, b) => a + b, 0) / durations.length;

    return {
      totalRequests,
      successRate: Math.round(successRate * 100) / 100,
      averageResponseTime: Math.round(averageResponseTime),
      lastRequest: this.requestHistory[0]?.timestamp || null,
      connectionMethod: this.connectionMethod.method
    };
  }

  /**
   * Limpiar historial
   */
  clearHistory() {
    this.requestHistory = [];
    console.log('🗑️ Chat request history cleared');
  }

  /**
   * Obtener estado actual del conector
   */
  getStatus() {
    return {
      isInitialized: this.isInitialized,
      connectionMethod: this.connectionMethod,
      performanceStats: this.getPerformanceStats()
    };
  }
}

// Export para uso global
window.ChatConnector = ChatConnector;