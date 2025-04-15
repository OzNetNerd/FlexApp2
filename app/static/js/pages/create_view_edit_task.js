import { setupAutoComplete } from '/static/js/autoComplete.js';
import log from '/static/js/logger.js';

const scriptName = 'create_view_edit_task.js';

document.addEventListener('DOMContentLoaded', function() {
    log('info', scriptName, 'init', '🚀 Initializing task edit page');
    initTaskAutocompletes();
});

/**
 * Initialize autocomplete fields for the task edit page
 */
function initTaskAutocompletes() {
    const functionName = 'initTaskAutocompletes';
    log('info', scriptName, functionName, '🔍 Setting up autocomplete fields for task');

    // Customer Autocomplete
    const customerInput = document.getElementById('customer-input');
    if (customerInput) {
        log('debug', scriptName, functionName, '📋 Found customer input field');

        // Get initial value if present
        let initialIds = [];
        try {
            initialIds = JSON.parse(customerInput.dataset.initial || '[]');

            // If there's an initial value, set the input field text
            if (initialIds.length > 0 && customerInput.dataset.entityName) {
                customerInput.value = customerInput.dataset.entityName;
            }

            log('debug', scriptName, functionName, '🏷️ Initial customer ID:', initialIds);
        } catch (e) {
            log('error', scriptName, functionName, '❌ Error parsing initial customer data:', e);
        }

        // Set up the autocomplete
        setupAutoComplete({
            inputSelector: '#customer-input',
            dataUrl: '/api/search/companies',
            inputName: 'customer_id',
            initialIds: initialIds,
            singleSelect: true
        }).then(() => {
            log('info', scriptName, functionName, '✅ Customer autocomplete setup complete');

            // Event handler for customer selection
            const autocompleteItems = document.querySelectorAll('#customer-results .autocomplete-item');
            autocompleteItems.forEach(item => {
                item.addEventListener('click', function() {
                    const customerId = this.dataset.id;
                    const customerName = this.textContent;

                    // Update the hidden input
                    document.getElementById('customer_id').value = customerId;

                    log('info', scriptName, functionName, `✅ Selected customer: ${customerName} (ID: ${customerId})`);
                });
            });
        });
    } else {
        log('warn', scriptName, functionName, '⚠️ Customer input field not found');
    }

    // Owner Autocomplete
    const ownerInput = document.getElementById('owner-input');
    if (ownerInput) {
        log('debug', scriptName, functionName, '📋 Found owner input field');

        // Get initial value if present
        let initialIds = [];
        try {
            initialIds = JSON.parse(ownerInput.dataset.initial || '[]');

            // If there's an initial value, set the input field text
            if (initialIds.length > 0 && ownerInput.dataset.entityName) {
                ownerInput.value = ownerInput.dataset.entityName;
            }

            log('debug', scriptName, functionName, '🏷️ Initial owner ID:', initialIds);
        } catch (e) {
            log('error', scriptName, functionName, '❌ Error parsing initial owner data:', e);
        }

        // Set up the autocomplete
        setupAutoComplete({
            inputSelector: '#owner-input',
            dataUrl: '/api/search/users',
            inputName: 'owner_id',
            initialIds: initialIds,
            singleSelect: true
        }).then(() => {
            log('info', scriptName, functionName, '✅ Owner autocomplete setup complete');

            // Event handler for owner selection
            const autocompleteItems = document.querySelectorAll('#owner-results .autocomplete-item');
            autocompleteItems.forEach(item => {
                item.addEventListener('click', function() {
                    const ownerId = this.dataset.id;
                    const ownerName = this.textContent;

                    // Update the hidden input
                    document.getElementById('owner_id').value = ownerId;

                    log('info', scriptName, functionName, `✅ Selected owner: ${ownerName} (ID: ${ownerId})`);
                });
            });
        });
    } else {
        log('warn', scriptName, functionName, '⚠️ Owner input field not found');
    }
}

// Update the autocomplete.js to handle single select fields
// This code extends the existing functionality

export function updateSingleSelectAutoComplete() {
    // Get all autocomplete fields that have already been initialized
    const autocompleteInputs = document.querySelectorAll('.autocomplete-input');

    autocompleteInputs.forEach(input => {
        const hiddenInput = input.nextElementSibling;
        const resultsContainer = input.nextElementSibling.nextElementSibling;

        if (hiddenInput && resultsContainer) {
            // Update the hidden input when a selection is made
            resultsContainer.addEventListener('click', function(e) {
                if (e.target.classList.contains('autocomplete-item')) {
                    const id = e.target.dataset.id;
                    const name = e.target.textContent.trim();

                    // Update hidden input
                    hiddenInput.value = id;

                    // Update display input
                    input.value = name;

                    // Hide dropdown
                    resultsContainer.style.display = 'none';

                    log('info', scriptName, 'updateSingleSelectAutoComplete', `Selected item with ID ${id}: ${name}`);
                }
            });
        }
    });
}