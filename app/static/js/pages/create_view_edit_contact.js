// static/js/pages/create_view_edit_contact.js
import log from '/static/js/logger.js';
import { setupAutoComplete } from '/static/js/autoComplete.js';

// Wait for page to fully load
window.addEventListener('load', function() {
  log("info", "create_view_edit_contact", "load", "Page loaded, initializing autocomplete for inputs");

  // Setup autocomplete for managers
  const managersInput = document.querySelector('#managers-input');
  if (managersInput) {
    log("info", "create_view_edit_contact", "setup", "Setting up autocomplete for managers");
    setupAutoComplete({
      inputSelector: '#managers-input',
      dataUrl: '/api/contacts',
      inputName: 'managers',
      initialIds: JSON.parse(managersInput.dataset.initial || '[]')
    }).then(response => {
      log("info", "create_view_edit_contact", "autocomplete_success", "Autocomplete setup for managers succeeded", response);
    }).catch(error => {
      log("error", "create_view_edit_contact", "autocomplete_error", "Autocomplete setup for managers failed", error);
    });
  }

  // Setup autocomplete for direct reports (previously called subordinates)
  const directReportsInput = document.querySelector('#direct-reports-input');
  if (directReportsInput) {
    log("info", "create_view_edit_contact", "setup", "Setting up autocomplete for direct reports");
    setupAutoComplete({
      inputSelector: '#direct-reports-input',
      dataUrl: '/api/contacts',
      inputName: 'subordinates', // Keep original field name for backend compatibility
      initialIds: JSON.parse(directReportsInput.dataset.initial || '[]')
    }).then(response => {
      log("info", "create_view_edit_contact", "autocomplete_success", "Autocomplete setup for direct reports succeeded", response);
    }).catch(error => {
      log("error", "create_view_edit_contact", "autocomplete_error", "Autocomplete setup for direct reports failed", error);
    });
  }

  // Setup autocomplete for opportunities
  const opportunitiesInput = document.querySelector('#opportunities-input');
  if (opportunitiesInput) {
    log("info", "create_view_edit_contact", "setup", "Setting up autocomplete for opportunities");
    setupAutoComplete({
      inputSelector: '#opportunities-input',
      dataUrl: '/api/opportunities',
      inputName: 'opportunities',
      initialIds: JSON.parse(opportunitiesInput.dataset.initial || '[]')
    }).then(response => {
      log("info", "create_view_edit_contact", "autocomplete_success", "Autocomplete setup for opportunities succeeded", response);
    }).catch(error => {
      log("error", "create_view_edit_contact", "autocomplete_error", "Autocomplete setup for opportunities failed", error);
    });
  }
});
