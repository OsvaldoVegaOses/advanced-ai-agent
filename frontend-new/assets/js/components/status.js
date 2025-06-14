/**
 * Status Component - Gestión del estado de conexión
 */
class StatusComponent {
  constructor(indicatorElement, textElement) {
    this.indicatorElement = indicatorElement;
    this.textElement = textElement;
    this.currentStatus = 'connecting';
    this.healthCheckInterval = null;
  }

  /**
   * Inicializar verificación de estado
   */
  init() {
    this.checkStatus();
    this.startHealthCheck();
  }

  /**
   * Verificar estado del backend
   */
  async checkStatus() {
    this.setStatus('connecting', 'Conectando...');
    
    const result = await window.apiService.checkHealth();
    
    if (result.success) {
      this.setStatus('connected', 'Conectado');
    } else {
      this.setStatus('error', 'Sin conexión');
    }
  }

  /**
   * Establecer estado visual
   */
  setStatus(status, text) {
    this.currentStatus = status;
    
    // Remover clases anteriores
    this.indicatorElement.className = 'status-indicator';
    
    // Agregar clase correspondiente
    switch (status) {
      case 'connected':
        this.indicatorElement.classList.add('status-connected');
        break;
      case 'connecting':
        this.indicatorElement.classList.add('status-connecting');
        break;
      case 'error':
        this.indicatorElement.classList.add('status-error');
        break;
    }
    
    this.textElement.textContent = text;
  }

  /**
   * Iniciar verificación periódica
   */
  startHealthCheck() {
    // Verificar cada 30 segundos
    this.healthCheckInterval = setInterval(() => {
      this.checkStatus();
    }, 30000);
  }

  /**
   * Detener verificación periódica
   */
  stopHealthCheck() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }

  /**
   * Obtener estado actual
   */
  getStatus() {
    return this.currentStatus;
  }
}