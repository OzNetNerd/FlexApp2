/**
 * core/utils/utils.js
 * Generic utility functions
 */

import log from '../utils/logger.js';

const scriptName = "utils.js";

// Cache to store API responses
const apiCache = new Map();

/**
 * Fetches JSON data from an API and logs the process.
 * Uses caching to prevent duplicate requests.
 * @param {string} scriptName - The name of the calling script.
 * @param {string} functionName - The function calling this utility.
 * @param {string} apiUrl - The API endpoint to fetch data from.
 * @returns {Promise<any>} Resolves with API data or rejects with an error.
 */
export async function fetchApiData(scriptName, functionName, apiUrl) {
    // Check if this URL has already been requested
    if (apiCache.has(apiUrl)) {
        log("info", scriptName, functionName, `Using cached data for: ${apiUrl}`);
        return apiCache.get(apiUrl);
    }

    log("info", scriptName, functionName, `Fetching data from API: ${apiUrl}`);

    try {
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (!response.ok) {
            const errorMsg = `HTTP error ${response.status} (${response.statusText}) when fetching from ${apiUrl}`;
            log("error", scriptName, functionName, "❌ API Request Failed", { errorMsg });
            throw new Error(errorMsg);
        }

        // Try to parse as JSON, but handle potential parsing errors
        let data;
        try {
            data = await response.json();
        } catch (parseError) {
            const errorMsg = `Failed to parse API response as JSON: ${parseError.message}`;
            log("error", scriptName, functionName, "❌ JSON Parse Error", { errorMsg });
            throw new Error(errorMsg);
        }

        // Validate data structure
        if (!data) {
            log("warn", scriptName, functionName, "⚠️ API returned empty data");
            data = { data: [] }; // Provide fallback empty data structure
        }

        log("info", scriptName, functionName, `✅📥 API data received from ${apiUrl}`);

        // Store in cache for future requests
        apiCache.set(apiUrl, data);

        return data;

    } catch (error) {
        log("error", scriptName, functionName, "❌ Error fetching API data", {
            error: error.message,
            url: apiUrl,
            stack: error.stack
        });
        throw error;
    }
}

/**
 * Gets dataset attributes from a container element
 * @param {string} containerId - The ID of the container element
 * @returns {Object|null} - The dataset object or null if not found
 */
export function getDatasetVariables(containerId) {
    const functionName = "getDatasetVariables";

    log("debug", scriptName, functionName, `📦 Looking for HTML container ID: ${containerId}`);

    const container = document.getElementById(containerId);

    if (!container) {
        log("error", scriptName, "checkContainer", `❌📦 Could not find container in HTML with ID: ${containerId}`);
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
        log("info", scriptName, functionName, `✅📦 ${containerId} entries:`, containerDatasetVariables);
    }

    return containerDatasetVariables;
}

/**
 * Gets a specific value from a dataset object
 * @param {string} scriptName - The name of the calling script
 * @param {Object} payload - The dataset object
 * @param {string} variableName - The name of the variable to retrieve
 * @returns {string|null} - The value or null if not found
 */
export function getDatasetValue(scriptName, payload, variableName) {
    const functionName = "getDatasetValue";
    log("info", scriptName, functionName, `Looking for ${variableName} in dataset:`, payload);

    if (payload && payload[variableName]) {
        log("info", scriptName, functionName, `Found it. Its value is: ${payload[variableName]}`);
        return payload[variableName];
    } else {
        log("error", scriptName, functionName, `❌ Missing or invalid ${variableName} in dataset`, payload);
        return null; // Return null if the variable does not exist or is falsy
    }
}