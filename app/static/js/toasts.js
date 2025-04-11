// toasts.js

import log from '/static/js/logger.js';

// Simple toast system that doesn't rely heavily on Bootstrap
const ToastSystem = {
  initialized: false,
  container: null,
  template: null,
  queue: [],

  init: function() {
    if (this.initialized) return;

    log("debug", "toasts.js", "init", "Initializing simplified toast system");

    // Create container if it doesn't exist
    this.container = document.querySelector('.toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
      this.container.style.zIndex = '9999';
      // Important for stacking
      this.container.style.display = 'flex';
      this.container.style.flexDirection = 'column-reverse'; // New toasts at the top
      this.container.style.maxHeight = '80vh'; // Limit height
      this.container.style.overflowY = 'auto'; // Allow scrolling
      document.body.appendChild(this.container);
    }

    // Save template
    this.template = document.getElementById('liveToast');

    this.initialized = true;
    log("info", "toasts.js", "init", "Simplified toast system initialized");

    // Process any queued toasts
    this.processQueue();
  },

  processQueue: function() {
    if (this.queue.length > 0) {
      this.queue.forEach(item => {
        this.createToast(item.message, item.type);
      });
      this.queue = [];
    }
  },

  createToast: function(message, type) {
    try {
      // Create new toast element
      const toast = document.createElement('div');
      toast.className = `toast show`;
      toast.style.backgroundColor = type === 'danger' || type === 'error' ? '#dc3545' :
                                   type === 'warning' ? '#ffc107' :
                                   type === 'success' ? '#198754' : '#0d6efd';
      toast.style.color = (type === 'warning') ? '#000' : '#fff';
      toast.style.minWidth = '250px';
      toast.style.margin = '0.5rem 0'; // Vertical spacing
      toast.style.opacity = '1'; // Ensure visible
      toast.style.boxShadow = '0 0.25rem 0.75rem rgba(0, 0, 0, 0.1)';
      toast.style.borderRadius = '0.25rem';

      // Create toast content
      const content = document.createElement('div');
      content.className = 'd-flex';

      const body = document.createElement('div');
      body.className = 'toast-body';
      body.style.flex = '1';
      body.textContent = message;

      const closeBtn = document.createElement('button');
      closeBtn.type = 'button';
      closeBtn.className = 'btn-close btn-close-white me-2 m-auto';
      closeBtn.style.fontSize = '0.875rem';
      closeBtn.style.fontWeight = '700';
      closeBtn.style.opacity = '0.8';
      closeBtn.setAttribute('aria-label', 'Close');
      closeBtn.onclick = function() {
        toast.remove();
      };

      content.appendChild(body);
      content.appendChild(closeBtn);
      toast.appendChild(content);

      // Add to container (at the beginning for newest at top)
      this.container.prepend(toast);

      // Auto remove after 5 seconds
      setTimeout(() => {
        toast.remove();
      }, 6000);

      log("debug", "toasts.js", "createToast", `🍞 Showing toast: ${message} (${type})`);
    } catch (err) {
      console.error("Error creating toast:", err);
    }
  }
};

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
  log("debug", "toasts.js", "DOMContentLoaded", "Initializing toast notifications");

  // Initialize in a small delay to ensure DOM is ready
  setTimeout(() => {
    ToastSystem.init();
  }, 100);
});

// Public function for showing toasts
export function showToast(message, type = 'success') {
  // Convert "error" to "danger" to match Bootstrap's classes
  if (type === "error") {
    type = "danger";
  }

  // Clean and limit message
  const cleanMessage = typeof message === "string"
    ? message.replace(/\n/g, ' ').slice(0, 500)
    : JSON.stringify(message).slice(0, 500);

  // If system not initialized, queue the toast
  if (!ToastSystem.initialized) {
    ToastSystem.queue.push({ message: cleanMessage, type });
    return;
  }

  ToastSystem.createToast(cleanMessage, type);
}

// Expose to global scope for direct use
window.showToast = showToast;