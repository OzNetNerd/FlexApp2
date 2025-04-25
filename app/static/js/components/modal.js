import log from '/static/js/core/logger.js';
import eventSystem from '/static/js/core/events.js';

/**
 * Standardized modal component
 */
class ModalManager {
  constructor() {
    this.modals = new Map();
    log('info', 'modal.js', 'constructor', 'Modal manager created');
  }

  /**
   * Create a modal programmatically
   * @param {Object} options - Modal options
   * @returns {Object} - Modal controller
   */
  createModal(options = {}) {
    const functionName = 'createModal';

    // Generate ID if not provided
    const modalId = options.id || `modal-${Date.now()}`;

    // Default options
    const defaults = {
      title: 'Modal Title',
      body: '',
      confirmText: 'Confirm',
      cancelText: 'Cancel',
      size: '', // '', 'modal-sm', 'modal-lg', 'modal-xl'
      staticBackdrop: false,
      confirmButtonClass: 'btn-primary',
      cancelButtonClass: 'btn-secondary',
      showConfirm: true,
      showCancel: true,
      hideAfterConfirm: true,
      onConfirm: null,
      onCancel: null,
      onShow: null,
      onHide: null
    };

    // Merge defaults with provided options
    const config = { ...defaults, ...options };

    log('debug', 'modal.js', functionName, `Creating modal with ID: ${modalId}`, config);

    // Check if a modal with this ID already exists
    let modalElement = document.getElementById(modalId);
    let isNewModal = false;

    if (!modalElement) {
      isNewModal = true;

      // Create modal element
      modalElement = document.createElement('div');
      modalElement.id = modalId;
      modalElement.className = 'modal fade';
      modalElement.setAttribute('tabindex', '-1');
      modalElement.setAttribute('aria-hidden', 'true');

      if (config.staticBackdrop) {
        modalElement.setAttribute('data-bs-backdrop', 'static');
        modalElement.setAttribute('data-bs-keyboard', 'false');
      }

      // Create modal content
      modalElement.innerHTML = `
        <div class="modal-dialog ${config.size}">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">${config.title}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              ${config.body}
            </div>
            <div class="modal-footer">
              ${config.showCancel ? `<button type="button" class="btn ${config.cancelButtonClass}" data-bs-dismiss="modal">${config.cancelText}</button>` : ''}
              ${config.showConfirm ? `<button type="button" class="btn ${config.confirmButtonClass}" id="${modalId}-confirm">${config.confirmText}</button>` : ''}
            </div>
          </div>
        </div>
      `;

      // Append to document body
      document.body.appendChild(modalElement);

      log('debug', 'modal.js', functionName, `Modal ${modalId} created and added to DOM`);
    } else {
      // Update existing modal
      modalElement.querySelector('.modal-title').textContent = config.title;
      modalElement.querySelector('.modal-body').innerHTML = config.body;

      // Update footer buttons
      const footer = modalElement.querySelector('.modal-footer');
      footer.innerHTML = '';

      if (config.showCancel) {
        const cancelBtn = document.createElement('button');
        cancelBtn.type = 'button';
        cancelBtn.className = `btn ${config.cancelButtonClass}`;
        cancelBtn.setAttribute('data-bs-dismiss', 'modal');
        cancelBtn.textContent = config.cancelText;
        footer.appendChild(cancelBtn);
      }

      if (config.showConfirm) {
        const confirmBtn = document.createElement('button');
        confirmBtn.type = 'button';
        confirmBtn.className = `btn ${config.confirmButtonClass}`;
        confirmBtn.id = `${modalId}-confirm`;
        confirmBtn.textContent = config.confirmText;
        footer.appendChild(confirmBtn);
      }

      log('debug', 'modal.js', functionName, `Modal ${modalId} updated`);
    }

    // Initialize Bootstrap modal
    let bsModal;
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
      try {
        bsModal = new bootstrap.Modal(modalElement);
        log('debug', 'modal.js', functionName, `Bootstrap Modal initialized for ${modalId}`);
      } catch (error) {
        log('error', 'modal.js', functionName, `Error initializing Bootstrap Modal for ${modalId}:`, error);
      }
    } else {
      log('warn', 'modal.js', functionName, 'Bootstrap Modal component not found. Modal functionality will be limited.');
    }

