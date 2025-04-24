/**
 * components/tables/utils.js
 * Utility functions for table operations
 */

import log from '../../core/utils/logger.js';
import { formatDisplayText } from '../../core/api/apiService.js';

const scriptName = "tables/utils.js";

/**
 * Generate table headers based on data
 * @param {Array} data - Array of data objects
 * @param {Object} columnConfig - Column configuration
 * @returns {Array} - Array of header objects
 */
export function generateHeaders(data, columnConfig = {}) {
    const functionName = "generateHeaders";

    if (!data || !data.length) {
        log("warn", scriptName, functionName, "No data provided for header generation");
        return [];
    }

    log("info", scriptName, functionName, `Generating headers from ${data.length} data items`);

    // Get keys from first data object
    const sampleObject = data[0];
    const keys = Object.keys(sampleObject);

    // Transform keys into header objects
    const headers = keys.map(key => {
        const config = columnConfig[key] || {};

        return {
            id: key,
            text: formatDisplayText(key),
            sortable: config.sortable !== false,
            filterable: config.filterable !== false,
            hidden: config.hidden === true
        };
    });

    log("debug", scriptName, functionName, `Generated ${headers.length} headers`);
    return headers;
}

/**
 * Sort table data based on column and direction
 * @param {Array} data - Data to sort
 * @param {string} column - Column to sort by
 * @param {string} direction - Sort direction ('asc' or 'desc')
 * @returns {Array} - Sorted data
 */
export function sortData(data, column, direction = 'asc') {
    const functionName = "sortData";

    if (!data || !data.length) {
        return [];
    }

    log("info", scriptName, functionName, `Sorting data by ${column} in ${direction} order`);

    return [...data].sort((a, b) => {
        let valueA = a[column];
        let valueB = b[column];

        // Handle null/undefined values
        if (valueA === null || valueA === undefined) valueA = '';
        if (valueB === null || valueB === undefined) valueB = '';

        // Convert to string for comparison if not already
        if (typeof valueA !== 'string') valueA = String(valueA);
        if (typeof valueB !== 'string') valueB = String(valueB);

        // Compare values
        if (direction === 'asc') {
            return valueA.localeCompare(valueB);
        } else {
            return valueB.localeCompare(valueA);
        }
    });
}

/**
 * Filter data based on search criteria
 * @param {Array} data - Data to filter
 * @param {string} searchTerm - Search term
 * @param {Array} columns - Columns to search in (if empty, search all)
 * @returns {Array} - Filtered data
 */
export function filterData(data, searchTerm, columns = []) {
    const functionName = "filterData";

    if (!data || !data.length || !searchTerm) {
        return data;
    }

    log("info", scriptName, functionName, `Filtering data by "${searchTerm}"`);

    const term = searchTerm.toLowerCase();

    return data.filter(item => {
        // Define which columns to search
        const keysToSearch = columns.length ? columns : Object.keys(item);

        // Check if any of the specified columns contain the search term
        return keysToSearch.some(key => {
            const value = item[key];
            if (value === null || value === undefined) return false;

            return String(value).toLowerCase().includes(term);
        });
    });
}

/**
 * Export table data to CSV
 * @param {Array} data - Data to export
 * @param {Array} headers - Table headers
 * @param {string} filename - Output filename
 */
export function exportToCsv(data, headers, filename = 'export.csv') {
    const functionName = "exportToCsv";

    if (!data || !data.length) {
        log("warn", scriptName, functionName, "No data to export");
        return;
    }

    log("info", scriptName, functionName, `Exporting ${data.length} rows to CSV`);

    // Filter visible headers
    const visibleHeaders = headers.filter(header => !header.hidden);

    // Create CSV header row
    let csv = visibleHeaders.map(header => `"${header.text}"`).join(',') + '\n';

    // Add data rows
    data.forEach(item => {
        const row = visibleHeaders.map(header => {
            const value = item[header.id];
            return value !== null && value !== undefined ? `"${String(value).replace(/"/g, '""')}"` : '""';
        }).join(',');
        csv += row + '\n';
    });

    // Create download link
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    log("info", scriptName, functionName, `CSV export complete: ${filename}`);
}