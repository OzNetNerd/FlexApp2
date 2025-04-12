const scriptName = "tableInit.js";

import log from '/static/js/logger.js';
import { getDatasetVariables } from '/static/js/utils.js';
import { fetchApiDataFromContainer, normalizeData, formatDisplayText } from '/static/js/apiService.js';
import getGridOptions, { setGridApi } from '/static/js/table/tableConfig.js';

import { createGrid, ModuleRegistry } from 'https://cdnjs.cloudflare.com/ajax/libs/ag-grid/31.0.1/ag-grid-community.esm.min.js';
import { ClientSideRowModelModule } from 'https://cdnjs.cloudflare.com/ajax/libs/ag-grid/31.0.1/ag-grid-community.esm.min.js';

log("info", scriptName, "module", "Starting table initialization module");

ModuleRegistry.registerModules([ClientSideRowModelModule]);
log("info", scriptName, "module", "AG Grid modules registered successfully");

const tableContainerId = "table-container";
const gridDiv = document.querySelector(`#${tableContainerId}`);
log("info", scriptName, "module", `Looking for table container with ID: ${tableContainerId}`, { found: !!gridDiv });

// Make gridApi global for other components to access
window.gridApi = null;

/**
 * Sets up the global search input to filter the AG Grid.
 */
function setupGlobalSearch(api, scriptName, functionName) {
    log("info", scriptName, functionName, "Setting up global search functionality");

    const input = document.getElementById('globalSearch');
    if (input) {
        log("info", scriptName, functionName, "Global search input found, attaching event listener");
        input.addEventListener('input', () => {
            const searchValue = input.value;
            log("debug", scriptName, functionName, `Applying quick filter with value: "${searchValue}"`);
            api.setQuickFilter(searchValue);
        });
        log("info", scriptName, functionName, "Global search setup complete");
    } else {
        log("warn", scriptName, functionName, "🔍 Search input (#globalSearch) not found.");
    }
}

/**
 * Creates a value formatter for handling object data types.
 * @param {Object} params - Cell params from AG Grid
 * @returns {String} - Formatted cell value
 */
function objectValueFormatter(params) {
    if (params.value === null || params.value === undefined) {
        return '';
    }

    // Handle arrays (like notes array)
    if (Array.isArray(params.value)) {
        if (params.value.length === 0) return '';
        return `${params.value.length} item${params.value.length > 1 ? 's' : ''}`;
    }

    // Handle objects
    if (typeof params.value === 'object') {
        // For company and similar references
        return `Ref #${params.value}`;
    }

    // Default case - return the value as is
    return params.value;
}

/**
 * Sets up the column selector dropdown for toggling column visibility.
 */
/**
 * Sets up the column selector dropdown for toggling column visibility.
 */
