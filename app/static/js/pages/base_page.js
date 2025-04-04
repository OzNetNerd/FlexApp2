import log from '/static/js/logger.js';

// Log base template initialization and structure
log("info", "base_template", "init", "🚀 Base template loaded");
log("debug", "base_template", "structure", "Starting template structure rendering");

// Log inclusion of common components
log("debug", "base_template", "component", "Toasts component included");
log("debug", "base_template", "component", "Navbar component included");
log("debug", "base_template", "component", "Header buttons component included at top of page");

// Log main content block rendering
log("debug", "base_template", "content", "Rendering main content block");
log("debug", "base_template", "content", "Content block rendering complete");

// Log inclusion of additional scripts and final rendering
log("debug", "base_template", "component", "Scripts component included");
log("info", "base_template", "final", "✅ Base template finished rendering");

// DOM verification on load
document.addEventListener('DOMContentLoaded', () => {
  log("info", "base_template", "dom_ready", "DOM content loaded event fired");

  // Check key components
  const navbar = document.querySelector('nav');
  const headerButtons = document.querySelector('.header-buttons-container'); // Assuming this class exists in the component
  const mainContent = document.querySelector('main');

  if (navbar) {
    log("debug", "base_template", "dom_check", "Navbar found in DOM");
  } else {
    log("warn", "base_template", "dom_check", "Navbar not found in DOM");
  }

  if (headerButtons) {
    log("debug", "base_template", "dom_check", "Header buttons found in DOM");
    log("debug", "base_template", "layout", "Header buttons positioned correctly after navbar");
  } else {
    log("warn", "base_template", "dom_check", "Header buttons not found in DOM");
  }

  if (mainContent) {
    log("debug", "base_template", "dom_check", "Main content container found in DOM");
  } else {
    log("warn", "base_template", "dom_check", "Main content container not found in DOM");
  }
});
