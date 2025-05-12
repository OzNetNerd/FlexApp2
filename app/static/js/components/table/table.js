/**
 * table.js - Consolidated AG Grid table implementation.
 */

import log from '/static/js/core/logger.js';
const scriptName = "table.js";

import { fetchApiDataFromContainer, normalizeData } from '/static/js/services/apiService.js';
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
 * Main table initialization function
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

  // Fetch and process data
  let actualData;
  try {
    const raw = await fetchApiDataFromContainer(tableContainerId);
    log("debug", scriptName, "initTable", "Raw data received");

    const arr = Array.isArray(raw?.data?.data) ? raw.data.data :
               Array.isArray(raw?.data) ? raw.data : [];

    log("debug", scriptName, "initTable", `Rows extracted: ${arr.length}`);
    actualData = normalizeData(arr);
    log("info", scriptName, "initTable", `Normalized rows: ${actualData.length}`);
  } catch (err) {
    log("error", scriptName, "initTable", "❌ Fetch/process failed", err);
    return Promise.reject(err);
  }

  // Create grid options with data
  const gridOptions = getGridOptions(getEditModeState());

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

  if (actualData && actualData.length) {
    gridOptions.columnDefs = generateColumnDefs(actualData, getEditModeState(), cellRenderers);
    window.columnDefs = gridOptions.columnDefs;
    gridOptions.rowData = actualData;
  } else {
    log("warn", scriptName, "initTable", "No data for columns");
  }

  // Create grid
  try {
    const grid = new createGrid(gridDiv, gridOptions);
    log("info", scriptName, "initTable", "AG Grid created");
  } catch (err) {
    log("error", scriptName, "initTable", "Grid creation failed", err);
    return Promise.reject(err);
  }

  log("info", scriptName, "initTable", "Table init completed");
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