/**
 * table.js
 * Combined module: configuration, utilities, initialization, and bootstrap.
 * Merges tableConfig.js, tableInit.js, tableUtils.js, and original table.js into one file.
 */

import log from '/static/js/core/logger.js';
import { fetchApiDataFromContainer, normalizeData, formatDisplayText } from '/static/js/services/apiService.js';
import { createGrid, ModuleRegistry } from 'https://cdnjs.cloudflare.com/ajax/libs/ag-grid/31.0.1/ag-grid-community.esm.min.js';
import { ClientSideRowModelModule } from 'https://cdnjs.cloudflare.com/ajax/libs/ag-grid/31.0.1/ag-grid-community.esm.min.js';

const scriptName = "table.js";

// --- Configuration (from tableConfig.js) ---

let gridApiReference = null;
let columnApiReference = null;
let columnStateInitialized = false;

/**
 * Set the AG Grid and Column APIs, register events, and restore state.
 * @param {Object} api
 * @param {Object} columnApi
 */
export function setGridApi(api, columnApi) {
  gridApiReference = api;
  columnApiReference = columnApi;
  log("info", scriptName, "setGridApi", "Grid APIs externally set");
  registerEvents();
  restoreColumnState();
}

/**
 * @returns {Object|null}
 */
export function getGridApi() {
  return gridApiReference;
}

/**
 * @returns {Object|null}
 */
export function getColumnApi() {
  return columnApiReference;
}

/**
 * Debounce helper
 */
function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

/**
 * Register grid events to auto-save column state
 */
function registerEvents() {
  if (!gridApiReference) {
    log("warn", scriptName, "registerEvents", "Cannot register events - API not available");
    return false;
  }
  try {
    const events = [
      'columnMoved', 'columnResized', 'columnVisible', 'columnPinned',
      'sortChanged', 'filterChanged', 'columnRowGroupChanged',
      'columnValueChanged', 'dragStopped'
    ];
    events.forEach(eventName => {
      gridApiReference.addEventListener(eventName, () => {
        log("debug", scriptName, "eventHandler", `Event triggered: ${eventName}`);
        debouncedSaveColumnState();
      });
    });
    log("info", scriptName, "registerEvents", "Column event listeners registered successfully");
    return true;
  } catch (e) {
    log("error", scriptName, "registerEvents", "Error registering event listeners:", e);
    return false;
  }
}

/**
 * Restore column state from localStorage
 */
function restoreColumnState() {
  if (!gridApiReference) {
    log("warn", scriptName, "restoreColumnState", "Cannot restore state - API not available");
    return false;
  }
  try {
    const saved = localStorage.getItem("agGridColumnState");
    if (saved) {
      const columnState = JSON.parse(saved);
      if (Array.isArray(columnState) && columnState.length > 0) {
        log("info", scriptName, "restoreColumnState", `Restoring state with ${columnState.length} columns`);
        gridApiReference.applyColumnState({ state: columnState, applyOrder: true });
        columnStateInitialized = true;
        log("info", scriptName, "restoreColumnState", "Column state successfully restored");
        return true;
      } else {
        log("warn", scriptName, "restoreColumnState", "Invalid saved column state format");
      }
    } else {
      log("info", scriptName, "restoreColumnState", "No saved column state found");
    }
  } catch (e) {
    log("error", scriptName, "restoreColumnState", "Error restoring column state:", e);
  }
  return false;
}

/**
 * Manually trigger save
 */
export function manualSaveColumnState() {
  return saveColumnState();
}

/**
 * Save current column state to localStorage
 */
function saveColumnState() {
  if (!gridApiReference) {
    log("warn", scriptName, "saveColumnState", "Grid API not initialized, cannot save column state");
    return false;
  }
  try {
    const state = gridApiReference.getColumnState();
    if (Array.isArray(state) && state.length > 0) {
      localStorage.setItem("agGridColumnState", JSON.stringify(state));
      log("info", scriptName, "saveColumnState", `💾 Saved column state with ${state.length} columns`);
      return true;
    } else {
      log("warn", scriptName, "saveColumnState", "No valid column state to save");
      return false;
    }
  } catch (e) {
    log("error", scriptName, "saveColumnState", "Error saving column state:", e);
    return false;
  }
}

