import log from '/static/js/core/logger.js';
import eventSystem from '/static/js/core/events.js';
import modalManager from '/static/js/components/modal.js';

/**
 * Button utilities for header and footer buttons
 */
class ButtonsComponent {
  constructor() {
    this.instances = new Map();
    log('info', 'buttons.js', 'constructor', 'Buttons component created');
  }

  /**
   * Initialize header buttons
   * @param {Object} options - Header button options
   * @returns {Object} - Button controller
   */
  initHeaderButtons(options = {}) {
    const functionName = 'initHeaderButtons';

    // Use window data if available, otherwise use provided options
    const windowData = window.headerButtonsData || {};

    // Default options
    const defaults = {
      hasId: false,
      readOnly: false,
      endpoint: 'unknown',
      entityName: 'item',
      deleteUrl: null
    };

    // Merge defaults with window data and provided options
    const config = { ...defaults, ...windowData, ...options };

    const SOURCE = '_header_buttons.html';

    log("info", SOURCE, "init", "🚀 Buttons template loaded");
    log("debug", SOURCE, "config", `Has ID: ${config.hasId}`);
    log("debug", SOURCE, "config", `Read-only mode: ${config.readOnly}`);
    log("debug", SOURCE, "route", `Current endpoint: ${config.endpoint}`);

    if (config.hasId) {
      log("debug", SOURCE, "entity_id", "Working with provided item ID");
    } else {
      log("debug", SOURCE, "entity_id", "No item ID provided");
    }

    // DOM check on load
    document.addEventListener('DOMContentLoaded', () => {
      log("debug", SOURCE, "dom_ready", "DOM fully loaded and parsed");

      const buttonContainer = document.querySelector('.d-flex.justify-content-end.align-items-center.gap-2');
      if (!buttonContainer) {
        log("warn", SOURCE, "dom_check", "Button container not found in DOM");
        return;
      }

      const buttonCount = buttonContainer.querySelectorAll('a, button').length;
      log("debug", SOURCE, "dom_check", `Button container found with ${buttonCount} controls`);

      // Set up delete button
      const deleteButton = document.getElementById('delete-button');
      if (deleteButton) {
        log("debug", SOURCE, "listener_setup", "Attempting to attach listener to #delete-button");
        deleteButton.addEventListener('click', (event) => {
          event.preventDefault();
          log("info", SOURCE, "interaction", "Delete button clicked - triggering modal");
          log("debug", SOURCE, "interaction", `Delete button event: defaultPrevented=${event.defaultPrevented}`);

          // Show delete confirmation modal
          modalManager.showDeleteConfirmation({
            id: 'deleteConfirmationModal',
            title: `Delete ${config.entityName}`,
            message: `Are you sure you want to delete this ${config.entityName}? This action cannot be undone.`,
            entityName: config.entityName,
            deleteUrl: config.deleteUrl || `${window.location.pathname}/delete`
          });
        });
        log("info", SOURCE, "listener_setup", "Listener attached to #delete-button");
      } else {
        log("warn", SOURCE, "listener_setup", "Delete button (#delete-button) not found in DOM");
      }

      // Attach listeners to other buttons
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

          // Specific check for SUBMIT buttons (Update/Save)
          if (buttonType === 'submit') {
            log("info", SOURCE, "submit_check", `Submit button "${buttonText}" clicked.`);

            // Critical checks
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
            } else {
              log("info", SOURCE, "submit_check", `✅ Button "${buttonText}" IS associated with a form. ID: ${associatedForm.id || 'No ID'}, Action: ${associatedForm.action}`);
              // Check if form is valid (browser validation)
              if (typeof associatedForm.checkValidity === 'function') {
                log("debug", SOURCE, "submit_check", `Checking form validity...`);
                if (!associatedForm.checkValidity()) {
                  log("warn", SOURCE, "submit_check", `Browser form validation failed. Submission likely blocked.`);
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

      log("info", SOURCE, "final", "Header buttons initialized and listeners attached");
    });

    // Return a controller object
    return {
      getConfig: () => ({ ...config })
    };
  }

  /**
   * Initialize footer buttons
   * @param {Object} options - Footer button options
   * @returns {Object} - Button controller
   */
  initFooterButtons(options = {}) {
    const functionName = 'initFooterButtons';

    // Use window config if available, otherwise use provided options
    const windowConfig = window.footerButtonsConfig || {};

    // Default options
    const defaults = {
      hasId: false,
      endpoint: 'unknown',
      baseRoute: '',
      viewUrl: '',
      indexUrl: '',
      submitLabel: '',
      cancelLabel: ''
    };

    // Merge defaults with window config and provided options
    const config = { ...defaults, ...windowConfig, ...options };

    const SOURCE = '_footer_buttons.html';

    log("info", SOURCE, "init", "🚀 Footer buttons template loaded");
    log("debug", SOURCE, "config", "Has ID: " + config.hasId);
    log("debug", SOURCE, "route", "Current endpoint: " + config.endpoint);

    // Mode-specific logging
    if (config.hasId) {
      log("debug", SOURCE, "entity_id", "Working with item ID");
      try {
        const viewUrl = config.viewUrl;
        log("debug", SOURCE, "url_gen", "Generated view URL: " + viewUrl);
      } catch (e) {
        log("error", SOURCE, "url_gen", "Failed to generate view URL: " + e.message);
      }
    } else {
      log("debug", SOURCE, "entity_id", "No item ID provided - new item mode");
      try {
        const indexUrl = config.indexUrl;
        log("debug", SOURCE, "url_gen", "Generated index URL: " + indexUrl);
      } catch (e) {
        log("error", SOURCE, "url_gen", "Failed to generate index URL: " + e.message);
      }
    }

    // Set up context for DOM verification
    const context = {
      hasId: config.hasId,
      endpoint: config.endpoint,
      baseRoute: config.baseRoute,
      buttons: []
    };

    if (context.hasId) {
      context.buttons.push("Cancel (to view)", "Update");
      context.cancelTarget = "view";
    } else {
      context.buttons.push("Cancel (to index)", "Create");
      context.cancelTarget = "index";
    }

    log("info", SOURCE, "render", "🔘 Footer buttons render context", context);

    // DOM verification on load
    document.addEventListener('DOMContentLoaded', () => {
      const footerContainer = document.querySelector('.footer-buttons-container');
      if (footerContainer) {
        const buttonCount = footerContainer.querySelectorAll('a, button').length;
        log("debug", SOURCE, "dom_check", `Footer container found with ${buttonCount} controls`);

        if (buttonCount !== context.buttons.length) {
          log("warn", SOURCE, "dom_check", `Expected ${context.buttons.length} buttons but found ${buttonCount}`);
        } else {
          log("info", SOURCE, "dom_check", "All expected buttons are present in the DOM");
        }

        // Check if the buttons are enclosed in a form element
        const isInForm = footerContainer.closest('form') !== null;
        if (isInForm) {
          log("debug", SOURCE, "dom_check", "Footer buttons are properly enclosed in a form element");
        } else {
          log("warn", SOURCE, "dom_check", "Footer buttons are not in a form - submit button may not work");
        }
      } else {
        log("warn", SOURCE, "dom_check", "Footer container not found in DOM");
      }

      // Set up button event listeners
      const buttons = document.querySelectorAll('.footer-buttons-container a, .footer-buttons-container button');
      buttons.forEach(button => {
        button.addEventListener('click', () => {
          const buttonText = button.textContent.trim();
          const isSubmit = button.getAttribute('type') === 'submit';
          if (isSubmit) {
            log("info", SOURCE, "interaction", `Form submit initiated via ${buttonText} button`);
          } else {
            log("info", SOURCE, "interaction", `Navigation button clicked: ${buttonText}`);
          }
        });
      });

      log("info", SOURCE, "final", "Footer buttons template finished rendering");
    });

    // Return a controller object
    return {
      getConfig: () => ({ ...config })
    };
  }
}

// Create singleton instance
const buttonsComponent = new ButtonsComponent();
export default buttonsComponent;