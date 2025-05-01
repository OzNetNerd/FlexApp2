// Navbar JS functionality
import log from '/static/js/core/logger.js';

// Script name from template
const scriptName = 'navbar.js';

// Initialize the template
log("info", scriptName, "init", "🚀 Navbar template loaded");

// Debug events
document.addEventListener('DOMContentLoaded', () => {
  // Log main sections rendering
  log("debug", scriptName, "render", "Rendering navbar container");
  log("debug", scriptName, "render", "Brand logo rendered");
  log("debug", scriptName, "render", "Starting nav items rendering");

  // Log nav items rendering
  const navItems = document.querySelectorAll('.navbar-nav .nav-item');
  navItems.forEach(item => {
    const linkText = item.querySelector('.nav-link').textContent.trim();
    log("debug", scriptName, "nav_item", `Rendered nav item: ${linkText}`);
  });

  log("debug", scriptName, "blocks", "additional_nav_items block position");
  log("debug", scriptName, "render", "Search box rendered");
  log("debug", scriptName, "render", "Starting user menu rendering");

  // Log user state
  const userAvatar = document.querySelector('.user-avatar');
  if (userAvatar) {
    const userName = document.querySelector('.user-name').textContent.trim();
    log("debug", scriptName, "user", `Authenticated user avatar rendered for: ${userName}`);
    log("debug", scriptName, "auth", "Authenticated user menu items rendered");
  } else {
    log("debug", scriptName, "user", "Anonymous user icon rendered");
    log("debug", scriptName, "auth", "Anonymous user menu items rendered");
  }

  log("debug", scriptName, "render", "Dropdown menu items start");

  // Theme Toggle Button Functionality
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', toggleTheme);
  }
});

// Theme toggle function
function toggleTheme() {
  const body = document.body;
  const currentTheme = body.getAttribute('data-theme');

  if (currentTheme === 'dark') {
    body.removeAttribute('data-theme');
    localStorage.setItem('theme', 'light');
    log("info", scriptName, "theme", "Theme changed to light");
  } else {
    body.setAttribute('data-theme', 'dark');
    localStorage.setItem('theme', 'dark');
    log("info", scriptName, "theme", "Theme changed to dark");
  }
}

// Apply saved theme on page load
(function() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    document.body.setAttribute('data-theme', 'dark');
    log("info", scriptName, "theme", "Applied saved dark theme");
  }
})();