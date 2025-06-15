/**
 * STATUS REPORTER MODULE
 * Módulo independiente para reportar el estado del sistema al usuario de forma clara
 */
class StatusReporter {
  constructor() {
    this.statusElement = null;
    this.indicatorElement = null;
    this.detailsElement = null;
    this.currentStatus = {
      level: 'unknown',
      message: 'Iniciando...',
      details: null,
      timestamp: null
    };
    this.statusHistory = [];
    this.maxHistorySize = 20;
  }

  /**
   * Inicializar con elementos DOM
   */
  initialize(statusElementId, indicatorElementId, detailsElementId = null) {
    this.statusElement = document.getElementById(statusElementId);
    this.indicatorElement = document.getElementById(indicatorElementId);
    
    if (detailsElementId) {
      this.detailsElement = document.getElementById(detailsElementId);
    }

    if (!this.statusElement || !this.indicatorElement) {
      console.error('❌ StatusReporter: Required DOM elements not found');
      return false;
    }

    console.log('📊 StatusReporter initialized');
    this.updateDisplay();
    return true;
  }

  /**
   * Reportar estado de conexión
   */
  reportConnectionStatus(connectionReport) {
    const { summary, recommendations } = connectionReport;
    
    let status = {
      timestamp: new Date().toISOString()
    };

    if (summary.proxyWorks) {
      status = {
        ...status,
        level: 'success',
        message: 'Conectado vía proxy',
        details: {
          method: 'Azure Static Web Apps Proxy',
          recommendation: 'Usando /api/* routes',
          technical: recommendations[0]
        }
      };
    } else if (summary.directWorks && summary.corsWorks) {
      status = {
        ...status,
        level: 'success',
        message: 'Conectado directamente',
        details: {
          method: 'Direct CORS connection',
          recommendation: 'Usando conexión directa al backend',
          technical: recommendations[0]
        }
      };
    } else if (summary.directWorks && !summary.corsWorks) {
      status = {
        ...status,
        level: 'warning',
        message: 'Backend disponible con limitaciones CORS',
        details: {
          method: 'Limited connectivity',
          recommendation: 'Backend funciona pero hay problemas CORS',
          technical: recommendations[0]
        }
      };
    } else {
      status = {
        ...status,
        level: 'error',
        message: 'Sin conexión al backend',
        details: {
          method: 'No connection',
          recommendation: 'Verificar estado del backend',
          technical: recommendations[0] || 'No working connection found'
        }
      };
    }

    this.updateStatus(status);
  }

  /**
   * Reportar estado de health check
   */
  reportHealthStatus(healthStatus) {
    let status = {
      timestamp: healthStatus.timestamp
    };

    if (healthStatus.success) {
      status = {
        ...status,
        level: 'success',
        message: 'Backend operativo',
        details: {
          service: healthStatus.details?.service || 'Unknown',
          version: healthStatus.details?.version || 'Unknown',
          uptime: this.formatUptime(healthStatus.details?.uptime || 0),
          ai_status: healthStatus.details?.ai_enabled || 'Unknown',
          connection: healthStatus.connectionMethod
        }
      };
    } else {
      status = {
        ...status,
        level: 'error',
        message: healthStatus.message || 'Error de health check',
        details: {
          error: healthStatus.details || 'Unknown error',
          connection: healthStatus.connectionMethod || 'Unknown',
          suggestion: this.getHealthErrorSuggestion(healthStatus)
        }
      };
    }

    this.updateStatus(status);
  }

  /**
   * Reportar estado de chat
   */
  reportChatStatus(chatResult) {
    let status = {
      timestamp: chatResult.timestamp
    };

    if (chatResult.success) {
      const responseTime = chatResult.duration || 0;
      status = {
        ...status,
        level: 'success',
        message: `Chat funcionando (${responseTime}ms)`,
        details: {
          responseTime: `${responseTime}ms`,
          requestId: chatResult.requestId,
          model: chatResult.data?.model_used || 'Unknown',
          tokens: chatResult.data?.tokens_used || 'Unknown'
        }
      };
    } else {
      status = {
        ...status,
        level: 'error',
        message: 'Error en chat',
        details: {
          error: chatResult.error || 'Unknown error',
          requestId: chatResult.requestId,
          suggestion: this.getChatErrorSuggestion(chatResult)
        }
      };
    }

    this.updateStatus(status);
  }

  /**
   * Actualizar estado interno y display
   */
  updateStatus(newStatus) {
    this.currentStatus = { ...newStatus };
    this.addToHistory(newStatus);
    this.updateDisplay();
    
    console.log(`📊 Status updated [${newStatus.level}]:`, newStatus.message);
  }

