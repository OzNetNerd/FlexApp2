const scriptName = "utils";

import log from './logger.js';

/**
 * Fetches JSON data from an API and logs the process.
 * @param {string} scriptName - The name of the calling script.
 * @param {string} functionName - The function calling this utility.
 * @param {string} apiUrl - The API endpoint to fetch data from.
 * @returns {Promise<any>} Resolves with API data or rejects with an error.
 */
export async function fetchApiData(scriptName, functionName, apiUrl) {
    log("info", scriptName, functionName, `🔄 Fetching data from API: ${apiUrl}`);

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            const errorMsg = `HTTP error ${response.status} (${response.statusText}) when fetching from ${apiUrl}`;
            log("error", scriptName, functionName, "❌ API Request Failed", { errorMsg });
            throw new Error(errorMsg);
        }

        const data = await response.json();
        log("info", scriptName, functionName, `✅📥 API data received: `, {...data});
        return data;

    } catch (error) {
        log("error", scriptName, functionName, "❌ Error fetching API data", { error: error.message });
        throw error;
    }
}


// Function to get the 'data-*' attributes configuration, which works with any container ID
export function getDatasetVariables(containerId) {
    const functionName = "getDatasetVariables";

    log("debug", scriptName, functionName, `📦 Looking for HTML container ID: ${containerId}`);

    const container = document.getElementById(containerId);

    if (!container) {
        log("error", scriptName, "checkContainer", `❌📦 Could not find container in HTMLfound with ID: ${containerId}`);
        return null;
    } else {
        log("debug", scriptName, "checkContainer", `✅📦 Container found with ID: ${containerId}`);
    }

    // Extract `data-*` attributes
    const containerDatasetVariables = container.dataset;

    log("debug", scriptName, functionName, `📦 Extracting dataset from: ${containerId}`);

    // Check if dataset is empty and log error if it is
    if (Object.keys(containerDatasetVariables).length === 0) {
        log("error", scriptName, functionName, `❌📦 HTML dataset is empty for container: ${containerId}`);
    } else {
        log("debug", scriptName, functionName, `✅📦 Number of dataset entries found in ${containerId}: ${Object.keys(containerDatasetVariables).length}`);
        log("info", scriptName, functionName, `✅📦 ${containerId} entries:`, {...containerDatasetVariables});
    }

    return containerDatasetVariables
}


export function getDatasetValue(scriptName, payload, variableName) {
    const functionName = "getDatasetValue";
    // log("debug", scriptName, functionName, `🔍 Extracting API URL from: ${tableContainerId}`);
    log("info", scriptName, functionName, `Looking for ${variableName} in dataset:`,  {...payload});

    if (payload && payload[variableName]) {
        log("info", scriptName, functionName, `✅ Found it. It's value is: ${payload[variableName]}`);
        return payload[variableName];
    } else {
        log("error", scriptName, functionName, `❌ Missing or invalid ${variableName} in dataset`, {...payload});
        return null; // Return null if the variable does not exist or is falsy
    }
}
