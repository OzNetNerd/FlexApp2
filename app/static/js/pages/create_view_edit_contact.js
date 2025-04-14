// static/js/pages/create_view_edit_contact.js
import { setupAutoComplete } from '/static/js/autoComplete.js';

// Wait for page to fully load
window.addEventListener('load', function() {
  // Setup autocomplete for managers
  const managersInput = document.querySelector('#managers-input');
  if (managersInput) {
    setupAutoComplete({
      inputSelector: '#managers-input',
      dataUrl: '/api/contacts',
      inputName: 'managers',
      initialIds: JSON.parse(managersInput.dataset.initial || '[]')
    });
  }

  // Setup autocomplete for direct reports (previously called subordinates)
  const directReportsInput = document.querySelector('#direct-reports-input');
  if (directReportsInput) {
    setupAutoComplete({
      inputSelector: '#direct-reports-input',
      dataUrl: '/api/contacts',
      inputName: 'subordinates', // Keep original field name for backend compatibility
      initialIds: JSON.parse(directReportsInput.dataset.initial || '[]')
    });
  }

  // Setup autocomplete for opportunities
  const opportunitiesInput = document.querySelector('#opportunities-input');
  if (opportunitiesInput) {
    setupAutoComplete({
      inputSelector: '#opportunities-input',
      dataUrl: '/api/opportunities',
      inputName: 'opportunities',
      initialIds: JSON.parse(opportunitiesInput.dataset.initial || '[]')
    });
  }
});