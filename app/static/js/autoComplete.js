import log from './logger.js';

const scriptName = 'autoComplete.js';
console.log('🚀 Loading autoComplete.js');

/**
 * Sets up the autocomplete functionality for an input field.
 *
 * Data is fetched from the specified endpoint.
 *
 * Endpoints:
 * - For users: '/users/data'
 * - For companies: '/companies/data'
 *
 * @param {Object} params
 * @param {string} params.inputSelector - CSS selector for the input field.
 * @param {string} params.dataUrl - URL endpoint to fetch autocomplete data.
 * @param {string} params.inputName - Name of the input field (used for badges, etc.).
 * @param {Array<number>} [params.initialIds=[]] - Array of initial selected IDs.
 */
export function setupAutoComplete({ inputSelector, dataUrl, inputName, initialIds = [] }) {
  const functionName = 'setupAutoComplete';

  log("info", scriptName, functionName, `📍 Function called with params:`, { inputSelector, dataUrl, inputName, initialIds });

  const input = document.querySelector(inputSelector);
  if (!input) {
    log("error", scriptName, functionName, `❌ Input not found: ${inputSelector}`);
    return;
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

  fetch(dataUrl)
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

      // Log warning if no suggestions were returned
      if (!suggestions || suggestions.length === 0) {
        log('warn', scriptName, functionName, `⚠️ No suggestions returned from ${dataUrl}`);
      } else {
        // Log sample data to help with debugging
        const sampleData = suggestions.slice(0, 3);
        log('debug', scriptName, functionName, `🔍 Sample data (first 3 items):`, sampleData);
      }

      if (Array.isArray(initialIds) && initialIds.length > 0) {
        log('debug', scriptName, functionName, `🔍 Looking for initial IDs in data:`, initialIds);
        const prefillItems = suggestions.filter(s => initialIds.includes(s.id));

        // Log warning if some initial IDs weren't found
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
    const functionName = 'input:filter';
    const query = input.value.trim().toLowerCase();
    log('debug', scriptName, functionName, `🔍 Filtering with query: "${query}"`);

    autocompleteList.innerHTML = '';
    highlightIndex = -1;

    let filtered;

    if (!query) {
      filtered = suggestions
        .filter(s => !selected.some(sel => sel.id === s.id))
        .slice(0, 10);
      log('debug', scriptName, functionName, `ℹ️ Showing first 10 '${inputName}' results (${filtered.length} items)`);
    } else {
      filtered = suggestions
        .filter(s => !selected.some(sel => sel.id === s.id))
        .filter(s =>
          ((s.name || `${s.first_name || ''} ${s.last_name || ''}`).toLowerCase().includes(query)) ||
          (s.email && s.email.toLowerCase().includes(query))
        );

      log('debug', scriptName, functionName, `🔍 Filter results for "${query}": ${filtered.length} matches`);

      if (!filtered.length) {
        log('warn', scriptName, functionName, `⚠️ No matches found in '${inputName}' for query '${query}'`);
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
        const functionName = 'click:addItem';
        addItem(item);
        input.value = '';
        autocompleteList.innerHTML = '';
        autocompleteList.style.display = 'none';
        log('info', scriptName, functionName, `➕ Selected '${fullName}' (ID: ${item.id})`);
      });

      autocompleteList.appendChild(div);
    });

    autocompleteList.style.display = 'block';
  }

  input.addEventListener('keydown', (e) => {
    const functionName = 'keydown:navigate';
    const items = autocompleteList.querySelectorAll('.autocomplete-item');

    log('debug', scriptName, functionName, `⌨️ Key pressed: ${e.key}`);

    if (e.key === 'ArrowDown') {
      highlightIndex = (highlightIndex + 1) % items.length;
      log('debug', scriptName, functionName, `⬇️ Arrow down: highlight index ${highlightIndex}`);
    } else if (e.key === 'ArrowUp') {
      highlightIndex = (highlightIndex - 1 + items.length) % items.length;
      log('debug', scriptName, functionName, `⬆️ Arrow up: highlight index ${highlightIndex}`);
    } else if (e.key === 'Enter' || e.key === 'Tab') {
      if (highlightIndex >= 0 && highlightIndex < items.length) {
        e.preventDefault();
        log('debug', scriptName, functionName, `✅ Selection confirmed for item at index ${highlightIndex}`);
        items[highlightIndex].click();
      }
    } else if (e.key === 'Backspace' && input.value === '' && selected.length > 0) {
      const removed = selected.pop();
      const removedName = removed.name || `${removed.first_name || ''} ${removed.last_name || ''}`.trim();
      renderBadges();
      log('info', scriptName, functionName, `🗑️ Removed last item: ${removedName} (ID: ${removed.id})`);
    }

    items.forEach((item, i) => {
      item.classList.toggle('highlight', i === highlightIndex);
    });
  });

  document.addEventListener('click', (e) => {
    const functionName = 'document:click';
    if (!container.contains(e.target)) {
      autocompleteList.style.display = 'none';
      log('debug', scriptName, functionName, `👆 Click outside container, hiding dropdown`);
    }
  });

  function addItem(item) {
    const functionName = 'addItem';
    const fullName = item.name || `${item.first_name || ''} ${item.last_name || ''}`.trim();
    selected.push(item);
    renderBadges();
    log('info', scriptName, functionName, `🏷️ Added: ${fullName} (ID: ${item.id})`);
  }

  function removeItem(id) {
    const functionName = 'removeItem';
    const itemToRemove = selected.find(i => i.id === id);
    const itemName = itemToRemove ? (itemToRemove.name || `${itemToRemove.first_name || ''} ${itemToRemove.last_name || ''}`.trim()) : 'unknown';

    selected = selected.filter(i => i.id !== id);
    renderBadges();
    log('info', scriptName, functionName, `➖ Removed: ${itemName} (ID: ${id})`);
  }

  function renderBadges() {
    const functionName = 'renderBadges';
    badgeContainer.innerHTML = '';

    log('debug', scriptName, functionName, `🔄 Rendering ${selected.length} badges`);

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
    log('debug', scriptName, functionName, `🏷️ Updated badges. Current selection IDs:`, selectedIds);
  }
}

