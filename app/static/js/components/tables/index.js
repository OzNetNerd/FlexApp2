/**
 * components/tables/index.js
 * Main entry point for the table functionality
 */

import log from '../../core/utils/logger.js';
import initializeTable from './init.js';

const scriptName = "tables/index.js";

// Prevent multiple initializations
if (!window.__tableInitialized) {
  window.__tableInitialized = true;

  document.addEventListener('DOMContentLoaded', () => {
    const functionName = "DOMContentLoaded";
    log("info", scriptName, functionName, "Initializing table and column selector...");
    initializeTable();
  });
}

// Export initializeTable so it can be imported elsewhere
export default initializeTable;