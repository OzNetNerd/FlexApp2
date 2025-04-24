/**
 * js/components/common/autoComplete.js
 * Autocomplete component for input fields
 */

import log from '/static/js/core/utils/logger.js';
import { fetchApiData } from '/static/js/core/utils/utils.js';

const scriptName = "autoComplete.js";

// Track instances of autocomplete fields
const activeAutoCompletes = new Map();

/**
 * Initialize autocomplete on all fields with data-autocomplete attribute
 */
document.addEventListener('DOMContentLoaded', () => {
    const functionName = "DOMContentLoaded";

    // Find all autocomplete fields
    const autoCompleteFields = document.querySelectorAll('[data-autocomplete]');

    if (autoCompleteFields.length === 0) {
        log("debug", scriptName, functionName, "No autocomplete fields found");
        return;
    }

    log("info", scriptName, functionName, `Found ${autoCompleteFields.length} autocomplete fields`);

    // Initialize each field
    autoCompleteFields.forEach(field => {
        const sourceUrl = field.dataset.autocompleteSource;
        const displayField = field.dataset.autocompleteDisplay || 'name';
        const valueField = field.dataset.autocompleteValue || 'id';
        const minChars = parseInt(field.dataset.autocompleteMinChars || '2', 10);

        if (!sourceUrl) {
            log("error", scriptName, functionName, "❌ Missing data-autocomplete-source attribute", { fieldId: field.id });
            return;
        }

        initAutoComplete(field.id, {
            sourceUrl,
            displayField,
            valueField,
            minChars
        });
    });
});

/**
 * Initialize autocomplete on a specific field
 * @param {string} fieldId - The ID of the input field
 * @param {Object} options - Autocomplete options
 * @param {string} options.sourceUrl - API URL for autocomplete suggestions
 * @param {string} options.displayField - Field name to display in suggestions
 * @param {string} options.valueField - Field name to use as value
 * @param {number} options.minChars - Minimum characters before triggering autocomplete
 * @param {Function} options.onSelect - Callback when item is selected
 */
