import log from '/static/js/core/logger.js';
import eventSystem from '/static/js/core/events.js';

/**
 * Form validation and state tracking
 */
class FormManager {
  constructor() {
    this.forms = new Map();
    log('info', 'form.js', 'constructor', 'Form manager created');
  }

  /**
   * Initialize a form with tracking and validation
   * @param {string} formId - Form element ID
   * @param {Object} options - Form options
   * @returns {Object} - Form controller
   */
  initForm(formId, options = {}) {
    const functionName = 'initForm';

    // Default options
    const defaults = {
      trackChanges: true,
      validateOnChange: false,
      validateOnSubmit: true,
      confirmUnsavedChanges: true,
      resetFormOnSubmit: false,
      onValidate: null,
      onSubmit: null,
      redirectAfterSubmit: null
    };

    // Merge defaults with provided options
    const config = { ...defaults, ...options };

    // Find the form element
    const form = document.getElementById(formId);
    if (!form) {
      log('error', 'form.js', functionName, `Form not found: ${formId}`);
      return null;
    }

    log('info', 'form.js', functionName, `Initializing form: ${formId}`, config);

    // Form state
    const state = {
      formId,
      formChanged: false,
      isSubmitting: false,
      originalValues: new Map(),
      validationErrors: new Map()
    };

    // Store original values
    const formElements = form.querySelectorAll('input, select, textarea');
    formElements.forEach(element => {
      if (element.name || element.id) {
        const key = element.name || element.id;
        if (element.type === 'checkbox' || element.type === 'radio') {
          state.originalValues.set(key, element.checked);
        } else {
          state.originalValues.set(key, element.value);
        }
      }
    });

    log('debug', 'form.js', functionName, `Stored original values for form: ${formId}`);

    // Set up change tracking
    if (config.trackChanges) {
      formElements.forEach(element => {
        element.addEventListener('change', () => {
          if (!state.formChanged) {
            state.formChanged = true;

            log('info', 'form.js', 'onChange', `Form state changed - unsaved changes detected: ${formId}`, {
              element: element.name || element.id,
              type: element.type,
              value: element.value
            });

            // Publish form changed event
            eventSystem.publish('form.changed', {
              formId,
              element: element.name || element.id,
              changed: true
            });
          }

          // Validate on change if enabled
          if (config.validateOnChange) {
            validateForm();
          }
        });
      });
    }

    // Set up unsaved changes confirmation
    if (config.confirmUnsavedChanges) {
      setupUnsavedChangesWarning(form, state);
    }

    // Validation function
    function validateForm() {
      state.validationErrors.clear();

      // Default validation (HTML5)
      const isValid = form.checkValidity();

      // Get validation errors from invalid fields
      if (!isValid) {
        const invalidElements = form.querySelectorAll(':invalid');
        invalidElements.forEach(element => {
          if (element.name || element.id) {
            const key = element.name || element.id;
            state.validationErrors.set(key, element.validationMessage);
          }
        });
      }

      // Custom validation if provided
      if (config.onValidate) {
        try {
          const customValidation = config.onValidate(form);

          // Process custom validation errors
          if (customValidation && customValidation.errors) {
            for (const [key, message] of Object.entries(customValidation.errors)) {
              state.validationErrors.set(key, message);
            }
          }
        } catch (error) {
          log('error', 'form.js', 'validateForm', `Custom validation error for form ${formId}:`, error);
        }
      }

      // Show validation errors
      showValidationErrors();

      // Return validation result
      return state.validationErrors.size === 0;
    }

    // Function to show validation errors
    function showValidationErrors() {
      // Remove existing error messages
      form.querySelectorAll('.validation-error').forEach(element => {
        element.remove();
      });

      // Show new error messages
      state.validationErrors.forEach((message, key) => {
        const field = form.querySelector(`[name="${key}"], #${key}`);
        if (field) {
          // Add error class to field
          field.classList.add('is-invalid');

          // Create error message element
          const errorElement = document.createElement('div');
          errorElement.className = 'invalid-feedback validation-error';
          errorElement.textContent = message;

          // Insert after field
          field.parentNode.insertBefore(errorElement, field.nextSibling);
        }
      });

      // Publish validation event
      eventSystem.publish('form.validated', {
        formId,
        isValid: state.validationErrors.size === 0,
        errors: Object.fromEntries(state.validationErrors)
      });
    }

    // Function to handle form submission
    function handleSubmit(event) {
      const isValid = validateForm();

      if (!isValid) {
        event.preventDefault();
        log('info', 'form.js', 'handleSubmit', `Form ${formId} validation failed, submission prevented`);
        return false;
      }

      // Set submitting state
      state.isSubmitting = true;

      // Reset form changed state
      state.formChanged = false;

      // Call custom submit handler if provided
      if (config.onSubmit) {
        event.preventDefault();

        try {
          log('info', 'form.js', 'handleSubmit', `Custom submit handler for form ${formId}`);
          const result = config.onSubmit(form, event);

          // Handle promise return
          if (result instanceof Promise) {
            result
              .then(() => {
                state.isSubmitting = false;

                if (config.resetFormOnSubmit) {
                  form.reset();
                }

                if (config.redirectAfterSubmit) {
                  window.location.href = config.redirectAfterSubmit;
                }

                log('info', 'form.js', 'handleSubmit', `Form ${formId} submitted successfully`);

                // Publish submit success event
                eventSystem.publish('form.submit.success', { formId });
              })
              .catch(error => {
                state.isSubmitting = false;

                log('error', 'form.js', 'handleSubmit', `Custom submit handler error for form ${formId}:`, error);

                // Publish submit error event
                eventSystem.publish('form.submit.error', { formId, error });
              });
          } else {
            state.isSubmitting = false;

            if (config.resetFormOnSubmit) {
              form.reset();
            }

            if (config.redirectAfterSubmit) {
              window.location.href = config.redirectAfterSubmit;
            }

            log('info', 'form.js', 'handleSubmit', `Form ${formId} submitted successfully`);

            // Publish submit success event
            eventSystem.publish('form.submit.success', { formId });
          }
        } catch (error) {
          state.isSubmitting = false;

          log('error', 'form.js', 'handleSubmit', `Custom submit handler error for form ${formId}:`, error);

          // Publish submit error event
          eventSystem.publish('form.submit.error', { formId, error });
        }
      } else {
        log('info', 'form.js', 'handleSubmit', `Form ${formId} submitted`);

        // Publish submit event
        eventSystem.publish('form.submit', { formId });
      }

      return true;
    }

    // Set up form submission
    form.addEventListener('submit', handleSubmit);

    // Set up unsaved changes warning
    function setupUnsavedChangesWarning(form, state) {
      // Find cancel button if it exists
      const cancelButton = form.querySelector('.btn-secondary, [data-action="cancel"]');

      if (cancelButton) {
        cancelButton.addEventListener('click', function(event) {
          if (state.formChanged && !state.isSubmitting) {
            event.preventDefault();

            log('info', 'form.js', 'cancelClick', `Form ${formId} has unsaved changes, showing confirmation`);

            // Show confirmation modal (check if a modal with unsavedChangesModal id exists)
            const modal = document.getElementById('unsavedChangesModal');
            if (modal && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
              const bsModal = new bootstrap.Modal(modal);
              bsModal.show();

              // Set up confirm leave button
              const confirmLeaveBtn = document.getElementById('confirmLeaveBtn');
              if (confirmLeaveBtn) {
                confirmLeaveBtn.addEventListener('click', function() {
                  // Get the current URL and build the appropriate return URL
                  const currentPath = window.location.pathname;
                  const isEdit = currentPath.includes('/edit/');
                  const hasId = /\/\d+\//.test(currentPath);

                  let redirectUrl;
                  if (hasId) {
                    // If editing an existing item, go to view page
                    redirectUrl = currentPath.replace('/edit/', '/view/');
                  } else {
                    // If creating a new item, go to index page
                    redirectUrl = currentPath.split('/create')[0];
                  }

                  window.location.href = redirectUrl;
                });
              }
            } else {
              // Fallback to browser confirm dialog
              if (confirm('You have unsaved changes. Are you sure you want to leave?')) {
                // Determine redirect URL
                const href = cancelButton.getAttribute('href');
                if (href) {
                  window.location.href = href;
                } else {
                  // If no href, just go back
                  window.history.back();
                }
              }
            }
          }
        });
      }

      // Add window unload handler
      window.addEventListener('beforeunload', function(e) {
        if (state.formChanged && !state.isSubmitting) {
          e.preventDefault();
          e.returnValue = '';
          return '';
        }
      });
    }

    // Form controller object
    const controller = {
      getForm: () => form,
      getState: () => ({ ...state }),
      validate: validateForm,
      isDirty: () => state.formChanged,
      resetChanges: () => {
        state.formChanged = false;

        // Publish form reset event
        eventSystem.publish('form.reset', { formId });

        log('info', 'form.js', 'resetChanges', `Form ${formId} changes reset`);
      },
      setFieldValue: (fieldName, value) => {
        const field = form.querySelector(`[name="${fieldName}"], #${fieldName}`);
        if (field) {
          if (field.type === 'checkbox' || field.type === 'radio') {
            field.checked = value;
          } else {
            field.value = value;
          }

          log('debug', 'form.js', 'setFieldValue', `Set ${fieldName} value for form ${formId}`, { value });
        } else {
          log('warn', 'form.js', 'setFieldValue', `Field not found: ${fieldName} in form ${formId}`);
        }
      },
      getFieldValue: (fieldName) => {
        const field = form.querySelector(`[name="${fieldName}"], #${fieldName}`);
        if (field) {
          if (field.type === 'checkbox' || field.type === 'radio') {
            return field.checked;
          } else {
            return field.value;
          }
        }

        log('warn', 'form.js', 'getFieldValue', `Field not found: ${fieldName} in form ${formId}`);
        return null;
      }
    };

    // Store the form controller
    this.forms.set(formId, controller);

    return controller;
  }

  /**
   * Get a form controller by ID
   * @param {string} formId - Form ID
   * @returns {Object|null} - Form controller or null if not found
   */
  getForm(formId) {
    return this.forms.get(formId) || null;
  }
}

// Create singleton instance
const formManager = new FormManager();
export default formManager;