const debouncedSaveColumnState = debounce(() => {
  log("debug", scriptName, "debouncedSaveColumnState", "Executing debounced save");
  saveColumnState();
}, 300);

/**
 * Default grid options factory
 */
export function getGridOptions() {
  return {
    columnDefs: [], rowData: [], maintainColumnOrder: true,
    pagination: true, enableCellTextSelection: true,
    enableBrowserTooltips: true, suppressCopyRowsToClipboard: false,
    suppressCellFocus: true, suppressRowClickSelection: false,
    rowSelection: 'single', paginationPageSize: 20,
    domLayout: 'autoHeight', suppressColumnVirtualisation: false,
    animateRows: true,
    defaultColDef: { flex: 1, minWidth: 100, resizable: true, wrapText: true, autoHeight: true },
    onRowClicked: event => {
      if (event.event.ctrlKey || event.event.metaKey || event.event.shiftKey || event.event.button !== 0) return;
      const id = event.data?.id;
      if (!id) return;
      const basePath = window.location.pathname.split('/')[1];
      if (basePath) window.location.href = `/${basePath}/${id}`;
    },
    onGridReady: params => {
      gridApiReference = params.api;
      columnApiReference = params.columnApi;
      log("info", scriptName, "onGridReady", "Grid API initialized in tableConfig");
    },
    onFirstDataRendered: params => {
      if (!gridApiReference) {
        log("info", scriptName, "onFirstDataRendered", "Fallback API init");
        gridApiReference = params.api;
        columnApiReference = params.columnApi;
        registerEvents(); restoreColumnState();
        setTimeout(() => {
          const ok = saveColumnState();
          log("info", scriptName, "onFirstDataRendered", `Fallback save: ${ok ? 'SUCCESS':'FAILED'}`);
        }, 200);
      }
    },
    onColumnMoved: () => debouncedSaveColumnState(),
    onColumnResized: () => debouncedSaveColumnState(),
    onColumnVisible: () => debouncedSaveColumnState(),
    onColumnPinned: () => debouncedSaveColumnState(),
    onSortChanged: () => debouncedSaveColumnState(),
    onFilterChanged: () => debouncedSaveColumnState(),
    onColumnRowGroupChanged: () => debouncedSaveColumnState(),
    onColumnValueChanged: () => debouncedSaveColumnState(),
    onDragStopped: () => debouncedSaveColumnState()
  };
}

// --- Utilities (from tableUtils.js) ---

/**
 * Wait for AG Grid to load
 */
export function waitForAgGrid() {
  const functionName = "waitForAgGrid";
  return new Promise((resolve, reject) => {
    try {
      if (typeof Grid !== "undefined") {
        log("info", scriptName, functionName, "AG Grid loaded");
        return resolve(Grid);
      }
      log("info", scriptName, functionName, "⏳ Waiting for AG Grid...");
      const interval = setInterval(() => {
        if (typeof Grid !== "undefined") {
          clearInterval(interval);
          log("info", scriptName, functionName, "AG Grid has loaded.");
          resolve(Grid);
        }
      }, 100);
      setTimeout(() => {
        clearInterval(interval);
        log("error", scriptName, functionName, "❌ AG Grid failed to load after timeout.");
        reject(new Error("AG Grid failed to load"));
      }, 5000);
    } catch (error) {
      log("error", scriptName, functionName, `❌ Error checking AG Grid: ${error.message}`);
      reject(error);
    }
  });
}

/**
 * Load data into the table via AG Grid API
 */
export function loadTableData(data) {
  const functionName = 'loadTableData';
  if (!data || data.length === 0) {
    const error = new Error("❌ No data available for the table.");
    log("error", scriptName, functionName, error.message);
    throw error;
  }
  log("info", scriptName, functionName, `📊 Initializing table with data:`, data);
  try {
    if (gridApiReference) {
      gridApiReference.setRowData(data);
      log("info", scriptName, functionName, "📊 Table initialized with data", data);
      return true;
    } else {
      const error = new Error("❌ AG Grid API not available.");
      log("error", scriptName, functionName, error.message);
      throw error;
    }
  } catch (error) {
    log("error", scriptName, functionName, `❌ Error displaying AG Grid table: ${error.message}`);
    throw error;  // Re-throw to propagate to caller
  }
}

