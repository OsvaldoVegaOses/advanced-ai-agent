/**
 * SYSTEM MANAGER MODULE
 * Orquestador principal que coordina todos los módulos independientes
 */
class SystemManager {
  constructor() {
    this.modules = {};
    this.isInitialized = false;
    this.initializationStatus = {
      connectionTester: false,
      healthChecker: false,
      chatConnector: false,
      statusReporter: false
    };
    this.systemState = 'initializing';
    this.diagnostics = [];
  }

  /**
   * Inicializar todo el sistema paso a paso
   */
  async initialize() {
    console.log('🚀 SystemManager: Starting system initialization...');
    this.addDiagnostic('info', 'System initialization started');

    try {
      // Paso 1: Inicializar StatusReporter
      await this.initializeStatusReporter();
      
      // Paso 2: Inicializar ConnectionTester
      await this.initializeConnectionTester();
      
      // Paso 3: Inicializar HealthChecker
      await this.initializeHealthChecker();
      
      // Paso 4: Inicializar ChatConnector
      await this.initializeChatConnector();
      
      // Paso 5: Configurar interconexiones
      this.setupModuleInterconnections();
      
      // Paso 6: Iniciar monitoreo
      this.startSystemMonitoring();
      
      this.isInitialized = true;
      this.systemState = 'operational';
      this.addDiagnostic('success', 'System fully initialized and operational');
      console.log('✅ SystemManager: System initialization completed successfully');
      
      return true;

    } catch (error) {
      this.systemState = 'error';
      this.addDiagnostic('error', `System initialization failed: ${error.message}`);
      console.error('❌ SystemManager: Initialization failed:', error);
      
      // Reportar error al usuario
      if (this.modules.statusReporter) {
        this.modules.statusReporter.updateStatus({
          level: 'error',
          message: 'Error al inicializar el sistema',
          details: {
            error: error.message,
            suggestion: 'Recargar la página para reintentar'
          },
          timestamp: new Date().toISOString()
        });
      }
      
      return false;
    }
  }

  /**
   * Inicializar StatusReporter
   */
  async initializeStatusReporter() {
    console.log('📊 Initializing StatusReporter...');
    
    this.modules.statusReporter = new StatusReporter();
    const success = this.modules.statusReporter.initialize('status-text', 'status-indicator');
    
    if (!success) {
      throw new Error('Failed to initialize StatusReporter');
    }
    
    this.initializationStatus.statusReporter = true;
    this.modules.statusReporter.updateStatus({
      level: 'warning',
      message: 'Inicializando sistema...',
      details: {
        step: 'StatusReporter inicializado',
        progress: '25%'
      },
      timestamp: new Date().toISOString()
    });
    
    this.addDiagnostic('success', 'StatusReporter initialized');
  }

  /**
   * Inicializar ConnectionTester
   */
  async initializeConnectionTester() {
    console.log('🔍 Initializing ConnectionTester...');
    
    this.modules.connectionTester = new ConnectionTester();
    this.initializationStatus.connectionTester = true;
    
    this.modules.statusReporter.updateStatus({
      level: 'warning',
      message: 'Probando conectividad...',
      details: {
        step: 'ConnectionTester inicializado',
        progress: '50%'
      },
      timestamp: new Date().toISOString()
    });
    
    // Ejecutar tests de conectividad
    const connectionReport = await this.modules.connectionTester.runAllTests();
    this.modules.statusReporter.reportConnectionStatus(connectionReport);
    
    this.addDiagnostic('success', 'ConnectionTester initialized and tests completed');
  }

  /**
   * Inicializar HealthChecker
   */
  async initializeHealthChecker() {
    console.log('🏥 Initializing HealthChecker...');
    
    this.modules.healthChecker = new HealthChecker(this.modules.connectionTester);
    const success = await this.modules.healthChecker.initialize();
    
    if (!success) {
      throw new Error('Failed to initialize HealthChecker');
    }
    
    this.initializationStatus.healthChecker = true;
    
    this.modules.statusReporter.updateStatus({
      level: 'warning',
      message: 'Verificando estado del backend...',
      details: {
        step: 'HealthChecker inicializado',
        progress: '75%'
      },
      timestamp: new Date().toISOString()
    });
    
    // Configurar listener para health status
    this.modules.healthChecker.addListener((healthStatus) => {
      this.modules.statusReporter.reportHealthStatus(healthStatus);
    });
    
    // Iniciar health checks periódicos
    this.modules.healthChecker.startPeriodicChecks();
    
    this.addDiagnostic('success', 'HealthChecker initialized and monitoring started');
  }

