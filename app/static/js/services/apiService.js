// /static/js/services/apiService.js

import log from '../core/logger.js'; // Adjusted path
import { getDatasetVariables, getDatasetValue, fetchApiData } from '../core/utils.js'; // Adjusted path

const scriptName = "apiService.js";

/**
 * Fetches data from an API endpoint specified in a container element's dataset.
 * @param {string} containerId - The ID of the container element holding 'data-api-url'.
 * @returns {Promise<Array|Object>} - The normalized data fetched from the API.
 * @throws {Error} If the container, API URL, or data fetching fails.
 */
export async function fetchApiDataFromContainer(containerId) {
    const functionName = "fetchApiDataFromContainer";

    log("info", scriptName, functionName, `🚀 Starting API fetch for container: ${containerId}`);

    const datasetVariables = getDatasetVariables(containerId); // Util handles logging if container not found
    if (!datasetVariables) {
        // Error already logged by getDatasetVariables
        throw new Error(`Container with ID '${containerId}' not found.`);
    }

    const apiUrl = getDatasetValue(scriptName, datasetVariables, "apiUrl"); // Util handles logging
    if (!apiUrl) {
        throw new Error(`'data-api-url' attribute not found or empty in container '${containerId}'.`);
    }

    log("info", scriptName, functionName, `✅🌐 API URL retrieved: ${apiUrl}`);

    try {
        // Get raw data from API using the utility function
        // Pass our script/function name for context in util logs
        const rawResponse = await fetchApiData(scriptName, functionName, apiUrl);

        // Check specifically for an error structure within a successful response (if API wraps errors)
        // Adjust this check based on your actual API error response format
        if (rawResponse && rawResponse.data && rawResponse.data.error && typeof rawResponse.data.error === 'object') {
            const error = rawResponse.data.error;
            const errorMessage = error.message || "Unknown API error structure";
            const statusCode = error.status_code || 'N/A';
            log("error", scriptName, functionName, `❌ API returned an error within data: ${errorMessage}`, { statusCode, apiUrl });
            // Throw an error matching the API's message
            throw new Error(`API Error (${statusCode}): ${errorMessage}`);
        }

        // Normalize the data structure before returning
        const normalized = normalizeData(rawResponse);
        log("info", scriptName, functionName, `✅📊 Data fetched and normalized successfully from ${apiUrl}. Items: ${normalized.length}`);
        log("debug", scriptName, functionName, "📊 Normalized Data Sample:", normalized.slice(0, 5)); // Log first 5 items

        return normalized; // Return the normalized data

    } catch (error) {
        // Catch errors from fetchApiData or the error check above
        log("error", scriptName, functionName, `❌ Failed to fetch or process data from API: ${apiUrl}`, { errorMessage: error.message });
        // Re-throw the error to be handled by the caller (e.g., tableInit)
        throw error;
    }
}

/**
 * Normalizes data structure from various common API response formats into a consistent array.
 * Handles: `[...]`, `{data: [...]}`. Logs warnings for unexpected structures.
 * @param {any} rawData - The raw data received from the API (after JSON parsing).
 * @returns {Array} - Normalized data as an array of objects, or an empty array if normalization fails or data is invalid.
 */
export function normalizeData(rawData) {
    const functionName = "normalizeData";

    if (!rawData) {
        log("warn", scriptName, functionName, "⚠️ Received null or undefined data for normalization. Returning [].");
        return [];
    }

    // Case 1: Data is already an array (common standard)
    if (Array.isArray(rawData)) {
        log("debug", scriptName, functionName, "ℹ️ Data is already an array. No normalization needed.");
        return rawData;
    }

    // Case 2: Data is an object containing a 'data' property which is an array
    if (typeof rawData === 'object' && rawData.data && Array.isArray(rawData.data)) {
        log("debug", scriptName, functionName, "ℹ️ Normalizing from {data: [...]}. Using data property.");
        return rawData.data;
    }

    // Case 3: Data is a single object (not in an array, not under 'data'). Wrap it in an array.
    // Be careful with this case - ensure it's not an error object or metadata wrapper.
    // Example check: Make sure it's not an error structure we know about.
    if (typeof rawData === 'object' && !Array.isArray(rawData) && !(rawData.error && typeof rawData.error === 'object')) {
        log("debug", scriptName, functionName, "ℹ️ Data is a single object. Wrapping in an array.");
        return [rawData];
    }


    // Log a warning if the structure doesn't match expected formats
    log("warn", scriptName, functionName, "⚠️ Unrecognized data structure received. Returning [].", { receivedData: rawData });
    return []; // Fallback to empty array for unrecognized structures
}

/**
 * Formats a raw string (like an object key) for display (e.g., as a column header).
 * Replaces underscores with spaces, capitalizes words, and handles 'Id' -> 'ID', 'At' -> 'at'.
 * @param {string} text - Raw text to format.
 * @returns {string} - Formatted text. Returns empty string if input is not a string.
 */
export function formatDisplayText(text) {
    if (typeof text !== 'string') {
        // log("warn", scriptName, "formatDisplayText", "⚠️ Input was not a string.", { input: text });
        return ''; // Return empty string for non-string input
    }

    // Ensure 'Id' and 'At' transformations happen correctly, even at word boundaries
    const formatted = text
        .replace(/_/g, ' ')                                    // Replace underscores with spaces
        .replace(/\b(Id)\b/gi, 'ID')                           // Handle 'Id' or 'id' -> 'ID' (case-insensitive boundary)
        .replace(/\b(At)\b/g, 'at')                            // Handle 'At' -> 'at' (case-sensitive boundary)
        .replace(/\w\S*/g, (txt) => {                         // Capitalize first letter of each word
            // Handle already uppercase words like 'ID'
            if (txt === 'ID' || txt === 'at') return txt;
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
         });

    // log("debug", scriptName, "formatDisplayText", `Formatted "${text}" -> "${formatted}"`);
    return formatted;
}