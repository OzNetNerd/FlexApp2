/**
 * tableGrid.js - Grid configuration and setup
 */

import log from '/static/js/core/logger.js';
const scriptName = "tableGrid.js";
import { getEditModeState, columnStateHelpers } from './tableState.js';
import { handleGridResize } from './tableUtils.js';

/**
 * Get grid options with all necessary configurations
 */
export function getGridOptions(isEditModeActive) {
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
      suppressSizeToFit: false,
      editable: false, // Start in view mode by default
      // Add double-click to edit functionality
      cellClassRules: {
        'editable-cell': () => true
      }
    },

    // Row double-click handler for navigation
    onRowDoubleClicked: event => {
      // If in edit mode, don't navigate
      if (isEditModeActive) return;

      if (event.event.ctrlKey || event.event.metaKey ||
          event.event.shiftKey || event.event.button !== 0) return;

      const id = event.data?.id;
      if (!id) return;

      const basePath = window.location.pathname.split('/')[1];
      if (basePath) window.location.href = `/${basePath}/${id}`;
    },

    // Add context menu (right-click) options
    getContextMenuItems: params => {
      const id = params.node?.data?.id;
      if (!id) return [];

      const basePath = window.location.pathname.split('/')[1] || '';

      const menuItems = [
        {
          name: 'View Details',
          action: () => {
            window.location.href = `/${basePath}/${id}`;
          }
        },
        {
          name: 'Edit',
          action: () => {
            window.location.href = `/${basePath}/edit/${id}`;
          }
        },
        'separator',
        {
          name: 'Delete',
          action: () => {
            if (confirm('Are you sure you want to delete this item?')) {
              window.location.href = `/${basePath}/delete/${id}`;
            }
          }
        },
        'separator',
        'copy',
        'export'
      ];

      // Add toggle edit option if in cell edit mode
      if (getEditModeState()) {
        menuItems.unshift('separator');
        menuItems.unshift({
          name: 'Edit Cell',
          action: () => {
            // Start cell editing programmatically
            if (params.column && params.column.getColDef().editable) {
              params.api.startEditingCell({
                rowIndex: params.node.rowIndex,
                colKey: params.column.getColId()
              });
            }
          }
        });
      }

      return menuItems;
    },

    // Add cell value changed handler to save updates
    onCellValueChanged: params => {
      log("info", scriptName, "onCellValueChanged", `Value changed: ${params.oldValue} -> ${params.newValue}`);

      // Here you would typically send an API request to update the data
      // For example:
      const id = params.data?.id;
      const field = params.column.getColId();
      const value = params.newValue;
      const basePath = window.location.pathname.split('/')[1];

      if (id && field) {
        // Example API call (you'd need to implement this)
        fetch(`/api/${basePath}/${id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ [field]: value })
        })
        .then(response => response.json())
        .then(data => {
          log("info", scriptName, "onCellValueChanged", "Update successful");
        })
        .catch(error => {
          log("error", scriptName, "onCellValueChanged", "Update failed", error);
          // Optionally revert the change in the grid
          params.node.setDataValue(field, params.oldValue);
        });
      }
    },

    // Grid ready handler - single point for API initialization
    onGridReady: null, // This will be set in table.js

    // After data is loaded, resize columns
    onFirstDataRendered: params => {
      if (params.api) {
        params.api.sizeColumnsToFit();
      }
    }
  };
}