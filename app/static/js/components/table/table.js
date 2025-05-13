/**
 * table.js - Consolidated AG Grid table implementation for server-rendered data.
 */

import log from '/static/js/core/logger.js';
const scriptName = "table.js";

import { normalizeData } from '/static/js/services/apiService.js';
import { createGrid, ModuleRegistry, ClientSideRowModelModule } from 'https://cdnjs.cloudflare.com/ajax/libs/ag-grid/31.0.1/ag-grid-community.esm.min.js';

// Import modules
import { debounce, fixLayoutSpacing, handleGridResize } from './tableUtils.js';
import { cellRenderers, generateColumnDefs } from './tableRenderers.js';
import { getEditModeState, toggleEditMode, setupModeToggleButtons, columnStateHelpers } from './tableState.js';
import { setupGlobalSearch, setupColumnSelector, addTableStyles } from './tableUI.js';
import { getGridOptions } from './tableGrid.js';

// Global variables
let gridApiReference = null;
let columnApiReference = null;
const tableContainerId = "table-container";
window.__tableInitialized = window.__tableInitialized || false;
window.gridApi = null;

// Initialize module registry
log("info", scriptName, "module", "Starting table initialization module");
ModuleRegistry.registerModules([ClientSideRowModelModule]);
log("info", scriptName, "module", "AG Grid modules registered successfully");

// Add required styles
addTableStyles();

// Create debounced save function once
const debouncedSaveColumnState = debounce(() => {
  log("debug", scriptName, "debouncedSaveColumnState", "Executing debounced save");
  columnStateHelpers.save(gridApiReference);
}, 300);

/**
 * Set up the APIs and register events
 */
function setUpApis(api, columnApi) {
  log("info", scriptName, "setUpApis", "Setting grid APIs");
  gridApiReference = api;
  columnApiReference = columnApi;
  window.gridApi = api;

  // Register all events at once
  const events = [
    'columnMoved', 'columnResized', 'columnVisible', 'columnPinned',
    'sortChanged', 'filterChanged', 'columnRowGroupChanged',
    'columnValueChanged', 'dragStopped', 'gridColumnsChanged'
  ];

  events.forEach(eventName => {
    api.addEventListener(eventName, () => {
      if (eventName === 'gridColumnsChanged') {
        setupColumnSelector(api);
      } else if (eventName === 'columnVisible') {
        // Handle resize explicitly when column visibility changes
        handleGridResize(gridApiReference);
      } else {
        log("debug", scriptName, "eventHandler", `Event triggered: ${eventName}`);
      }
      debouncedSaveColumnState();
    });
  });

  log("info", scriptName, "setUpApis", "Event listeners registered");
  columnStateHelpers.restore(gridApiReference);

  // Setup mode toggle buttons after API is initialized
  setupModeToggleButtons(gridApiReference);
}

/**
 * Main table initialization function optimized for server-rendered data
 */
async function initializeTable() {
  log("info", scriptName, "initTable", "🚀 Starting table init");

  // Get and prepare container
  const gridDiv = document.querySelector(`#${tableContainerId}`);
  if (!gridDiv) {
    const error = new Error(`⚠️ Container #${tableContainerId} not found`);
    log("error", scriptName, "initTable", error.message);
    return Promise.reject(error);
  }

  // Apply default styles if needed
  if (!gridDiv.style.height && !gridDiv.classList.contains('ag-theme-alpine')) {
    log("info", scriptName, "initTable", "Applying default height/theme");
    gridDiv.style.height = '500px';
    gridDiv.classList.add('ag-theme-alpine');
  }

  // Get data from the data attribute set by Jinja template
  let tableData = [];
  try {
    // Extract data from the data-table-data attribute
    const rawData = gridDiv.dataset.tableData;
    if (rawData) {
      tableData = JSON.parse(rawData);
      log("info", scriptName, "initTable", `Loaded server-side data: ${tableData.length} rows`);

      // Normalize the data if needed
      if (tableData.length > 0) {
        tableData = normalizeData(tableData);
        log("info", scriptName, "initTable", "Data normalized successfully");
      }
    } else {
      log("warn", scriptName, "initTable", "No table data found in data-table-data attribute");
    }
  } catch (err) {
    log("error", scriptName, "initTable", "Failed to parse server-side data", err);
    return Promise.reject(new Error(`Failed to parse table data: ${err.message}`));
  }

  // Create grid options with the data
  const gridOptions = getGridOptions();

  // Set up onGridReady handler
  gridOptions.onGridReady = params => {
    log("info", scriptName, "onGridReady", "Grid API initialized");
    setUpApis(params.api, params.columnApi);
    setupGlobalSearch(params.api);
    setupColumnSelector(params.api);

    // Ensure grid fits all columns initially
    if (params.api) {
      setTimeout(() => params.api.sizeColumnsToFit(), 0);
    }

    // Initialize in view mode
    setTimeout(() => toggleEditMode('view', gridApiReference), 0);
  };

  // Set column definitions and row data if we have data
  if (tableData && tableData.length) {
    gridOptions.columnDefs = generateColumnDefs(tableData, getEditModeState(), cellRenderers);
    window.columnDefs = gridOptions.columnDefs;
    gridOptions.rowData = tableData;
  } else {
    log("warn", scriptName, "initTable", "No data available for column generation");
    gridOptions.columnDefs = [];
    gridOptions.rowData = [];
  }

  // Create grid
  try {
    const grid = new createGrid(gridDiv, gridOptions);
    log("info", scriptName, "initTable", "AG Grid created successfully");
  } catch (err) {
    log("error", scriptName, "initTable", "Grid creation failed", err);
    return Promise.reject(err);
  }

  log("info", scriptName, "initTable", "Table initialization completed");
  return Promise.resolve(gridOptions);
}

// Export public functions
export function getGridApi() {
  return gridApiReference;
}

export function getColumnApi() {
  return columnApiReference;
}

export function manualSaveColumnState() {
  return columnStateHelpers.save(gridApiReference);
}

// Export mode toggle function
export function setEditMode(enabled) {
  toggleEditMode(enabled ? 'edit' : 'view', gridApiReference);
}

// Bootstrap code - run once
if (!window.__tableInitialized) {
  window.__tableInitialized = true;
  document.addEventListener('DOMContentLoaded', () => {
    log("info", scriptName, "DOMContentLoaded", "Initializing table...");
    initializeTable()
      .then(() => {
        log("info", scriptName, "DOMContentLoaded", "Table initialization completed successfully");
        fixLayoutSpacing(gridApiReference); // Call layout spacing fix after table init
      })
      .catch(error => {
        log("error", scriptName, "DOMContentLoaded", "Table initialization failed:", error);
        // Display error to user
        const container = document.querySelector('#table-container');
        if (container) {
          container.innerHTML = `<div class="alert alert-danger m-3">Error loading table: ${error.message}</div>`;
        }
      });
  });
}

// Global error handler
window.addEventListener('error', function(e) {
  log("error", "global", "uncaught", `Script error: ${e.message} in ${e.filename} line ${e.lineno}`);
  const container = document.querySelector('#table-container');
  if (container) {
    container.innerHTML = `<div class="alert alert-danger m-3">Error loading table: ${e.message}</div>`;
  }
});

export default initializeTable;