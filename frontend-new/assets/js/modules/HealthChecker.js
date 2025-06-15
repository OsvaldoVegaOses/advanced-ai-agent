/**
 * HEALTH CHECKER MODULE  
 * Módulo independiente para verificar el estado del backend de forma continua
 */
class HealthChecker {
  constructor(connectionTester) {
    this.connectionTester = connectionTester;
    this.connectionMethod = null;
    this.isRunning = false;
    this.intervalId = null;
    this.checkInterval = 30000; // 30 seconds
    this.listeners = [];
    this.lastHealthStatus = null;
  }

  /**
   * Inicializar con el mejor método de conexión disponible
   */
  async initialize() {
    console.log('🏥 Initializing HealthChecker...');
    
    // Ejecutar tests de conectividad
    const report = await this.connectionTester.runAllTests();
    this.connectionMethod = this.connectionTester.getBestConnectionMethod();
    
    console.log('🔗 Selected connection method:', this.connectionMethod);
    
    if (this.connectionMethod.method === 'none') {
      console.error('❌ No working connection method found');
      this.notifyListeners({
        status: 'error',
        message: 'No se puede conectar al backend',
        details: 'Ningún método de conexión disponible',
        timestamp: new Date().toISOString()
      });
      return false;
    }
    
    return true;
  }

  /**
   * Realizar un health check único
   */
  async performHealthCheck() {
    if (!this.connectionMethod || this.connectionMethod.method === 'none') {
      return {
        success: false,
        status: 'error',
        message: 'Sin método de conexión configurado'
      };
    }

    const url = this.buildHealthUrl();
    console.log(`🏥 Performing health check: ${url}`);

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        mode: this.connectionMethod.method === 'direct' ? 'cors' : 'same-origin',
        credentials: 'omit'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      
      if (!contentType || !contentType.includes('application/json')) {
        return {
          success: false,
          status: 'error',
          message: 'Backend devuelve HTML en lugar de JSON',
          details: `Content-Type: ${contentType}`,
          timestamp: new Date().toISOString()
        };
      }

      const data = await response.json();
      
      const healthStatus = {
        success: true,
        status: 'connected',
        message: 'Backend operativo',
        details: {
          service: data.service || 'Unknown',
          version: data.version || 'Unknown',
          uptime: data.uptime_seconds || 0,
          ai_enabled: data.ai_models ? 'Yes' : 'No'
        },
        connectionMethod: this.connectionMethod.method,
        timestamp: new Date().toISOString()
      };

      console.log('✅ Health check successful:', healthStatus);
      this.lastHealthStatus = healthStatus;
      this.notifyListeners(healthStatus);
      
      return healthStatus;

    } catch (error) {
      const errorStatus = {
        success: false,
        status: 'error', 
        message: 'Error al conectar con el backend',
        details: error.message,
        connectionMethod: this.connectionMethod.method,
        timestamp: new Date().toISOString()
      };

      console.log('❌ Health check failed:', errorStatus);
      this.lastHealthStatus = errorStatus;
      this.notifyListeners(errorStatus);
      
      return errorStatus;
    }
  }

  /**
   * Construir URL para health check
   */
  buildHealthUrl() {
    if (this.connectionMethod.method === 'proxy') {
      return '/api/health';
    } else if (this.connectionMethod.method === 'direct') {
      return `${this.connectionMethod.baseUrl}/health`;
    }
    throw new Error('Invalid connection method');
  }

  /**
   * Iniciar verificaciones periódicas
   */
  startPeriodicChecks() {
    if (this.isRunning) {
      console.log('⚠️ Health checks already running');
      return;
    }

    console.log(`🔄 Starting periodic health checks every ${this.checkInterval/1000} seconds`);
    this.isRunning = true;
    
    // Realizar check inmediato
    this.performHealthCheck();
    
    // Programar checks periódicos
    this.intervalId = setInterval(() => {
      this.performHealthCheck();
    }, this.checkInterval);
  }

  /**
   * Detener verificaciones periódicas
   */
  stopPeriodicChecks() {
    if (!this.isRunning) {
      console.log('⚠️ Health checks not running');
      return;
    }

    console.log('⏹️ Stopping periodic health checks');
    this.isRunning = false;
    
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  /**
   * Agregar listener para cambios de estado
   */
  addListener(callback) {
    this.listeners.push(callback);
  }

  /**
   * Remover listener
   */
  removeListener(callback) {
    const index = this.listeners.indexOf(callback);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }

  /**
   * Notificar a todos los listeners
   */
  notifyListeners(status) {
    this.listeners.forEach(callback => {
      try {
        callback(status);
      } catch (error) {
        console.error('Error in health status listener:', error);
      }
    });
  }

  /**
   * Obtener último estado conocido
   */
  getLastStatus() {
    return this.lastHealthStatus;
  }

  /**
   * Cambiar intervalo de verificación
   */
  setCheckInterval(intervalMs) {
    this.checkInterval = intervalMs;
    
    if (this.isRunning) {
      this.stopPeriodicChecks();
      this.startPeriodicChecks();
    }
  }

  /**
   * Obtener estadísticas de conectividad
   */
  getConnectionStats() {
    return {
      method: this.connectionMethod?.method || 'none',
      isRunning: this.isRunning,
      checkInterval: this.checkInterval,
      lastCheck: this.lastHealthStatus?.timestamp || null,
      listenersCount: this.listeners.length
    };
  }
}

// Export para uso global
window.HealthChecker = HealthChecker;