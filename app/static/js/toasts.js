/**
 * static/js/toasts.js
 */
import log from './logger.js';

document.addEventListener('DOMContentLoaded', function () {
    const scriptName = "toastInit";
    const functionName = "DOMContentLoaded";

    log("debug", scriptName, functionName, "🔄 Initializing toast notifications");

    // Initialize all .toast elements but don't show them yet
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        new bootstrap.Toast(toast);
    });

    log("info", scriptName, functionName, `✅🔄 Initialized ${toasts.length} toast notifications`);
});

/**
 * Dynamically show a toast with a given message and type.
 * @param {string} message - The text to display in the toast.
 * @param {string} type - Bootstrap background type: success, danger, warning, info.
 */
export function showToast(message, type = 'success') {
    const toastEl = document.getElementById('liveToast');
    const toastMsg = document.getElementById('toastMessage');

    if (!toastEl || !toastMsg) {
        console.warn("Toast elements not found in DOM.");
        return;
    }

    toastMsg.textContent = message;
    toastEl.className = `toast align-items-center text-bg-${type} border-0`;

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}
