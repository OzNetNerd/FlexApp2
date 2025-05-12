/**
 * table.js - Consolidated AG Grid table implementation.
 */

import log from '/static/js/core/logger.js';
const scriptName = "table.js";

import { fetchApiDataFromContainer, normalizeData, formatDisplayText } from '/static/js/services/apiService.js';
import { createGrid, ModuleRegistry, ClientSideRowModelModule } from 'https://cdnjs.cloudflare.com/ajax/libs/ag-grid/31.0.1/ag-grid-community.esm.min.js';

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

// Add column selector styles
document.head.appendChild(Object.assign(document.createElement('style'), {
  textContent: `
    .column-selector-item { display:flex; align-items:center; margin:8px 0; padding:4px; background:white; border-radius:4px; }
    .column-selector-checkbox { margin-right:10px; }
    .column-selector-label { 
      font-family: var(--font-family); 
      font-size: var(--font-size-sm);
      font-weight: var(--font-weight-normal);
      cursor: pointer; 
      user-select: none; 
    }
  `
}));

/**
 * Save/restore column state utilities
 */
const columnStateHelpers = {
  save: function() {
    if (!gridApiReference) {
      log("warn", scriptName, "saveColumnState", "Grid API not initialized");
      return false;
    }
    try {
      const state = gridApiReference.getColumnState();
      if (Array.isArray(state) && state.length > 0) {
        localStorage.setItem("agGridColumnState", JSON.stringify(state));
        log("info", scriptName, "saveColumnState", `💾 Saved column state with ${state.length} columns`);
        return true;
      }
      log("warn", scriptName, "saveColumnState", "No valid column state to save");
      return false;
    } catch (e) {
      log("error", scriptName, "saveColumnState", "Error saving column state:", e);
      return false;
    }
  },

  restore: function() {
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
          log("info", scriptName, "restoreColumnState", "Column state successfully restored");
          return true;
        }
        log("warn", scriptName, "restoreColumnState", "Invalid saved column state format");
      } else {
        log("info", scriptName, "restoreColumnState", "No saved column state found");
      }
    } catch (e) {
      log("error", scriptName, "restoreColumnState", "Error restoring column state:", e);
    }
    return false;
  }
};

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

// Create debounced save function once
const debouncedSaveColumnState = debounce(() => {
  log("debug", scriptName, "debouncedSaveColumnState", "Executing debounced save");
  columnStateHelpers.save();
}, 300);

/**
 * Cell renderers
 */
const cellRenderers = {
  badge: function(params) {
    if (params.value == null) return '';
    let badgeClass = 'ag-badge ag-badge-primary';
    const colId = params.column.colId.toLowerCase();

    if (colId.includes('contact')) {
      badgeClass = 'ag-badge ag-badge-info';
    } else if (colId.includes('note')) {
      badgeClass = 'ag-badge ag-badge-secondary';
    } else if (colId.includes('capabilit')) {
      badgeClass = 'ag-badge ag-badge-success';
    }

    return `<span class="${badgeClass}">${params.value}</span>`;
  },

  action: function(params) {
    const id = params.data?.id || '';
    const basePath = window.location.pathname.split('/')[1] || '';

    return `
      <div class="ag-action-cell">
        <a href="/${basePath}/${id}" class="ag-icon-btn ag-icon-primary" title="View">
          <i class="fas fa-eye"></i>
        </a>
        <a href="/${basePath}/edit/${id}" class="ag-icon-btn ag-icon-info" title="Edit">
          <i class="fas fa-edit"></i>
        </a>
        <a href="/${basePath}/delete/${id}" class="ag-icon-btn ag-icon-danger" title="Delete" 
           onclick="return confirm('Are you sure you want to delete this item?')">
          <i class="fas fa-trash"></i>
        </a>
      </div>
    `;
  },

  objectValue: function(params) {
    if (params.value == null) return '';
    if (Array.isArray(params.value)) {
      return params.value.length ? `${params.value.length} item${params.value.length > 1 ? 's':''}` : '';
    }
    if (typeof params.value === 'object') {
      return `Ref #${params.value}`;
    }
    return params.value;
  }
};

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
        handleGridResize();
      } else {
        log("debug", scriptName, "eventHandler", `Event triggered: ${eventName}`);
      }
      debouncedSaveColumnState();
    });
  });

  log("info", scriptName, "setUpApis", "Event listeners registered");
  columnStateHelpers.restore();
}