function setupColumnSelector(api, scriptName, functionName) {
    log("info", scriptName, functionName, "Setting up column selector functionality");

    const columnSelector = document.getElementById('columnSelectorItems');
    const selectAllBtn = document.getElementById('selectAllColumns');
    const clearAllBtn = document.getElementById('clearAllColumns');

    if (!columnSelector) {
        log("warn", scriptName, functionName, "📋 Column selector (#columnSelectorItems) not found");
        return;
    }

    if (!api) {
        log("warn", scriptName, functionName, "📋 Grid API not available");
        return;
    }

    // Clear any previously inserted checkboxes
    columnSelector.innerHTML = '';
    log("debug", scriptName, functionName, "Cleared existing column checkboxes");

    // Use getColumns() instead of getAllColumns()
    const allColumns = api.getColumns();

    if (!allColumns || allColumns.length === 0) {
        log("warn", scriptName, functionName, "No columns found in the grid");
        return;
    }

    log("info", scriptName, functionName, `Found ${allColumns.length} columns to display in selector`);

    allColumns.forEach(col => {
        const colId = col.getColId ? col.getColId() : col.getId();
        const colDef = col.getColDef();
        // Format column name with special case handling for "ID" and "at"
        const colName = (colDef.headerName || colId)
            .replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase())
            .replace(/\bId\b/g, 'ID')
            .replace(/\bAt\b/g, 'at');

        const div = document.createElement('div');
        div.classList.add('form-check', 'mb-1');

        const isVisible = !(api.getColumnState().find(c => c.colId === colId)?.hide === true);
        log("debug", scriptName, functionName, `Adding column selector: ${colName} (${colId}), visible: ${isVisible}`);

        div.innerHTML = `
            <input class="form-check-input" type="checkbox" value="${colId}" id="chk-${colId}" ${isVisible ? 'checked' : ''}>
            <label class="form-check-label" for="chk-${colId}">${colName}</label>
        `;

        const checkbox = div.querySelector('input');
        checkbox.addEventListener('change', (e) => {
            const isChecked = e.target.checked;
            log("debug", scriptName, functionName, `Column visibility changed: ${colName} (${colId}) - ${isChecked ? 'visible' : 'hidden'}`);
            api.setColumnVisible(colId, isChecked);
        });

        columnSelector.appendChild(div);
    });

    if (selectAllBtn) {
        log("debug", scriptName, functionName, "Select all columns button found, attaching event listener");
        selectAllBtn.addEventListener('click', () => {
            log("info", scriptName, functionName, "Select all columns button clicked");
            allColumns.forEach(col => {
                const colId = col.getColId ? col.getColId() : col.getId();
                api.setColumnVisible(colId, true);
                const checkbox = document.getElementById(`chk-${colId}`);
                if (checkbox) checkbox.checked = true;
            });
        });
    }

    if (clearAllBtn) {
        log("debug", scriptName, functionName, "Clear all columns button found, attaching event listener");
        clearAllBtn.addEventListener('click', () => {
            log("info", scriptName, functionName, "Clear all columns button clicked");
            allColumns.forEach(col => {
                const colId = col.getColId ? col.getColId() : col.getId();
                api.setColumnVisible(colId, false);
                const checkbox = document.getElementById(`chk-${colId}`);
                if (checkbox) checkbox.checked = false;
            });
        });
    }

    log("info", scriptName, functionName, "Column selector setup complete");
}

/**
 * Generates column definitions based on the data
 * @param {Array} data - The processed data array
 * @returns {Array} - Column definitions for AG Grid
 */
function generateColumnDefs(data) {
    const functionName = "generateColumnDefs";
    log("info", scriptName, functionName, "Generating column definitions from data");

    if (!data || data.length === 0) {
        log("warn", scriptName, functionName, "No data available to generate columns");
        return [];
    }

    log("debug", scriptName, functionName, `Data sample for column generation: ${JSON.stringify(data[0]).substring(0, 200)}...`);

    const sampleRow = data[0];
    const columnKeys = Object.keys(sampleRow);
    log("info", scriptName, functionName, `Found ${columnKeys.length} unique columns in data`);

    const columnDefs = columnKeys.map(key => {
        const headerName = formatDisplayText(key);
        log("debug", scriptName, functionName, `Creating column definition for: ${key} -> "${headerName}"`);

        const colDef = {
            field: key,
            headerName: headerName,
            sortable: true,
            filter: true
        };

        // Add valueFormatter for object types based on field content
        const sampleValue = sampleRow[key];
        if (sampleValue !== null && typeof sampleValue === 'object') {
            colDef.valueFormatter = objectValueFormatter;
        }

        return colDef;
    });

    log("info", scriptName, functionName, `Column definitions generated successfully: ${columnDefs.length} columns`);
    return columnDefs;
}

/**
 * Initializes the AG Grid table and applies search + column toggle functionality.
 */
