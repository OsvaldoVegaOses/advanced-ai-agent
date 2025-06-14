/**
 * Message Component - Renderizado de mensajes del chat
 */
class MessageComponent {
  constructor(container) {
    this.container = container;
  }

  /**
   * Agregar mensaje al chat
   */
  addMessage(content, sender, timestamp = null) {
    const messageElement = this.createMessageElement(content, sender, timestamp);
    this.container.appendChild(messageElement);
    this.scrollToBottom();
    
    // Animar entrada
    setTimeout(() => {
      messageElement.classList.add('animate-fade-in');
    }, 10);
  }

  /**
   * Crear elemento DOM del mensaje
   */
  createMessageElement(content, sender, timestamp) {
    const messageDiv = document.createElement('div');
    const timeStr = timestamp ? new Date(timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
    
    if (sender === 'user') {
      messageDiv.innerHTML = `
        <div class="flex items-start space-x-3 justify-end opacity-0 transition-all duration-300">
          <div class="message-bubble message-user">
            <p class="text-white">${this.escapeHtml(content)}</p>
            <span class="text-xs text-blue-200 mt-2 block">${timeStr}</span>
          </div>
          <div class="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center flex-shrink-0">
            👤
          </div>
        </div>
      `;
    } else {
      messageDiv.innerHTML = `
        <div class="flex items-start space-x-3 opacity-0 transition-all duration-300">
          <div class="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center flex-shrink-0">
            🤖
          </div>
          <div class="message-bubble message-ai">
            <p class="text-gray-800">${this.escapeHtml(content)}</p>
            <span class="text-xs text-gray-500 mt-2 block">${timeStr}</span>
          </div>
        </div>
      `;
    }
    
    return messageDiv;
  }

  /**
   * Mostrar indicador de escritura
   */
  showTypingIndicator() {
    const existingIndicator = this.container.querySelector('.typing-indicator');
    if (existingIndicator) return;

    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = `
      <div class="flex items-start space-x-3">
        <div class="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center flex-shrink-0">
          🤖
        </div>
        <div class="message-bubble message-ai">
          <div class="flex space-x-1">
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style="animation-delay: 0.2s"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style="animation-delay: 0.4s"></div>
          </div>
          <span class="text-xs text-gray-500 mt-2 block">Escribiendo...</span>
        </div>
      </div>
    `;

    this.container.appendChild(typingDiv);
    this.scrollToBottom();
  }

  /**
   * Ocultar indicador de escritura
   */
  hideTypingIndicator() {
    const indicator = this.container.querySelector('.typing-indicator');
    if (indicator) {
      indicator.remove();
    }
  }

  /**
   * Limpiar mensajes
   */
  clearMessages() {
    this.container.innerHTML = '';
  }

  /**
   * Scroll automático al final
   */
  scrollToBottom() {
    const scrollContainer = this.container.parentElement;
    scrollContainer.scrollTop = scrollContainer.scrollHeight;
  }

  /**
   * Escapar HTML para prevenir XSS
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}