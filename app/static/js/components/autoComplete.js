// /static/js/components/autoComplete.js

import log from '../core/logger.js'; // Adjusted path

const scriptName = 'autoComplete.js';

/**
 * Sets up autocomplete functionality for a single input field.
 * Fetches data, displays suggestions, manages selected items as badges.
 *
 * @param {object} config - Configuration object.
 * @param {string} config.inputSelector - CSS selector for the input field.
 * @param {string} config.dataUrl - URL endpoint to fetch autocomplete suggestions (expects { data: [...] }).
 * @param {string} config.inputName - The `name` attribute for the hidden inputs storing selected IDs.
 * @param {Array<number|string>} [config.initialIds=[]] - Array of IDs to pre-select.
 * @returns {Promise<void>} Resolves when setup and initial data fetch (if applicable) is complete or fails gracefully.
 */
export function setupAutoComplete({ inputSelector, dataUrl, inputName, initialIds = [] }) {
    const functionName = 'setupAutoComplete';

    log("info", scriptName, functionName, `🚀 Initializing autocomplete for selector: ${inputSelector}`, { dataUrl, inputName, initialIds });

    const input = document.querySelector(inputSelector);
    if (!input) {
        log("error", scriptName, functionName, `❌ Input field not found: ${inputSelector}. Aborting setup.`);
        return Promise.resolve(); // Resolve gracefully, nothing to set up
    }

    // --- Create DOM structure ---
    const container = document.createElement('div');
    container.className = 'autocomplete-container'; // Main wrapper

    const badgeContainer = document.createElement('div');
    badgeContainer.className = 'autocomplete-badge-container'; // Holds selected item badges
    badgeContainer.id = `${inputName}-badges`; // Make ID more specific

    const autocompleteList = document.createElement('div');
    autocompleteList.className = 'autocomplete-items-list'; // Dropdown list
    autocompleteList.style.display = 'none'; // Initially hidden

    // Restyle input slightly (optional)
    input.classList.add('autocomplete-input');
    input.placeholder = `Search for ${inputName}...`; // Add placeholder

    // Inject container and move input inside
    input.parentNode.insertBefore(container, input);
    container.appendChild(badgeContainer); // Badges first
    container.appendChild(input);          // Then the input
    container.appendChild(autocompleteList); // Then the dropdown

    // --- State variables ---
    let selectedItems = []; // Array to store selected {id, name, email?, ...} objects
    let allSuggestions = []; // Array to store all fetched suggestions {id, name, email?, ...}
    let currentHighlightIndex = -1; // For keyboard navigation

    // --- Fetch Data ---
    log("info", scriptName, functionName, `⏳ Fetching suggestions from: ${dataUrl}`);
    const fetchPromise = fetch(dataUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status} (${response.statusText})`);
            }
            return response.json();
        })
        .then(json => {
            log("debug", scriptName, functionName, `📦 Raw data received from ${dataUrl}:`, json);

            // **Crucial:** Validate data structure
            if (!json || !Array.isArray(json.data)) {
                 log("error", scriptName, functionName, `❌ Invalid data format from ${dataUrl}. Expected { data: [...] }.`, { received: json });
                 allSuggestions = []; // Ensure suggestions is an empty array on error
                 // Optionally show an error message to the user here
                 return; // Stop processing if data is invalid
            }

            // Expecting data in format { id: number|string, name?: string, first_name?: string, last_name?: string, email?: string }
            // Map to a consistent structure immediately
            allSuggestions = json.data.map(item => ({
                id: item.id,
                // Construct a display name, prioritizing 'name', then 'first/last', then 'id'
                name: item.name || `${item.first_name || ''} ${item.last_name || ''}`.trim() || `ID: ${item.id}`,
                email: item.email || '' // Ensure email is always defined (as string)
            }));

            log('info', scriptName, functionName, `✅ Loaded ${allSuggestions.length} suggestions from ${dataUrl}`);

            if (allSuggestions.length === 0) {
                log('warn', scriptName, functionName, `⚠️ No suggestions returned from ${dataUrl}`);
            } else {
                 // Log a few samples for debugging structure
                 log('debug', scriptName, functionName, `🔍 Sample suggestions (first 3):`, allSuggestions.slice(0, 3));
            }

            // Pre-fill selected items based on initialIds
            if (Array.isArray(initialIds) && initialIds.length > 0) {
                log('debug', scriptName, functionName, `🔍 Matching initial IDs:`, initialIds);
                const initialItems = allSuggestions.filter(s => initialIds.includes(s.id));

                const foundIds = initialItems.map(item => item.id);
                const missingIds = initialIds.filter(id => !foundIds.includes(id));
                if (missingIds.length > 0) {
                    log('warn', scriptName, functionName, `⚠️ Some initial IDs were not found in fetched data:`, missingIds);
                }

                // Use the mapped items, not the raw suggestions
                selectedItems = initialItems;
                renderBadges(); // Update UI with pre-filled items
                log('info', scriptName, functionName, `✅ Pre-filled ${selectedItems.length} items.`, selectedItems);
            }
        })
        .catch(error => {
            log('error', scriptName, functionName, `❌ Failed to fetch or process suggestions from ${dataUrl}`, { errorMessage: error.message });
            // Handle fetch error - maybe display a message in the input's container
            input.placeholder = `Error loading ${inputName}`;
            input.disabled = true; // Disable input if data load failed
        });

    // --- Event Listeners ---

    // Handle filtering and showing dropdown on input/focus
    const handleInputOrFocus = (event) => {
        const localFunctionName = `event:${event.type}`;
        const query = input.value.trim().toLowerCase();
        log('debug', scriptName, localFunctionName, `⚡ Event triggered. Query: "${query}"`);

        filterAndDisplaySuggestions(query);
    };

    input.addEventListener('input', handleInputOrFocus);
    input.addEventListener('focus', handleInputOrFocus); // Show suggestions on focus too

    // Handle keyboard navigation and selection
    input.addEventListener('keydown', (e) => {
        const localFunctionName = 'event:keydown';
        const suggestionElements = autocompleteList.querySelectorAll('.autocomplete-item'); // Get current items

        log('debug', scriptName, localFunctionName, `⌨️ Key pressed: ${e.key}`);

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault(); // Prevent cursor move
                if (suggestionElements.length > 0) {
                    currentHighlightIndex = (currentHighlightIndex + 1) % suggestionElements.length;
                    updateHighlight(suggestionElements);
                    log('debug', scriptName, localFunctionName, `⬇️ Arrow down: highlight index ${currentHighlightIndex}`);
                }
                break;
            case 'ArrowUp':
                e.preventDefault(); // Prevent cursor move
                 if (suggestionElements.length > 0) {
                     currentHighlightIndex = (currentHighlightIndex - 1 + suggestionElements.length) % suggestionElements.length;
                    updateHighlight(suggestionElements);
                     log('debug', scriptName, localFunctionName, `⬆️ Arrow up: highlight index ${currentHighlightIndex}`);
                 }
                break;
            case 'Enter':
                 if (currentHighlightIndex >= 0 && currentHighlightIndex < suggestionElements.length) {
                    e.preventDefault(); // Prevent form submission
                    log('debug', scriptName, localFunctionName, `✅ Enter pressed: Selecting highlighted item index ${currentHighlightIndex}`);
                    suggestionElements[currentHighlightIndex].click(); // Simulate click on highlighted item
                 }
                break;
            case 'Tab':
                // Select highlighted item on Tab ONLY if the list is visible and an item is highlighted
                if (autocompleteList.style.display !== 'none' && currentHighlightIndex >= 0 && currentHighlightIndex < suggestionElements.length) {
                    e.preventDefault(); // Prevent tabbing away
                    log('debug', scriptName, localFunctionName, `✅ Tab pressed: Selecting highlighted item index ${currentHighlightIndex}`);
                    suggestionElements[currentHighlightIndex].click();
                } else {
                    // Allow normal tab behavior if list hidden or no item highlighted
                    hideAutocompleteList();
                }
                break;
            case 'Escape':
                hideAutocompleteList();
                log('debug', scriptName, localFunctionName, `⏹️ Escape pressed: Hiding list.`);
                break;
            case 'Backspace':
                // Remove last badge if backspace is pressed in an empty input
                if (input.value === '' && selectedItems.length > 0) {
                    log('debug', scriptName, localFunctionName, `⬅️ Backspace in empty input: Removing last item.`);
                    const lastItem = selectedItems[selectedItems.length - 1];
                    removeItem(lastItem.id); // Use the existing removeItem function
                }
                break;
            default:
                // Reset highlight on other key presses that modify input
                 currentHighlightIndex = -1;
                 break; // Allow default input behavior
        }
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!container.contains(e.target)) {
            hideAutocompleteList();
            // log('debug', scriptName, 'event:documentClick', `🖱️ Click outside container, hiding dropdown.`);
        }
    });


    // --- Helper Functions ---

    function filterAndDisplaySuggestions(query) {
        const localFunctionName = 'filterAndDisplaySuggestions';
        autocompleteList.innerHTML = ''; // Clear previous suggestions
        currentHighlightIndex = -1;    // Reset highlight

        const lowerCaseQuery = query.toLowerCase();

        // Filter suggestions: exclude already selected items and match query
        const filteredSuggestions = allSuggestions.filter(suggestion => {
            // Exclude if already selected
            if (selectedItems.some(selected => selected.id === suggestion.id)) {
                return false;
            }
            // If query is empty, show some suggestions (e.g., first 10)
            if (!lowerCaseQuery) {
                return true; // Include all non-selected items when query is empty
            }
            // Match query against name or email
            const nameMatch = suggestion.name.toLowerCase().includes(lowerCaseQuery);
            const emailMatch = suggestion.email && suggestion.email.toLowerCase().includes(lowerCaseQuery);
            return nameMatch || emailMatch;
        }).slice(0, 10); // Limit results

        log('debug', scriptName, localFunctionName, `🔍 Query: "${query}". Found ${filteredSuggestions.length} suggestions.`);

        if (filteredSuggestions.length === 0) {
            autocompleteList.style.display = 'none';
            if (query) { // Only log warning if there was an actual query
                 log('warn', scriptName, localFunctionName, `⚠️ No suggestions found for query '${query}'`);
            }
            return;
        }

        // Create and append suggestion elements
        filteredSuggestions.forEach((item) => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item';
            // Display name and email (if available)
            div.textContent = item.email ? `${item.name} (${item.email})` : item.name;
            // Store item data directly on the element for easy access on click
            div.dataset.itemId = item.id; // Store ID for adding

            div.addEventListener('click', () => {
                log('debug', scriptName, 'event:suggestionClick', `🖱️ Clicked suggestion:`, item);
                addItem(item);
                input.value = ''; // Clear input after selection
                hideAutocompleteList(); // Hide list after selection
                input.focus(); // Keep focus on input for next entry
            });
            autocompleteList.appendChild(div);
        });

        autocompleteList.style.display = 'block'; // Show the list
    }

     function updateHighlight(suggestionElements) {
         suggestionElements.forEach((item, index) => {
             item.classList.toggle('highlight', index === currentHighlightIndex);
             // Scroll into view if needed
             if (index === currentHighlightIndex) {
                 item.scrollIntoView({ block: 'nearest' });
             }
         });
     }

    function hideAutocompleteList() {
        autocompleteList.style.display = 'none';
        currentHighlightIndex = -1; // Reset highlight when hiding
    }


    function addItem(item) {
        const localFunctionName = 'addItem';
        // Prevent duplicates
        if (selectedItems.some(selected => selected.id === item.id)) {
            log('warn', scriptName, localFunctionName, `⚠️ Item already selected:`, item);
            return;
        }
        selectedItems.push(item);
        renderBadges();
        log('info', scriptName, localFunctionName, `➕ Added item: ${item.name} (ID: ${item.id})`);
    }

    function removeItem(idToRemove) {
        const localFunctionName = 'removeItem';
        const itemIndex = selectedItems.findIndex(item => item.id === idToRemove);
        if (itemIndex > -1) {
            const removedItem = selectedItems.splice(itemIndex, 1)[0];
            renderBadges();
            log('info', scriptName, localFunctionName, `➖ Removed item: ${removedItem.name} (ID: ${removedItem.id})`);
            // Optionally, refresh suggestions if list is open
            if (autocompleteList.style.display === 'block') {
                 filterAndDisplaySuggestions(input.value.trim());
            }
        } else {
            log('warn', scriptName, localFunctionName, `⚠️ Tried to remove item ID not found in selection: ${idToRemove}`);
        }
    }

    // Renders badges and hidden inputs based on `selectedItems`
    function renderBadges() {
        const localFunctionName = 'renderBadges';
        badgeContainer.innerHTML = ''; // Clear existing badges and hidden inputs

        log('debug', scriptName, localFunctionName, `🔄 Rendering ${selectedItems.length} badges...`);

        selectedItems.forEach(item => {
            // Badge visual element
            const badge = document.createElement('div');
            badge.className = 'badge autocomplete-badge'; // Add custom class

            const span = document.createElement('span');
             // Display name and email (if available and distinct from name)
             span.textContent = (item.email && item.email !== item.name) ? `${item.name} (${item.email})` : item.name;


            const removeBtn = document.createElement('span');
            removeBtn.className = 'badge-remove-btn'; // Style this for clickable 'x'
            removeBtn.textContent = '×'; // Use multiplication sign for 'x'
            removeBtn.title = `Remove ${item.name}`; // Tooltip
            removeBtn.onclick = (e) => {
                e.stopPropagation(); // Prevent click from propagating to container
                removeItem(item.id);
            };

            badge.appendChild(span);
            badge.appendChild(removeBtn);
            badgeContainer.appendChild(badge);

            // Hidden input for form submission
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = inputName; // Use the provided input name
            hiddenInput.value = item.id;
            badgeContainer.appendChild(hiddenInput); // Append hidden input *after* its badge
        });

        const selectedIds = selectedItems.map(item => item.id);
        log('debug', scriptName, localFunctionName, `🏷️ Badges updated. Current selected IDs:`, selectedIds);
    }

    // Return the promise that resolves when the initial data fetch is done
    return fetchPromise;
}


/**
 * Initializes all autocomplete fields defined by data attributes on the page.
 * Looks for inputs with `data-autocomplete="true"` and expects other data attributes like
 * `data-url`, `data-input-name`, `data-initial`.
 */
export function initAutoCompleteFromDataAttributes() {
    const functionName = 'initAutoCompleteFromDataAttributes';
    log("info", scriptName, functionName, "🏁 Scanning for autocomplete fields marked with data attributes...");

    const inputs = document.querySelectorAll('input[data-autocomplete="true"]');
    log("info", scriptName, functionName, `🔍 Found ${inputs.length} potential autocomplete inputs.`);

    if (inputs.length === 0) {
        return Promise.resolve(); // No fields found, resolve immediately
    }

    const setupPromises = [];

    inputs.forEach((input, index) => {
        const inputId = input.id || `autocomplete-input-${index}`; // Use ID or generate one for logging
        log("debug", scriptName, functionName, `⚙️ Processing input: #${inputId}`);

        const dataUrl = input.dataset.url;
        const inputName = input.dataset.inputName;
        const initialDataJson = input.dataset.initial || '[]'; // Default to empty array string

        // Basic validation
        if (!dataUrl) {
            log("error", scriptName, functionName, `❌ Input #${inputId} is missing 'data-url'. Skipping.`);
            return; // Skip this input
        }
        if (!inputName) {
            log("error", scriptName, functionName, `❌ Input #${inputId} is missing 'data-input-name'. Skipping.`);
            return; // Skip this input
        }

        let initialIds = [];
        try {
            initialIds = JSON.parse(initialDataJson);
            if (!Array.isArray(initialIds)) {
                log("warn", scriptName, functionName, `⚠️ Input #${inputId} 'data-initial' is not a valid JSON array. Using [].`, { raw: initialDataJson });
                initialIds = [];
            }
        } catch (e) {
            log("error", scriptName, functionName, `❌ Input #${inputId} has invalid JSON in 'data-initial'. Using [].`, { raw: initialDataJson, error: e.message });
            initialIds = [];
        }

        // Use the input's ID as the selector for setupAutoComplete
        if (!input.id) { input.id = inputId; } // Ensure the input has an ID

        const config = {
            inputSelector: `#${input.id}`,
            dataUrl: dataUrl,
            inputName: inputName,
            initialIds: initialIds
        };

        log("info", scriptName, functionName, `➕ Adding setup promise for #${input.id}`, config);
        // setupAutoComplete returns a promise, collect them
        setupPromises.push(setupAutoComplete(config));
    });

    // Wait for all autocomplete setups (including fetches) to complete
    return Promise.all(setupPromises).then(() => {
        log("info", scriptName, functionName, `✅ All (${setupPromises.length}) autocomplete fields initialized.`);
    }).catch(error => {
        log("error", scriptName, functionName, `❌ Error during initialization of one or more autocomplete fields.`, error);
        // Even if some fail, we might consider the overall process "done" but flawed.
        // Depending on requirements, you might want to reject the promise here.
    });
}

// Example of how you might call the initialization function in your main script:
// document.addEventListener('DOMContentLoaded', () => {
//   initAutoCompleteFromDataAttributes();
// });