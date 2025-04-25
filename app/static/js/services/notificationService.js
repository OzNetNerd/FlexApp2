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
      log('debug', data.scriptName || 'unknown', 'notificationService.js', functionName, 'Received API error event', data);
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

  // Other functions remain the same...
}

// Create singleton instance
const notificationService = new NotificationService();
export default notificationService;
