/**
 * core/config.js
 * Global configuration settings
 */

// API configuration
export const API_CONFIG = {
    baseUrl: '/api/v1',
    defaultHeaders: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    },
    timeout: 30000 // 30 seconds
};

// Logger configuration
export const LOGGER_CONFIG = {
    enabledLevels: ['info', 'warn', 'error'],
    // Set to true to enable verbose debugging
    debug: false
};

// Table configuration defaults
export const TABLE_CONFIG = {
    pagination: true,
    perPageOptions: [10, 25, 50, 100],
    defaultPerPage: 25,
    enableExport: true,
    exportFormats: ['csv', 'json']
};