/**
 * Set up global search functionality
 */
function setupGlobalSearch(api) {
  const input = document.getElementById('globalSearch');
  if (input) {
    log("info", scriptName, "setupGlobalSearch", "Search input found");
    input.addEventListener('input', () => {
      api.setQuickFilter(input.value);
      log("debug", scriptName, "setupGlobalSearch", `Filter: "${input.value}"`);
    });
  } else {
    log("warn", scriptName, "setupGlobalSearch", "🔍 #globalSearch not found");
  }
}

/**
 * Setup column visibility selector UI
 */
function setupColumnSelector(api) {
  const container = document.getElementById('columnSelectorItems');
  // Fix: Select buttons by their attributes instead of IDs
  const selectAll = document.querySelector('[form="selectAllColumns"]');
  const clearAll = document.querySelector('[form="clearAllColumns"]');
  // Find the dropdown parent container
  const dropdownContainer = container?.closest('.dropdown-menu') || container?.parentElement;

  if (!container || !api) {
    log("warn", scriptName, "setupColumnSelector", "Selector elements or API missing");
    return;
  }

  // Prevent dropdown from closing when clicking inside
  if (dropdownContainer) {
    dropdownContainer.addEventListener('click', function(event) {
      event.stopPropagation();
    });
    log("info", scriptName, "setupColumnSelector", "Added dropdown click prevention");
  }

  // Clear and style container
  container.innerHTML = '';
  Object.assign(container.style, {
    maxHeight: '300px',
    overflowY: 'auto',
    padding: '0 10px'
  });

  // Add custom scrollbar styles
  const styleElement = document.createElement('style');
  styleElement.textContent = `
    #columnSelectorItems::-webkit-scrollbar {
      width: 6px;
    }
    #columnSelectorItems::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 4px;
    }
    #columnSelectorItems::-webkit-scrollbar-thumb {
      background: #888;
      border-radius: 4px;
    }
    #columnSelectorItems::-webkit-scrollbar-thumb:hover {
      background: #555;
    }
    #columnSelectorItems {
      scrollbar-width: thin;
      scrollbar-color: #888 #f1f1f1;
    }
  `;
  document.head.appendChild(styleElement);

  // Get columns and column state
  const cols = api.getColumns ? api.getColumns() : [];
  if (!Array.isArray(cols) || cols.length === 0) {
    log("warn", scriptName, "setupColumnSelector", "No columns available from API");
    return;
  }

  // Sort columns alphabetically by header name
  cols.sort((a, b) => {
    const aName = a.getColDef?.()?.headerName || a.getColId?.() || '';
    const bName = b.getColDef?.()?.headerName || b.getColId?.() || '';
    return aName.localeCompare(bName);
  });

  const columnState = typeof api.getColumnState === 'function' ? api.getColumnState() : [];

  // Create checkbox for each column
  cols.forEach(col => {
    if (!col) return;

    const colId = col.getColId?.() || col.getId?.();
    if (!colId) {
      log("warn", scriptName, "setupColumnSelector", "Column without ID found, skipping");
      return;
    }

    const def = col.getColDef?.() || {};
    const name = (def.headerName || colId).replace(/\w\S*/g, txt =>
      txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());

    const visible = !(Array.isArray(columnState) &&
      columnState.find(c => c.colId === colId)?.hide);

    // Create elements
    const div = document.createElement('div');
    div.className = 'column-selector-item';

    const chk = document.createElement('input');
    chk.type = 'checkbox';
    chk.className = 'column-selector-checkbox';
    chk.id = `chk-${colId}`;
    chk.checked = visible;

    const lbl = document.createElement('label');
    lbl.className = 'column-selector-label';
    lbl.htmlFor = `chk-${colId}`;
    lbl.textContent = name;

    // Add change handler with resize
    chk.addEventListener('change', e => {
      if (typeof api.setColumnVisible === 'function') {
        api.setColumnVisible(colId, e.target.checked);
        handleGridResize(); // Add grid resize handler
      }
    });

    // Add click handler to entire div
    div.addEventListener('click', e => {
      if (e.target !== chk) {
        chk.checked = !chk.checked;
        const changeEvent = new Event('change', { bubbles: true });
        chk.dispatchEvent(changeEvent);
      }
    });

    div.append(chk, lbl);
    container.appendChild(div);
  });

  // Set up select/clear all buttons
  if (selectAll) {
    selectAll.addEventListener('click', () => {
      cols.forEach(c => {
        const colId = c.getColId?.();
        if (colId && api.setColumnVisible) {
          api.setColumnVisible(colId, true);
          const checkbox = document.getElementById(`chk-${colId}`);
          if (checkbox) checkbox.checked = true;
        }
      });
      handleGridResize(); // Add grid resize after all columns are shown
    });
  } else {
    log("warn", scriptName, "setupColumnSelector", "Select All button not found");
  }

  if (clearAll) {
    clearAll.addEventListener('click', () => {
      cols.forEach(c => {
        const colId = c.getColId?.();
        if (colId && api.setColumnVisible) {
          api.setColumnVisible(colId, false);
          const checkbox = document.getElementById(`chk-${colId}`);
          if (checkbox) checkbox.checked = false;
        }
      });
      handleGridResize(); // Add grid resize after all columns are hidden
    });
  } else {
    log("warn", scriptName, "setupColumnSelector", "Clear All button not found");
  }

  log("info", scriptName, "setupColumnSelector", "Column selector configured");
}

