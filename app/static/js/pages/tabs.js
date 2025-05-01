/**
 * Tab Initialization Script
 *
 * Handles the activation of Bootstrap tabs when the DOM is loaded.
 * Ensures that the active tab is properly displayed by adding necessary classes.
 */
document.addEventListener('DOMContentLoaded', function() {
  // Get the active tab button
  const activeTab = document.querySelector('.nav-link.active[data-bs-toggle="tab"]');
  if (activeTab) {
    // Get the target tab pane ID
    const targetId = activeTab.getAttribute('data-bs-target');
    // Find the tab pane
    const tabPane = document.querySelector(targetId);
    if (tabPane) {
      // Add the necessary classes to make it visible
      tabPane.classList.add('show', 'active');
    }
  }
});