  /**
   * Actualizar elementos DOM
   */
  updateDisplay() {
    if (!this.statusElement || !this.indicatorElement) {
      return;
    }

    // Actualizar texto de estado
    this.statusElement.textContent = this.currentStatus.message;

    // Actualizar indicador visual
    this.updateIndicator();

    // Actualizar detalles si existe el elemento
    if (this.detailsElement && this.currentStatus.details) {
      this.updateDetails();
    }
  }

  /**
   * Actualizar indicador visual
   */
  updateIndicator() {
    // Remover clases anteriores
    this.indicatorElement.className = 'status-indicator';

    // Agregar clase según el nivel
    switch (this.currentStatus.level) {
      case 'success':
        this.indicatorElement.classList.add('status-connected');
        break;
      case 'warning':
        this.indicatorElement.classList.add('status-warning');
        break;
      case 'error':
        this.indicatorElement.classList.add('status-error');
        break;
      default:
        this.indicatorElement.classList.add('status-connecting');
    }
  }

  /**
   * Actualizar detalles extendidos
   */
  updateDetails() {
    if (!this.detailsElement || !this.currentStatus.details) {
      return;
    }

    const details = this.currentStatus.details;
    let detailsHtml = '<div class="status-details">';

    for (const [key, value] of Object.entries(details)) {
      const label = this.formatLabel(key);
      detailsHtml += `
        <div class="status-detail-item">
          <span class="status-detail-label">${label}:</span>
          <span class="status-detail-value">${value}</span>
        </div>
      `;
    }

    detailsHtml += '</div>';
    this.detailsElement.innerHTML = detailsHtml;
  }

  /**
   * Formatear etiquetas para mostrar
   */
  formatLabel(key) {
    const labels = {
      method: 'Método',
      service: 'Servicio',
      version: 'Versión',
      uptime: 'Tiempo activo',
      ai_status: 'IA',
      connection: 'Conexión',
      responseTime: 'Tiempo respuesta',
      requestId: 'ID Request',
      model: 'Modelo',
      tokens: 'Tokens',
      error: 'Error',
      suggestion: 'Sugerencia',
      recommendation: 'Recomendación',
      technical: 'Detalles técnicos'
    };
    
    return labels[key] || key.charAt(0).toUpperCase() + key.slice(1);
  }

  /**
   * Formatear tiempo de actividad
   */
  formatUptime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
      return `${minutes}m`;
    } else {
      return `${Math.floor(seconds)}s`;
    }
  }

  /**
   * Obtener sugerencia para errores de health
   */
  getHealthErrorSuggestion(healthStatus) {
    if (healthStatus.details?.includes('HTML')) {
      return 'El backend está devolviendo HTML. Revisar configuración de proxy.';
    }
    if (healthStatus.details?.includes('CORS')) {
      return 'Problema de CORS. Verificar headers en el backend.';
    }
    if (healthStatus.details?.includes('Network')) {
      return 'Error de red. Verificar que el backend esté funcionando.';
    }
    return 'Error desconocido. Revisar logs del backend.';
  }

  /**
   * Obtener sugerencia para errores de chat
   */
  getChatErrorSuggestion(chatResult) {
    if (chatResult.error?.includes('405')) {
      return 'Método no permitido. Verificar endpoint y configuración.';
    }
    if (chatResult.error?.includes('CORS')) {
      return 'Error CORS en el chat. Revisar configuración del backend.';
    }
    if (chatResult.error?.includes('HTML')) {
      return 'Chat devuelve HTML en lugar de JSON. Problema de routing.';
    }
    return 'Error de chat. Verificar logs y conectividad.';
  }

  /**
   * Agregar al historial
   */
  addToHistory(status) {
    this.statusHistory.unshift({ ...status });
    
    if (this.statusHistory.length > this.maxHistorySize) {
      this.statusHistory = this.statusHistory.slice(0, this.maxHistorySize);
    }
  }

  /**
   * Obtener historial de estados
   */
  getHistory(limit = 10) {
    return this.statusHistory.slice(0, limit);
  }

  /**
   * Obtener estado actual
   */
  getCurrentStatus() {
    return { ...this.currentStatus };
  }

  /**
   * Limpiar historial
   */
  clearHistory() {
    this.statusHistory = [];
    console.log('🗑️ Status history cleared');
  }
}

// Export para uso global
window.StatusReporter = StatusReporter;