/**
 * Generate column definitions based on data
 */
function generateColumnDefs(data) {
  log("info", scriptName, "generateColumnDefs", "Generating columns");
  if (!data || !data.length) {
    log("warn", scriptName, "generateColumnDefs", "No data to generate columns");
    return [];
  }

  const keys = Object.keys(data[0]);
  log("debug", scriptName, "generateColumnDefs", "Columns found:", keys);

  // Map data keys to column definitions
  const columnDefs = keys.map(key => {
    const def = {
      field: key,
      headerName: formatDisplayText(key),
      sortable: true,
      filter: true
    };

    // Add badge renderer for certain columns
    if (/count|opportunit|contact|note|capabilit/i.test(key)) {
      def.cellRenderer = cellRenderers.badge;
    }

    // Format objects/arrays
    if (data[0][key] != null && typeof data[0][key] === 'object') {
      def.valueFormatter = cellRenderers.objectValue;
    }

    return def;
  });

  // Add actions column
  columnDefs.push({
    headerName: 'Actions',
    field: 'actions',
    cellRenderer: cellRenderers.action,
    sortable: false,
    filter: false,
    flex: 0.8,
    minWidth: 150,
    cellClass: 'text-center'
  });

  return columnDefs;
}

/**
 * Get grid options with all necessary configurations
 */
