import log from './logger.js';
import initializeTable from './table/tableInit.js';

const scriptName = "table.js";

document.addEventListener('DOMContentLoaded', () => {
    const functionName = "DOMContentLoaded";
    log("info", scriptName, functionName, "Initializing table and column selector...");

    // Initialize the table.
    initializeTable();
});
