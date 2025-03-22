// import log from './logger.js';

// // Function to log page and table details
// document.addEventListener("DOMContentLoaded", () => {
//     const scriptName = "pageLogger";
//     const functionName = "DOMContentLoaded";

//     const pageName = document.title || "Unknown Page";
//     const tableContainer = document.getElementById("table-container");
//     const tableDetails = tableContainer ? { apiUrl: tableContainer.dataset.apiUrl } : "No table found";

//     // Retrieve page configuration from the script tag
//     let pageConfig = {};
//     try {
//         const configElement = document.getElementById("page-config");
//         if (configElement) {
//             pageConfig = JSON.parse(configElement.textContent);
//         }
//     } catch (error) {
//         log("error", scriptName, functionName, "❌ Failed to parse page config", { error: error.message });
//     }

//     // Log page details
//     log("info", scriptName, functionName, "✅💾 Page Loaded", { pageName });
//     log("info", scriptName, functionName, "✅💾 Table Details", tableDetails);
//     log("debug", scriptName, functionName, "✅💾 Page Config", pageConfig);
// });
