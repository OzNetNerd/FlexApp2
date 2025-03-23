import log from './logger.js';

document.addEventListener('DOMContentLoaded', function () {
    const scriptName = "toastInit";
    const functionName = "DOMContentLoaded";

    log("debug", scriptName, functionName, "🔄 Initializing toast notifications");

    // Initialize all .toast elements with 10s auto-dismiss
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        new bootstrap.Toast(toast, { delay: 10000 });
    });

    log("info", scriptName, functionName, `✅🔄 Initialized ${toasts.length} toast notifications`);
});

export function showToast(message, type = 'success') {
    const toastEl = document.getElementById('liveToast');
    const toastMsg = document.getElementById('toastMessage');

    if (!toastEl || !toastMsg) {
        console.warn("Toast elements not found in DOM.");
        return;
    }

    toastMsg.textContent = message;
    toastEl.className = `toast align-items-center text-bg-${type} border-0`;

    const existingToast = bootstrap.Toast.getInstance(toastEl);
    if (existingToast) {
        existingToast.hide();
    }

    const toast = new bootstrap.Toast(toastEl, { delay: 10000 });
    toast.show();
}
