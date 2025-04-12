/**
 * table.js
 * Logger Module – Updated to support file and function grouping.
 */


import log from '/static/js/logger.js';
import initializeTable from './table/tableInit.js';
const scriptName = "table.js";

// Add this check to prevent multiple initializations
if (!window.__tableInitialized) {
  window.__tableInitialized = true;

  document.addEventListener('DOMContentLoaded', () => {
      const functionName = "DOMContentLoaded";
      log("info", scriptName, functionName, "Initializing table and column selector...");
      // Initialize the table.
      initializeTable();
  });
}