/**
 * Automatically initialize autocomplete fields for both users and companies.
 *
 * It pulls data from the following endpoints:
 * - Users: '/users/data'
 * - Companies: '/companies/data'
 */
export function initAutoCompleteFields() {
  console.log('🚀 initAutoCompleteFields called');
  log("info", scriptName, "initAutoCompleteFields", "📋 Initializing autocomplete fields");

  const usersInput = document.querySelector('#users-input');
  if (usersInput) {
    const usersInitial = JSON.parse(usersInput.dataset.initial || '[]');
    log("info", scriptName, "initAutoCompleteFields", `🔍 Found users input with initial data:`, usersInitial);

    setupAutoComplete({
      inputSelector: '#users-input',
      dataUrl: '/users/data',
      inputName: 'users',
      initialIds: usersInitial
    });
  } else {
    log("warn", scriptName, "initAutoCompleteFields", "⚠️ No users input field found with selector '#users-input'");
  }

  const companiesInput = document.querySelector('#companies-input');
  if (companiesInput) {
    const companiesInitial = JSON.parse(companiesInput.dataset.initial || '[]');
    log("info", scriptName, "initAutoCompleteFields", `🔍 Found companies input with initial data:`, companiesInitial);

    setupAutoComplete({
      inputSelector: '#companies-input',
      dataUrl: '/companies/data',
      inputName: 'company_id',
      initialIds: companiesInitial
    });
  } else {
    log("warn", scriptName, "initAutoCompleteFields", "⚠️ No companies input field found with selector '#companies-input'");
  }

  log("info", scriptName, "initAutoCompleteFields", "✅ Autocomplete initialization complete");
}