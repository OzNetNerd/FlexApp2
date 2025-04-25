import log from '/static/js/core/logger.js';
import eventSystem from '/static/js/core/events.js';
import uiService from '/static/js/services/uiService.js';

/**
 * Notification service for showing toasts and alerts
 */
class NotificationService {
  constructor() {
    log('info', 'notificationService.js', 'constructor', 'Notification service created');

    // Set up event listeners for various error types
    this.setupErrorListeners();
  }

  /**
   * Set up listeners for various error events
   */
  setupErrorListeners() {
    const functionName = 'setupErrorListeners';

    // API errors
    eventSystem.subscribe('api.error', (data) => {
      log('debug', 'notificationService.js', functionName, 'Received API error event', data);
      this.showError(data.message || 'API Error', {
        title: data.title || 'API Error',
        details: data.error
      });
    });

    // Form validation errors
    eventSystem.subscribe('form.validated', (data) => {
      if (!data.isValid) {
        log('debug', 'notificationService.js', functionName, 'Received form validation error event', data);
        this.showFormErrors(data.errors, data.formId);
      }
    });

    // Form submission errors
    eventSystem.subscribe('form.submit.error', (data) => {
      log('debug', 'notificationService.js', functionName, 'Received form submission error event', data);
      this.showError('Form submission failed', {
        title: 'Form Error',
        details: data.error
      });
    });

    // Modal errors
    eventSystem.subscribe('modal.confirm.error', (data) => {
      log('debug', 'notificationService.js', functionName, 'Received modal confirmation error event', data);
      this.showError('Action failed', {
        title: 'Error',
        details: data.error
      });
    });

    // Table errors
    eventSystem.subscribe('table.data.error', (data) => {
      log('debug', 'notificationService.js', functionName, 'Received table data error event', data);
      this.showError('Failed to load table data', {
        title: 'Data Error',
        details: data.error
      });
    });

    eventSystem.subscribe('table.delete.error', (data) => {
      log('debug', 'notificationService.js', functionName, 'Received table delete error event', data);
      this.showError('Failed to delete item', {
        title: 'Delete Error',
        details: data.error
      });
    });

    // Global unhandled errors
    window.addEventListener('error', (event) => {
      log('error', 'notificationService.js', functionName, 'Caught unhandled error', event.error);
      this.showError('An unexpected error occurred', {
        title: 'Application Error',
        details: event.error
      });
    });

    // Global promise rejection
    window.addEventListener('unhandledrejection', (event) => {
      log('error', 'notificationService.js', functionName, 'Caught unhandled promise rejection', event.reason);
      this.showError('An unexpected error occurred', {
        title: 'Application Error',
        details: event.reason
      });
    });
  }

  /**
   * Show an error notification
   * @param {string} message - Error message
   * @param {Object} options - Error options
   */
  showError(message, options = {}) {
    const functionName = 'showError';

    log('debug', 'notificationService.js', functionName, `Showing error: ${message}`, options);

    // Show error toast
    uiService.showError(message, options);

    // If details are provided and console is available, log them
    if (options.details) {
      log('error', 'notificationService.js', functionName, 'Error details:', options.details);
    }
  }

  /**
   * Show a success notification
   * @param {string} message - Success message
   * @param {Object} options - Success options
   */
  showSuccess(message, options = {}) {
    const functionName = 'showSuccess';

    log('debug', 'notificationService.js', functionName, `Showing success: ${message}`, options);

    // Show success toast
    uiService.showSuccess(message, options);
  }

  /**
   * Show a warning notification
   * @param {string} message - Warning message
   * @param {Object} options - Warning options
   */
  showWarning(message, options = {}) {
    const functionName = 'showWarning';

    log('debug', 'notificationService.js', functionName, `Showing warning: ${message}`, options);

    // Show warning toast
    uiService.showWarning(message, options);
  }

  /**
   * Show an info notification
   * @param {string} message - Info message
   * @param {Object} options - Info options
   */
  showInfo(message, options = {}) {
    const functionName = 'showInfo';

    log('debug', 'notificationService.js', functionName, `Showing info: ${message}`, options);

    // Show info toast
    uiService.showInfo(message, options);
  }

  /**
   * Show form validation errors
   * @param {Object} errors - Error object with field names as keys and error messages as values
   * @param {string} formId - Form ID
   */
  showFormErrors(errors, formId) {
    const functionName = 'showFormErrors';

    if (!errors || Object.keys(errors).length === 0) {
      return;
    }

    log('debug', 'notificationService.js', functionName, `Showing form errors for form ${formId}`, errors);

    // Get the form element
    const form = document.getElementById(formId);
    if (!form) {
      // If form not found, show a generic error
      this.showError('Form validation failed', {
        title: 'Validation Error',
        details: errors
      });
      return;
    }

    // Remove any existing error messages and highlights
    form.querySelectorAll('.is-invalid').forEach(element => {
      element.classList.remove('is-invalid');
    });

    form.querySelectorAll('.invalid-feedback').forEach(element => {
      element.remove();
    });

    // Show a summary notification
    const errorCount = Object.keys(errors).length;
    this.showError(`Form contains ${errorCount} error${errorCount > 1 ? 's' : ''}`, {
      title: 'Validation Failed'
    });

    // Add error messages and highlights
    for (const [fieldName, errorMessage] of Object.entries(errors)) {
      const field = form.querySelector(`[name="${fieldName}"], #${fieldName}`);
      if (field) {
        // Add error class to field
        field.classList.add('is-invalid');

        // Create error message element
        const errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        errorElement.textContent = errorMessage;

        // Insert after field
        field.parentNode.insertBefore(errorElement, field.nextSibling);
      }
    }
  }
}

// Create singleton instance
const notificationService = new NotificationService();
export default notificationService;