// /static/js/main.js

// Import custom modules; paths adjusted for new structure
import { initAutoCompleteFields } from './components/autoComplete.js'; // Adjusted path
import log from './core/logger.js'; // Adjusted path

// DOMContentLoaded event to ensure the DOM is ready before running scripts.
document.addEventListener('DOMContentLoaded', () => {
  const scriptName = "main.js";
  const functionName = "DOMContentLoaded";

  // Initialize AutoComplete fields if they exist on the page.
  try {
    // Note: initAutoCompleteFields logs internally, no need for separate log here unless desired.
    initAutoCompleteFields();
    log("info", scriptName, functionName, "✅ AutoComplete fields initialization initiated.");
  } catch (error) {
    log("error", scriptName, functionName, "❌ Failed to initialize AutoComplete fields", error);
  }

  // Handle unsaved changes modal logic.
  const cancelButton = document.querySelector('#cancel-button');
  if (cancelButton) {
    cancelButton.addEventListener('click', function (event) {
      event.preventDefault();
      const modalEl = document.getElementById('unsavedChangesModal');
      if (modalEl) {
        try {
           // Ensure bootstrap is loaded or handle potential error
          const modal = new bootstrap.Modal(modalEl);
          modal.show();
           log("info", scriptName, "cancelButton:click", "Unsaved changes modal shown.");
        } catch (e) {
           log("error", scriptName, "cancelButton:click", "❌ Failed to show modal. Is Bootstrap loaded?", e);
        }
      } else {
        log("warn", scriptName, "cancelButton:click", "⚠️ Unsaved changes modal element not found (#unsavedChangesModal).");
      }
    });
     log("info", scriptName, functionName, "Cancel button listener added.");
  } else {
     log("debug", scriptName, functionName, "Cancel button (#cancel-button) not found on this page.");
  }

  const confirmLeaveBtn = document.getElementById('confirmLeaveBtn');
  if (confirmLeaveBtn) {
    confirmLeaveBtn.addEventListener('click', function () {
      // Retrieve a cancel URL from a data attribute on the form or default to '/'
      const form = document.querySelector('form');
      // Use optional chaining and nullish coalescing for safety
      const cancelUrl = form?.dataset.cancelUrl ?? '/';
       log("info", scriptName, "confirmLeaveBtn:click", `Navigating away to cancel URL: ${cancelUrl}`);
      window.location.href = cancelUrl;
    });
     log("info", scriptName, functionName, "Confirm leave button listener added.");
  } else {
      log("debug", scriptName, functionName, "Confirm leave button (#confirmLeaveBtn) not found on this page.");
  }

  log("info", scriptName, functionName, "🏁 Main initialization complete.");
});