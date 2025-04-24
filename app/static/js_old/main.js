// main.js

// Import custom modules; these files must exist in your /static/js directory.
import { initAutoCompleteFields } from './autoComplete.js';
import log from '/static/js/core/logger.js';

// DOMContentLoaded event to ensure the DOM is ready before running scripts.
document.addEventListener('DOMContentLoaded', () => {
  // Initialize AutoComplete fields if they exist on the page.
  try {
    initAutoCompleteFields();
    log("info", "main.js", "init", "AutoComplete fields initialized successfully.");
  } catch (error) {
    log("error", "main.js", "init", "Failed to initialize AutoComplete fields", error);
  }

  // Handle unsaved changes modal logic.
  const cancelButton = document.querySelector('#cancel-button');
  if (cancelButton) {
    cancelButton.addEventListener('click', function (event) {
      event.preventDefault();
      const modalEl = document.getElementById('unsavedChangesModal');
      if (modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
      }
    });
  }

  const confirmLeaveBtn = document.getElementById('confirmLeaveBtn');
  if (confirmLeaveBtn) {
    confirmLeaveBtn.addEventListener('click', function () {
      // Retrieve a cancel URL from a data attribute on the form or default to '/'
      const form = document.querySelector('form');
      const cancelUrl = form?.getAttribute('data-cancel-url') || '/';
      window.location.href = cancelUrl;
    });
  }
});
