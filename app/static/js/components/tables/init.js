/**
 * components/tables/init.js
 * Table initialization and event handling
 */

import log from '../../core/utils/logger.js';
import { getTableConfig, getColumnConfig } from './config.js';
import { generateHeaders, sortData, filterData, exportToCsv } from './utils.js';
import { fetchApiDataFromContainer, normalizeData } from '../../core/api/apiService.js';

const scriptName = "tables/init.js";

/**
 * Initialize tables in the document
 * Searches for elements with data-table attribute
 */
export default function initializeTable() {
    const functionName = "initializeTable";
    log("info", scriptName, functionName, "Initializing tables on page");

    // Find all table containers
    const tableContainers = document.querySelectorAll('[data-table]');

    if (tableContainers.length === 0) {
        log("info", scriptName, functionName, "No tables found on page");
        return;
    }

    log("info", scriptName, functionName, `Found ${tableContainers.length} tables`);

    // Initialize each table
    tableContainers.forEach(container => {
        const tableId = container.id;
        if (!tableId) {
            log("error", scriptName, functionName, "Table container has no ID", { container });
            return;
        }

        initializeTableInstance(tableId);
    });
}

/**
 * Initialize a specific table instance
 * @param {string} tableId - ID of the table container
 */
async function initializeTableInstance(tableId) {
    const functionName = "initializeTableInstance";
    log("info", scriptName, functionName, `Initializing table: ${tableId}`);

    try {
        // Get table configuration
        const tableConfig = getTableConfig(tableId);
        const columnConfig = getColumnConfig(tableId);

        // Fetch data
        const apiResponse = await fetchApiDataFromContainer(tableId);
        const data = normalizeData(apiResponse);

        if (!data || !data.length) {
            log("warn", scriptName, functionName, `No data returned for table: ${tableId}`);
            displayNoDataMessage(tableId);
            return;
        }

        log("info", scriptName, functionName, `Received ${data.length} rows for table: ${tableId}`);

        // Generate headers
        const headers = generateHeaders(data, columnConfig);

        // Build table structure
        buildTableStructure(tableId, headers, data, tableConfig);

        // Set up event listeners
        setupTableEventListeners(tableId, headers, data, tableConfig);

        log("info", scriptName, functionName, `Table ${tableId} initialized successfully`);
    } catch (error) {
        log("error", scriptName, functionName, `Error initializing table: ${tableId}`, { error });
        displayErrorMessage(tableId, error.message);
    }
}

/**
 * Build the table DOM structure
 * @param {string} tableId - Table container ID
 * @param {Array} headers - Table headers
 * @param {Array} data - Table data
 * @param {Object} config - Table configuration
 */