export function initAutoComplete(fieldId, options) {
    const functionName = "initAutoComplete";

    const field = document.getElementById(fieldId);
    if (!field) {
        log("error", scriptName, functionName, `❌ Field not found: ${fieldId}`);
        return;
    }

    log("info", scriptName, functionName, `Initializing autocomplete for ${fieldId}`);

    // Default options
    const defaultOptions = {
        minChars: 2,
        displayField: 'name',
        valueField: 'id',
        onSelect: null
    };

    // Merge options
    const config = { ...defaultOptions, ...options };

    // Create suggestion container
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'autocomplete-suggestions';
    suggestionsContainer.style.display = 'none';
    suggestionsContainer.style.position = 'absolute';
    suggestionsContainer.style.zIndex = '1000';
    suggestionsContainer.style.backgroundColor = '#fff';
    suggestionsContainer.style.border = '1px solid #ddd';
    suggestionsContainer.style.maxHeight = '200px';
    suggestionsContainer.style.overflowY = 'auto';
    suggestionsContainer.style.width = `${field.offsetWidth}px`;

    // Add suggestions container after field
    field.parentNode.style.position = 'relative';
    field.parentNode.appendChild(suggestionsContainer);

    // Create hidden input for value if it doesn't exist
    let valueInput = document.getElementById(`${fieldId}-value`);
    if (!valueInput) {
        valueInput = document.createElement('input');
        valueInput.type = 'hidden';
        valueInput.id = `${fieldId}-value`;
        valueInput.name = `${field.name}_value`;
        field.parentNode.appendChild(valueInput);
    }

    // Variables for autocomplete state
    let suggestions = [];
    let currentFocus = -1;
    let lastQuery = '';
    let debounceTimer = null;

    // Store instance
    activeAutoCompletes.set(fieldId, {
        field,
        suggestionsContainer,
        valueInput,
        config,
        suggestions
    });

    // Event listeners
    field.addEventListener('input', handleInput);
    field.addEventListener('keydown', handleKeyDown);
    document.addEventListener('click', handleDocumentClick);

    /**
     * Handle input event
     */
    function handleInput() {
        const query = field.value.trim();

        // Skip if query is too short or unchanged
        if (query === lastQuery || query.length < config.minChars) {
            if (query.length === 0) {
                // Clear suggestions and value if field is empty
                suggestionsContainer.style.display = 'none';
                valueInput.value = '';
            }
            return;
        }

        lastQuery = query;

        // Clear previous debounce timer
        if (debounceTimer) {
            clearTimeout(debounceTimer);
        }

        // Debounce API calls
        debounceTimer = setTimeout(() => {
            fetchSuggestions(query);
        }, 300);
    }

    /**
     * Fetch suggestions from API
     * @param {string} query - The search query
     */
    async function fetchSuggestions(query) {
        try {
            // Build the API URL with query parameter
            const url = `${config.sourceUrl}?q=${encodeURIComponent(query)}`;

            log("debug", scriptName, functionName, `Fetching suggestions for: ${query}`);

            const response = await fetchApiData(scriptName, functionName, url);

            if (response && (response.data || Array.isArray(response))) {
                // Handle different response structures
                suggestions = Array.isArray(response) ? response : (Array.isArray(response.data) ? response.data : []);

                // Display suggestions
                displaySuggestions(suggestions);
            } else {
                log("warn", scriptName, functionName, "⚠️ No suggestions returned from API");
                suggestionsContainer.style.display = 'none';
            }
        } catch (error) {
            log("error", scriptName, functionName, "❌ Error fetching suggestions", { error, query });
            suggestionsContainer.style.display = 'none';
        }
    }

    /**
     * Display suggestions
     * @param {Array} items - Suggestion items
     */
    function displaySuggestions(items) {
        // Clear suggestions container
        suggestionsContainer.innerHTML = '';

        if (items.length === 0) {
            suggestionsContainer.style.display = 'none';
            return;
        }

        // Create suggestion items
        items.forEach((item, index) => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item';
            div.style.padding = '8px 12px';
            div.style.cursor = 'pointer';
            div.style.borderBottom = '1px solid #f4f4f4';

            // Display text
            const displayText = item[config.displayField] || 'Unknown';
            div.innerHTML = highlightMatch(displayText, lastQuery);

            // Store value
            div.dataset.value = item[config.valueField] || '';
            div.dataset.index = index;

            // Hover effect
            div.addEventListener('mouseover', () => {
                removeActive();
                currentFocus = parseInt(div.dataset.index, 10);
                addActive();
            });

            // Click to select
            div.addEventListener('click', () => {
                selectItem(item);
            });

            suggestionsContainer.appendChild(div);
        });

        // Position and show suggestions
        suggestionsContainer.style.width = `${field.offsetWidth}px`;
        suggestionsContainer.style.display = 'block';

        // Reset focus
        currentFocus = -1;
    }

    /**
     * Handle keyboard navigation
     * @param {KeyboardEvent} e - Keyboard event
     */
    function handleKeyDown(e) {
        if (suggestionsContainer.style.display === 'none') {
            return;
        }

        const items = suggestionsContainer.querySelectorAll('.autocomplete-item');

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                currentFocus++;
                currentFocus = Math.min(currentFocus, items.length - 1);
                removeActive();
                addActive();
                break;

            case 'ArrowUp':
                e.preventDefault();
                currentFocus--;
                currentFocus = Math.max(currentFocus, -1);
                removeActive();
                addActive();
                break;

            case 'Enter':
                e.preventDefault();
                if (currentFocus > -1) {
                    // Simulate click on active item
                    items[currentFocus].click();
                }
                break;

            case 'Escape':
                e.preventDefault();
                suggestionsContainer.style.display = 'none';
                break;
        }
    }

    /**
     * Add active class to focused suggestion
     */
    function addActive() {
        const items = suggestionsContainer.querySelectorAll('.autocomplete-item');

        if (currentFocus >= 0 && currentFocus < items.length) {
            items[currentFocus].style.backgroundColor = '#e9ecef';

            // Scroll item into view if needed
            const container = suggestionsContainer;
            const item = items[currentFocus];

            const itemTop = item.offsetTop;
            const itemBottom = itemTop + item.offsetHeight;
            const containerTop = container.scrollTop;
            const containerBottom = containerTop + container.offsetHeight;

            if (itemTop < containerTop) {
                container.scrollTop = itemTop;
            } else if (itemBottom > containerBottom) {
                container.scrollTop = itemBottom - container.offsetHeight;
            }
        }
    }

    /**
     * Remove active class from all suggestions
     */
    function removeActive() {
        const items = suggestionsContainer.querySelectorAll('.autocomplete-item');

        items.forEach(item => {
            item.style.backgroundColor = '';
        });
    }

    /**
     * Select an item from suggestions
     * @param {Object} item - The selected item
     */
    function selectItem(item) {
        const displayText = item[config.displayField] || 'Unknown';
        const value = item[config.valueField] || '';

        // Update field and value
        field.value = displayText;
        valueInput.value = value;

        // Hide suggestions
        suggestionsContainer.style.display = 'none';

        // Call onSelect callback if provided
        if (typeof config.onSelect === 'function') {
            config.onSelect(item);
        }

        log("info", scriptName, functionName, `Item selected: ${displayText} (${value})`);

        // Trigger change event on field
        field.dispatchEvent(new Event('change', { bubbles: true }));
    }

    /**
     * Handle clicks outside autocomplete
     * @param {MouseEvent} e - Mouse event
     */
    function handleDocumentClick(e) {
        if (!field.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.style.display = 'none';
        }
    }

    /**
     * Highlight matching text in suggestions
     * @param {string} text - The full text
     * @param {string} query - The search query
     * @returns {string} - HTML with highlighted text
     */
    function highlightMatch(text, query) {
        if (!query) return text;

        try {
            const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
            return text.replace(regex, '<strong>$1</strong>');
        } catch (e) {
            return text;
        }
    }

    /**
     * Escape regex special characters
     * @param {string} string - The string to escape
     * @returns {string} - Escaped string
     */
    function escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // Return cleanup function
    return () => {
        field.removeEventListener('input', handleInput);
        field.removeEventListener('keydown', handleKeyDown);
        document.removeEventListener('click', handleDocumentClick);
        suggestionsContainer.remove();
        activeAutoCompletes.delete(fieldId);
    };
}