function getGridOptions() {
  return {
    columnDefs: [],
    rowData: [],
    maintainColumnOrder: true,
    pagination: true,
    enableCellTextSelection: true,
    enableBrowserTooltips: true,
    suppressCopyRowsToClipboard: false,
    suppressCellFocus: true,
    suppressRowClickSelection: false,
    rowSelection: 'single',
    paginationPageSize: 20,
    domLayout: 'autoHeight',
    suppressColumnVirtualisation: false,
    animateRows: true,
    defaultColDef: {
      flex: 1,
      minWidth: 100,
      resizable: true,
      wrapText: true,
      autoHeight: true,
      sortable: true,
      filter: true,
      suppressSizeToFit: false
    },

    // Row click handler
    onRowClicked: event => {
      if (event.event.ctrlKey || event.event.metaKey ||
          event.event.shiftKey || event.event.button !== 0) return;

      const id = event.data?.id;
      if (!id) return;

      const basePath = window.location.pathname.split('/')[1];
      if (basePath) window.location.href = `/${basePath}/${id}`;
    },

    // Grid ready handler - single point for API initialization
    onGridReady: params => {
      log("info", scriptName, "onGridReady", "Grid API initialized");
      setUpApis(params.api, params.columnApi);
      setupGlobalSearch(params.api);
      setupColumnSelector(params.api);

      // Ensure grid fits all columns initially
      if (params.api) {
        setTimeout(() => params.api.sizeColumnsToFit(), 0);
      }
    },

    // After data is loaded, resize columns
    onFirstDataRendered: params => {
      if (params.api) {
        params.api.sizeColumnsToFit();
      }
    }
  };
}

/**
 * Handle grid resize when columns are toggled
 */
function handleGridResize() {
  if (!gridApiReference) {
    log("warn", scriptName, "handleGridResize", "Grid API not available");
    return;
  }

  log("info", scriptName, "handleGridResize", "Triggering grid resize");

  // Use setTimeout to ensure this runs after the DOM has updated
  setTimeout(() => {
    try {
      // Size columns to fit available width
      gridApiReference.sizeColumnsToFit();

      // Manually trigger redraw
      gridApiReference.refreshCells({ force: true });
      gridApiReference.redrawRows();

      // FIX: Don't manually dispatch gridSizeChanged event
      // Let AG Grid handle this internally
    } catch (err) {
      log("error", scriptName, "handleGridResize", "Error during grid resize:", err);
    }
  }, 0);
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
  const gridOptions = getGridOptions();
  if (actualData && actualData.length) {
    gridOptions.columnDefs = generateColumnDefs(actualData);
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

/**
 * Function to ensure proper spacing between sections
 */
function fixLayoutSpacing() {
  // Add a resize observer to table container
  const tableContainer = document.getElementById('table-container');
  const chartSection = document.querySelector('.dashboard-section:last-child');

  if (!tableContainer || !chartSection) return;

  // Determine if we need additional spacing
  function adjustSpacing() {
    const tableRect = tableContainer.getBoundingClientRect();
    const tableBottom = tableRect.bottom;

    // Add more spacing if needed
    const sections = document.querySelectorAll('.dashboard-section');
    sections.forEach(section => {
      section.style.marginBottom = '3rem';
      section.style.overflow = 'visible';
    });

    // Ensure chart section has enough space
    chartSection.style.paddingTop = '1rem';
    chartSection.style.marginTop = '2rem';
  }

  // Run adjustment once on page load
  window.addEventListener('DOMContentLoaded', () => {
    setTimeout(adjustSpacing, 500); // Wait for grid to render
  });

  // Run adjustment after grid is ready - safer way to add event listener
  if (typeof gridApiReference !== 'undefined' && gridApiReference) {
    try {
      gridApiReference.addEventListener('gridSizeChanged', adjustSpacing);
    } catch (e) {
      log("warn", scriptName, "fixLayoutSpacing", "Could not add gridSizeChanged listener", e);
      // Alternative fallback for layout adjustments if event listener fails
      setTimeout(adjustSpacing, 1000);
    }
  }

  // Run adjustment on window resize
  window.addEventListener('resize', adjustSpacing);
}

// Export public functions
export function getGridApi() {
  return gridApiReference;
}

export function getColumnApi() {
  return columnApiReference;
}

export function manualSaveColumnState() {
  return columnStateHelpers.save();
}

// Bootstrap code - run once
if (!window.__tableInitialized) {
  window.__tableInitialized = true;
  document.addEventListener('DOMContentLoaded', () => {
    log("info", scriptName, "DOMContentLoaded", "Initializing table...");
    initializeTable()
      .then(() => {
        log("info", scriptName, "DOMContentLoaded", "Table initialization completed successfully");
        fixLayoutSpacing(); // Call layout spacing fix after table init
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