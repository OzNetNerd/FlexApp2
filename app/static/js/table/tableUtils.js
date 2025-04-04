// table/tableUtils.js

import log from '/static/js/logger.js';

const scriptName = "tableUtils";

export function waitForAgGrid() {
    const functionName = "waitForAgGrid";

    return new Promise((resolve, reject) => {
        try {
            // Immediately resolve if AG Grid is already loaded
            if (typeof Grid !== "undefined") {
                log("info", scriptName, functionName, "✅ AG Grid library is fully loaded and ready for use");
                return resolve(Grid);
            }

            log("info", scriptName, functionName, "⏳ Waiting for AG Grid to load...");

            // Poll every 100ms to check for AG Grid availability
            const checkInterval = setInterval(() => {
                if (typeof Grid !== "undefined") {
                    clearInterval(checkInterval);
                    log("info", scriptName, functionName, "✅ AG Grid has loaded.");
                    resolve(Grid);
                }
            }, 100);

            // Timeout to prevent infinite waiting
            setTimeout(() => {
                clearInterval(checkInterval);
                log("error", scriptName, functionName, "❌ AG Grid failed to load after timeout.");
                reject(new Error("AG Grid failed to load after timeout"));
            }, 5000);
        } catch (error) {
            log("error", scriptName, functionName, `❌ Error checking AG Grid: ${error.message}`);
            reject(error);
        }
    });
}

function loadTableData(data) {
    const functionName = 'loadTableData';

    // Check if data is available before initializing the table
    if (!data || data.length === 0) {
        throw new Error("❌ No data available for the table.");
    }

    // Log data before initializing the table
    log("info", scriptName, functionName, `📊 Initializing table with data:`, data);

    // Use AG Grid's API to set the row data using the updated method
    try {
        if (gridOptions.api) {
            gridOptions.api.setGridOption('rowData', data);
            console.log("📊 Table initialized with data:", data);
        } else {
            throw new Error("❌ AG Grid API not available.");
        }
    } catch (error) {
        console.error("❌ Error displaying the AG Grid table:", error);
        log("error", scriptName, functionName, `❌ Error displaying the AG Grid table: ${error.message}`);
    }
}