/**
 * Get autocomplete instance
 * @param {string} fieldId - The ID of the input field
 * @returns {Object|null} - The autocomplete instance or null if not found
 */
export function getAutoComplete(fieldId) {
    return activeAutoCompletes.get(fieldId) || null;
}

/**
 * Set value programmatically
 * @param {string} fieldId - The ID of the input field
 * @param {string} displayText - Text to display in field
 * @param {string|number} value - Value to set in hidden field
 */
export function setAutoCompleteValue(fieldId, displayText, value) {
    const functionName = "setAutoCompleteValue";

    const instance = activeAutoCompletes.get(fieldId);
    if (!instance) {
        log("error", scriptName, functionName, `❌ Autocomplete instance not found: ${fieldId}`);
        return;
    }

    instance.field.value = displayText;
    instance.valueInput.value = value;

    log("info", scriptName, functionName, `Set value for ${fieldId}: ${displayText} (${value})`);
}

/**
 * Clear autocomplete field
 * @param {string} fieldId - The ID of the input field
 */
export function clearAutoComplete(fieldId) {
    const functionName = "clearAutoComplete";

    const instance = activeAutoCompletes.get(fieldId);
    if (!instance) {
        log("error", scriptName, functionName, `❌ Autocomplete instance not found: ${fieldId}`);
        return;
    }

    instance.field.value = '';
    instance.valueInput.value = '';
    instance.suggestionsContainer.style.display = 'none';

    log("info", scriptName, functionName, `Cleared autocomplete: ${fieldId}`);
}