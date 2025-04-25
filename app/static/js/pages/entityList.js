import log from '/static/js/core/logger.js';
import moduleSystem from '/static/js/core/module.js';
import eventSystem from '/static/js/core/events.js';
import tableComponent from '/static/js/components/table.js';

/**
 * Entity list page functionality
 */
class EntityListPage {
  constructor() {
    log('info', 'entityList.js', 'constructor', 'Entity list page module created');
  }

  /**
   * Initialize list page functionality
   */
  init() {
    const functionName = 'init';
    log('info', 'entityList.js', functionName, 'Initializing entity list page');

    // Initialize data table if it exists
    this.initTable();

    // Initialize highlights animation if it exists
    this.initHighlights();

    log('info', 'entityList.js', functionName, 'Entity list page initialization complete');
  }

  /**
   * Initialize data table if it exists
   */
  initTable() {
    const functionName = 'initTable';

    // Check if the table container exists
    const tableContainer = document.getElementById('table-container');
    if (!tableContainer) {
      log('debug', 'entityList.js', functionName, 'Table container not found');
      return;
    }

    log('debug', 'entityList.js', functionName, 'Initializing data table');

    // Initialize table with the table component
    const tableController = tableComponent.initTable('table-container');

    // Attach event listeners for column visibility and searching
    this.setupTableCustomizations(tableController);

    // Listen for table events
    eventSystem.subscribe('table.delete.success', (data) => {
      log('info', 'entityList.js', 'tableDeleteSuccess', `Item ${data.id} deleted successfully`);
    });

    eventSystem.subscribe('table.sort', (data) => {
      log('debug', 'entityList.js', 'tableSort', 'Table sorted', data.sort);
    });

    eventSystem.subscribe('table.filter', (data) => {
      log('debug', 'entityList.js', 'tableFilter', 'Table filtered', data.filter);
    });
  }

  /**
   * Set up table customizations like column visibility and search
   * @param {Object} tableController - Table controller
   */
  setupTableCustomizations(tableController) {
    const functionName = 'setupTableCustomizations';

    // Set up search input
    const searchInput = document.getElementById('table-search');
    if (searchInput) {
      let debounceTimer;

      searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);

        debounceTimer = setTimeout(() => {
          const query = searchInput.value.trim();

          if (query.length > 0) {
            tableController.setFilter(query);
            log('debug', 'entityList.js', functionName, `Table search: ${query}`);
          } else {
            tableController.setFilter(null);
            log('debug', 'entityList.js', functionName, 'Table search cleared');
          }
        }, 300);
      });

      log('debug', 'entityList.js', functionName, 'Search input initialized');
    }

    // Set up column selector
    const columnSelector = document.getElementById('column-selector');
    if (columnSelector) {
      const checkboxes = columnSelector.querySelectorAll('input[type="checkbox"]');

      checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
          // Get all checked columns
          const checkedColumns = Array.from(checkboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);

          // Get all available columns
          const allColumns = tableController.getState().columns;

          // Filter visible columns
          const visibleColumns = allColumns.filter(column =>
            checkedColumns.includes(column.field)
          );

          // Update table
          tableController.setVisibleColumns(visibleColumns);

          log('debug', 'entityList.js', functionName, 'Column visibility changed', checkedColumns);
        });
      });

      log('debug', 'entityList.js', functionName, 'Column selector initialized');
    }
  }

  /**
   * Initialize highlights animation if it exists
   */
  initHighlights() {
    const functionName = 'initHighlights';

    const highlights = document.querySelectorAll('.highlight-item');
    if (highlights.length === 0) {
      return;
    }

    log('debug', 'entityList.js', functionName, `Initializing highlights animation with ${highlights.length} items`);

    let currentHighlight = 0;
    let interval;

    // Initialize first highlight
    highlights[0].classList.add('active');

    // Functions to control highlights
    function showHighlight(index) {
      highlights.forEach(item => item.classList.remove('active'));
      highlights[index].classList.add('active');
      currentHighlight = index;

      log('debug', 'entityList.js', 'highlightChange', `Highlight changed to ${index}`);
    }

    function nextHighlight() {
      let next = currentHighlight + 1;
      if (next >= highlights.length) next = 0;
      showHighlight(next);
    }

    function prevHighlight() {
      let prev = currentHighlight - 1;
      if (prev < 0) prev = highlights.length - 1;
      showHighlight(prev);
    }

    function startRotation() {
      interval = setInterval(nextHighlight, 4000);
    }

    function stopRotation() {
      clearInterval(interval);
    }

    // Set up navigation controls
    const nextBtn = document.querySelector('.btn-highlight-next');
    const prevBtn = document.querySelector('.btn-highlight-prev');

    if (nextBtn && prevBtn) {
      nextBtn.addEventListener('click', function () {
        stopRotation();
        nextHighlight();
        startRotation();
      });

      prevBtn.addEventListener('click', function () {
        stopRotation();
        prevHighlight();
        startRotation();
      });

      startRotation();

      log('debug', 'entityList.js', functionName, 'Highlights controls initialized');
    }
  }
}

// Create instance and register with the module system
const entityListPage = new EntityListPage();
moduleSystem.register('entityList', () => entityListPage.init(), ['common'], true);

export default entityListPage;