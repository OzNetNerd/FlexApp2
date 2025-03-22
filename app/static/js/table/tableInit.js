// table/tableInit.js

import { createGrid, ModuleRegistry } from 'https://cdnjs.cloudflare.com/ajax/libs/ag-grid/31.0.1/ag-grid-community.esm.min.js';
import { ClientSideRowModelModule } from 'https://cdnjs.cloudflare.com/ajax/libs/ag-grid/31.0.1/ag-grid-community.esm.min.js';

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const scriptName = "tableInit";

import log from '../logger.js';
import { getDatasetVariables, getDatasetValue, fetchApiData } from '../utils.js';
import getGridOptions, { setGridApi } from './tableConfig.js';

const tableContainerId = "table-container";
const gridDiv = document.querySelector(`#${tableContainerId}`);

/**
 * Sets up the global search input to filter the AG Grid.
 */
function setupGlobalSearch(api, scriptName, functionName) {
    const input = document.getElementById('globalSearch');
    if (input) {
        input.addEventListener('input', () => {
            api.setGridOption('quickFilterText', input.value);
        });
    } else {
        log("warn", scriptName, functionName, "🔍 Search input (#globalSearch) not found.");
    }
}

/**
 * Sets up the column selector dropdown for toggling column visibility.
 */
function setupColumnSelector(api, scriptName, functionName) {
    const columnSelector = document.getElementById('columnSelector');
    const selectAllBtn = document.getElementById('selectAllColumns');
    const clearAllBtn = document.getElementById('clearAllColumns');

    if (!columnSelector || !api) {
        log("warn", scriptName, functionName, "📋 Column selector or grid API not available");
        return;
    }

    // Clear any previously inserted checkboxes
    columnSelector.querySelectorAll('li.form-check').forEach(el => el.remove());

    const allColumns = api.getColumns();

    allColumns.forEach(col => {
        const colId = col.colId;
        const colName = col.colDef.headerName || colId;

        const li = document.createElement('li');
        li.classList.add('form-check');

        li.innerHTML = `
            <input class="form-check-input" type="checkbox" value="${colId}" id="chk-${colId}" ${
            col.visible ? 'checked' : ''
        }>
            <label class="form-check-label" for="chk-${colId}">${colName}</label>
        `;

        const input = li.querySelector('input');
        input.addEventListener('change', (e) => {
            api.setColumnVisible(colId, e.target.checked);
        });

        columnSelector.appendChild(li);
    });

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            allColumns.forEach(col => {
                api.setColumnVisible(col.colId, true);
                const checkbox = document.getElementById(`chk-${col.colId}`);
                if (checkbox) checkbox.checked = true;
            });
        });
    }

    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', () => {
            allColumns.forEach(col => {
                api.setColumnVisible(col.colId, false);
                const checkbox = document.getElementById(`chk-${col.colId}`);
                if (checkbox) checkbox.checked = false;
            });
        });
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

    const datasetVariables = getDatasetVariables(tableContainerId);
    const apiUrl = getDatasetValue(scriptName, datasetVariables, "apiUrl");
    log("info", scriptName, functionName, `✅🌐 API URL Retrieved: ${apiUrl}`);

    let data;
    try {
        data = await fetchApiData(scriptName, functionName, apiUrl);
        log("info", scriptName, functionName, `✅📥 API data received: `, data);
    } catch (error) {
        log("error", scriptName, functionName, "❌ Failed to fetch data from API", { error: error.message || String(error) });
        return;
    }

    const gridOptions = getGridOptions();

    if (data?.data?.[0]) {
        const sampleRow = data.data[0];
        const columnDefs = Object.keys(sampleRow).map(key => ({
            field: key,
            headerName: key.replace(/_/g, ' ').toUpperCase(),
            sortable: true,
            filter: true
        }));
        gridOptions.columnDefs = columnDefs;
    }

    const originalOnGridReady = gridOptions.onGridReady;

    gridOptions.onGridReady = (params) => {
        if (originalOnGridReady) {
            originalOnGridReady(params);
        }

        setGridApi(params.api, params.api); // passing api as both gridApi and columnApi for compatibility
        params.api.setGridOption('rowData', data.data || data);

        setupGlobalSearch(params.api, scriptName, functionName);
        setupColumnSelector(params.api, scriptName, functionName);

        log("info", scriptName, functionName, "✅ Table data initialized successfully");
    };

    new createGrid(gridDiv, gridOptions);

    return gridOptions;
}