    // Set up event listeners
    if (isNewModal) {
      // Confirm button handler
      const confirmBtn = document.getElementById(`${modalId}-confirm`);
      if (confirmBtn) {
        confirmBtn.addEventListener('click', () => {
          log('debug', 'modal.js', 'confirmClick', `Confirm button clicked for modal ${modalId}`);

          let shouldClose = true;

          if (config.onConfirm) {
            try {
              const result = config.onConfirm();

              // If handler returns false, prevent modal from closing
              if (result === false) {
                shouldClose = false;
              }

              // If handler returns a promise, handle async result
              if (result instanceof Promise) {
                shouldClose = false;

                result
                  .then((promiseResult) => {
                    if (promiseResult !== false && config.hideAfterConfirm && bsModal) {
                      bsModal.hide();
                    }

                    // Publish confirm success event
                    eventSystem.publish('modal.confirm.success', { modalId });
                  })
                  .catch(error => {
                    log('error', 'modal.js', 'confirmClick', `Error in confirm handler for modal ${modalId}:`, error);

                    // Publish confirm error event
                    eventSystem.publish('modal.confirm.error', { modalId, error });
                  });
              }
            } catch (error) {
              log('error', 'modal.js', 'confirmClick', `Error in confirm handler for modal ${modalId}:`, error);

              // Publish confirm error event
              eventSystem.publish('modal.confirm.error', { modalId, error });
            }
          }

          if (shouldClose && config.hideAfterConfirm && bsModal) {
            bsModal.hide();
          }

          // Publish confirm event
          eventSystem.publish('modal.confirm', { modalId });
        });
      }

      // Modal show event
      modalElement.addEventListener('shown.bs.modal', () => {
        log('debug', 'modal.js', 'modalShown', `Modal ${modalId} shown`);

        if (config.onShow) {
          try {
            config.onShow();
          } catch (error) {
            log('error', 'modal.js', 'modalShown', `Error in show handler for modal ${modalId}:`, error);
          }
        }

        // Publish show event
        eventSystem.publish('modal.shown', { modalId });
      });

      // Modal hide event
      modalElement.addEventListener('hidden.bs.modal', () => {
        log('debug', 'modal.js', 'modalHidden', `Modal ${modalId} hidden`);

        if (config.onCancel) {
          try {
            config.onCancel();
          } catch (error) {
            log('error', 'modal.js', 'modalHidden', `Error in cancel handler for modal ${modalId}:`, error);
          }
        }

        if (config.onHide) {
          try {
            config.onHide();
          } catch (error) {
            log('error', 'modal.js', 'modalHidden', `Error in hide handler for modal ${modalId}:`, error);
          }
        }

        // Publish hide event
        eventSystem.publish('modal.hidden', { modalId });
      });
    }

    // Modal controller object
    const controller = {
      show: () => {
        if (bsModal) {
          bsModal.show();
          log('debug', 'modal.js', 'show', `Showing modal ${modalId}`);
        } else {
          log('warn', 'modal.js', 'show', `Cannot show modal ${modalId}, Bootstrap Modal not available`);
        }
      },
      hide: () => {
        if (bsModal) {
          bsModal.hide();
          log('debug', 'modal.js', 'hide', `Hiding modal ${modalId}`);
        } else {
          log('warn', 'modal.js', 'hide', `Cannot hide modal ${modalId}, Bootstrap Modal not available`);
        }
      },
      update: (options = {}) => {
        const updatedConfig = { ...config, ...options };

        // Update title and body
        if (options.title) {
          modalElement.querySelector('.modal-title').textContent = options.title;
        }

        if (options.body) {
          modalElement.querySelector('.modal-body').innerHTML = options.body;
        }

        // Update buttons if needed
        if (options.confirmText) {
          const confirmBtn = document.getElementById(`${modalId}-confirm`);
          if (confirmBtn) {
            confirmBtn.textContent = options.confirmText;
          }
        }

        if (options.cancelText) {
          const cancelBtn = modalElement.querySelector(`.modal-footer .${config.cancelButtonClass}`);
          if (cancelBtn) {
            cancelBtn.textContent = options.cancelText;
          }
        }

        log('debug', 'modal.js', 'update', `Updated modal ${modalId}`);

        return controller;
      },
      getElement: () => modalElement,
      getConfig: () => ({ ...config })
    };

    // Store the modal controller
    this.modals.set(modalId, controller);

    return controller;
  }

  /**
   * Get a modal controller by ID
   * @param {string} modalId - Modal ID
   * @returns {Object|null} - Modal controller or null if not found
   */
  getModal(modalId) {
    return this.modals.get(modalId) || null;
  }

  /**
   * Show a delete confirmation modal
   * @param {Object} options - Delete confirmation options
   * @returns {Object} - Modal controller
   */
  showDeleteConfirmation(options = {}) {
    const functionName = 'showDeleteConfirmation';

    // Default options
    const defaults = {
      id: 'deleteConfirmationModal',
      title: 'Confirm Delete',
      message: 'Are you sure you want to delete this item? This action cannot be undone.',
      entityName: 'item',
      deleteUrl: null,
      onConfirm: null
    };

    // Merge defaults with provided options
    const config = { ...defaults, ...options };

    log('debug', 'modal.js', functionName, 'Showing delete confirmation modal', config);

    // Create modal
    const modalController = this.createModal({
      id: config.id,
      title: config.title,
      body: config.message,
      confirmText: 'Delete',
      confirmButtonClass: 'btn-danger',
      staticBackdrop: true,
      onConfirm: () => {
        if (config.onConfirm) {
          return config.onConfirm();
        } else if (config.deleteUrl) {
          // Create and submit a form to delete the item
          const form = document.createElement('form');
          form.method = 'POST';
          form.action = config.deleteUrl;
          document.body.appendChild(form);

          log('info', 'modal.js', functionName, `Deletion confirmed - submitting delete form to ${config.deleteUrl}`);

          form.submit();
          return true;
        }
      }
    });

    // Show the modal
    modalController.show();

    return modalController;
  }
}

// Create singleton instance
const modalManager = new ModalManager();
export default modalManager;