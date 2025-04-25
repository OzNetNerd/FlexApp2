import log from '/static/js/core/logger.js';
import eventSystem from '/static/js/core/events.js';

/**
 * UI service for common UI operations
 */
class UiService {
  constructor() {
    this.modals = new Map();
    this.toasts = new Map();
    log('info', 'uiService.js', 'constructor', 'UI service created');
  }

  /**
   * Show a loading indicator
   * @param {string} elementId - Element ID to show loading in, or null for global loading
   * @param {string} message - Loading message
   * @returns {Object} - Loading controller with hide method
   */
  showLoading(elementId = null, message = 'Loading...') {
    const functionName = 'showLoading';

    // Create a unique ID for this loading indicator
    const loadingId = `loading-${Date.now()}`;

    log('debug', 'uiService.js', functionName, `Showing loading indicator: ${loadingId}`, {
      elementId: elementId,
      message: message
    });

    // Create loading indicator element
    const loadingElement = document.createElement('div');
    loadingElement.className = 'loading-indicator';
    loadingElement.innerHTML = `
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <div class="loading-message mt-2">${message}</div>
    `;

    // Position the loading indicator
    if (elementId) {
      // Show loading within a specific element
      const container = document.getElementById(elementId);
      if (container) {
        // Position relative if not already
        const computedStyle = window.getComputedStyle(container);
        if (computedStyle.position === 'static') {
          container.style.position = 'relative';
        }

        // Add loading indicator to container
        loadingElement.style.position = 'absolute';
        loadingElement.style.top = '0';
        loadingElement.style.left = '0';
        loadingElement.style.width = '100%';
        loadingElement.style.height = '100%';
        loadingElement.style.display = 'flex';
        loadingElement.style.flexDirection = 'column';
        loadingElement.style.alignItems = 'center';
        loadingElement.style.justifyContent = 'center';
        loadingElement.style.backgroundColor = 'rgba(255, 255, 255, 0.7)';
        loadingElement.style.zIndex = '1000';

        container.appendChild(loadingElement);
      } else {
        log('warn', 'uiService.js', functionName, `Container element not found: ${elementId}`);
      }
    } else {
      // Show global loading indicator
      loadingElement.style.position = 'fixed';
      loadingElement.style.top = '0';
      loadingElement.style.left = '0';
      loadingElement.style.width = '100%';
      loadingElement.style.height = '100%';
      loadingElement.style.display = 'flex';
      loadingElement.style.flexDirection = 'column';
      loadingElement.style.alignItems = 'center';
      loadingElement.style.justifyContent = 'center';
      loadingElement.style.backgroundColor = 'rgba(255, 255, 255, 0.7)';
      loadingElement.style.zIndex = '9999';

      document.body.appendChild(loadingElement);
    }

    // Create loading controller
    const controller = {
      hide: () => {
        if (loadingElement.parentNode) {
          loadingElement.parentNode.removeChild(loadingElement);
          log('debug', 'uiService.js', 'hideLoading', `Hidden loading indicator: ${loadingId}`);
        }
      },
      updateMessage: (newMessage) => {
        const messageElement = loadingElement.querySelector('.loading-message');
        if (messageElement) {
          messageElement.textContent = newMessage;
          log('debug', 'uiService.js', 'updateLoadingMessage', `Updated loading message for ${loadingId}: ${newMessage}`);
        }
      },
      getId: () => loadingId
    };

    return controller;
  }

  /**
   * Disable form while an operation is in progress
   * @param {string} formId - Form ID
   * @param {boolean} disabled - Whether to disable or enable the form
   */
  disableForm(formId, disabled = true) {
    const functionName = 'disableForm';

    const form = document.getElementById(formId);
    if (!form) {
      log('warn', 'uiService.js', functionName, `Form not found: ${formId}`);
      return;
    }

    // Get all interactive elements
    const elements = form.querySelectorAll('input, select, textarea, button');

    elements.forEach(element => {
      element.disabled = disabled;
    });

    log('debug', 'uiService.js', functionName, `${disabled ? 'Disabled' : 'Enabled'} form: ${formId}`);
  }

  /**
   * Show a toast message
   * @param {string} message - Toast message
   * @param {string} type - Toast type (success, error, warning, info)
   * @param {Object} options - Toast options
   * @returns {Object} - Toast controller with hide method
   */
  showToast(message, type = 'info', options = {}) {
    const functionName = 'showToast';

    // Default options
    const defaults = {
      title: '',
      duration: 5000, // ms
      showClose: true,
      position: 'top-right'
    };

    // Merge defaults with provided options
    const config = { ...defaults, ...options };

    // Get or create toast container
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'toast-container';
      toastContainer.className = `position-fixed p-3 ${getPositionClass(config.position)}`;
      toastContainer.style.zIndex = '9999';
      document.body.appendChild(toastContainer);
    }

