/**
 * MAIN MODULAR - Sistema modular paso a paso
 * Implementación modular que reemplaza el sistema anterior
 */

// Sistema Global
let systemManager = null;
let isSystemReady = false;

/**
 * Inicializar sistema modular
 */
async function initializeModularSystem() {
  console.log('🚀 Initializing Advanced AI Agent - Modular System');

  try {
    // Crear instancia del SystemManager
    systemManager = new SystemManager();
    
    // Mostrar loading
    showLoadingIndicator('Inicializando sistema modular...');
    
    // Inicializar todo el sistema
    const success = await systemManager.initialize();
    
    if (success) {
      console.log('✅ Modular system initialized successfully');
      isSystemReady = true;
      
      // Configurar UI handlers
      setupUIHandlers();
      
      // Mostrar mensaje de bienvenida
      showWelcomeMessage();
      
      // Ocultar loading
      hideLoadingIndicator();
      
    } else {
      throw new Error('System initialization failed');
    }
    
  } catch (error) {
    console.error('❌ Failed to initialize modular system:', error);
    isSystemReady = false;
    
    showErrorMessage('Error al inicializar el sistema', error.message);
    hideLoadingIndicator();
  }
}

/**
 * Configurar manejadores de UI
 */
function setupUIHandlers() {
  console.log('🎛️ Setting up UI handlers...');

  // Input de mensaje
  const messageInput = document.getElementById('message-input');
  const sendButton = document.getElementById('send-button');

  if (messageInput && sendButton) {
    // Handler para envío de mensaje
    const handleSendMessage = async () => {
      const message = messageInput.value.trim();
      if (!message) return;

      if (!isSystemReady) {
        showErrorMessage('Sistema no listo', 'El sistema aún se está inicializando');
        return;
      }

      // Limpiar input
      messageInput.value = '';
      
      // Deshabilitar envío temporalmente
      setUIEnabled(false);

      try {
        // Mostrar mensaje del usuario
        addMessageToUI('user', message);
        
        // Mostrar typing indicator
        showTypingIndicator();

        // Enviar mensaje usando SystemManager
        const result = await systemManager.sendChatMessage(message, {
          conversationId: getConversationId(),
          temperature: 0.7,
          maxTokens: 1000
        });

        // Ocultar typing indicator
        hideTypingIndicator();

        if (result.success) {
          // Mostrar respuesta de la IA
          addMessageToUI('assistant', result.data.response);
          
          // Actualizar estadísticas si están visibles
          updateChatStats();
        } else {
          // Mostrar error de chat
          addMessageToUI('system', `Error: ${result.error}`);
        }

      } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        addMessageToUI('system', `Error inesperado: ${error.message}`);
      } finally {
        // Rehabilitar UI
        setUIEnabled(true);
        messageInput.focus();
      }
    };

    // Event listeners
    sendButton.addEventListener('click', handleSendMessage);
    
    messageInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    });

    // Focus inicial
    messageInput.focus();
  }

  // Panel de información del sistema
  setupSystemInfoPanel();
  
  console.log('✅ UI handlers configured');
}

/**
 * Configurar panel de información del sistema
 */
