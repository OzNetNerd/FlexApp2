const scriptName = "tableConfig.js";
import log from '/static/js/logger.js';

// Create variables to store the grid API outside the gridOptions
let gridApiReference = null;
let columnApiReference = null;
let columnStateInitialized = false;

/**
 * Export a function to set the grid API from outside
 * This is critical - allows tableInit.js to set the API reference
 */
export function setGridApi(api, columnApi) {
    gridApiReference = api;
    columnApiReference = columnApi;
    log("info", scriptName, "setGridApi", "Grid APIs externally set");

    // Register events when APIs are set
    registerEvents();

    // Try to restore column state
    restoreColumnState();
}

/**
 * Get the grid API
 */
export function getGridApi() {
    return gridApiReference;
}

/**
 * Get the column API
 */
export function getColumnApi() {
    return columnApiReference;
}

/**
 * Debounce function to prevent multiple rapid saves
 */
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

/**
 * Register all column state change events
 */
function registerEvents() {
    if (!gridApiReference) {
        log("warn", scriptName, "registerEvents", "Cannot register events - API not available");
        return false;
    }

    try {
        // Define all events we want to listen to
        const events = [
            'columnMoved',
            'columnResized',
            'columnVisible',
            'columnPinned',
            'sortChanged',
            'filterChanged',
            'columnRowGroupChanged',
            'columnValueChanged',
            'dragStopped'
        ];

        // Add event listeners to grid API
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
 * Restore column state from localStorage if available
 */
function restoreColumnState() {
    if (!gridApiReference) {
        log("warn", scriptName, "restoreColumnState", "Cannot restore state - API not available");
        return false;
    }

    try {
        const savedState = localStorage.getItem("agGridColumnState");
        if (savedState) {
            const columnState = JSON.parse(savedState);

            if (columnState && Array.isArray(columnState) && columnState.length > 0) {
                log("info", scriptName, "restoreColumnState", `Restoring state with ${columnState.length} columns`);

                gridApiReference.applyColumnState({
                    state: columnState,
                    applyOrder: true
                });

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
 * Manually save column state - exported for external use
 */
export function manualSaveColumnState() {
    return saveColumnState();
}

/**
 * Save column state to localStorage
 */
function saveColumnState() {
    // Check if grid API is available
    if (!gridApiReference) {
        log("warn", scriptName, "saveColumnState", "Grid API not initialized, cannot save column state");
        return false;
    }

    try {
        // Get current column state
        const columnState = gridApiReference.getColumnState();

        if (columnState && Array.isArray(columnState) && columnState.length > 0) {
            // Save to localStorage
            localStorage.setItem("agGridColumnState", JSON.stringify(columnState));
            log("info", scriptName, "saveColumnState", `💾 Saved column state with ${columnState.length} columns`);
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

// Create debounced version of saveColumnState
const debouncedSaveColumnState = debounce(() => {
    log("debug", scriptName, "debouncedSaveColumnState", "Executing debounced save");
    saveColumnState();
}, 300);

// Default grid options
export default function getGridOptions() {
    return {
        columnDefs: [],
        rowData: [],
        maintainColumnOrder: true,
        pagination: true,
        enableCellTextSelection: true, // allow text selection
        enableBrowserTooltips: true,   // allow tooltips on hover
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
            wrapText: true,           // ✅ enables cell wrapping
            autoHeight: true          // ✅ adjusts row height to fit content
        },
        onRowClicked: event => {
            if (event.event.ctrlKey || event.event.metaKey || event.event.shiftKey || event.event.button !== 0) {
              return; // Allow copy/drag/select actions
            }

            const id = event.data?.id;
            if (!id) return;

            // Derive base path (e.g., /contacts, /opportunities)
            const basePath = window.location.pathname.split('/')[1];
            if (basePath) {
              window.location.href = `/${basePath}/${id}`;
            }
          },
        // IMPORTANT: We keep onGridReady minimal since it might be overwritten
        onGridReady: (params) => {
            // Store references to grid APIs
            gridApiReference = params.api;
            columnApiReference = params.columnApi;
            log("info", scriptName, "onGridReady", "Grid API initialized in tableConfig");

            // Don't do anything else here as tableInit.js will overwrite this handler
        },

        // Use onFirstDataRendered as a backup in case setGridApi isn't called
        onFirstDataRendered: (params) => {
            // Only set APIs if they haven't been set externally
            if (!gridApiReference) {
                log("info", scriptName, "onFirstDataRendered", "Setting grid API from onFirstDataRendered (fallback)");
                gridApiReference = params.api;
                columnApiReference = params.columnApi;

                // Register events and restore state since this is the fallback
                registerEvents();
                restoreColumnState();

                // Test save with delay
                setTimeout(() => {
                    const success = saveColumnState();
                    log("info", scriptName, "onFirstDataRendered", "Fallback column state save test:", success ? "SUCCESS" : "FAILED");
                }, 200);
            }
        },

        // Fallback event handlers (these will work even if dynamic registration fails)
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
