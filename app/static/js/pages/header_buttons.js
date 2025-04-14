// header_buttons.js
import log from '/static/js/logger.js';

const data = window.headerButtonsData || {};
const SOURCE = "_header_buttons.html"; // Define source once

log("info", SOURCE, "init", "🚀 Buttons template loaded");
log("debug", SOURCE, "config", `Has ID: ${data.hasId}`);
log("debug", SOURCE, "config", `Read-only mode: ${data.readOnly}`);
log("debug", SOURCE, "route", `Current endpoint: ${data.endpoint}`);

if (data.hasId) {
  log("debug", SOURCE, "entity_id", "Working with provided item ID");
} else {
  log("debug", SOURCE, "entity_id", "No item ID provided");
}

// --- Function to handle showing the delete modal ---
function showDeleteModal() {
  const deleteModalEl = document.getElementById('deleteConfirmationModal');
  if (!deleteModalEl) {
    log("warn", SOURCE, "modal", "Delete modal element not found");
    return;
  }
  if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
    try {
        const deleteModal = bootstrap.Modal.getOrCreateInstance(deleteModalEl); // Use getOrCreateInstance
        deleteModal.show();
        log("info", SOURCE, "modal", "Delete confirmation modal shown");
    } catch (e) {
        log("error", SOURCE, "modal", `Error showing Bootstrap modal: ${e.message}`, e);
    }
  } else {
      log("error", SOURCE, "modal", "Bootstrap Modal component not found.");
  }
}

// --- DOM Ready ---
document.addEventListener('DOMContentLoaded', () => {
  log("debug", SOURCE, "dom_ready", "DOM fully loaded and parsed");

  const buttonContainer = document.querySelector('.d-flex.justify-content-end.align-items-center.gap-2');
  if (!buttonContainer) {
    log("warn", SOURCE, "dom_check", "Button container not found in DOM");
    return; // Exit if container isn't found
  }

  const buttonCount = buttonContainer.querySelectorAll('a, button').length;
  log("debug", SOURCE, "dom_check", `Button container found with ${buttonCount} controls`);


  // --- Attach listener specifically to the Delete button ---
  const deleteButton = document.getElementById('delete-button');
  if (deleteButton) {
    log("debug", SOURCE, "listener_setup", "Attempting to attach listener to #delete-button");
    deleteButton.addEventListener('click', (event) => {
      event.preventDefault();
      log("info", SOURCE, "interaction", "Delete button clicked - triggering modal");
      log("debug", SOURCE, "interaction", `Delete button event: defaultPrevented=${event.defaultPrevented}`);
      showDeleteModal();
    });
    log("info", SOURCE, "listener_setup", "Listener attached to #delete-button");
  } else {
     log("warn", SOURCE, "listener_setup", "Delete button (#delete-button) not found in DOM");
  }


  // --- Attach generic listener for logging AND specific submit checks ---
  log("debug", SOURCE, "listener_setup", "Attempting to attach generic listener to all buttons/links in container");
  const allButtons = buttonContainer.querySelectorAll('a, button');
   allButtons.forEach(button => {
       // Skip adding another listener to the delete button
       if (button.id === 'delete-button') {
            log("debug", SOURCE, "listener_setup", "Skipping delete button in generic listener setup");
            return;
       }

       button.addEventListener('click', (event) => {
            const buttonText = button.textContent.trim();
            const elementType = button.tagName; // BUTTON or A
            const buttonType = button.type; // submit, button, reset, or undefined for <a>

            // Log basic click info immediately
            log("info", SOURCE, "interaction", `${elementType} clicked: "${buttonText}" (Type: ${buttonType || 'link'})`);
            log("debug", SOURCE, "interaction", `Event target:`, event.target);
            log("debug", SOURCE, "interaction", `Event defaultPrevented (start): ${event.defaultPrevented}`);

            // --- Specific check for SUBMIT buttons (Update/Save) ---
            if (buttonType === 'submit') {
                log("info", SOURCE, "submit_check", `Submit button "${buttonText}" clicked.`);

                // **CRITICAL CHECKS**
                const associatedForm = button.form; // Direct property referencing the owning form
                const closestForm = button.closest('form'); // Check ancestor

                log("debug", SOURCE, "submit_check", `Associated Form (button.form):`, associatedForm);
                log("debug", SOURCE, "submit_check", `Closest Ancestor Form (button.closest('form'))`, closestForm);

                if (!associatedForm) {
                    log("error", SOURCE, "submit_check", `❌ Button "${buttonText}" is NOT associated with any form (button.form is null/undefined). It needs to be INSIDE a <form> or use the 'form' attribute.`);
                    // Check if the ancestor search finds one, indicating it *might* be inside but association failed?
                    if (closestForm) {
                         log("warn", SOURCE, "submit_check", `🤔 Found an ancestor form via closest(), but button.form is null. Check for nested forms or non-standard HTML structure.`);
                    }
                     // Submission likely won't happen automatically.
                     // If you absolutely MUST submit manually (use as last resort):
                     /*
                     if (closestForm) {
                        log("warn", SOURCE, "submit_check", "Attempting manual form submission via closest('form')...");
                        event.preventDefault(); // Prevent potential default action if any exists
                        closestForm.submit();
                     } else {
                        log("error", SOURCE, "submit_check", "Cannot submit manually, no ancestor form found either.");
                     }
                     */
                } else {
                    log("info", SOURCE, "submit_check", `✅ Button "${buttonText}" IS associated with a form. ID: ${associatedForm.id || 'No ID'}, Action: ${associatedForm.action}`);
                    // Check if form is valid (browser validation)
                    if (typeof associatedForm.checkValidity === 'function') {
                        log("debug", SOURCE, "submit_check", `Checking form validity...`);
                        if (!associatedForm.checkValidity()) {
                            log("warn", SOURCE, "submit_check", `Browser form validation failed. Submission likely blocked.`);
                            // You might want to call reportValidity() to show messages,
                            // but often the browser does this automatically on submit failure.
                            // associatedForm.reportValidity();
                        } else {
                             log("info", SOURCE, "submit_check", `Form appears valid according to checkValidity().`);
                        }
                    }
                }
            }
            // Log if default was prevented AFTER our handler ran (by us or something else)
            // Use setTimeout to check after this event handler finishes execution stack
            setTimeout(() => {
                 log("debug", SOURCE, "interaction", `Event defaultPrevented (end): ${event.defaultPrevented}`);
            }, 0);
       });
   });
   log("info", SOURCE, "listener_setup", `Generic listeners attached to ${allButtons.length} buttons/links`);

  // --- Attach listener for the modal confirm button ---
  const modalConfirmBtn = document.getElementById('modalConfirmBtn');
  if (modalConfirmBtn) {
     log("debug", SOURCE, "listener_setup", "Attempting to attach listener to #modalConfirmBtn");
    modalConfirmBtn.addEventListener('click', () => {
      log("info", SOURCE, "interaction", "Modal confirm button clicked");
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = data.deleteUrl && data.deleteUrl !== '#' ? data.deleteUrl : window.location.pathname + '/delete';
      document.body.appendChild(form);
      log("info", SOURCE, "interaction", `Deletion confirmed - submitting delete form to ${form.action}`);
      form.submit();
    });
     log("info", SOURCE, "listener_setup", "Listener attached to #modalConfirmBtn");
  } else {
    log("warn", SOURCE, "listener_setup", "Modal confirm button (#modalConfirmBtn) not found");
  }

  log("info", SOURCE, "final", "Buttons template finished rendering and listeners attached");
});