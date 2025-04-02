import log from './logger.js';

const scriptName = 'autoComplete.js';

/**
 * Sets up the autocomplete functionality for an input field.
 *
 * Data is fetched from the specified endpoint.
 *
 * @param {Object} params
 * @param {string} params.inputSelector - CSS selector for the input field.
 * @param {string} params.dataUrl - URL endpoint to fetch autocomplete data.
 * @param {string} params.inputName - Name of the input field (used for badges, etc.).
 * @param {Array<number>} [params.initialIds=[]] - Array of initial selected IDs.
 * @returns {Promise<void>} - Resolves when autocomplete is set up.
 */
export function setupAutoComplete({ inputSelector, dataUrl, inputName, initialIds = [] }) {
  const functionName = 'setupAutoComplete';

  log("info", scriptName, functionName, `📍 Function called with params:`, { inputSelector, dataUrl, inputName, initialIds });

  const input = document.querySelector(inputSelector);
  if (!input) {
    log("error", scriptName, functionName, `❌ Input not found: ${inputSelector}`);
    return Promise.resolve();
  }

  log("info", scriptName, functionName, `🎯 Initializing autocomplete for '${inputName}' using endpoint ${dataUrl}`);
  log("debug", scriptName, functionName, "📌 Initial IDs:", initialIds);

  const container = document.createElement('div');
  const badgeContainer = document.createElement('div');
  const autocompleteList = document.createElement('div');

  input.classList.add('entity-input');
  container.classList.add('input-container');
  badgeContainer.id = `${inputName}-badges`;
  autocompleteList.className = 'autocomplete-items';
  autocompleteList.style.display = 'none';

  input.parentNode.replaceChild(container, input);
  container.appendChild(badgeContainer);
  container.appendChild(input);
  container.appendChild(autocompleteList);

  let selected = [];
  let suggestions = [];
  let highlightIndex = -1;

  log("info", scriptName, functionName, `🔄 Fetching data from: ${dataUrl}`);
  console.log(`🔄 Fetching data from: ${dataUrl}`);

  const fetchPromise = fetch(dataUrl)
    .then(res => {
      console.log(`📡 Response status from ${dataUrl}: ${res.status}`);
      log("debug", scriptName, functionName, `📡 Response status from ${dataUrl}: ${res.status}`);
      return res.json();
    })
    .then(json => {
      log("debug", scriptName, functionName, `📦 Raw data received from ${dataUrl}:`, json);

      if (!json.data) {
        log("error", scriptName, functionName, `❌ Invalid data format from ${dataUrl}. Expected 'data' property.`, json);
        return;
      }

      suggestions = json.data;
      log('info', scriptName, functionName, `📦 Loaded ${suggestions.length} suggestions from ${dataUrl}`);

      if (!suggestions || suggestions.length === 0) {
        log('warn', scriptName, functionName, `⚠️ No suggestions returned from ${dataUrl}`);
      } else {
        const sampleData = suggestions.slice(0, 3);
        log('debug', scriptName, functionName, `🔍 Sample data (first 3 items):`, sampleData);
      }

      if (Array.isArray(initialIds) && initialIds.length > 0) {
        log('debug', scriptName, functionName, `🔍 Looking for initial IDs in data:`, initialIds);
        const prefillItems = suggestions.filter(s => initialIds.includes(s.id));

        const missingIds = initialIds.filter(id => !suggestions.some(s => s.id === id));
        if (missingIds.length > 0) {
          log('warn', scriptName, functionName, `⚠️ Some initial IDs were not found in the data:`, missingIds);
        }

        selected = prefillItems;
        renderBadges();
        log('debug', scriptName, functionName, "✅ Prefilled items:", prefillItems);
      }
    })
    .catch(err => {
      log('error', scriptName, functionName, `❌ Failed to fetch suggestions from ${dataUrl}`, err);
    });

  input.addEventListener('input', handleInputEvent);
  input.addEventListener('focus', handleInputEvent);

  function handleInputEvent() {
    const innerFunctionName = 'input:filter';
    const query = input.value.trim().toLowerCase();
    log('debug', scriptName, innerFunctionName, `🔍 Filtering with query: "${query}"`);

    autocompleteList.innerHTML = '';
    highlightIndex = -1;

    let filtered;

    if (!query) {
      filtered = suggestions
        .filter(s => !selected.some(sel => sel.id === s.id))
        .slice(0, 10);
      log('debug', scriptName, innerFunctionName, `ℹ️ Showing first 10 '${inputName}' results (${filtered.length} items)`);
    } else {
      filtered = suggestions
        .filter(s => !selected.some(sel => sel.id === s.id))
        .filter(s =>
          ((s.name || `${s.first_name || ''} ${s.last_name || ''}`).toLowerCase().includes(query)) ||
          (s.email && s.email.toLowerCase().includes(query))
        );

      log('debug', scriptName, innerFunctionName, `🔍 Filter results for "${query}": ${filtered.length} matches`);

      if (!filtered.length) {
        log('warn', scriptName, innerFunctionName, `⚠️ No matches found in '${inputName}' for query '${query}'`);
        autocompleteList.style.display = 'none';
        return;
      }
    }

    filtered.forEach((item) => {
      const div = document.createElement('div');
      const fullName = item.name || `${item.first_name || ''} ${item.last_name || ''}`.trim();
      div.className = 'autocomplete-item';
      div.textContent = item.email ? `${fullName} (${item.email})` : fullName;

      div.addEventListener('click', () => {
        const clickFunctionName = 'click:addItem';
        addItem(item);
        input.value = '';
        autocompleteList.innerHTML = '';
        autocompleteList.style.display = 'none';
        log('info', scriptName, clickFunctionName, `➕ Selected '${fullName}' (ID: ${item.id})`);
      });

      autocompleteList.appendChild(div);
    });

    autocompleteList.style.display = 'block';
  }

  input.addEventListener('keydown', (e) => {
    const innerFunctionName = 'keydown:navigate';
    const items = autocompleteList.querySelectorAll('.autocomplete-item');

    log('debug', scriptName, innerFunctionName, `⌨️ Key pressed: ${e.key}`);

    if (e.key === 'ArrowDown') {
      highlightIndex = (highlightIndex + 1) % items.length;
      log('debug', scriptName, innerFunctionName, `⬇️ Arrow down: highlight index ${highlightIndex}`);
    } else if (e.key === 'ArrowUp') {
      highlightIndex = (highlightIndex - 1 + items.length) % items.length;
      log('debug', scriptName, innerFunctionName, `⬆️ Arrow up: highlight index ${highlightIndex}`);
    } else if (e.key === 'Enter' || e.key === 'Tab') {
      if (highlightIndex >= 0 && highlightIndex < items.length) {
        e.preventDefault();
        log('debug', scriptName, innerFunctionName, `✅ Selection confirmed for item at index ${highlightIndex}`);
        items[highlightIndex].click();
      }
    } else if (e.key === 'Backspace' && input.value === '' && selected.length > 0) {
      const removed = selected.pop();
      const removedName = removed.name || `${removed.first_name || ''} ${removed.last_name || ''}`.trim();
      renderBadges();
      log('info', scriptName, innerFunctionName, `🗑️ Removed last item: ${removedName} (ID: ${removed.id})`);
    }

    items.forEach((item, i) => {
      item.classList.toggle('highlight', i === highlightIndex);
    });
  });

  document.addEventListener('click', (e) => {
    const innerFunctionName = 'document:click';
    if (!container.contains(e.target)) {
      autocompleteList.style.display = 'none';
      log('debug', scriptName, innerFunctionName, `👆 Click outside container, hiding dropdown`);
    }
  });

  function addItem(item) {
    const innerFunctionName = 'addItem';
    const fullName = item.name || `${item.first_name || ''} ${item.last_name || ''}`.trim();
    selected.push(item);
    renderBadges();
    log('info', scriptName, innerFunctionName, `🏷️ Added: ${fullName} (ID: ${item.id})`);
  }

  function removeItem(id) {
    const innerFunctionName = 'removeItem';
    const itemToRemove = selected.find(i => i.id === id);
    const itemName = itemToRemove
      ? (itemToRemove.name || `${itemToRemove.first_name || ''} ${itemToRemove.last_name || ''}`.trim())
      : 'unknown';

    selected = selected.filter(i => i.id !== id);
    renderBadges();
    log('info', scriptName, innerFunctionName, `➖ Removed: ${itemName} (ID: ${id})`);
  }

  function renderBadges() {
    const innerFunctionName = 'renderBadges';
    badgeContainer.innerHTML = '';

    log('debug', scriptName, innerFunctionName, `🔄 Rendering ${selected.length} badges`);

    selected.forEach(item => {
      const badge = document.createElement('div');
      badge.className = 'badge';

      const fullName = item.name || `${item.first_name || ''} ${item.last_name || ''}`.trim();
      const span = document.createElement('span');
      span.textContent = item.email ? `${fullName} (${item.email})` : fullName;

      const remove = document.createElement('span');
      remove.className = 'badge-remove';
      remove.textContent = '×';
      remove.onclick = () => removeItem(item.id);

      const hidden = document.createElement('input');
      hidden.type = 'hidden';
      hidden.name = inputName;
      hidden.value = item.id;

      badge.appendChild(span);
      badge.appendChild(remove);
      badge.appendChild(hidden);
      badgeContainer.appendChild(badge);
    });

    const selectedIds = selected.map(item => item.id);
    log('debug', scriptName, 'renderBadges', `🏷️ Updated badges. Current selection IDs:`, selectedIds);
  }

  return fetchPromise;
}