function buildTableStructure(tableId, headers, data, config) {
    const functionName = "buildTableStructure";

    const container = document.getElementById(tableId);
    if (!container) {
        log("error", scriptName, functionName, `Container not found: ${tableId}`);
        return;
    }

    // Clear container
    container.innerHTML = '';

    // Create wrapper
    const wrapper = document.createElement('div');
    wrapper.classList.add('table-responsive');

    // Create table element
    const table = document.createElement('table');
    table.classList.add('table', 'table-striped');
    table.id = `${tableId}-table`;

    // Create header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');

    headers.forEach(header => {
        if (header.hidden) return;

        const th = document.createElement('th');
        th.textContent = header.text;
        th.dataset.column = header.id;

        if (header.sortable) {
            th.classList.add('sortable');
            th.innerHTML += ' <span class="sort-indicator"></span>';
        }

        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create table body
    const tbody = document.createElement('tbody');
    renderTableRows(tbody, data, headers);
    table.appendChild(tbody);

    // Add table to wrapper
    wrapper.appendChild(table);

    // Add search input if needed
    if (config.search !== false) {
        const searchWrapper = document.createElement('div');
        searchWrapper.classList.add('table-search-wrapper', 'mb-3');

        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.classList.add('form-control');
        searchInput.placeholder = 'Search...';
        searchInput.id = `${tableId}-search`;

        searchWrapper.appendChild(searchInput);
        container.appendChild(searchWrapper);
    }

    // Add table wrapper
    container.appendChild(wrapper);

    // Add pagination if enabled
    if (config.pagination) {
        const paginationWrapper = document.createElement('div');
        paginationWrapper.classList.add('table-pagination', 'mt-3');
        paginationWrapper.id = `${tableId}-pagination`;

        container.appendChild(paginationWrapper);
        initializePagination(tableId, data.length, config.defaultPerPage);
    }

    // Add export buttons if enabled
    if (config.enableExport) {
        const exportWrapper = document.createElement('div');
        exportWrapper.classList.add('table-export-wrapper', 'mt-3');

        const exportCsvBtn = document.createElement('button');
        exportCsvBtn.classList.add('btn', 'btn-sm', 'btn-outline-secondary', 'me-2');
        exportCsvBtn.textContent = 'Export CSV';
        exportCsvBtn.id = `${tableId}-export-csv`;

        exportWrapper.appendChild(exportCsvBtn);
        container.appendChild(exportWrapper);
    }

    log("debug", scriptName, functionName, `Table structure built for: ${tableId}`);
}

/**
 * Render table rows
 * @param {HTMLElement} tbody - Table body element
 * @param {Array} data - Data to render
 * @param {Array} headers - Table headers
 */
function renderTableRows(tbody, data, headers) {
    // Clear existing rows
    tbody.innerHTML = '';

    // Filter visible headers
    const visibleHeaders = headers.filter(header => !header.hidden);

    // Render each row
    data.forEach(item => {
        const row = document.createElement('tr');

        visibleHeaders.forEach(header => {
            const cell = document.createElement('td');
            cell.textContent = item[header.id] !== null && item[header.id] !== undefined
                ? item[header.id]
                : '';
            row.appendChild(cell);
        });

        tbody.appendChild(row);
    });
}

/**
 * Setup event listeners for table
 * @param {string} tableId - Table container ID
 * @param {Array} headers - Table headers
 * @param {Array} data - Table data
 * @param {Object} config - Table configuration
 */
function setupTableEventListeners(tableId, headers, data, config) {
    const functionName = "setupTableEventListeners";

    // Store original data
    const originalData = [...data];
    let currentData = [...data];
    let currentPage = 1;

    // Sorting
    const table = document.getElementById(`${tableId}-table`);
    if (table) {
        table.querySelectorAll('th.sortable').forEach(th => {
            th.addEventListener('click', () => {
                const column = th.dataset.column;

                // Remove sorting from other columns
                th.parentElement.querySelectorAll('th').forEach(header => {
                    if (header !== th) {
                        header.classList.remove('sort-asc', 'sort-desc');
                    }
                });

                // Toggle sort direction
                let direction = 'asc';
                if (th.classList.contains('sort-asc')) {
                    th.classList.remove('sort-asc');
                    th.classList.add('sort-desc');
                    direction = 'desc';
                } else {
                    th.classList.remove('sort-desc');
                    th.classList.add('sort-asc');
                }

                // Sort data
                currentData = sortData(currentData, column, direction);

                // Re-render table
                const tbody = table.querySelector('tbody');
                if (tbody) {
                    if (config.pagination) {
                        const perPage = config.defaultPerPage;
                        const startIdx = (currentPage - 1) * perPage;
                        renderTableRows(tbody, currentData.slice(startIdx, startIdx + perPage), headers);
                    } else {
                        renderTableRows(tbody, currentData, headers);
                    }
                }

                log("debug", scriptName, functionName, `Table sorted by ${column} ${direction}`);
            });
        });
    }

    // Search
    const searchInput = document.getElementById(`${tableId}-search`);
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const searchTerm = searchInput.value.trim();

            if (searchTerm) {
                currentData = filterData(originalData, searchTerm);
            } else {
                currentData = [...originalData];
            }

            // Reset to first page
            currentPage = 1;

            // Re-render table
            const tbody = table.querySelector('tbody');
            if (tbody) {
                if (config.pagination) {
                    const perPage = config.defaultPerPage;
                    renderTableRows(tbody, currentData.slice(0, perPage), headers);

                    // Update pagination
                    updatePagination(tableId, currentData.length, perPage, 1);
                } else {
                    renderTableRows(tbody, currentData, headers);
                }
            }

            log("debug", scriptName, functionName, `Table filtered by "${searchTerm}", ${currentData.length} results`);
        });
    }

    // Export
    const exportCsvBtn = document.getElementById(`${tableId}-export-csv`);
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', () => {
            exportToCsv(currentData, headers, `${tableId}-export.csv`);
        });
    }

    // Pagination events will be handled in initializePagination

    log("debug", scriptName, functionName, `Event listeners set up for table: ${tableId}`);
}

/**
 * Initialize pagination
 * @param {string} tableId - Table container ID
 * @param {number} totalItems - Total number of items
 * @param {number} perPage - Items per page
 */
function initializePagination(tableId, totalItems, perPage) {
    const functionName = "initializePagination";

    const paginationContainer = document.getElementById(`${tableId}-pagination`);
    if (!paginationContainer) {
        log("error", scriptName, functionName, `Pagination container not found: ${tableId}-pagination`);
        return;
    }

    updatePagination(tableId, totalItems, perPage, 1);

    log("debug", scriptName, functionName, `Pagination initialized for table: ${tableId}`);
}

/**
 * Update pagination
 * @param {string} tableId - Table container ID
 * @param {number} totalItems - Total number of items
 * @param {number} perPage - Items per page
 * @param {number} currentPage - Current page
 */
