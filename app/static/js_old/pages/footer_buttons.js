// footer_buttons.js
import log from '/static/js/core/logger.js';

document.addEventListener('DOMContentLoaded', () => {
  // Log initial messages
  log("info", "_footer_buttons.html", "init", "🚀 Footer buttons template loaded");
  log("debug", "_footer_buttons.html", "config", "Has ID: " + window.footerButtonsConfig.hasId);
  log("debug", "_footer_buttons.html", "route", "Current endpoint: " + window.footerButtonsConfig.endpoint);

  // Mode-specific logging
  if (window.footerButtonsConfig.hasId) {
    log("debug", "_footer_buttons.html", "entity_id", "Working with item ID");
    try {
      const viewUrl = window.footerButtonsConfig.viewUrl;
      log("debug", "_footer_buttons.html", "url_gen", "Generated view URL: " + viewUrl);
    } catch (e) {
      log("error", "_footer_buttons.html", "url_gen", "Failed to generate view URL: " + e.message);
    }
  } else {
    log("debug", "_footer_buttons.html", "entity_id", "No item ID provided - new item mode");
    try {
      const indexUrl = window.footerButtonsConfig.indexUrl;
      log("debug", "_footer_buttons.html", "url_gen", "Generated index URL: " + indexUrl);
    } catch (e) {
      log("error", "_footer_buttons.html", "url_gen", "Failed to generate index URL: " + e.message);
    }
  }

  // Set up footer context for DOM verification
  const context = {
    hasId: window.footerButtonsConfig.hasId,
    endpoint: window.footerButtonsConfig.endpoint,
    baseRoute: window.footerButtonsConfig.baseRoute,
    buttons: []
  };

  if (context.hasId) {
    context.buttons.push("Cancel (to view)", "Update");
    context.cancelTarget = "view";
  } else {
    context.buttons.push("Cancel (to index)", "Create");
    context.cancelTarget = "index";
  }

  log("info", "_footer_buttons.html", "render", "🔘 Footer buttons render context", context);

  // DOM verification
  const footerContainer = document.querySelector('.footer-buttons-container');
  if (footerContainer) {
    const buttonCount = footerContainer.querySelectorAll('a, button').length;
    log("debug", "_footer_buttons.html", "dom_check", `Footer container found with ${buttonCount} controls`);

    if (buttonCount !== context.buttons.length) {
      log("warn", "_footer_buttons.html", "dom_check", `Expected ${context.buttons.length} buttons but found ${buttonCount}`);
    } else {
      log("info", "_footer_buttons.html", "dom_check", "All expected buttons are present in the DOM");
    }

    // Check if the buttons are enclosed in a form element
    const isInForm = footerContainer.closest('form') !== null;
    if (isInForm) {
      log("debug", "_footer_buttons.html", "dom_check", "Footer buttons are properly enclosed in a form element");
    } else {
      log("warn", "_footer_buttons.html", "dom_check", "Footer buttons are not in a form - submit button may not work");
    }
  } else {
    log("warn", "_footer_buttons.html", "dom_check", "Footer container not found in DOM");
  }

  // Final logging and event monitoring
  log("info", "_footer_buttons.html", "final", "Footer buttons template finished rendering");

  const buttons = document.querySelectorAll('.footer-buttons-container a, .footer-buttons-container button');
  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const buttonText = button.textContent.trim();
      const isSubmit = button.getAttribute('type') === 'submit';
      if (isSubmit) {
        log("info", "_footer_buttons.html", "interaction", `Form submit initiated via ${buttonText} button`);
      } else {
        log("info", "_footer_buttons.html", "interaction", `Navigation button clicked: ${buttonText}`);
      }
    });
  });
});
