/**
 * tableUI.js - UI components for table functionality
 */

import log from '/static/js/core/logger.js';
const scriptName = "tableUI.js";
import { handleGridResize } from './tableUtils.js';

/**
 * Set up global search functionality
 */
export function setupGlobalSearch(api) {
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
export function setupColumnSelector(api) {
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
        handleGridResize(api); // Add grid resize handler
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
      handleGridResize(api); // Add grid resize after all columns are shown
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
      handleGridResize(api); // Add grid resize after all columns are hidden
    });
  } else {
    log("warn", scriptName, "setupColumnSelector", "Clear All button not found");
  }

  log("info", scriptName, "setupColumnSelector", "Column selector configured");
}

/**
 * Add required CSS styles for table functionality
 */
export function addTableStyles() {
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

  // Add cell styling
  const cellStylesElement = document.createElement('style');
  cellStylesElement.id = 'editable-cell-styles';
  cellStylesElement.textContent = `
    /* Add styling for editable cells */
    .editable-cell {
      background-color: #fcfcfc;
      border: 1px solid transparent;
    }
    .editable-cell:hover {
      background-color: #f0f7ff;
      border: 1px dashed #ccc;
    }
    
    /* Context menu styling */
    .ag-menu {
      font-family: var(--font-family);
      font-size: var(--font-size-sm);
    }

    /* View mode styling (no edit indicators) */
    .view-mode .editable-cell {
      background-color: transparent;
      border: 1px solid transparent;
    }
    .view-mode .editable-cell:hover {
      background-color: rgba(0, 0, 0, 0.05);
      border: 1px solid transparent;
    }

    /* Edit mode styling (clear indicators) */
    .edit-mode .editable-cell {
      background-color: #fcfcfc;
      border: 1px solid transparent;
    }
    .edit-mode .editable-cell:hover {
      background-color: #e6f3ff;
      border: 1px dashed #99c2ff;
      cursor: cell;
    }
  `;
  document.head.appendChild(cellStylesElement);
}