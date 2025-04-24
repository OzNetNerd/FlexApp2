/**
 * js/components/common/toasts.js
 * Toast notification component
 */

import log from '/static/js/core/utils/logger.js';

const scriptName = "toasts.js";

/**
 * Shows a toast notification
 * @param {string} message - The message to show
 * @param {string} type - The type of toast (success, info, warning, danger)
 * @param {number} duration - Duration in milliseconds to show the toast
 */
export function showToast(message, type = 'info', duration = 5000) {
    const functionName = "showToast";
    log("info", scriptName, functionName, `Showing ${type} toast: ${message}`);

    // Get toast container
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        log("error", scriptName, functionName, "❌ Toast container not found");
        console.error("Toast container not found");
        return;
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast fade show toast-${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    // Set appropriate color based on type
    let bgColor = '';
    let iconClass = '';

    switch(type) {
        case 'success':
            bgColor = 'bg-success text-white';
            iconClass = 'bi-check-circle-fill';
            break;
        case 'danger':
        case 'error': // Allow 'error' as an alias for 'danger'
            bgColor = 'bg-danger text-white';
            iconClass = 'bi-exclamation-triangle-fill';
            break;
        case 'warning':
            bgColor = 'bg-warning';
            iconClass = 'bi-exclamation-circle-fill';
            break;
        case 'info':
        default:
            bgColor = 'bg-info text-white';
            iconClass = 'bi-info-circle-fill';
            break;
    }

    // Create toast content
    toast.innerHTML = `
        <div class="toast-header ${bgColor}">
            <i class="bi ${iconClass} me-2"></i>
            <strong class="me-auto">${capitalizeFirstLetter(type)}</strong>
            <small>Just now</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    // Add toast to container (prepend to show newest at top)
    toastContainer.prepend(toast);

    // Initialize Bootstrap toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: duration
    });

    // Show toast
    bsToast.show();

    // Remove toast from DOM after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
        log("debug", scriptName, functionName, "Toast removed from DOM");
    });

    // Return the toast instance in case it needs to be manipulated later
    return toast;
}

/**
 * Helper function to capitalize the first letter of a string
 * @param {string} str - The string to capitalize
 * @returns {string} - The capitalized string
 */
function capitalizeFirstLetter(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Initialize toast container when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const functionName = "DOMContentLoaded";
    log("info", scriptName, functionName, "🍞 Toast component initialized");
});