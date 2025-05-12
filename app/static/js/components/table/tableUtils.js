/**
 * tableUtils.js - Utility functions for table management
 */

import log from '/static/js/core/logger.js';
const scriptName = "tableUtils.js";

/**
 * Debounce helper
 */
export function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

/**
 * Function to ensure proper spacing between sections
 */
export function fixLayoutSpacing(gridApiReference) {
  // Add a resize observer to table container
  const tableContainer = document.getElementById('table-container');
  const chartSection = document.querySelector('.dashboard-section:last-child');

  if (!tableContainer || !chartSection) return;

  // Determine if we need additional spacing
  function adjustSpacing() {
    const tableRect = tableContainer.getBoundingClientRect();
    const tableBottom = tableRect.bottom;

    // Add more spacing if needed
    const sections = document.querySelectorAll('.dashboard-section');
    sections.forEach(section => {
      section.style.marginBottom = '3rem';
      section.style.overflow = 'visible';
    });

    // Ensure chart section has enough space
    chartSection.style.paddingTop = '1rem';
    chartSection.style.marginTop = '2rem';
  }

  // Run adjustment once on page load
  window.addEventListener('DOMContentLoaded', () => {
    setTimeout(adjustSpacing, 500); // Wait for grid to render
  });

  // Run adjustment after grid is ready - safer way to add event listener
  if (typeof gridApiReference !== 'undefined' && gridApiReference) {
    try {
      gridApiReference.addEventListener('gridSizeChanged', adjustSpacing);
    } catch (e) {
      log("warn", scriptName, "fixLayoutSpacing", "Could not add gridSizeChanged listener", e);
      // Alternative fallback for layout adjustments if event listener fails
      setTimeout(adjustSpacing, 1000);
    }
  }

  // Run adjustment on window resize
  window.addEventListener('resize', adjustSpacing);
}

/**
 * Handle grid resize when columns are toggled
 */
export function handleGridResize(gridApiReference) {
  if (!gridApiReference) {
    log("warn", scriptName, "handleGridResize", "Grid API not available");
    return;
  }

  log("info", scriptName, "handleGridResize", "Triggering grid resize");

  // Use setTimeout to ensure this runs after the DOM has updated
  setTimeout(() => {
    try {
      // Size columns to fit available width
      gridApiReference.sizeColumnsToFit();

      // Manually trigger redraw
      gridApiReference.refreshCells({ force: true });
      gridApiReference.redrawRows();
    } catch (err) {
      log("error", scriptName, "handleGridResize", "Error during grid resize:", err);
    }
  }, 0);
}