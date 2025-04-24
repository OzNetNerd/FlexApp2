/**
 * main.js
 * Main application entry point
 */

import log from './core/utils/logger.js';
import initializeTable from './components/tables/index.js';

const scriptName = "main.js";

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const functionName = "DOMContentLoaded";
    log("info", scriptName, functionName, "Application initializing...");

    try {
        // Initialize tables
        initializeTable();

        // Initialize other components as needed
        // initializeAutoComplete();
        // initializeToasts();

        log("info", scriptName, functionName, "Application initialized successfully");
    } catch (error) {
        log("error", scriptName, functionName, "Error initializing application", {
            error: error.message,
            stack: error.stack
        });
    }
});