  /**
   * Inicializar ChatConnector
   */
  async initializeChatConnector() {
    console.log('💬 Initializing ChatConnector...');
    
    this.modules.chatConnector = new ChatConnector(this.modules.connectionTester);
    const success = await this.modules.chatConnector.initialize();
    
    if (!success) {
      this.addDiagnostic('warning', 'ChatConnector failed to initialize - chat may be limited');
      // No lanzamos error aquí porque el sistema puede funcionar sin chat
    } else {
      this.initializationStatus.chatConnector = true;
      this.addDiagnostic('success', 'ChatConnector initialized successfully');
    }
    
    this.modules.statusReporter.updateStatus({
      level: 'success',
      message: 'Sistema inicializado',
      details: {
        step: 'Todos los módulos cargados',
        progress: '100%',
        chatAvailable: success ? 'Sí' : 'Limitado'
      },
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Configurar interconexiones entre módulos
   */
  setupModuleInterconnections() {
    console.log('🔗 Setting up module interconnections...');
    
    // Los listeners ya están configurados en los métodos de inicialización
    // Aquí podríamos agregar más interconexiones si fuera necesario
    
    this.addDiagnostic('info', 'Module interconnections established');
  }

  /**
   * Iniciar monitoreo del sistema
   */
  startSystemMonitoring() {
    console.log('🔄 Starting system monitoring...');
    
    // Monitoreo cada 5 minutos
    setInterval(() => {
      this.performSystemHealthCheck();
    }, 5 * 60 * 1000);
    
    this.addDiagnostic('info', 'System monitoring started');
  }

  /**
   * Realizar health check del sistema completo
   */
  async performSystemHealthCheck() {
    console.log('🔍 Performing system health check...');
    
    const systemHealth = {
      timestamp: new Date().toISOString(),
      modules: {},
      overall: 'unknown'
    };

    // Check StatusReporter
    systemHealth.modules.statusReporter = {
      initialized: this.initializationStatus.statusReporter,
      working: !!this.modules.statusReporter
    };

    // Check ConnectionTester
    systemHealth.modules.connectionTester = {
      initialized: this.initializationStatus.connectionTester,
      working: !!this.modules.connectionTester
    };

    // Check HealthChecker
    if (this.modules.healthChecker) {
      const healthStats = this.modules.healthChecker.getConnectionStats();
      systemHealth.modules.healthChecker = {
        initialized: this.initializationStatus.healthChecker,
        working: healthStats.isRunning,
        lastCheck: healthStats.lastCheck
      };
    }

    // Check ChatConnector
    if (this.modules.chatConnector) {
      const chatStatus = this.modules.chatConnector.getStatus();
      const perfStats = this.modules.chatConnector.getPerformanceStats();
      systemHealth.modules.chatConnector = {
        initialized: chatStatus.isInitialized,
        working: chatStatus.isInitialized,
        successRate: perfStats.successRate,
        totalRequests: perfStats.totalRequests
      };
    }

    // Determinar estado general
    const workingModules = Object.values(systemHealth.modules).filter(m => m.working).length;
    const totalModules = Object.keys(systemHealth.modules).length;
    
    if (workingModules === totalModules) {
      systemHealth.overall = 'healthy';
    } else if (workingModules >= totalModules * 0.75) {
      systemHealth.overall = 'degraded';
    } else {
      systemHealth.overall = 'unhealthy';
    }

    this.addDiagnostic('info', `System health check: ${systemHealth.overall} (${workingModules}/${totalModules} modules working)`);
    
    return systemHealth;
  }

  /**
   * Enviar mensaje usando ChatConnector
   */
  async sendChatMessage(message, options = {}) {
    if (!this.modules.chatConnector || !this.initializationStatus.chatConnector) {
      const error = {
        success: false,
        error: 'Chat no disponible',
        details: 'ChatConnector no inicializado correctamente'
      };
      
      this.modules.statusReporter?.reportChatStatus(error);
      return error;
    }

    const result = await this.modules.chatConnector.sendMessage(message, options);
    this.modules.statusReporter?.reportChatStatus(result);
    
    return result;
  }

  /**
   * Obtener estado del sistema
   */
  getSystemStatus() {
    return {
      isInitialized: this.isInitialized,
      systemState: this.systemState,
      initializationStatus: { ...this.initializationStatus },
      modules: {
        statusReporter: !!this.modules.statusReporter,
        connectionTester: !!this.modules.connectionTester,
        healthChecker: !!this.modules.healthChecker,
        chatConnector: !!this.modules.chatConnector
      },
      diagnostics: this.getDiagnostics(5)
    };
  }

  /**
   * Agregar diagnóstico
   */
  addDiagnostic(level, message) {
    this.diagnostics.unshift({
      level,
      message,
      timestamp: new Date().toISOString()
    });

    // Mantener solo los últimos 100
    if (this.diagnostics.length > 100) {
      this.diagnostics = this.diagnostics.slice(0, 100);
    }
  }

  /**
   * Obtener diagnósticos recientes
   */
  getDiagnostics(limit = 10) {
    return this.diagnostics.slice(0, limit);
  }

  /**
   * Reiniciar sistema
   */
  async restart() {
    console.log('🔄 Restarting system...');
    
    // Detener monitoreo
    if (this.modules.healthChecker) {
      this.modules.healthChecker.stopPeriodicChecks();
    }

    // Reinicializar
    this.isInitialized = false;
    this.systemState = 'restarting';
    this.modules = {};
    this.initializationStatus = {
      connectionTester: false,
      healthChecker: false,
      chatConnector: false,
      statusReporter: false
    };

    this.addDiagnostic('info', 'System restart initiated');
    
    return await this.initialize();
  }

  /**
   * Obtener módulo específico
   */
  getModule(moduleName) {
    return this.modules[moduleName] || null;
  }
}

// Export para uso global
window.SystemManager = SystemManager;