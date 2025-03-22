/**
 * js/toasts.js
 */
import log from './logger.js';

document.addEventListener('DOMContentLoaded', function() {
    const scriptName = "toastInit";
    const functionName = "DOMContentLoaded";

    log("debug", scriptName, functionName, "🔄 Initializing toast notifications");

    // Initialize toasts but don't auto-dismiss
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        new bootstrap.Toast(toast);
    });

    log("info", scriptName, functionName, `✅🔄 Initialized ${toasts.length} toast notifications`);
});
