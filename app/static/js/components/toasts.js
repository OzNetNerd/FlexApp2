// /static/js/components/toasts.js

import log from '../core/logger.js'; // Adjusted path

const scriptName = "toasts.js";

// Enhanced Toast System using a self-invoking function for encapsulation
const ToastSystem = (() => {
    let initialized = false;
    let container = null;
    const queue = []; // Queue for toasts shown before init
    let toastCount = 0; // Counter for unique IDs

    const defaultOptions = {
        delay: 6000, // Auto-hide delay in ms
        position: 'bottom-0 end-0', // Default Bootstrap position classes
        zIndex: 1090, // Common z-index for toasts (Bootstrap uses 1090 for modals)
        containerId: 'toast-container-custom' // Unique ID for the container
    };

    // Colors mapped to types (adjust as needed)
    const typeStyles = {
        success: { bg: '#198754', text: '#fff' }, // Green
        info:    { bg: '#0dcaf0', text: '#000' }, // Cyan
        warning: { bg: '#ffc107', text: '#000' }, // Yellow
        danger:  { bg: '#dc3545', text: '#fff' }, // Red (maps from 'error')
        primary: { bg: '#0d6efd', text: '#fff' }, // Blue (default)
        secondary: { bg: '#6c757d', text: '#fff'}, // Grey
        light:   { bg: '#f8f9fa', text: '#000'}, // Light
        dark:    { bg: '#212529', text: '#fff'}  // Dark
    };


    /** Initialize the toast container */
    function init() {
        if (initialized) return;
        const functionName = "init";
        log("debug", scriptName, functionName, "🚀 Initializing ToastSystem...");

        // Find or create container
        container = document.getElementById(defaultOptions.containerId);
        if (!container) {
            log("debug", scriptName, functionName, `🛠️ Creating toast container #${defaultOptions.containerId}`);
            container = document.createElement('div');
            container.id = defaultOptions.containerId;
            // Apply Bootstrap positioning classes + custom class
            container.className = `toast-container position-fixed p-3 ${defaultOptions.position}`;
            container.style.zIndex = String(defaultOptions.zIndex); // Set z-index
            // Style for stacking (newest on top if using flex-column-reverse)
            container.style.display = 'flex';
            container.style.flexDirection = 'column-reverse'; // New toasts appear above old ones
            container.style.maxHeight = '90vh'; // Limit height to prevent overflow
            container.style.overflowY = 'auto';  // Allow scrolling if many toasts
             container.setAttribute('aria-live', 'polite'); // Accessibility
             container.setAttribute('aria-atomic', 'true');

            document.body.appendChild(container);
        } else {
            log("debug", scriptName, functionName, `✅ Using existing toast container #${defaultOptions.containerId}`);
        }

        initialized = true;
        log("info", scriptName, functionName, "🍞 Toast system initialized successfully.");

        // Process any queued toasts
        processQueue();
    }

    /** Process toasts queued before initialization */
    function processQueue() {
        if (queue.length > 0) {
            log("debug", scriptName, "processQueue", `⚙️ Processing ${queue.length} queued toasts.`);
            // Process in FIFO order
            while (queue.length > 0) {
                const item = queue.shift();
                createToast(item.message, item.type);
            }
        }
    }

    /**
     * Creates and displays a single toast message.
     * @param {string} message - The message to display.
     * @param {string} type - The type ('success', 'info', 'warning', 'danger', etc.).
     */
    function createToast(message, type = 'primary') {
        const functionName = "createToast";
        if (!initialized) {
            log("warn", scriptName, functionName, "⚠️ Toast system not initialized. Queuing toast.", { message, type });
            queue.push({ message, type });
            // Attempt lazy initialization if not done yet
            if (document.readyState === 'complete' || document.readyState === 'interactive') {
                 init();
            }
            return;
        }

        if (!container) {
            log("error", scriptName, functionName, "❌ Cannot create toast: container is missing.");
            return;
        }

         if (!message) {
             log("warn", scriptName, functionName, "⚠️ Attempted to show toast with empty message.");
             return;
         }


        // Normalize type ('error' -> 'danger')
        const normalizedType = (type === 'error') ? 'danger' : type;
        const styles = typeStyles[normalizedType] || typeStyles.primary; // Fallback to primary

        toastCount++;
        const toastId = `toast-${toastCount}`;

        try {
            // Create toast element using Bootstrap structure (can be simplified if no Bootstrap)
            const toastEl = document.createElement('div');
            toastEl.id = toastId;
            // Basic ARIA roles for accessibility
            toastEl.setAttribute('role', 'alert');
            toastEl.setAttribute('aria-live', 'assertive');
            toastEl.setAttribute('aria-atomic', 'true');
            // Add 'show' class for visibility, 'fade' for transitions (optional)
            toastEl.className = `toast show`;
            toastEl.style.backgroundColor = styles.bg;
            toastEl.style.color = styles.text;
            toastEl.style.minWidth = '250px'; // Ensure minimum width
            toastEl.style.margin = '0.5rem 0'; // Vertical spacing
            // toastEl.style.opacity = '0.95'; // Slightly transparent (optional)
            toastEl.style.boxShadow = '0 0.25rem 0.75rem rgba(0, 0, 0, 0.1)';
            toastEl.style.borderRadius = '0.25rem';
            toastEl.style.transition = 'opacity 0.5s ease-out'; // Fade out transition

            // --- Toast structure (using Bootstrap's d-flex for alignment) ---
            const flexContainer = document.createElement('div');
            flexContainer.className = 'd-flex';

            // Toast body
            const body = document.createElement('div');
            body.className = 'toast-body';
            body.textContent = message; // Safely sets text content
            body.style.flexGrow = '1'; // Allow body to take available space

            // Close button (Bootstrap style)
            const closeBtn = document.createElement('button');
            closeBtn.type = 'button';
            // Adapt button color based on background for contrast
            const closeBtnClass = (normalizedType === 'light' || normalizedType === 'warning' || normalizedType === 'info')
                ? 'btn-close-black' : 'btn-close-white';
            closeBtn.className = `btn-close ${closeBtnClass} me-2 m-auto`; // Standard BS classes
            closeBtn.setAttribute('aria-label', 'Close');
            closeBtn.onclick = () => {
                // Add fade-out effect before removing
                toastEl.style.opacity = '0';
                setTimeout(() => toastEl.remove(), 500); // Remove after transition
                log("debug", scriptName, "closeBtn:click", `🖱️ Closed toast: ${toastId}`);
            };

            flexContainer.appendChild(body);
            flexContainer.appendChild(closeBtn);
            toastEl.appendChild(flexContainer);

            // Add to container (prepend puts newest at the top/bottom depending on flex-direction)
            container.prepend(toastEl); // Prepend for 'column-reverse' stacking
            log("info", scriptName, functionName, `🍞 Showing toast #${toastId}: (${normalizedType}) "${message.substring(0,50)}..."`);

            // Auto-hide after delay
            setTimeout(() => {
                // Check if the element still exists before trying to remove
                const elToRemove = document.getElementById(toastId);
                if (elToRemove) {
                    elToRemove.style.opacity = '0'; // Start fade out
                    setTimeout(() => elToRemove.remove(), 500); // Remove after fade
                    log("debug", scriptName, "autoHide", `⏳ Auto-hiding toast: ${toastId}`);
                }
            }, defaultOptions.delay);

        } catch (err) {
            log("error", scriptName, functionName, `❌ Error creating toast element: ${err.message}`, err);
            // Fallback to simple console log if DOM manipulation fails
            console.error(`[Toast Error] ${type}: ${message}`);
        }
    }

    // --- Public Interface ---
    return {
        // Expose init for manual call if needed, but DOMContentLoaded is preferred
        init: init,
        // The main function to show a toast
        show: (message, type = 'success') => {
            // Clean and limit message length for display
             const cleanMessage = typeof message === "string"
                 ? message.replace(/\s+/g, ' ').trim().slice(0, 200) // Replace multiple spaces, trim, limit length
                 : String(message).slice(0, 200); // Convert non-strings and limit

            if (!initialized) {
                // Queue if not initialized and DOM isn't ready yet
                if (document.readyState !== 'complete' && document.readyState !== 'interactive') {
                    queue.push({ message: cleanMessage, type });
                    log("debug", scriptName, "show", " queuing toast - system/DOM not ready.", { message: cleanMessage, type });
                    return;
                } else {
                    // If DOM is ready, try initializing now before showing
                    init();
                }
            }
             // Now that we ensure it's initialized (or attempted), create the toast
             createToast(cleanMessage, type);
        }
    };
})(); // Immediately invoke the function to create the ToastSystem object

// --- Initialization ---
// Initialize automatically when the DOM is ready
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    // Already loaded
    ToastSystem.init();
} else {
    document.addEventListener('DOMContentLoaded', ToastSystem.init);
}


// --- Global Access ---
// Expose a simplified global function for easy use elsewhere
// (e.g., inline `<script>` tags or other modules)
/**
 * Shows a toast notification.
 * @param {string} message - The message to display.
 * @param {'success'|'info'|'warning'|'error'|'danger'|'primary'|'secondary'|'light'|'dark'} [type='success'] - The type of toast. 'error' is mapped to 'danger'.
 */
window.showToast = (message, type = 'success') => {
    ToastSystem.show(message, type);
};

// Export the main show function if needed for ES module imports
export const showToast = window.showToast;

log("debug", scriptName, "module", "Toast module loaded. Global showToast attached.");