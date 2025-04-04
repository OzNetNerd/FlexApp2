// Use an absolute path (or relative, as appropriate) for your logger
import log from '/static/js/logger.js';

// Access dynamic data passed from the HTML template
const data = window.headerButtonsData || {};

log("info", "_header_buttons.html", "init", "🚀 Buttons template loaded");
log("debug", "_header_buttons.html", "config", `Has ID: ${data.hasId}`);
log("debug", "_header_buttons.html", "config", `Read-only mode: ${data.readOnly}`);
log("debug", "_header_buttons.html", "route", `Current endpoint: ${data.endpoint}`);

if (data.hasId) {
  log("debug", "_header_buttons.html", "item_id", "Working with provided item ID");
} else {
  log("debug", "_header_buttons.html", "item_id", "No item ID provided");
}

if (data.hasId && !data.readOnly) {
  log("debug", "_header_buttons.html", "mode", "Edit mode - rendering Cancel button");
  log("debug", "_header_buttons.html", "url_gen", "Generating view URL for the provided item ID");
  log("debug", "_header_buttons.html", "button_rendered", "Cancel button rendered");
} else if (data.hasId && data.readOnly) {
  log("debug", "_header_buttons.html", "mode", "Read-only mode with ID - rendering action buttons");
  log("debug", "_header_buttons.html", "url_gen", "Generating create URL");
  log("debug", "_header_buttons.html", "button_rendered", "Add button rendered");
  log("debug", "_header_buttons.html", "url_gen", "Generating edit URL for the provided item ID");
  log("debug", "_header_buttons.html", "button_rendered", "Edit button rendered");
  log("debug", "_header_buttons.html", "button_rendered", "Delete button rendered (modal trigger)");
  log("debug", "_header_buttons.html", "url_gen", "Generating index URL for Back button");
  log("debug", "_header_buttons.html", "button_rendered", "Back button rendered");
} else {
  log("debug", "_header_buttons.html", "mode", "No buttons to render in current mode");
}

log("info", "_header_buttons.html", "render", "🔘 Button render context", data);

// DOM and event handling after the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Verify the button container and the number of controls
  const buttonContainer = document.querySelector('.d-flex.justify-content-end.align-items-center.gap-2');
  if (buttonContainer) {
    const buttonCount = buttonContainer.querySelectorAll('a, button').length;
    log("debug", "_header_buttons.html", "dom_check", `Button container found with ${buttonCount} controls`);

    if (buttonCount !== (data.buttons ? data.buttons.length : 0)) {
      log("warn", "_header_buttons.html", "dom_check", `Expected ${data.buttons.length} buttons but found ${buttonCount}`);
    } else {
      log("info", "_header_buttons.html", "dom_check", "All expected buttons are present in the DOM");
    }
  } else {
    log("warn", "_header_buttons.html", "dom_check", "Button container not found in DOM");
  }

  // Attach click event listeners to each button
  const buttons = document.querySelectorAll('.d-flex.justify-content-end.align-items-center.gap-2 a, .d-flex.justify-content-end.align-items-center.gap-2 button');
  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const buttonText = button.textContent.trim();
      log("info", "_header_buttons.html", "interaction", `Button clicked: ${buttonText}`);

      if (buttonText === "Delete") {
        log("debug", "_header_buttons.html", "modal", "Delete button clicked - should trigger modal");
      }
    });
  });

  log("info", "_header_buttons.html", "final", "✅ Buttons template finished rendering");
});
