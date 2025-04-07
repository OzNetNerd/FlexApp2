// apiService.js

import log from '/static/js/logger.js';
import { getDatasetVariables, getDatasetValue, fetchApiData } from '/static/js/utils.js';

const scriptName = "apiService.js";

/**
 * Fetches data from an API endpoint using the dataset variables on a container element
 * @param {string} containerId - The ID of the container element with dataset attributes
 * @returns {Promise<Array|Object>} - The data fetched from the API
 */
export async function fetchApiDataFromContainer(containerId) {
    const functionName = "fetchApiDataFromContainer";

    const datasetVariables = getDatasetVariables(containerId);
    const apiUrl = getDatasetValue(scriptName, datasetVariables, "apiUrl");
    log("info", scriptName, functionName, `✅🌐 API URL Retrieved: ${apiUrl}`);

    try {
        // Get data from API
        const data = await fetchApiData(scriptName, functionName, apiUrl);
        // Log the actual data for debugging
        log("info", scriptName, functionName, "📊 Data structure:", data);
        return data;
    } catch (error) {
        log("error", scriptName, functionName, "❌ Failed to fetch data from API", { error: error.message || String(error) });
        throw error; // Re-throw to let the caller handle it
    }
}

/**
 * Normalizes data structure from various API response formats
 * @param {Array|Object} data - The raw data from the API
 * @returns {Array} - Normalized data array
 */
export function normalizeData(data) {
    // Handle both data structures: data = [{...}] or data = {data: [{...}]}
    return Array.isArray(data) ? data : (data.data || []);
}

/**
 * Formats a string for use as a column header or display text
 * @param {string} text - Raw text to format
 * @returns {string} - Formatted text
 */
export function formatDisplayText(text) {
    return text
        .replace(/_/g, ' ') // Replace underscores with spaces
        .replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()) // Capitalize first letter
        .replace(/\bId\b/g, 'ID') // Make "Id" into "ID"
        .replace(/\bAt\b/g, 'at'); // Make "At" into "at"
}