function setupSystemInfoPanel() {
  const toggleBtn = document.getElementById('system-toggle-btn');
  const systemInfo = document.getElementById('system-info');
  const toggleIcon = document.getElementById('system-toggle-icon');

  if (toggleBtn && systemInfo && toggleIcon) {
    toggleBtn.addEventListener('click', () => {
      const isHidden = systemInfo.classList.contains('hidden');
      
      if (isHidden) {
        systemInfo.classList.remove('hidden');
        toggleIcon.textContent = '▲';
        toggleBtn.setAttribute('aria-expanded', 'true');
        
        // Actualizar información del sistema
        updateSystemInfo();
      } else {
        systemInfo.classList.add('hidden');
        toggleIcon.textContent = '▼';
        toggleBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }
}

/**
 * Actualizar información del sistema
 */
function updateSystemInfo() {
  if (!systemManager) return;

  const systemInfo = document.getElementById('system-info');
  if (!systemInfo) return;

  const status = systemManager.getSystemStatus();
  const diagnostics = systemManager.getDiagnostics(3);

  const infoHtml = `
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
      <div>
        <strong class="text-gray-700">Sistema:</strong>
        <span class="text-${status.systemState === 'operational' ? 'green' : 'yellow'}-600">
          ${status.systemState === 'operational' ? '✅ Operativo' : '⚠️ ' + status.systemState}
        </span>
      </div>
      <div>
        <strong class="text-gray-700">Módulos:</strong>
        <span class="text-green-600">
          ✅ ${Object.values(status.modules).filter(Boolean).length}/4 activos
        </span>
      </div>
      <div>
        <strong class="text-gray-700">Chat:</strong>
        <span class="text-${status.initializationStatus.chatConnector ? 'green' : 'red'}-600">
          ${status.initializationStatus.chatConnector ? '✅ Disponible' : '❌ No disponible'}
        </span>
      </div>
    </div>
    
    <div class="mt-3 pt-3 border-t border-gray-200">
      <div class="text-xs">
        <strong>Diagnósticos recientes:</strong>
        <div class="mt-1 space-y-1">
          ${diagnostics.map(d => `
            <div class="flex items-center space-x-2">
              <span class="w-2 h-2 rounded-full bg-${d.level === 'success' ? 'green' : d.level === 'warning' ? 'yellow' : d.level === 'error' ? 'red' : 'blue'}-400"></span>
              <span class="text-gray-600">${d.message}</span>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
    
    <div class="mt-3 pt-3 border-t border-gray-200">
      <div class="flex flex-wrap gap-4 text-xs">
        <button onclick="showSystemDiagnostics()" class="text-blue-600 hover:underline">
          📊 Diagnósticos completos
        </button>
        <button onclick="restartSystem()" class="text-orange-600 hover:underline">
          🔄 Reiniciar sistema
        </button>
        <a href="https://github.com/OsvaldoVegaOses/advanced-ai-agent" 
           target="_blank" 
           rel="noopener noreferrer"
           class="text-blue-600 hover:underline">
          📂 Código fuente
        </a>
        <span class="text-gray-500">Version 3.0.0 - Modular</span>
      </div>
    </div>
  `;

  systemInfo.innerHTML = infoHtml;
}

/**
 * Mostrar estadísticas de chat
 */
function updateChatStats() {
  if (!systemManager) return;

  const chatConnector = systemManager.getModule('chatConnector');
  if (!chatConnector) return;

  const stats = chatConnector.getPerformanceStats();
  console.log('📊 Chat Stats:', stats);
}

/**
 * Agregar mensaje a la UI
 */
function addMessageToUI(role, content) {
  const messagesContainer = document.getElementById('messages');
  if (!messagesContainer) return;

  const messageElement = document.createElement('div');
  messageElement.className = `message message-${role}`;
  
  const timestamp = new Date().toLocaleTimeString();
  
  messageElement.innerHTML = `
    <div class="message-content">
      <div class="message-header">
        <span class="message-role">${role === 'user' ? '👤 Tú' : role === 'assistant' ? '🤖 AI' : '⚙️ Sistema'}</span>
        <span class="message-time">${timestamp}</span>
      </div>
      <div class="message-text">${content}</div>
    </div>
  `;

  messagesContainer.appendChild(messageElement);
  
  // Scroll hacia abajo
  const container = document.getElementById('messages-container');
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

/**
 * Mostrar/ocultar typing indicator
 */
function showTypingIndicator() {
  addMessageToUI('assistant', '<div class="typing-indicator">🤖 Escribiendo...</div>');
}

function hideTypingIndicator() {
  const messages = document.querySelectorAll('.message-assistant .typing-indicator');
  messages.forEach(msg => msg.closest('.message').remove());
}

/**
 * Habilitar/deshabilitar UI
 */
function setUIEnabled(enabled) {
  const messageInput = document.getElementById('message-input');
  const sendButton = document.getElementById('send-button');
  
  if (messageInput) messageInput.disabled = !enabled;
  if (sendButton) sendButton.disabled = !enabled;
}

/**
 * Obtener ID de conversación
 */
function getConversationId() {
  // Por ahora usar un ID fijo, en el futuro se puede hacer dinámico
  return 'default';
}

/**
 * Mostrar/ocultar indicador de carga
 */
function showLoadingIndicator(message = 'Cargando...') {
  const loading = document.getElementById('loading');
  if (loading) {
    loading.querySelector('span').textContent = message;
    loading.classList.remove('hidden');
  }
}

function hideLoadingIndicator() {
  const loading = document.getElementById('loading');
  if (loading) {
    loading.classList.add('hidden');
  }
}

/**
 * Mostrar mensaje de bienvenida
 */
function showWelcomeMessage() {
  addMessageToUI('assistant', '¡Hola! 👋 Soy tu Advanced AI Agent. El sistema modular se ha inicializado correctamente y estoy listo para ayudarte. ¿En qué puedo asistirte?');
}

/**
 * Mostrar mensaje de error
 */
function showErrorMessage(title, details) {
  addMessageToUI('system', `❌ ${title}: ${details}`);
}

/**
 * Mostrar diagnósticos del sistema
 */
function showSystemDiagnostics() {
  if (!systemManager) return;

  const diagnostics = systemManager.getDiagnostics(10);
  const status = systemManager.getSystemStatus();
  
  let message = '📊 **Diagnósticos del Sistema**\n\n';
  message += `**Estado general:** ${status.systemState}\n`;
  message += `**Módulos activos:** ${Object.values(status.modules).filter(Boolean).length}/4\n\n`;
  message += '**Últimos eventos:**\n';
  
  diagnostics.forEach(d => {
    const icon = d.level === 'success' ? '✅' : d.level === 'warning' ? '⚠️' : d.level === 'error' ? '❌' : 'ℹ️';
    message += `${icon} ${d.message}\n`;
  });

  addMessageToUI('system', message);
}

/**
 * Reiniciar sistema
 */
async function restartSystem() {
  if (!systemManager) return;

  addMessageToUI('system', '🔄 Reiniciando sistema...');
  showLoadingIndicator('Reiniciando sistema...');

  try {
    const success = await systemManager.restart();
    
    if (success) {
      addMessageToUI('system', '✅ Sistema reiniciado correctamente');
    } else {
      addMessageToUI('system', '❌ Error al reiniciar el sistema');
    }
  } catch (error) {
    addMessageToUI('system', `❌ Error durante el reinicio: ${error.message}`);
  } finally {
    hideLoadingIndicator();
  }
}

// Hacer funciones disponibles globalmente para botones
window.showSystemDiagnostics = showSystemDiagnostics;
window.restartSystem = restartSystem;

/**
 * Inicializar cuando DOM esté listo
 */
document.addEventListener('DOMContentLoaded', () => {
  console.log('📄 DOM loaded, initializing modular system...');
  initializeModularSystem();
});

/**
 * Manejar errores no capturados
 */
window.addEventListener('error', (event) => {
  console.error('Unhandled error:', event.error);
  if (isSystemReady) {
    addMessageToUI('system', `❌ Error inesperado: ${event.error.message}`);
  }
});

console.log('📦 Main-Modular loaded and ready');