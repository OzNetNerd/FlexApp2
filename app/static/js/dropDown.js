// js/dropDown.js

import log from 'logger.js';

const scriptName = "dropDown";

document.addEventListener('DOMContentLoaded', () => {
    const functionName = "init";

    log("info", scriptName, functionName, "Initializing column selector...");

    // Check if the initializer function exists
    if (typeof initColumnSelector === 'function') {
        initColumnSelector();
    } else {
        log("error", scriptName, functionName, "❌ initColumnSelector function is not defined.");
    }
});
