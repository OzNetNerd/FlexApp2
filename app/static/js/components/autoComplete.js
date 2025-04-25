import log from '/static/js/core/logger.js';
import eventSystem from '/static/js/core/events.js';

/**
 * Enhanced autocomplete component
 */
export function setupAutoComplete(options) {
  const functionName = 'setupAutoComplete';

  // Validate required options
  if (!options.inputSelector || !options.dataUrl || !options.inputName) {
    log('error', 'autoComplete.js', functionName, 'Missing required options', options);
    return Promise.reject(new Error('Missing required options'));
  }

  const defaults = {
    initialIds: [],
    singleSelect: false,
    placeholder: 'Search...',
    minLength: 2,
    debounceTime: 300,
    resultLimit: 10
  };

  // Merge defaults with provided options
  const config = { ...defaults, ...options };
  log('debug', 'autoComplete.js', functionName, 'Configuration:', config);

  // Find the input element
  const inputElement = document.querySelector(config.inputSelector);
  if (!inputElement) {
    log('error', 'autoComplete.js', functionName, `Input element not found: ${config.inputSelector}`);
    return Promise.reject(new Error(`Input element not found: ${config.inputSelector}`));
  }

  // Set up the UI elements
  const containerId = `${config.inputName}-container`;
  const resultsId = `${config.inputName}-results`;
  const hiddenInputId = `${config.inputName}-hidden`;

  // Create container if it doesn't exist
  let containerElement = inputElement.parentElement;
  if (!containerElement.classList.contains('autocomplete-container')) {
    // Wrap input in container
    containerElement = document.createElement('div');
    containerElement.id = containerId;
    containerElement.className = 'autocomplete-container position-relative';
    inputElement.parentNode.insertBefore(containerElement, inputElement);
    containerElement.appendChild(inputElement);

    log('debug', 'autoComplete.js', functionName, `Created container for ${config.inputName}`);
  }

  // Add autocomplete class to input
  inputElement.classList.add('autocomplete-input', 'form-control');
  inputElement.setAttribute('placeholder', config.placeholder);
  inputElement.setAttribute('autocomplete', 'off');

  // Create hidden input for storing selected values
  let hiddenInput = document.getElementById(hiddenInputId);
  if (!hiddenInput) {
    hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.id = hiddenInputId;
    hiddenInput.name = config.inputName;
    containerElement.appendChild(hiddenInput);

    log('debug', 'autoComplete.js', functionName, `Created hidden input for ${config.inputName}`);
  }

  // Create results container
  let resultsElement = document.getElementById(resultsId);
  if (!resultsElement) {
    resultsElement = document.createElement('div');
    resultsElement.id = resultsId;
    resultsElement.className = 'autocomplete-results position-absolute w-100 mt-1 border rounded bg-white shadow-sm d-none';
    containerElement.appendChild(resultsElement);

    log('debug', 'autoComplete.js', functionName, `Created results container for ${config.inputName}`);
  }

  // Store selected items
  let selectedItems = [];

  // Set initial values if provided
  if (config.initialIds && config.initialIds.length > 0) {
    if (config.singleSelect && config.initialIds.length > 1) {
      log('warn', 'autoComplete.js', functionName,
          `Multiple initial IDs provided for single-select field ${config.inputName}`,
          config.initialIds);
    }

    // For single select, use the first ID
    if (config.singleSelect) {
      hiddenInput.value = config.initialIds[0];
      log('debug', 'autoComplete.js', functionName,
          `Set initial value for ${config.inputName}: ${config.initialIds[0]}`);
    } else {
      // For multi-select, use all IDs
      hiddenInput.value = JSON.stringify(config.initialIds);
      selectedItems = [...config.initialIds];
      log('debug', 'autoComplete.js', functionName,
          `Set initial values for ${config.inputName}:`, selectedItems);
    }
  }

  // Variables for search functionality
  let debounceTimer;
  let isLoading = false;

  // Function to show loading indicator
  function showLoading() {
    isLoading = true;
    inputElement.classList.add('loading');
    resultsElement.innerHTML = '<div class="p-2 text-center text-muted">Loading...</div>';
    resultsElement.classList.remove('d-none');

    log('debug', 'autoComplete.js', 'showLoading', `Loading indicator shown for ${config.inputName}`);
  }

  // Function to hide loading indicator
  function hideLoading() {
    isLoading = false;
    inputElement.classList.remove('loading');

    log('debug', 'autoComplete.js', 'hideLoading', `Loading indicator hidden for ${config.inputName}`);
  }

  // Function to show results
  function showResults(results) {
    if (results.length === 0) {
      resultsElement.innerHTML = '<div class="p-2 text-center text-muted">No results found</div>';
      log('debug', 'autoComplete.js', 'showResults', `No results for ${config.inputName}`);
    } else {
      resultsElement.innerHTML = '';

      results.forEach(item => {
        const resultItem = document.createElement('div');
        resultItem.className = 'autocomplete-item p-2 cursor-pointer hover:bg-light';
        resultItem.dataset.id = item.id;
        resultItem.textContent = item.name || item.title || item.label || item.text || item.id;
        resultItem.addEventListener('click', () => selectItem(item));
        resultsElement.appendChild(resultItem);
      });

      log('debug', 'autoComplete.js', 'showResults',
          `Showing ${results.length} results for ${config.inputName}`);
    }

    resultsElement.classList.remove('d-none');
  }

  // Function to hide results
  function hideResults() {
    resultsElement.classList.add('d-none');
    log('debug', 'autoComplete.js', 'hideResults', `Results hidden for ${config.inputName}`);
  }

  // Function to perform search
  function performSearch(query) {
    if (query.length < config.minLength) {
      hideResults();
      return;
    }

    showLoading();

    const url = `${config.dataUrl}?q=${encodeURIComponent(query)}&limit=${config.resultLimit}`;

    log('debug', 'autoComplete.js', 'performSearch',
        `Searching for ${query} at ${url} for ${config.inputName}`);

    fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error(`API responded with status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        hideLoading();
        showResults(data.data || data);

        // Publish search results event
        eventSystem.publish('autocomplete.search.completed', {
          inputName: config.inputName,
          query,
          results: data.data || data
        });
      })
      .catch(error => {
        hideLoading();
        resultsElement.innerHTML = `<div class="p-2 text-center text-danger">Error: ${error.message}</div>`;
        resultsElement.classList.remove('d-none');

        log('error', 'autoComplete.js', 'performSearch',
            `Error searching for ${query} for ${config.inputName}:`, error);

        // Publish search error event
        eventSystem.publish('autocomplete.search.error', {
          inputName: config.inputName,
          query,
          error
        });
      });
  }

  // Function to select an item
  function selectItem(item) {
    log('debug', 'autoComplete.js', 'selectItem',
        `Item selected for ${config.inputName}:`, item);

    if (config.singleSelect) {
      // For single-select, replace the current value
      hiddenInput.value = item.id;
      inputElement.value = item.name || item.title || item.label || item.text || item.id;

      // Publish selection event
      eventSystem.publish('autocomplete.item.selected', {
        inputName: config.inputName,
        singleSelect: true,
        item
      });
    } else {
      // For multi-select, add to the current values
      if (!selectedItems.includes(item.id)) {
        selectedItems.push(item.id);
        hiddenInput.value = JSON.stringify(selectedItems);

        // Create a pill for the selected item
        const pillsContainer = document.getElementById(`${config.inputName}-pills`);
        if (pillsContainer) {
          const pill = document.createElement('span');
          pill.className = 'badge bg-primary me-1 mb-1';
          pill.textContent = item.name || item.title || item.label || item.text || item.id;

          // Add remove button to pill
          const removeBtn = document.createElement('button');
          removeBtn.className = 'btn-close btn-close-white ms-1';
          removeBtn.setAttribute('aria-label', 'Remove');
          removeBtn.addEventListener('click', () => removeItem(item.id, pill));

          pill.appendChild(removeBtn);
          pillsContainer.appendChild(pill);
        }

        // Publish selection event
        eventSystem.publish('autocomplete.item.selected', {
          inputName: config.inputName,
          singleSelect: false,
          item,
          selectedItems: [...selectedItems]
        });
      }

      // Clear input field for multi-select
      inputElement.value = '';
    }

    hideResults();
  }

  // Function to remove an item (for multi-select)
  function removeItem(itemId, pillElement) {
    log('debug', 'autoComplete.js', 'removeItem',
        `Removing item ${itemId} from ${config.inputName}`);

    // Remove from selected items
    selectedItems = selectedItems.filter(id => id !== itemId);
    hiddenInput.value = JSON.stringify(selectedItems);

    // Remove pill element
    if (pillElement && pillElement.parentNode) {
      pillElement.parentNode.removeChild(pillElement);
    }

    // Publish removal event
    eventSystem.publish('autocomplete.item.removed', {
      inputName: config.inputName,
      itemId,
      selectedItems: [...selectedItems]
    });
  }

  // Set up event listeners
  inputElement.addEventListener('input', () => {
    clearTimeout(debounceTimer);

    const query = inputElement.value.trim();

    debounceTimer = setTimeout(() => {
      performSearch(query);
    }, config.debounceTime);
  });

  inputElement.addEventListener('focus', () => {
    const query = inputElement.value.trim();
    if (query.length >= config.minLength) {
      performSearch(query);
    }
  });

  // Close results when clicking outside
  document.addEventListener('click', (event) => {
    if (!containerElement.contains(event.target)) {
      hideResults();
    }
  });

  // For multi-select, create pills container if it doesn't exist
  if (!config.singleSelect) {
    const pillsId = `${config.inputName}-pills`;
    let pillsContainer = document.getElementById(pillsId);

    if (!pillsContainer) {
      pillsContainer = document.createElement('div');
      pillsContainer.id = pillsId;
      pillsContainer.className = 'autocomplete-pills d-flex flex-wrap mt-1';
      containerElement.appendChild(pillsContainer);

      log('debug', 'autoComplete.js', functionName, `Created pills container for ${config.inputName}`);
    }
  }

  // Return promise that resolves when component is ready
  return Promise.resolve({
    element: inputElement,
    container: containerElement,
    results: resultsElement,
    hiddenInput,
    selectedItems
  });
}

/**
 * Update single-select autocomplete fields
 */
export function updateSingleSelectAutoComplete() {
  const functionName = 'updateSingleSelectAutoComplete';
  log('info', 'autoComplete.js', functionName, 'Updating single-select autocomplete fields');

  // Get all autocomplete fields that have already been initialized
  const autocompleteInputs = document.querySelectorAll('.autocomplete-input');

  autocompleteInputs.forEach(input => {
    const hiddenInput = input.nextElementSibling;
    const resultsContainer = input.nextElementSibling?.nextElementSibling;

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

          log('info', 'autoComplete.js', functionName, `Selected item with ID ${id}: ${name}`);

          // Publish selection event
          eventSystem.publish('autocomplete.item.selected', {
            inputName: hiddenInput.name,
            singleSelect: true,
            item: { id, name }
          });
        }
      });
    }
  });
}