/**
 * Main Application - Inicialización y configuración global
 */
class App {
  constructor() {
    this.chat = null;
    this.initialized = false;
  }

  /**
   * Inicializar aplicación
   */
  init() {
    if (this.initialized) return;

    this.waitForDOMReady(() => {
      this.initChat();
      this.initSystemInfo();
      this.initialized = true;
      console.log('Advanced AI Agent initialized successfully');
    });
  }

  /**
   * Esperar a que el DOM esté listo
   */
  waitForDOMReady(callback) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', callback);
    } else {
      callback();
    }
  }

  /**
   * Inicializar chat
   */
  initChat() {
    this.chat = new ChatComponent();
    this.chat.init();
  }

  /**
   * Inicializar panel de información del sistema
   */
  initSystemInfo() {
    const toggleButton = document.getElementById('system-toggle-btn');
    const systemInfo = document.getElementById('system-info');
    const toggleIcon = document.getElementById('system-toggle-icon');

    if (toggleButton && systemInfo && toggleIcon) {
      toggleButton.addEventListener('click', () => {
        const isHidden = systemInfo.classList.contains('hidden');
        
        if (isHidden) {
          systemInfo.classList.remove('hidden');
          toggleIcon.textContent = '▲';
        } else {
          systemInfo.classList.add('hidden');
          toggleIcon.textContent = '▼';
        }
      });
    }
  }

  /**
   * Manejar errores globales
   */
  handleError(error) {
    console.error('Application error:', error);
    
    // Mostrar notificación de error al usuario si es necesario
    const errorMessage = document.createElement('div');
    errorMessage.className = 'fixed top-4 right-4 bg-red-500 text-white p-4 rounded-lg shadow-lg z-50';
    errorMessage.textContent = 'Ocurrió un error inesperado. Por favor, recarga la página.';
    
    document.body.appendChild(errorMessage);
    
    setTimeout(() => {
      errorMessage.remove();
    }, 5000);
  }
}

// Inicializar aplicación
const app = new App();

// Manejar errores no capturados
window.addEventListener('error', (e) => {
  app.handleError(e.error);
});

window.addEventListener('unhandledrejection', (e) => {
  app.handleError(e.reason);
});

// Inicializar cuando se cargue la página
app.init();