export default async function initTable() {
    const functionName = "initTable.js";
    log("info", scriptName, functionName, "🚀 Starting table initialization");

    if (!gridDiv) {
        log("error", scriptName, functionName, `⚠️ Grid container with ID '${tableContainerId}' not found.`);
        return;
    }

    // Ensure the grid container has a defined height
    log("debug", scriptName, functionName, `Grid container style check - height: ${gridDiv.style.height}, has theme class: ${gridDiv.classList.contains('ag-theme-alpine')}`);

    if (!gridDiv.style.height && !gridDiv.classList.contains('ag-theme-alpine')) {
        log("info", scriptName, functionName, "Applying default height and theme to grid container");
        gridDiv.style.height = '500px';
        gridDiv.classList.add('ag-theme-alpine');
    }

    // Directly read the API URL from the data attribute of the container
    const data_api_url = gridDiv.dataset.apiUrl || null;
    log("info", scriptName, functionName, `Fetching data from API: ${data_api_url}`);

    let actualData;
    try {
        const rawData = await fetchApiDataFromContainer(tableContainerId);
        log("debug", scriptName, functionName, `Raw data retrieved, size: ${JSON.stringify(rawData).length} bytes`);
        log("info", scriptName, functionName, "Normalizing data");
        actualData = normalizeData(rawData);
        log("info", scriptName, functionName, `Setting grid data with ${actualData.length} rows`);
        if (actualData.length > 0) {
            log("debug", scriptName, functionName, `Data sample (first row): ${JSON.stringify(actualData[0])}`);
        }
    } catch (error) {
        log("error", scriptName, functionName, "❌ Failed to fetch or process data", {
            error: error.message || String(error),
            stack: error.stack
        });
        return;
    }

    log("info", scriptName, functionName, "Getting grid options");
    const gridOptions = getGridOptions();
    log("debug", scriptName, functionName, "Grid options retrieved successfully", { options: gridOptions });

    if (actualData.length > 0) {
        log("info", scriptName, functionName, "Generating column definitions");
        gridOptions.columnDefs = generateColumnDefs(actualData);
        log("debug", scriptName, functionName, `Column definitions generated: ${gridOptions.columnDefs.length} columns`);

        // Make columnDefs globally available
        window.columnDefs = gridOptions.columnDefs;
    } else {
        log("warn", scriptName, functionName, "No data available to generate columns");
    }

    const originalOnGridReady = gridOptions.onGridReady;
    log("debug", scriptName, functionName, `Original onGridReady handler exists: ${!!originalOnGridReady}`);

    gridOptions.onGridReady = (params) => {
        log("info", scriptName, functionName, "AG Grid onGridReady event triggered");
        if (originalOnGridReady) {
            log("debug", scriptName, functionName, "Calling original onGridReady handler");
            originalOnGridReady(params);
        }

        log("debug", scriptName, functionName, "Setting grid API references");
        setGridApi(params.api, params.columnApi);

        // Store grid API globally
        window.gridApi = params.api;

        log("info", scriptName, functionName, `Setting grid data with ${actualData.length} rows`);
        params.api.setGridOption('rowData', actualData);

        log("info", scriptName, functionName, "Setting up global search functionality");
        setupGlobalSearch(params.api, scriptName, functionName);

        // Initial setup of column selector
        log("info", scriptName, functionName, "Setting up column selector");
        setupColumnSelector(params.api, scriptName, functionName);

        // Add the grid columns changed listener for future updates
        params.api.addEventListener('gridColumnsChanged', () => {
            log("debug", scriptName, functionName, "Grid columns changed event triggered");
            setupColumnSelector(params.api, scriptName, functionName);
        });

        log("debug", scriptName, functionName, "Refreshing grid header");
        params.api.refreshHeader();
        log("info", scriptName, functionName, "Table data initialized successfully");
    };

    log("info", scriptName, functionName, "Creating AG Grid instance");
    try {
        new createGrid(gridDiv, gridOptions);
        log("info", scriptName, functionName, "AG Grid instance created successfully");
    } catch (error) {
        log("error", scriptName, functionName, "Failed to create AG Grid instance", {
            error: error.message || String(error),
            stack: error.stack
        });
        throw error;
    }

    log("info", scriptName, functionName, "Table initialization completed");
    return gridOptions;
}