// static/js/dropDown/columnSelector.js

const scriptName = "columnSelector.js";

/**
 * Initializes the column selector by populating options and setting up event listeners.
 */
export function initColumnSelector() {
  const functionName = "initColumnSelector";
  log("info", `${scriptName}:${functionName}`, "🔄 Initializing column selector...");

  populateColumnSelectorOptions();
  setupColumnSelector();
}

/**
 * Populates the column selector options by dynamically extracting unique values
 * from the grid data for the specified column.
 */
export function populateColumnSelectorOptions() {
  const functionName = "populateColumnSelectorOptions";
  window.logger.group(`${scriptName}:${functionName}`, "📋 Populating column selector options");

  const container = document.getElementById('columnSelectorItems');
  if (!container) {
    log("warn", `${scriptName}:${functionName}`, "❌ Column selector container not found");
    window.logger.groupEnd(`${scriptName}:${functionName}`);
    return;
  }

  // Clear any existing options
  container.innerHTML = '';

  const gridApi = getGridApi();
  if (!gridApi) {
    log("warn", `${scriptName}:${functionName}`, "❌ Grid API not available");
    window.logger.groupEnd(`${scriptName}:${functionName}`);
    return;
  }

  // Retrieve the target column name from the container's data attribute
  const columnName = container.getAttribute('data-column-name');
  if (!columnName) {
    log("error", `${scriptName}:${functionName}`, "❌ No data-column-name attribute found on container");
    window.logger.groupEnd(`${scriptName}:${functionName}`);
    return;
  }

  // Retrieve grid data
  const rowData = gridApi.getModel().rowsToDisplay.map(row => row.data);
  if (!rowData || rowData.length === 0) {
    log("warn", `${scriptName}:${functionName}`, "❌ No row data available");
    window.logger.groupEnd(`${scriptName}:${functionName}`);
    return;
  }

  // Extract unique values from the specified column
  const uniqueValues = new Set();
  rowData.forEach(row => {
    if (row[columnName]) {
      uniqueValues.add(row[columnName]);
    }
  });

  const options = Array.from(uniqueValues).sort();
  log("debug", `${scriptName}:${functionName}`, "🔍 Found options:", options);

  // Create a checkbox for each option
  options.forEach((option, index) => {
    const checkboxId = `columnSelector_${index}`;

    const itemDiv = document.createElement('div');
    itemDiv.className = 'form-check';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'form-check-input';
    checkbox.id = checkboxId;
    checkbox.value = option;
    checkbox.checked = true; // Default to selected

    // Update the filter when the checkbox changes
    checkbox.addEventListener('change', () => {
      updateColumnSelector();
    });

    const label = document.createElement('label');
    label.className = 'form-check-label';
    label.htmlFor = checkboxId;
    label.textContent = option;

    itemDiv.appendChild(checkbox);
    itemDiv.appendChild(label);
    container.appendChild(itemDiv);
  });

  // Update UI elements like counters without immediately applying the filter
  updateColumnSelector(false);
  window.logger.success(`${scriptName}:${functionName}`, `✅ Created ${options.length} column selector options`);
  window.logger.groupEnd(`${scriptName}:${functionName}`);
}

/**
 * Sets up the column selector by removing duplicate event listeners and
 * initializing search functionality.
 */
export function setupColumnSelector() {
  const functionName = "setupColumnSelector";
  window.logger.group(`${scriptName}:${functionName}`, "🔄 Setting up column selector");

  const container = document.getElementById('columnSelectorItems');
  const searchInput = document.getElementById('columnSelectorSearch');
  const toggleEl = document.getElementById('columnSelectorDropdownToggle');
  const counterEl = document.getElementById('columnSelectorCounter');

  if (!container) {
    log("warn", `${scriptName}:${functionName}`, "❌ Column selector container not found");
    return;
  }

  // Remove duplicate event listeners by replacing checkboxes
  const checkboxes = container.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach(checkbox => {
    const newCheckbox = checkbox.cloneNode(true);
    checkbox.parentNode.replaceChild(newCheckbox, checkbox);

    newCheckbox.addEventListener('change', function() {
      log("debug", `${scriptName}:${functionName}`, `Checkbox changed: ${this.value} -> ${this.checked}`);
      updateColumnSelector();
    });
  });

  // Setup search functionality if the search input exists
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      const searchTerm = this.value.toLowerCase();
      log("debug", `${scriptName}:${functionName}`, `Searching for: ${searchTerm}`);
      const items = container.querySelectorAll('.form-check');
      items.forEach(item => {
        const label = item.querySelector('label');
        if (label) {
          item.style.display = label.textContent.toLowerCase().includes(searchTerm) ? 'block' : 'none';
        }
      });
    });
  }

  // Initialize the counter and dropdown toggle text
  updateColumnSelector(false);
  window.logger.success(`${scriptName}:${functionName}`, "✅ Column selector setup complete");
  window.logger.groupEnd(`${scriptName}:${functionName}`);
}