/**
 * Initialize autocomplete fields based on configuration.
 *
 * @param {Array<Object>} config - Array of configuration objects for autocomplete fields
 * @param {string} config[].selector - CSS selector for the input field
 * @param {string} config[].dataUrl - URL endpoint to fetch autocomplete data
 * @param {string} config[].inputName - Name of the input field
 * @returns {Promise<void>} - Resolves when all autocomplete fields have been set up.
 */
export function initAutoCompleteFields(config = []) {
  log("info", scriptName, "initAutoCompleteFields", `📋 Initializing ${config.length} autocomplete fields`);

  const promises = config.map(fieldConfig => {
    const input = document.querySelector(fieldConfig.selector);
    if (input) {
      try {
        const initialIds = JSON.parse(input.dataset.initial || '[]');
        log("info", scriptName, "initAutoCompleteFields", `🔍 Found input ${fieldConfig.selector} with initial data:`, initialIds);

        return setupAutoComplete({
          inputSelector: fieldConfig.selector,
          dataUrl: fieldConfig.dataUrl,
          inputName: fieldConfig.inputName,
          initialIds: initialIds
        });
      } catch (e) {
        log("error", scriptName, "initAutoCompleteFields", `❌ Error parsing initial data for ${fieldConfig.selector}:`, e);
        return Promise.resolve();
      }
    } else {
      log("warn", scriptName, "initAutoCompleteFields", `⚠️ No input field found with selector '${fieldConfig.selector}'`);
      return Promise.resolve();
    }
  });

  return Promise.all(promises).then(() => {
    log("info", scriptName, "final", "✅ Autocomplete initialization complete");
  });
}