function updatePagination(tableId, totalItems, perPage, currentPage) {
    const functionName = "updatePagination";

    const paginationContainer = document.getElementById(`${tableId}-pagination`);
    if (!paginationContainer) return;

    // Clear container
    paginationContainer.innerHTML = '';

    // Calculate pages
    const totalPages = Math.ceil(totalItems / perPage);

    if (totalPages <= 1) {
        log("debug", scriptName, functionName, `No pagination needed for table: ${tableId}`);
        return; // No need for pagination
    }

    // Create pagination nav
    const nav = document.createElement('nav');
    const ul = document.createElement('ul');
    ul.classList.add('pagination');

    // Previous button
    const prevLi = document.createElement('li');
    prevLi.classList.add('page-item');
    if (currentPage === 1) prevLi.classList.add('disabled');

    const prevLink = document.createElement('a');
    prevLink.classList.add('page-link');
    prevLink.href = '#';
    prevLink.textContent = 'Previous';
    prevLink.addEventListener('click', (e) => {
        e.preventDefault();
        if (currentPage > 1) {
            goToPage(tableId, currentPage - 1, perPage);
        }
    });

    prevLi.appendChild(prevLink);
    ul.appendChild(prevLi);

    // Page numbers
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
        const pageLi = document.createElement('li');
        pageLi.classList.add('page-item');
        if (i === currentPage) pageLi.classList.add('active');

        const pageLink = document.createElement('a');
        pageLink.classList.add('page-link');
        pageLink.href = '#';
        pageLink.textContent = i;
        pageLink.addEventListener('click', (e) => {
            e.preventDefault();
            goToPage(tableId, i, perPage);
        });

        pageLi.appendChild(pageLink);
        ul.appendChild(pageLi);
    }

    // Next button
    const nextLi = document.createElement('li');
    nextLi.classList.add('page-item');
    if (currentPage === totalPages) nextLi.classList.add('disabled');

    const nextLink = document.createElement('a');
    nextLink.classList.add('page-link');
    nextLink.href = '#';
    nextLink.textContent = 'Next';
    nextLink.addEventListener('click', (e) => {
        e.preventDefault();
        if (currentPage < totalPages) {
            goToPage(tableId, currentPage + 1, perPage);
        }
    });

    nextLi.appendChild(nextLink);
    ul.appendChild(nextLi);

    nav.appendChild(ul);
    paginationContainer.appendChild(nav);

    log("debug", scriptName, functionName, `Pagination updated for table: ${tableId}, page ${currentPage}/${totalPages}`);
}

/**
 * Go to specific page
 * @param {string} tableId - Table container ID
 * @param {number} page - Page number
 * @param {number} perPage - Items per page
 */
function goToPage(tableId, page, perPage) {
    const functionName = "goToPage";

    // Get table
    const table = document.getElementById(`${tableId}-table`);
    if (!table) return;

    // Get current data
    const searchInput = document.getElementById(`${tableId}-search`);
    const searchTerm = searchInput ? searchInput.value.trim() : '';

    // This is simplified - in a real implementation, you would have a more robust
    // state management approach rather than relying on DOM traversal

    // Calculate start and end index
    const startIdx = (page - 1) * perPage;

    // Get headers
    const headers = [];
    table.querySelectorAll('thead th').forEach(th => {
        if (th.dataset.column) {
            headers.push({
                id: th.dataset.column,
                text: th.textContent.trim(),
                hidden: false
            });
        }
    });

    // Get current data (simplified approach)
    // In reality, you would have a state management approach
    // This is a placeholder for the actual implementation
    const currentData = []; // This would be your actual dataset

    // Render rows
    const tbody = table.querySelector('tbody');
    if (tbody) {
        renderTableRows(tbody, currentData.slice(startIdx, startIdx + perPage), headers);
    }

    // Update pagination
    updatePagination(tableId, currentData.length, perPage, page);

    log("debug", scriptName, functionName, `Navigated to page ${page} for table: ${tableId}`);
}

/**
 * Display error message in table container
 * @param {string} tableId - Table container ID
 * @param {string} message - Error message
 */
function displayErrorMessage(tableId, message) {
    const functionName = "displayErrorMessage";

    const container = document.getElementById(tableId);
    if (!container) return;

    container.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <strong>Error:</strong> ${message}
        </div>
    `;

    log("debug", scriptName, functionName, `Error message displayed for table: ${tableId}`);
}

/**
 * Display no data message in table container
 * @param {string} tableId - Table container ID
 */
function displayNoDataMessage(tableId) {
    const functionName = "displayNoDataMessage";

    const container = document.getElementById(tableId);
    if (!container) return;

    container.innerHTML = `
        <div class="alert alert-info" role="alert">
            No data available.
        </div>
    `;

    log("debug", scriptName, functionName, `No data message displayed for table: ${tableId}`);
}