    // Create toast element
    const toastId = `toast-${Date.now()}`;
    const toastElement = document.createElement('div');
    toastElement.id = toastId;
    toastElement.className = `toast show bg-${getBootstrapColorClass(type)}`;
    toastElement.role = 'alert';
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');

    // Create toast content
    const hasTitle = config.title.trim() !== '';
    toastElement.innerHTML = `
      ${hasTitle ? `
        <div class="toast-header">
          <strong class="me-auto">${config.title}</strong>
          ${config.showClose ? '<button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>' : ''}
        </div>
      ` : ''}
      <div class="toast-body text-${hasTitle ? 'dark' : 'white'}">
        ${message}
        ${!hasTitle && config.showClose ? '<button type="button" class="btn-close float-end" data-bs-dismiss="toast" aria-label="Close"></button>' : ''}
      </div>
    `;

    // Add to container
    toastContainer.appendChild(toastElement);

    log('debug', 'uiService.js', functionName, `Showing toast: ${toastId}`, {
      message: message,
      type: type
    });

    // Set up auto-hide
    let autoHideTimeout;
    if (config.duration > 0) {
      autoHideTimeout = setTimeout(() => {
        hideToast();
      }, config.duration);
    }

    // Function to hide the toast
    function hideToast() {
      if (toastElement.parentNode) {
        toastElement.parentNode.removeChild(toastElement);
        log('debug', 'uiService.js', 'hideToast', `Hidden toast: ${toastId}`);

        // Clean up empty container
        if (toastContainer.children.length === 0) {
          toastContainer.parentNode.removeChild(toastContainer);
        }

        // Clear timeout if exists
        if (autoHideTimeout) {
          clearTimeout(autoHideTimeout);
        }
      }
    }

    // Add close button listener
    const closeButton = toastElement.querySelector('.btn-close');
    if (closeButton) {
      closeButton.addEventListener('click', () => {
        hideToast();
      });
    }

    // Create toast controller
    const controller = {
      hide: hideToast,
      getId: () => toastId
    };

    // Store controller
    this.toasts.set(toastId, controller);

    return controller;
  }

  /**
   * Show a success toast
   * @param {string} message - Toast message
   * @param {Object} options - Toast options
   * @returns {Object} - Toast controller
   */
  showSuccess(message, options = {}) {
    return this.showToast(message, 'success', {
      title: options.title || 'Success',
      ...options
    });
  }

  /**
   * Show an error toast
   * @param {string} message - Toast message
   * @param {Object} options - Toast options
   * @returns {Object} - Toast controller
   */
  showError(message, options = {}) {
    return this.showToast(message, 'danger', {
      title: options.title || 'Error',
      ...options
    });
  }

  /**
   * Show a warning toast
   * @param {string} message - Toast message
   * @param {Object} options - Toast options
   * @returns {Object} - Toast controller
   */
  showWarning(message, options = {}) {
    return this.showToast(message, 'warning', {
      title: options.title || 'Warning',
      ...options
    });
  }

  /**
   * Show an info toast
   * @param {string} message - Toast message
   * @param {Object} options - Toast options
   * @returns {Object} - Toast controller
   */
  showInfo(message, options = {}) {
    return this.showToast(message, 'info', {
      title: options.title || 'Information',
      ...options
    });
  }

  /**
   * Check the Bootstrap availability
   * @returns {boolean} - Whether Bootstrap is available
   */
  isBootstrapAvailable() {
    return typeof bootstrap !== 'undefined';
  }
}

/**
 * Get Bootstrap color class from type
 * @param {string} type - Toast type
 * @returns {string} - Bootstrap color class
 */
function getBootstrapColorClass(type) {
  switch (type) {
    case 'success': return 'success';
    case 'error': return 'danger';
    case 'danger': return 'danger';
    case 'warning': return 'warning';
    case 'info': return 'info';
    default: return 'secondary';
  }
}

/**
 * Get position class from position string
 * @param {string} position - Position string
 * @returns {string} - Position class
 */
function getPositionClass(position) {
  switch (position) {
    case 'top-left': return 'top-0 start-0';
    case 'top-center': return 'top-0 start-50 translate-middle-x';
    case 'top-right': return 'top-0 end-0';
    case 'middle-left': return 'top-50 start-0 translate-middle-y';
    case 'middle-center': return 'top-50 start-50 translate-middle';
    case 'middle-right': return 'top-50 end-0 translate-middle-y';
    case 'bottom-left': return 'bottom-0 start-0';
    case 'bottom-center': return 'bottom-0 start-50 translate-middle-x';
    case 'bottom-right': return 'bottom-0 end-0';
    default: return 'top-0 end-0';
  }
}

// Create singleton instance
const uiService = new UiService();
export default uiService;