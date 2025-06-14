/**
 * Chat Component - Lógica principal del chat
 */
class ChatComponent {
  constructor() {
    this.sessionId = 'default';
    this.isProcessing = false;
    this.messageComponent = null;
    this.statusComponent = null;
    this.elements = {};
  }

  /**
   * Inicializar chat
   */
  init() {
    this.initElements();
    this.initComponents();
    this.bindEvents();
    this.addWelcomeMessage();
    this.focusInput();
  }

  /**
   * Inicializar elementos DOM
   */
  initElements() {
    this.elements = {
      messageInput: document.getElementById('message-input'),
      sendButton: document.getElementById('send-button'),
      messagesContainer: document.getElementById('messages'),
      statusIndicator: document.getElementById('status-indicator'),
      statusText: document.getElementById('status-text')
    };

    // Verificar que todos los elementos existen
    Object.entries(this.elements).forEach(([key, element]) => {
      if (!element) {
        console.error(`Element not found: ${key}`);
      }
    });
  }

  /**
   * Inicializar componentes
   */
  initComponents() {
    this.messageComponent = new MessageComponent(this.elements.messagesContainer);
    this.statusComponent = new StatusComponent(
      this.elements.statusIndicator,
      this.elements.statusText
    );
    
    this.statusComponent.init();
  }

  /**
   * Vincular eventos
   */
  bindEvents() {
    // Evento de envío
    this.elements.sendButton.addEventListener('click', () => this.sendMessage());
    
    // Evento Enter en input
    this.elements.messageInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Evento focus automático
    this.elements.messageInput.addEventListener('blur', () => {
      setTimeout(() => this.focusInput(), 100);
    });
  }

  /**
   * Enviar mensaje
   */
  async sendMessage() {
    const message = this.elements.messageInput.value.trim();
    
    if (!message || this.isProcessing) return;

    // Limpiar input y deshabilitar envío
    this.elements.messageInput.value = '';
    this.setProcessingState(true);

    // Agregar mensaje del usuario
    this.messageComponent.addMessage(message, 'user');

    // Mostrar indicador de escritura
    this.messageComponent.showTypingIndicator();

    try {
      // Enviar al backend
      const result = await window.apiService.sendMessage(message, this.sessionId);

      // Ocultar indicador de escritura
      this.messageComponent.hideTypingIndicator();

      if (result.success) {
        // Respuesta exitosa del backend
        const responseText = result.data.response || result.data.message || 'Respuesta recibida';
        
        setTimeout(() => {
          this.messageComponent.addMessage(responseText, 'ai', result.data.timestamp);
          this.focusInput();
        }, 300);

      } else {
        // Error del backend - usar respuesta de fallback
        setTimeout(() => {
          const fallbackResponse = this.generateFallbackResponse(message);
          this.messageComponent.addMessage(fallbackResponse, 'ai');
          this.focusInput();
        }, 300);
      }

    } catch (error) {
      console.error('Chat error:', error);
      this.messageComponent.hideTypingIndicator();
      
      // Respuesta de error
      setTimeout(() => {
        const errorResponse = 'Lo siento, ocurrió un error. Por favor intenta nuevamente.';
        this.messageComponent.addMessage(errorResponse, 'ai');
        this.focusInput();
      }, 300);
    } finally {
      this.setProcessingState(false);
    }
  }

  /**
   * Establecer estado de procesamiento
   */
  setProcessingState(processing) {
    this.isProcessing = processing;
    this.elements.sendButton.disabled = processing;
    this.elements.sendButton.textContent = processing ? 'Enviando...' : 'Enviar';
    
    if (processing) {
      this.elements.sendButton.classList.add('opacity-50');
    } else {
      this.elements.sendButton.classList.remove('opacity-50');
    }
  }

  /**
   * Generar respuesta de fallback
   */
  generateFallbackResponse(userMessage) {
    const msg = userMessage.toLowerCase();
    
    const responses = {
      'hola|hello|hi': '¡Hola! 👋 Soy tu Advanced AI Agent. Estoy funcionando con respuestas de fallback mientras se actualiza la conexión con el backend.',
      'cómo estás|how are you': '¡Estoy funcionando correctamente! 🚀 El sistema está operativo, aunque temporalmente usando respuestas locales.',
      'azure|cloud': '¡Perfecto! Estoy desplegado en Azure Cloud. El sistema está funcionando al 100%. 💙☁️',
      'ayuda|help': '¡Por supuesto! Puedo ayudarte con consultas generales. ¿En qué necesitas asistencia? 🤝',
      'gracias|thank': '¡De nada! 😊 Siempre es un placer ayudar. Si tienes más preguntas, no dudes en escribirme.',
      'error|problema': 'Entiendo que hay un problema. Estoy trabajando para solucionarlo. Mientras tanto, puedo ayudarte con información general. 🔧'
    };
    
    // Buscar respuesta coincidente
    for (const [patterns, response] of Object.entries(responses)) {
      if (patterns.split('|').some(pattern => msg.includes(pattern))) {
        return response;
      }
    }
    
    // Respuesta por defecto
    return `Entiendo tu consulta sobre "${userMessage}". Como Advanced AI Agent, estoy aquí para ayudarte. ¿Podrías ser más específico sobre lo que necesitas? 🤖`;
  }

  /**
   * Agregar mensaje de bienvenida
   */
  addWelcomeMessage() {
    const welcomeText = '¡Hola! Soy tu Advanced AI Agent. Estoy aquí para ayudarte con cualquier consulta. ¿En qué puedo asistirte hoy?';
    this.messageComponent.addMessage(welcomeText, 'ai');
  }

  /**
   * Enfocar input
   */
  focusInput() {
    if (this.elements.messageInput) {
      this.elements.messageInput.focus();
    }
  }
}