// table/tableInit.js

const scriptName = "tableInit.js";

import log from '/static/js/logger.js';
import { getDatasetVariables, getDatasetValue, fetchApiData } from '../utils.js';
import getGridOptions, { setGridApi } from './tableConfig.js';

import { createGrid, ModuleRegistry } from 'https://cdnjs.cloudflare.com/ajax/libs/ag-grid/31.0.1/ag-grid-community.esm.min.js';
import { ClientSideRowModelModule } from 'https://cdnjs.cloudflare.com/ajax/libs/ag-grid/31.0.1/ag-grid-community.esm.min.js';

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const tableContainerId = "table-container";
const gridDiv = document.querySelector(`#${tableContainerId}`);

/**
 * Sets up the global search input to filter the AG Grid.
 */
function setupGlobalSearch(api, scriptName, functionName) {
    const input = document.getElementById('globalSearch');
    if (input) {
        input.addEventListener('input', () => {
            // Use the AG Grid quick filter method
            api.setQuickFilter(input.value);
        });
    } else {
        log("warn", scriptName, functionName, "🔍 Search input (#globalSearch) not found.");
    }
}

/**
 * Sets up the column selector dropdown for toggling column visibility.
 */
function setupColumnSelector(api, scriptName, functionName) {
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
    columnSelector.querySelectorAll('.form-check').forEach(el => el.remove());

    // In AG Grid 31.0.1, columnApi was merged into the main api
    const allColumns = api.getColumns();

    if (!allColumns || allColumns.length === 0) {
        log("warn", scriptName, functionName, "No columns found in the grid");
        return;
    }

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

        div.innerHTML = `
            <input class="form-check-input" type="checkbox" value="${colId}" id="chk-${colId}" ${
            api.getColumnState().find(c => c.colId === colId)?.hide === true ? '' : 'checked'
        }>
            <label class="form-check-label" for="chk-${colId}">${colName}</label>
        `;

        const checkbox = div.querySelector('input');
        checkbox.addEventListener('change', (e) => {
            api.setColumnVisible(colId, e.target.checked);
        });

        columnSelector.appendChild(div);
    });

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
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
        clearAllBtn.addEventListener('click', () => {
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
}

/**
 * Initializes the AG Grid table and applies search + column toggle functionality.
 */
export default async function initTable() {
    const functionName = "initTable";

    if (!gridDiv) {
        log("error", scriptName, functionName, `⚠️ Grid container with ID '${tableContainerId}' not found.`);
        return;
    }

    // Ensure the grid container has a defined height
    if (!gridDiv.style.height && !gridDiv.classList.contains('ag-theme-alpine')) {
        gridDiv.style.height = '500px'; // Default height if none specified
        gridDiv.classList.add('ag-theme-alpine'); // Add theme class if missing
    }

    const datasetVariables = getDatasetVariables(tableContainerId);
    const apiUrl = getDatasetValue(scriptName, datasetVariables, "apiUrl");
    log("info", scriptName, functionName, `✅🌐 API URL Retrieved: ${apiUrl}`);

    let data;
    try {
        // Get data from API
        data = await fetchApiData(scriptName, functionName, apiUrl);
        // Log the actual data for debugging
        log("info", scriptName, functionName, "📊 Table data structure:", data);
    } catch (error) {
        log("error", scriptName, functionName, "❌ Failed to fetch data from API", { error: error.message || String(error) });
        return;
    }

    const gridOptions = getGridOptions();

    // Handle both data structures: data = [{...}] or data = {data: [{...}]}
    let actualData = Array.isArray(data) ? data : (data.data || []);
    let sampleRow = actualData[0];

    if (sampleRow) {
        const columnDefs = Object.keys(sampleRow).map(key => ({
            field: key,
            headerName: formatColumnHeader(key),
            sortable: true,
            filter: true
        }));
        gridOptions.columnDefs = columnDefs;
    } else {
        log("warn", scriptName, functionName, "No data available to generate columns");
    }

    // Function to format column header text consistently
    function formatColumnHeader(headerText) {
        return headerText
            .replace(/_/g, ' ') // Replace underscores with spaces
            .replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()) // Capitalize first letter
            .replace(/\bId\b/g, 'ID') // Make "Id" into "ID"
            .replace(/\bAt\b/g, 'at'); // Make "At" into "at"
    }

    const originalOnGridReady = gridOptions.onGridReady;

    gridOptions.onGridReady = (params) => {
        if (originalOnGridReady) {
            originalOnGridReady(params);
        }

        // Pass the correct grid and column APIs
        setGridApi(params.api, params.columnApi);

        // Update rowData using the recommended setGridOption method
        params.api.setGridOption('rowData', actualData);

        setupGlobalSearch(params.api, scriptName, functionName);

        // Setup column selector after columns are fully initialized
        // Use grid columns changed event to ensure columns are ready
        params.api.addEventListener('gridColumnsChanged', () => {
            // Check if the column selector element exists in the DOM
            const columnSelectorExists = document.getElementById('columnSelectorItems');
            if (columnSelectorExists) {
                // In AG Grid 31.0.1, we pass the main grid API instead of columnApi
                setupColumnSelector(params.api, scriptName, functionName);
            } else {
                log("warn", scriptName, functionName, "📋 Column selector element (#columnSelectorItems) not found. Skipping column selector setup.");
            }
        });

        // Force column visibility update
        params.api.refreshHeader();

        log("info", scriptName, functionName, "Table data initialized successfully");
    };

    // Create the grid with proper dimensions
    new createGrid(gridDiv, gridOptions);

    return gridOptions;
}