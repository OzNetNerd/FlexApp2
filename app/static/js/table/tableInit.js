// table/tableInit.js

const scriptName = "tableInit.js";

import log from '/static/js/logger.js';
import { getDatasetVariables, getDatasetValue } from '/static/js/utils.js';
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

/**
 * Sets up the global search input to filter the AG Grid.
 */
function setupGlobalSearch(api, scriptName, functionName) {
    log("info", scriptName, functionName, "Setting up global search functionality");

    const input = document.getElementById('globalSearch');
    if (input) {
        log("info", scriptName, functionName, "Global search input found, attaching event listener");
        input.addEventListener('input', () => {
            // Use the AG Grid quick filter method
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
    const previousCheckboxes = columnSelector.querySelectorAll('.form-check');
    log("debug", scriptName, functionName, `Removing ${previousCheckboxes.length} existing column checkboxes`);
    previousCheckboxes.forEach(el => el.remove());

    // In AG Grid 31.0.1, columnApi was merged into the main api
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
            <input class="form-check-input" type="checkbox" value="${colId}" id="chk-${colId}" ${
            isVisible ? 'checked' : ''
        }>
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
    } else {
        log("warn", scriptName, functionName, "📋 Select all button (#selectAllColumns) not found");
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
    } else {
        log("warn", scriptName, functionName, "📋 Clear all button (#clearAllColumns) not found");
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
        return {
            field: key,
            headerName: headerName,
            sortable: true,
            filter: true
        };
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
        gridDiv.style.height = '500px'; // Default height if none specified
        gridDiv.classList.add('ag-theme-alpine'); // Add theme class if missing
    }

    let actualData;
    try {
        // Get data API URL from the dataset attribute or fallback to default
        const data_api_url = getDatasetValue(gridDiv, 'apiUrl', null);
        log("info", scriptName, functionName, `Fetching data from API: ${data_api_url}`);

        // Get data from API using our new service
        const rawData = await fetchApiDataFromContainer(tableContainerId);
        log("debug", scriptName, functionName, `Raw data retrieved, size: ${JSON.stringify(rawData).length} bytes`);

        // Process the data
        log("info", scriptName, functionName, "Normalizing data");
        actualData = normalizeData(rawData);
        log("info", scriptName, functionName, `Processed ${actualData.length} rows of data`);

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

    // Generate column definitions from data
    if (actualData.length > 0) {
        log("info", scriptName, functionName, "Generating column definitions");
        gridOptions.columnDefs = generateColumnDefs(actualData);
        log("debug", scriptName, functionName, `Column definitions generated: ${gridOptions.columnDefs.length} columns`);
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

        // Pass the correct grid and column APIs
        log("debug", scriptName, functionName, "Setting grid API references");
        setGridApi(params.api, params.columnApi);

        // Update rowData using the recommended setGridOption method
        log("info", scriptName, functionName, `Setting grid data with ${actualData.length} rows`);
        params.api.setGridOption('rowData', actualData);

        log("info", scriptName, functionName, "Setting up global search functionality");
        setupGlobalSearch(params.api, scriptName, functionName);

        // Setup column selector after columns are fully initialized
        // Use grid columns changed event to ensure columns are ready
        log("info", scriptName, functionName, "Adding grid columns changed event listener");
        params.api.addEventListener('gridColumnsChanged', () => {
            log("debug", scriptName, functionName, "Grid columns changed event triggered");

            // Check if the column selector element exists in the DOM
            const columnSelectorExists = document.getElementById('columnSelectorItems');
            if (columnSelectorExists) {
                log("info", scriptName, functionName, "Setting up column selector");
                // In AG Grid 31.0.1, we pass the main grid API instead of columnApi
                setupColumnSelector(params.api, scriptName, functionName);
            } else {
                log("warn", scriptName, functionName, "📋 Column selector element (#columnSelectorItems) not found. Skipping column selector setup.");
            }
        });

        // Force column visibility update
        log("debug", scriptName, functionName, "Refreshing grid header");
        params.api.refreshHeader();

        log("info", scriptName, functionName, "Table data initialized successfully");
    };

    // Create the grid with proper dimensions
    log("info", scriptName, functionName, "Creating AG Grid instance");
    try {
        new createGrid(gridDiv, gridOptions);
        log("info", scriptName, functionName, "AG Grid instance created successfully");
    } catch (error) {
        log("error", scriptName, functionName, "Failed to create AG Grid instance", {
            error: error.message || String(error),
            stack: error.stack
        });
        throw error; // Re-throw to allow caller to handle
    }

    log("info", scriptName, functionName, "Table initialization completed");
    return gridOptions;
}