// --- Initialization (from tableInit.js) ---

log("info", scriptName, "module", "Starting table initialization module");
ModuleRegistry.registerModules([ClientSideRowModelModule]);
log("info", scriptName, "module", "AG Grid modules registered successfully");

const tableContainerId = "table-container";
window.gridApi = null;

// Style element for column selector (created once)
const columnSelectorStyle = document.createElement('style');
columnSelectorStyle.textContent = `
  .column-selector-item { display:flex; align-items:center; margin:8px 0; padding:4px; background:white; border-radius:4px; }
  .column-selector-checkbox { margin-right:10px; }
  .column-selector-label { cursor:pointer; user-select:none; }
`;
document.head.appendChild(columnSelectorStyle);

/**
 * Global search setup
 */
function setupGlobalSearch(api) {
  const fn = "setupGlobalSearch";
  log("info", scriptName, fn, "Setting up global search");
  const input = document.getElementById('globalSearch');
  if (input) {
    log("info", scriptName, fn, "Search input found");
    input.addEventListener('input', () => {
      const val = input.value;
      log("debug", scriptName, fn, `Filter: "${val}"`);
      api.setQuickFilter(val);
    });
    log("info", scriptName, fn, "Global search complete");
  } else {
    log("warn", scriptName, fn, "🔍 #globalSearch not found.");
  }
}

/**
 * Formatter for object/array values
 */
function objectValueFormatter(params) {
  if (params.value == null) return '';
  if (Array.isArray(params.value)) {
    return params.value.length ? `${params.value.length} item${params.value.length > 1 ? 's':''}` : '';
  }
  if (typeof params.value === 'object') {
    return `Ref #${params.value}`;
  }
  return params.value;
}

/**
 * Column selector toggle UI
 */
function setupColumnSelector(api) {
  const fn = "setupColumnSelector";
  log("info", scriptName, fn, "Setting up column selector");
  const container = document.getElementById('columnSelectorItems');
  const selectAll = document.getElementById('selectAllColumns');
  const clearAll = document.getElementById('clearAllColumns');
  if (!container || !api) {
    log("warn", scriptName, fn, "Selector elements or API missing");
    return;
  }
  container.innerHTML = '';
  container.style.maxHeight='300px'; container.style.overflowY='auto'; container.style.padding='0 10px';

  const cols = api.getColumns ? api.getColumns() : [];
  if (!Array.isArray(cols)) {
    log("warn", scriptName, fn, "No columns available from API");
    return;
  }

  cols.forEach(col => {
    if (!col) return;

    const colId = typeof col.getColId === 'function' ? col.getColId() :
                 typeof col.getId === 'function' ? col.getId() : null;

    if (!colId) {
      log("warn", scriptName, fn, "Column without ID found, skipping");
      return;
    }

    const def = typeof col.getColDef === 'function' ? col.getColDef() : {};
    const name = (def.headerName || colId).replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase()+txt.substr(1).toLowerCase());

    const columnState = typeof api.getColumnState === 'function' ? api.getColumnState() : [];
    const visible = !(Array.isArray(columnState) && columnState.find(c => c.colId === colId)?.hide);

    const div = document.createElement('div'); div.className='column-selector-item';
    const chk = document.createElement('input'); chk.type='checkbox'; chk.className='column-selector-checkbox'; chk.id=`chk-${colId}`; chk.checked=visible;
    const lbl = document.createElement('label'); lbl.className='column-selector-label'; lbl.htmlFor=`chk-${colId}`; lbl.textContent=name;

    chk.addEventListener('change', e => {
      if (typeof api.setColumnVisible === 'function') {
        api.setColumnVisible(colId, e.target.checked);
      }
    });

    div.append(chk, lbl); container.appendChild(div);
  });

  if (selectAll) {
    selectAll.addEventListener('click', () => {
      cols.forEach(c => {
        const colId = typeof c.getColId === 'function' ? c.getColId() : null;
        if (colId && typeof api.setColumnVisible === 'function') {
          api.setColumnVisible(colId, true);
          const checkbox = document.getElementById(`chk-${colId}`);
          if (checkbox) checkbox.checked = true;
        }
      });
    });
  }

  if (clearAll) {
    clearAll.addEventListener('click', () => {
      cols.forEach(c => {
        const colId = typeof c.getColId === 'function' ? c.getColId() : null;
        if (colId && typeof api.setColumnVisible === 'function') {
          api.setColumnVisible(colId, false);
          const checkbox = document.getElementById(`chk-${colId}`);
          if (checkbox) checkbox.checked = false;
        }
      });
    });
  }
}

