/**
 * tableRenderers.js - Cell renderers for table components
 */

import log from '/static/js/core/logger.js';
const scriptName = "tableRenderers.js";

/**
 * Cell renderers
 */
export const cellRenderers = {
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

// Store editable state for columns separately instead of on colDef
export const editableColumnTracker = new Map();

/**
 * Generate column definitions based on data
 */
export function generateColumnDefs(data, isEditModeActive, cellRenderers) {
  log("info", scriptName, "generateColumnDefs", "Generating columns");
  if (!data || !data.length) {
    log("warn", scriptName, "generateColumnDefs", "No data to generate columns");
    return [];
  }

  const keys = Object.keys(data[0]);
  log("debug", scriptName, "generateColumnDefs", "Columns found:", keys);

  // Import formatDisplayText
  const formatDisplayText = text => {
    return text
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, str => str.toUpperCase())
      .trim();
  };

  // Map data keys to column definitions
  const columnDefs = keys.map(key => {
    const def = {
      field: key,
      headerName: formatDisplayText(key),
      sortable: true,
      filter: true
    };

    // Track if this column can be edited by default
    let canBeEdited = true;

    // Add badge renderer for certain columns
    if (/count|opportunit|contact|note|capabilit/i.test(key)) {
      def.cellRenderer = cellRenderers.badge;
      canBeEdited = false; // Badge columns are not editable
    }

    // Format objects/arrays
    if (data[0][key] != null && typeof data[0][key] === 'object') {
      def.valueFormatter = cellRenderers.objectValue;
      canBeEdited = false; // Object columns are not editable
    }

    // Make ID column not editable
    if (key === 'id') {
      canBeEdited = false;
    }

    // Store editability in our tracker instead of on the colDef
    editableColumnTracker.set(key, canBeEdited);

    // Set editable based on current mode
    def.editable = isEditModeActive && canBeEdited;

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
    cellClass: 'text-center',
    editable: false // Actions column is not editable
  });

  return columnDefs;
}