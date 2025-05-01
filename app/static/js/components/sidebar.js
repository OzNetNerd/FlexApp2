/**
 * Sidebar Component - Core Functionality
 *
 * Handles the main sidebar functionality including:
 * - Collapsing/expanding the sidebar
 * - Persisting sidebar state across page loads
 * - Logging sidebar interactions
 *
 * @module components/sidebar
 * @requires core/logger
 */

import log from '../core/logger.js';

const SCRIPT_NAME = 'sidebar.js';

// Log that the sidebar component has loaded
log("info", SCRIPT_NAME, "init", "🚀 Sidebar component loaded");

/**
 * Initialize the sidebar component when the DOM is fully loaded
 */
document.addEventListener('DOMContentLoaded', () => {
  log("info", SCRIPT_NAME, "dom", "Setting up sidebar interactions");

  const sidebar = document.getElementById('sidebar');
  const sidebarCollapseBtn = document.getElementById('sidebarCollapseBtn');
  const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
  const sidebarOverlay = document.getElementById('sidebar-overlay');
  const body = document.body;

  // Initialize sidebar state from localStorage
  initializeSidebarState();

  // Set up event listeners
  setupEventListeners();

  log("info", SCRIPT_NAME, "final", "Sidebar functionality initialized");

  /**
   * Initialize the sidebar state based on localStorage
   */
  function initializeSidebarState() {
    // Check if sidebar is collapsed in localStorage
    const isSidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isSidebarCollapsed) {
      body.classList.add('sidebar-collapsed');
      log("debug", SCRIPT_NAME, "state", "Sidebar initialized as collapsed from storage");
    }
  }

  /**
   * Set up all event listeners for sidebar interactions
   */
  function setupEventListeners() {
    // Collapse button (desktop)
    sidebarCollapseBtn.addEventListener('click', () => {
      body.classList.toggle('sidebar-collapsed');
      const isNowCollapsed = body.classList.contains('sidebar-collapsed');
      localStorage.setItem('sidebarCollapsed', isNowCollapsed);
      log("info", SCRIPT_NAME, "action", `Sidebar ${isNowCollapsed ? 'collapsed' : 'expanded'}`);
    });

    // Toggle button and overlay (mobile)
    sidebarToggleBtn.addEventListener('click', () => {
      body.classList.remove('sidebar-open');
      log("info", SCRIPT_NAME, "action", "Sidebar closed on mobile");
    });

    sidebarOverlay.addEventListener('click', () => {
      body.classList.remove('sidebar-open');
      log("info", SCRIPT_NAME, "action", "Sidebar closed via overlay");
    });
  }
});