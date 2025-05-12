/**
 * tableState.js - State management for table columns and modes
 */

import log from '/static/js/core/logger.js';
const scriptName = "tableState.js";
import { handleGridResize } from './tableUtils.js';
import { editableColumnTracker } from './tableRenderers.js';

// Global state
let isEditModeActive = false;

/**
 * Function to toggle between edit and view modes
 */
export function toggleEditMode(mode, gridApiReference) {
  isEditModeActive = mode === 'edit';
  log("info", scriptName, "toggleEditMode", `Edit mode ${isEditModeActive ? 'enabled' : 'disabled'}`);

  // Update container class for styling
  const container = document.getElementById('table-container');
  if (container) {
    container.classList.remove('edit-mode', 'view-mode');
    container.classList.add(isEditModeActive ? 'edit-mode' : 'view-mode');
  }

  // Update UI buttons
  const viewBtn = document.getElementById('viewModeBtn');
  const editBtn = document.getElementById('editModeBtn');

  if (viewBtn && editBtn) {
    // Toggle active classes
    if (isEditModeActive) {
      viewBtn.classList.remove('btn-primary');
      viewBtn.classList.add('btn-outline-primary');
      editBtn.classList.remove('btn-outline-primary');
      editBtn.classList.add('btn-primary');
    } else {
      viewBtn.classList.remove('btn-outline-primary');
      viewBtn.classList.add('btn-primary');
      editBtn.classList.remove('btn-primary');
      editBtn.classList.add('btn-outline-primary');
    }
  }

  // Update grid if available
  if (gridApiReference) {
    // Update column definitions to reflect the new edit state
    const columns = gridApiReference.getColumns();
    if (columns) {
      columns.forEach(column => {
        const colDef = column.getColDef();
        const field = colDef.field;

        // Skip special columns
        if (field !== 'actions' && field !== 'id') {
          // Get editability from our tracker
          const canEdit = editableColumnTracker.has(field)
            ? editableColumnTracker.get(field)
            : false;

          // Set editable based on mode
          colDef.editable = isEditModeActive && canEdit;
        }
      });
    }

    // Refresh the grid
    gridApiReference.refreshCells({ force: true });
  }
}

/**
 * Setup the mode toggle buttons
 */
export function setupModeToggleButtons(gridApiReference) {
  const viewBtn = document.getElementById('viewModeBtn');
  const editBtn = document.getElementById('editModeBtn');

  if (viewBtn && editBtn) {
    viewBtn.addEventListener('click', () => toggleEditMode('view', gridApiReference));
    editBtn.addEventListener('click', () => toggleEditMode('edit', gridApiReference));

    // Initialize in view mode
    toggleEditMode('view', gridApiReference);
  } else {
    log("warn", scriptName, "setupModeToggleButtons", "Toggle buttons not found in the DOM");
  }
}

/**
 * Get the current edit mode state
 */
export function getEditModeState() {
  return isEditModeActive;
}

/**
 * Save/restore column state utilities
 */
export const columnStateHelpers = {
  save: function(gridApiReference) {
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

  restore: function(gridApiReference) {
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