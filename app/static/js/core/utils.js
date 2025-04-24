// /static/js/core/utils.js

import log from '/static/js/core/logger.js';

const scriptName = "utils.js";

// Cache to store API responses to avoid redundant fetches within a page lifecycle
const apiCache = new Map();

/**
 * Fetches JSON data from an API, logs the process, and uses simple in-memory caching.
 * @param {string} callingScriptName - The name of the script calling this utility.
 * @param {string} callingFunctionName - The name of the function calling this utility.
 * @param {string} apiUrl - The API endpoint to fetch data from.
 * @returns {Promise<any>} Resolves with the parsed JSON data or rejects with an error.
 */
export async function fetchApiData(callingScriptName, callingFunctionName, apiUrl) {
    const functionName = "fetchApiData"; // Use a fixed name for logging within this utility

    // Input validation
    if (!apiUrl) {
        log("error", callingScriptName, callingFunctionName, `❌ ${functionName} called with invalid API URL.`);
        return Promise.reject(new Error("Invalid API URL provided."));
    }

    // Check cache first
    if (apiCache.has(apiUrl)) {
        log("info", callingScriptName, callingFunctionName, `✅ Cache hit for: ${apiUrl}`);
        // Return a clone to prevent modifying the cached object directly
        return Promise.resolve(JSON.parse(JSON.stringify(apiCache.get(apiUrl))));
    }

    log("info", callingScriptName, callingFunctionName, `⏳ Fetching data from API: ${apiUrl}`);

    try {
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                // 'Content-Type': 'application/json' // Not typically needed for GET requests
            },
            cache: 'no-cache', // Explicitly disable browser caching if needed, rely on our map cache
        });

        if (!response.ok) {
            // Attempt to get error details from the response body if possible
            let errorBody = '';
            try {
                errorBody = await response.text(); // Read as text first
            } catch (e) { /* Ignore if reading body fails */ }
            const errorMsg = `HTTP error ${response.status} (${response.statusText}) fetching ${apiUrl}. Body: ${errorBody.substring(0, 200)}`; // Log truncated body
            log("error", scriptName, functionName, `❌ API Request Failed: ${errorMsg}`, { status: response.status, url: apiUrl });
            throw new Error(errorMsg); // Throw with detailed message
        }

        // Try to parse as JSON
        let data;
        try {
            data = await response.json();
        } catch (parseError) {
            const errorMsg = `Failed to parse API response from ${apiUrl} as JSON: ${parseError.message}`;
            log("error", scriptName, functionName, "❌ JSON Parse Error", { errorMsg, url: apiUrl });
            throw new Error(errorMsg); // Re-throw parse error
        }

        // Basic validation of the data structure (optional, adjust as needed)
        if (data === null || data === undefined) {
            log("warn", scriptName, functionName, `⚠️ API returned null or undefined data from ${apiUrl}`);
            // Decide whether to treat this as an error or return a default (e.g., empty array/object)
            // Returning null here, caller should handle it.
        } else {
             log("info", scriptName, functionName, `✅📥 API data received successfully from ${apiUrl}`);
        }

        // Store the valid data in cache (clone to prevent mutation issues)
        apiCache.set(apiUrl, JSON.parse(JSON.stringify(data)));

        return data;

    } catch (error) {
        // Catch both fetch/network errors and parsing errors
        log("error", callingScriptName, callingFunctionName, `❌ Error during API fetch/processing for ${apiUrl}`, {
            errorMessage: error.message,
            url: apiUrl,
            // stack: error.stack // Stack trace can be very verbose, log conditionally if needed
        });
        // Re-throw the original error or a new error encapsulating the context
        throw error;
    }
}


/**
 * Retrieves all `data-*` attributes from a DOM element by its ID.
 * @param {string} containerId - The ID of the DOM element.
 * @returns {DOMStringMap | null} The dataset object, or null if the element is not found.
 */
export function getDatasetVariables(containerId) {
    const functionName = "getDatasetVariables";

    if (!containerId) {
        log("warn", scriptName, functionName, "⚠️ Called with no container ID.");
        return null;
    }

    log("debug", scriptName, functionName, `📦 Looking for HTML container with ID: ${containerId}`);
    const container = document.getElementById(containerId);

    if (!container) {
        log("error", scriptName, functionName, `❌📦 Container not found in HTML with ID: ${containerId}`);
        return null;
    }

    log("debug", scriptName, functionName, `✅📦 Container found: ${containerId}`);
    const dataset = container.dataset;

    if (Object.keys(dataset).length === 0) {
        log("warn", scriptName, functionName, `⚠️ HTML dataset is empty for container: ${containerId}`);
    } else {
        log("info", scriptName, functionName, `✅📦 Dataset entries for ${containerId}:`, { ...dataset }); // Log a copy
    }

    return dataset;
}

/**
 * Safely retrieves a specific value from a dataset object.
 * @param {string} callingScriptName - The name of the script calling this utility.
 * @param {DOMStringMap | null | undefined} dataset - The dataset object obtained from getDatasetVariables.
 * @param {string} variableName - The camelCase name of the `data-*` attribute (e.g., 'apiUrl' for 'data-api-url').
 * @returns {string | null} The value of the dataset variable, or null if not found or invalid.
 */
export function getDatasetValue(callingScriptName, dataset, variableName) {
    const functionName = "getDatasetValue";

    if (!variableName) {
        log("warn", callingScriptName, functionName, `⚠️ Called with no variable name to look for.`);
        return null;
    }
     if (!dataset) {
        log("warn", callingScriptName, functionName, `⚠️ Called with null or undefined dataset while looking for '${variableName}'.`);
        return null;
    }

    log("debug", callingScriptName, functionName, `🔎 Looking for '${variableName}' in dataset:`, { ...dataset });

    // Use hasOwnProperty to ensure it's a direct property and not from the prototype chain
    if (dataset && Object.prototype.hasOwnProperty.call(dataset, variableName)) {
        const value = dataset[variableName];
        if (value !== null && value !== undefined && value !== "") { // Check for non-empty value
             log("info", callingScriptName, functionName, `✅ Found '${variableName}'. Value: '${value}'`);
             return value;
        } else {
             log("warn", callingScriptName, functionName, `⚠️ Found '${variableName}' but its value is empty or null/undefined.`);
             return null;
        }
    } else {
        log("error", callingScriptName, functionName, `❌ Missing or invalid '${variableName}' in dataset.`, { dataset: { ...dataset } });
        return null; // Return null if the variable does not exist
    }
}
