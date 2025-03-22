// const scriptName = "columnDropdown.js";

// /**
//  * Populates the column visibility dropdown with checkboxes.
//  */
// function populateDropdown() {
//     const functionName = "populateDropdown";

//     const dropdownMenu = document.getElementById("dropdown-menu");

//     if (!dropdownMenu) {
//         log("error", `${scriptName}:${functionName}`, "❌ Dropdown menu element not found.");
//         return;
//     }

//     if (!window.gridOptions) {
//         log("error", `${scriptName}:${functionName}`, "❌ Grid options not available.");
//         return;
//     }

//     // Check API availability - try both main API and columnApi
//     const api = window.gridOptions.api;
//     const columnApi = window.gridOptions.columnApi;

//     if (!api) {
//         log("error", `${scriptName}:${functionName}`, "❌ Grid API not available.");
//         return;
//     }

//     // Check which API to use for column operations
//     let getColumnStateFn;
//     let setColumnVisibleFn;

//     if (typeof api.getColumnState === 'function') {
//         getColumnStateFn = () => api.getColumnState();
//         log("info", `${scriptName}:${functionName}`, "Using api.getColumnState()");
//     } else if (columnApi && typeof columnApi.getColumnState === 'function') {
//         getColumnStateFn = () => columnApi.getColumnState();
//         log("info", `${scriptName}:${functionName}`, "Using columnApi.getColumnState()");
//     } else {
//         log("error", `${scriptName}:${functionName}`, "❌ No compatible getColumnState method found");
//         return;
//     }

//     if (typeof api.setColumnVisible === 'function') {
//         setColumnVisibleFn = (colId, visible) => api.setColumnVisible(colId, visible);
//         log("info", `${scriptName}:${functionName}`, "Using api.setColumnVisible()");
//     } else if (columnApi && typeof columnApi.setColumnVisible === 'function') {
//         setColumnVisibleFn = (colId, visible) => columnApi.setColumnVisible(colId, visible);
//         log("info", `${scriptName}:${functionName}`, "Using columnApi.setColumnVisible()");
//     } else {
//         log("error", `${scriptName}:${functionName}`, "❌ No compatible setColumnVisible method found");
//         return;
//     }

//     // Store the functions on window.gridOptions for later use
//     window.gridOptions._getColumnStateFn = getColumnStateFn;
//     window.gridOptions._setColumnVisibleFn = setColumnVisibleFn;

//     dropdownMenu.innerHTML = ""; // Clear existing checkboxes
//     const columnDefs = window.gridOptions.columnDefs;
//     const columnState = getColumnStateFn(); // Get current column visibility state

//     log("info", `${scriptName}:${functionName}`, "📋 Populating dropdown with columns:", columnDefs);

//     columnDefs.forEach(col => {
//         const label = document.createElement("label");
//         const checkbox = document.createElement("input");
//         checkbox.type = "checkbox";

//         // Find the current state of the column and set the checkbox state accordingly
//         const column = columnState.find(c => c.colId === col.field);
//         checkbox.checked = column ? column.hide !== true : true; // If `hide` is `true`, it's hidden

//         checkbox.dataset.colId = col.field;
//         checkbox.addEventListener("change", function () {
//             const colId = this.dataset.colId;
//             const isVisible = this.checked;
//             log("info", `${scriptName}:${functionName}`, `🔄 Toggling column: ${colId} → ${isVisible ? "Visible" : "Hidden"}`);
//             window.gridOptions._setColumnVisibleFn(colId, isVisible);
//         });

//         label.appendChild(checkbox);
//         label.appendChild(document.createTextNode(` ${col.headerName}`));
//         dropdownMenu.appendChild(label);
//     });

//     log("info", `${scriptName}:${functionName}`, "✅ Dropdown population complete.");
// }

// /**
//  * Toggles the dropdown visibility.
//  */
// function toggleDropdown() {
//     const functionName = "toggleDropdown";
//     const dropdownMenu = document.getElementById("dropdown-menu");

//     if (!dropdownMenu) {
//         log("error", `${scriptName}:${functionName}`, "❌ Dropdown menu element not found.");
//         return;
//     }

//     const isCurrentlyOpen = dropdownMenu.style.display === "block";

//     dropdownMenu.style.display = isCurrentlyOpen ? "none" : "block";
//     log("info", `${scriptName}:${functionName}`, `🔄 Dropdown ${isCurrentlyOpen ? "closed" : "opened"}.`);
// }

// // Ensure dropdown closes when clicking outside
// document.addEventListener("click", function (event) {
//     const functionName = "outsideClickHandler";
//     const dropdown = document.getElementById("dropdown");

//     if (!dropdown) return;

//     if (!dropdown.contains(event.target)) {
//         const dropdownMenu = document.getElementById("dropdown-menu");
//         if (dropdownMenu) {
//             dropdownMenu.style.display = "none";
//             log("info", `${scriptName}:${functionName}`, "🔄 Dropdown closed due to outside click.");
//         }
//     }
// });

// // Make functions available globally
// window.populateDropdown = populateDropdown;
// window.toggleDropdown = toggleDropdown;

// // Ensure dropdown is populated after the grid is ready
// document.addEventListener("DOMContentLoaded", function () {
//     const functionName = "DOMContentLoadedHandler";
//     log("info", `${scriptName}:${functionName}`, "📋 DOM loaded, will check for grid initialization.");

//     // Check if gridOptions is already initialized
//     if (window.gridOptions && window.gridOptions.api) {
//         log("info", `${scriptName}:${functionName}`, "📋 Grid options already available, populating dropdown.");
//         populateDropdown();
//         return;
//     }

//     // Otherwise wait for grid initialization
//     let checkCount = 0;
//     const maxChecksd = 40; // 20 seconds (40 * 500ms)

//     const checkGridOptions = setInterval(() => {
//         checkCount++;

//         if (window.gridOptions && window.gridOptions.api) {
//             clearInterval(checkGridOptions);
//             log("info", `${scriptName}:${functionName}`, "📋 Grid options found, populating dropdown.");
//             populateDropdown();
//         } else if (checkCount >= maxChecks) {
//             clearInterval(checkGridOptions);
//             log("error", `${scriptName}:${functionName}`, "❌ Timed out waiting for grid options.");
//         }
//     }, 500);
// });