const scriptName = "tableInit.js";

import log from '/static/js/core/logger.js';
import { getDatasetVariables } from '/static/js/core/utils.js';
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

    if (!columnSelector || !api) {
        log("warn", scriptName, functionName, "Column selector elements or grid API not found");
        return;
    }

    // Clear any previously inserted checkboxes
    columnSelector.innerHTML = '';

    // Add container styling
    columnSelector.style.maxHeight = '300px';
    columnSelector.style.overflowY = 'auto';
    columnSelector.style.padding = '0 10px';

    // Get all columns
    const allColumns = api.getColumns();
    if (!allColumns || allColumns.length === 0) {
        log("warn", scriptName, functionName, "No columns found in the grid");
        return;
    }

    // Add custom styling to override any problematic CSS
    const styleEl = document.createElement('style');
    styleEl.textContent = `
        .column-selector-item {
            display: flex;
            align-items: center;
            margin: 8px 0;
            padding: 4px;
            border-radius: 4px;
            background: white;
            border: none;
        }
        .column-selector-checkbox {
            margin-right: 10px;
            min-width: 16px;
            min-height: 16px;
        }
        .column-selector-label {
            margin-bottom: 0;
            cursor: pointer;
            user-select: none;
        }
    `;
    document.head.appendChild(styleEl);

    allColumns.forEach(col => {
        const colId = col.getColId ? col.getColId() : col.getId();
        const colDef = col.getColDef();
        const colName = (colDef.headerName || colId)
            .replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase())
            .replace(/\bId\b/g, 'ID')
            .replace(/\bAt\b/g, 'at');

        const isVisible = !(api.getColumnState().find(c => c.colId === colId)?.hide === true);

        // Create container div with custom class instead of form-check
        const div = document.createElement('div');
        div.className = 'column-selector-item';

        // Create checkbox with custom class
        const input = document.createElement('input');
        input.type = 'checkbox';
        input.className = 'column-selector-checkbox';
        input.id = `chk-${colId}`;
        input.value = colId;
        input.checked = isVisible;

        // Create label with custom class
        const label = document.createElement('label');
        label.className = 'column-selector-label';
        label.htmlFor = `chk-${colId}`;
        label.textContent = colName;

        // Add event listener
        input.addEventListener('change', (e) => {
            api.setColumnVisible(colId, e.target.checked);
        });

        div.appendChild(input);
        div.appendChild(label);
        columnSelector.appendChild(div);
    });

    // Setup select/clear all buttons
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            allColumns.forEach(col => {
                const colId = col.getColId ? col.getColId() : col.getId();
                api.setColumnVisible(colId, true);
                const checkbox = document.getElementById(`chk-${colId}`);
                if (checkbox) checkbox.checked = true;
            });
        });
    }

    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', () => {
            allColumns.forEach(col => {
                const colId = col.getColId ? col.getColId() : col.getId();
                api.setColumnVisible(colId, false);
                const checkbox = document.getElementById(`chk-${colId}`);
                if (checkbox) checkbox.checked = false;
            });
        });
    }
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

    // ensure container has height + theme…
    if (!gridDiv.style.height && !gridDiv.classList.contains('ag-theme-alpine')) {
        log("info", scriptName, functionName, "Applying default height and theme to grid container");
        gridDiv.style.height = '500px';
        gridDiv.classList.add('ag-theme-alpine');
    }

    // fetch
    let actualData;
    try {
        const rawData = await fetchApiDataFromContainer(tableContainerId);
        log("debug", scriptName, functionName, `Raw payload: ${JSON.stringify(rawData).substring(0,200)}…`);

        // ── NEW: pull out the real array at rawData.data.data ──
        const extracted = Array.isArray(rawData?.data?.data)
          ? rawData.data.data
          : Array.isArray(rawData?.data)
            ? rawData.data
            : [];
        log("debug", scriptName, functionName, `Extracted ${extracted.length} rows for normalization`);

        actualData = normalizeData(extracted);
        log("info", scriptName, functionName, `Normalization complete; ${actualData.length} rows ready`);
    } catch (error) {
        log("error", scriptName, functionName, "❌ Failed to fetch or process data", {
            error: error.message || String(error),
            stack: error.stack
        });
        return;
    }

    // … the rest of your code stays exactly the same …
    log("info", scriptName, functionName, "Getting grid options");
    const gridOptions = getGridOptions();

    if (actualData.length > 0) {
        log("info", scriptName, functionName, "Generating column definitions");
        gridOptions.columnDefs = generateColumnDefs(actualData);
        window.columnDefs = gridOptions.columnDefs;
    } else {
        log("warn", scriptName, functionName, "No data available to generate columns");
    }

    const originalOnGridReady = gridOptions.onGridReady;
    gridOptions.onGridReady = params => {
        if (originalOnGridReady) originalOnGridReady(params);
        setGridApi(params.api, params.columnApi);
        window.gridApi = params.api;
        params.api.setGridOption('rowData', actualData);
        setupGlobalSearch(params.api, scriptName, functionName);
        setupColumnSelector(params.api, scriptName, functionName);
        params.api.addEventListener('gridColumnsChanged', () =>
          setupColumnSelector(params.api, scriptName, functionName)
        );
        params.api.refreshHeader();
        log("info", scriptName, functionName, "Table data initialized successfully");
    };

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
