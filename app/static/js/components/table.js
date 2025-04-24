/**
 * /static/js/components/table.js
 * Entry point for table initialization. Imports the actual table logic.
 */

import log from '../core/logger.js'; // Adjusted path
// Assuming tableInit.js is in the same directory or a subdirectory
// If tableInit.js is also moved, adjust this path accordingly.
// If it's complex, it might live in its own subdirectory: e.g., './table/tableInit.js'
import initializeTable from './tableInit.js'; // *** CHECK THIS PATH ***

const scriptName = "table.js";

// Prevent multiple initializations using a global flag (simple approach)
if (!window.__tableModuleInitialized) {
  window.__tableModuleInitialized = true; // Set flag immediately

  document.addEventListener('DOMContentLoaded', () => {
    const functionName = "DOMContentLoaded";
    log("info", scriptName, functionName, "🚀 DOM ready. Initializing table features...");

    try {
      // Call the actual initialization function from tableInit.js
      initializeTable();
      // Assuming initializeTable handles its own success logging
    } catch (error) {
       log("error", scriptName, functionName, "❌ Failed to initialize table features.", error);
    }
  });

  log("debug", scriptName, "init", "Table module loaded and DOMContentLoaded listener attached.");

} else {
  log("warn", scriptName, "init", "⚠️ Table module already initialized. Skipping setup.");
}

// Export initializeTable only if you need to call it manually from elsewhere,
// otherwise, it's self-contained via the DOMContentLoaded listener.
// export default initializeTable;