/**
 * components/tables/config.js
 * Configuration for tables component
 */

import log from '../../core/utils/logger.js';
import { TABLE_CONFIG } from '../../core/config.js';

const scriptName = "tables/config.js";

/**
 * Get table configuration from the container's dataset
 * @param {string} tableId - The ID of the table element
 * @returns {Object} - Table configuration
 */
export function getTableConfig(tableId) {
    const functionName = "getTableConfig";
    log("info", scriptName, functionName, `Loading configuration for table: ${tableId}`);

    const tableElement = document.getElementById(tableId);
    if (!tableElement) {
        log("error", scriptName, functionName, `Table element not found: ${tableId}`);
        return { ...TABLE_CONFIG };
    }

    // Get default config
    const config = { ...TABLE_CONFIG };

    // Override from dataset if available
    if (tableElement.dataset.perPage) {
        config.defaultPerPage = parseInt(tableElement.dataset.perPage, 10);
        log("debug", scriptName, functionName, `Using custom perPage: ${config.defaultPerPage}`);
    }

    if (tableElement.dataset.pagination === 'false') {
        config.pagination = false;
        log("debug", scriptName, functionName, `Pagination disabled for table: ${tableId}`);
    }

    if (tableElement.dataset.enableExport === 'false') {
        config.enableExport = false;
        log("debug", scriptName, functionName, `Export disabled for table: ${tableId}`);
    }

    log("info", scriptName, functionName, `Table configuration loaded:`, config);
    return config;
}

/**
 * Default column configuration
 */
export const DEFAULT_COLUMN_CONFIG = {
    sortable: true,
    filterable: true,
    hidden: false
};

/**
 * Get column configurations from the table element
 * @param {string} tableId - The ID of the table element
 * @returns {Object} - Column configurations
 */
export function getColumnConfig(tableId) {
    const functionName = "getColumnConfig";
    log("info", scriptName, functionName, `Loading column configuration for table: ${tableId}`);

    const tableElement = document.getElementById(tableId);
    if (!tableElement) {
        log("error", scriptName, functionName, `Table element not found: ${tableId}`);
        return {};
    }

    // Look for column-config in dataset
    if (tableElement.dataset.columnConfig) {
        try {
            const columnConfig = JSON.parse(tableElement.dataset.columnConfig);
            log("info", scriptName, functionName, `Column configuration found:`, columnConfig);
            return columnConfig;
        } catch (error) {
            log("error", scriptName, functionName, `Error parsing column configuration:`, { error });
            return {};
        }
    }

    log("debug", scriptName, functionName, `No column configuration found for table: ${tableId}`);
    return {};
}