/**
 * Generate column definitions based on data
 */
function generateColumnDefs(data) {
  const fn = "generateColumnDefs";
  log("info", scriptName, fn, "Generating columns");
  if (!data || !data.length) {
    log("warn", scriptName, fn, "No data to generate columns");
    return [];
  }
  const keys = Object.keys(data[0]);
  log("debug", scriptName, fn, `Columns found: ${keys}`);
  return keys.map(key => {
    const def = { field: key, headerName: formatDisplayText(key), sortable: true, filter: true };
    if (data[0][key] != null && typeof data[0][key] === 'object') {
      def.valueFormatter = objectValueFormatter;
    }
    return def;
  });
}

/**
 * Main initialization
 */
async function initializeTable() {
  const fn = "initTable";
  log("info", scriptName, fn, "🚀 Starting table init");

  // Get container element
  const gridDiv = document.querySelector(`#${tableContainerId}`);
  if (!gridDiv) {
    const error = new Error(`⚠️ Container #${tableContainerId} not found`);
    log("error", scriptName, fn, error.message);
    return Promise.reject(error);
  }

  if (!gridDiv.style.height && !gridDiv.classList.contains('ag-theme-alpine')) {
    log("info", scriptName, fn, "Applying default height/theme");
    gridDiv.style.height = '500px';
    gridDiv.classList.add('ag-theme-alpine');
  }

  let actualData;
  try {
    const raw = await fetchApiDataFromContainer(tableContainerId);
    log("debug", scriptName, fn, `Raw: ${JSON.stringify(raw).slice(0,100)}…`);
    const arr = Array.isArray(raw?.data?.data) ? raw.data.data :
               Array.isArray(raw?.data) ? raw.data : [];
    log("debug", scriptName, fn, `Rows extracted: ${arr.length}`);
    actualData = normalizeData(arr);
    log("info", scriptName, fn, `Normalized rows: ${actualData.length}`);
  } catch (err) {
    log("error", scriptName, fn, "❌ Fetch/process failed", err);
    return Promise.reject(err);
  }

  const gridOptions = getGridOptions();

  if (actualData && actualData.length) {
    gridOptions.columnDefs = generateColumnDefs(actualData);
    window.columnDefs = gridOptions.columnDefs;
  } else {
    log("warn", scriptName, fn, "No data for columns");
  }

  const orig = gridOptions.onGridReady;
  gridOptions.onGridReady = params => {
    if (typeof orig === 'function') {
      orig(params);
    }
    setGridApi(params.api, params.columnApi);
    window.gridApi = params.api;
    params.api.setRowData(actualData);
    setupGlobalSearch(params.api);
    setupColumnSelector(params.api);
    params.api.addEventListener('gridColumnsChanged', () => setupColumnSelector(params.api));
    params.api.refreshHeader();
    log("info", scriptName, fn, "Table data ready");
  };

  try {
    const grid = new createGrid(gridDiv, gridOptions);
    log("info", scriptName, fn, "AG Grid created");
  } catch (err) {
    log("error", scriptName, fn, "Grid creation failed", err);
    return Promise.reject(err);
  }

  log("info", scriptName, fn, "Table init completed");
  return Promise.resolve(gridOptions);
}

// --- Bootstrap (from original table.js) ---
if (!window.__tableInitialized) {
  window.__tableInitialized = true;
  document.addEventListener('DOMContentLoaded', () => {
    const fn = "DOMContentLoaded";
    log("info", scriptName, fn, "Initializing table and column selector...");
    initializeTable()
      .then(gridOptions => {
        log("info", scriptName, fn, "Table initialization completed successfully");
      })
      .catch(error => {
        log("error", scriptName, fn, "Table initialization failed:", error);
      });
  });
}

export default initializeTable;