/**
 * Updates the column selector UI elements (e.g., counter, toggle text) and optionally applies the filter.
 * @param {boolean} applyFilter - Whether to apply the filter after updating (default is true).
 */
export function updateColumnSelector(applyFilter = true) {
  const functionName = "updateColumnSelector";
  const container = document.getElementById('columnSelectorItems');
  const counterEl = document.getElementById('columnSelectorCounter');
  const toggleEl = document.getElementById('columnSelectorDropdownToggle');

  if (!container) return;

  const selectedCheckboxes = container.querySelectorAll('input[type="checkbox"]:checked');
  const selectedValues = Array.from(selectedCheckboxes).map(cb => cb.value);

  log("debug", `${scriptName}:${functionName}`, "🔍 Selected values:", selectedValues);

  if (counterEl) {
    counterEl.textContent = selectedValues.length > 0 ? `${selectedValues.length} selected` : '';
  }

  if (toggleEl) {
    toggleEl.textContent = selectedValues.length > 0 ? `${selectedValues.length} selected` : 'Select Column';
  }

  if (applyFilter) {
    applyColumnSelector(selectedValues);
  }
}

/**
 * Applies the column selector filter by updating the grid's filter model based on the selected values.
 * @param {Array} selectedValues - Array of selected values from the column selector.
 */
export function applyColumnSelector(selectedValues) {
  const functionName = "applyColumnSelector";
  window.logger.group(`${scriptName}:${functionName}`, "🔄 Applying column selector filter");
  log("debug", `${scriptName}:${functionName}`, "🔍 With values:", selectedValues);

  const gridApi = getGridApi();
  if (!gridApi) {
    log("warn", `${scriptName}:${functionName}`, "❌ Grid API not available");
    window.logger.groupEnd(`${scriptName}:${functionName}`);
    return;
  }

  const container = document.getElementById('columnSelectorItems');
  const columnName = container ? container.getAttribute('data-column-name') : null;

  const filterModel = gridApi.getFilterModel() || {};
  if (filterModel[columnName]) {
    delete filterModel[columnName];
  }

  if (selectedValues && selectedValues.length > 0) {
    filterModel[columnName] = {
      type: 'set',
      values: selectedValues
    };
  }

  log("debug", `${scriptName}:${functionName}`, "🔍 Setting filter model:", filterModel);
  gridApi.setFilterModel(filterModel);
  window.logger.success(`${scriptName}:${functionName}`, "✅ Filter applied successfully");
  window.logger.groupEnd(`${scriptName}:${functionName}`);
}

/**
 * Utility function to retrieve the AG Grid API from various sources.
 * @returns {object|null} The grid API if found, otherwise null.
 */
function getGridApi() {
  const functionName = "getGridApi";
  log("debug", `${scriptName}:${functionName}`, "🔍 Fetching grid API...");

  if (window.gridApi) {
    log("debug", `${scriptName}:${functionName}`, "✅ Found gridApi in window");
    return window.gridApi;
  }

  if (window.tableManager && window.tableManager.gridManager) {
    try {
      const api = window.tableManager.gridManager.getApi();
      if (api) {
        window.gridApi = api;
        log("debug", `${scriptName}:${functionName}`, "✅ Found gridApi in tableManager");
        return api;
      }
    } catch (e) {
      log("error", `${scriptName}:${functionName}`, "❌ Error retrieving gridApi from tableManager", e);
    }
  }

  const gridElement = document.querySelector('.ag-root-wrapper');
  if (gridElement && gridElement.__agComponent) {
    log("debug", `${scriptName}:${functionName}`, "✅ Found gridApi in DOM element");
    return gridElement.__agComponent.api;
  }

  log("warn", `${scriptName}:${functionName}`, "❌ Could not find AG Grid API");
  return null;
}
