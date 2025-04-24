/**
 * js/pages/base.js
 * Base page functionality for all pages
 */

import log from '/static/js/core/utils/logger.js';

const scriptName = "base.js";

document.addEventListener('DOMContentLoaded', () => {
    const functionName = "DOMContentLoaded";
    log("info", scriptName, functionName, "🚀 Base page functionality initializing");

    // Initialize common page elements
    setupFeedbackButtons();
    verifyRequiredElements();

    log("info", scriptName, functionName, "✅ Base page initialization complete");
});

/**
 * Set up feedback buttons (if present)
 */
function setupFeedbackButtons() {
    const functionName = "setupFeedbackButtons";

    const feedbackButtons = document.querySelectorAll('.feedback-btn');
    if (feedbackButtons.length === 0) {
        log("debug", scriptName, functionName, "No feedback buttons found on page");
        return;
    }

    log("info", scriptName, functionName, `Found ${feedbackButtons.length} feedback buttons`);

    feedbackButtons.forEach(button => {
        button.addEventListener('click', () => {
            const feedbackType = button.dataset.feedbackType;
            log("info", scriptName, functionName, `Feedback button clicked: ${feedbackType}`);

            // Show feedback form or trigger feedback action
            if (typeof window.showToast === 'function') {
                window.showToast(`Thank you for your ${feedbackType} feedback!`, 'success');
            }
        });
    });
}

/**
 * Verify that required page elements are present
 */
function verifyRequiredElements() {
    const functionName = "verifyRequiredElements";

    // Check for required containers
    const requiredElements = [
        { selector: 'main', name: 'Main content container' },
        { selector: '.container', name: 'Page container' },
        { selector: '.toast-container', name: 'Toast notification container' }
    ];

    let allFound = true;

    requiredElements.forEach(element => {
        const found = document.querySelector(element.selector);
        if (!found) {
            log("error", scriptName, functionName, `❌ Required element missing: ${element.name} (${element.selector})`);
            allFound = false;
        }
    });

    if (allFound) {
        log("debug", scriptName, functionName, "✅ All required page elements verified");
    }
}