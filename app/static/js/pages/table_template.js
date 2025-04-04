// File: static/js/table_custom.js

import log from './logger.js';

document.addEventListener('DOMContentLoaded', () => {
  // Attach event listener to the <li> element to prevent event propagation
  const stopPropagationLi = document.getElementById('stop-propagation-li');
  if (stopPropagationLi) {
    stopPropagationLi.addEventListener('click', (e) => {
      e.stopPropagation();
    });
  }

  // Attach event listeners for the column selector buttons
  const selectAllBtn = document.getElementById('selectAllColumns');
  const clearAllBtn = document.getElementById('clearAllColumns');

  if (selectAllBtn) {
    selectAllBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      // Insert your logic to select all columns here
      log("info", "table_custom.js", "selectAllColumns", "All columns selected.");
    });
  }

  if (clearAllBtn) {
    clearAllBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      // Insert your logic to clear all columns here
      log("info", "table_template.js", "clearAllColumns", "All columns cleared.");
    });
  }

  // Retrieve configuration data from the hidden element
  const tableConfigElem = document.getElementById('table-config');
  const title = tableConfigElem ? tableConfigElem.dataset.title : 'Untitled';
  const entityName = tableConfigElem ? tableConfigElem.dataset.entityName : 'item';

  // Retrieve API URL from the table container's data attribute
  const tableContainer = document.getElementById('table-container');
  const dataUrl = tableContainer ? tableContainer.dataset.apiUrl : '';

  // Log the configuration values for debugging
  log("info", "table_template.js", "DOMContentLoaded", "Page title: " + title);
  log("info", "table_template.js", "DOMContentLoaded", "Entity name: " + entityName);
  log("info", "table_template.js", "DOMContentLoaded", "Data API URL: " + dataUrl);
  log("debug", "table_template.js", "DOMContentLoaded", "DOM fully loaded and parsed.");
});
