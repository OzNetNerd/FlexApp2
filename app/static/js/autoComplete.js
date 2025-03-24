import log from './logger.js';

const scriptName = 'autoComplete.js';

export function setupAutoComplete({ inputSelector, dataUrl, inputName }) {
    const functionName = 'setupAutoComplete';

    const input = document.querySelector(inputSelector);
    if (!input) {
        log("error", scriptName, functionName, `❌ Input not found: ${inputSelector}`);
        return;
    }

    log("info", scriptName, functionName, `🎯 Initializing autocomplete for '${inputName}'`, { inputSelector, dataUrl });

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

    // Get pre-selected IDs from data-initial attribute
    let initialIds = [];
    try {
        initialIds = JSON.parse(input.dataset.initial || '[]');
        log('debug', scriptName, functionName, `📌 Initial IDs:`, initialIds);
    } catch (e) {
        log('warn', scriptName, functionName, `⚠️ Invalid JSON in data-initial`, e);
    }

    // Load suggestions and set initial selections
    fetch(dataUrl)
        .then(res => res.json())
        .then(json => {
            suggestions = json.data;
            log('info', scriptName, functionName, `📦 Loaded ${suggestions.length} suggestions`, suggestions);

            // Select items by initial ID
            selected = suggestions.filter(s => initialIds.includes(s.id));
            renderBadges();
        })
        .catch(err => {
            log('error', scriptName, functionName, `❌ Failed to fetch suggestions`, err);
        });

    input.addEventListener('input', handleInputEvent);
    input.addEventListener('focus', handleInputEvent);

    function handleInputEvent() {
        const functionName = 'input:filter';
        const query = input.value.trim().toLowerCase();
        autocompleteList.innerHTML = '';
        highlightIndex = -1;

        let filtered;

        if (!query) {
            filtered = suggestions
                .filter(s => !selected.some(sel => sel.id === s.id))
                .slice(0, 10);
            log('debug', scriptName, functionName, `ℹ️ Showing first 10 '${inputName}' results`, filtered);
        } else {
            filtered = suggestions
                .filter(s => !selected.some(sel => sel.id === s.id))
                .filter(s =>
                    ((s.name || `${s.first_name || ''} ${s.last_name || ''}`).toLowerCase().includes(query)) ||
                    (s.email && s.email.toLowerCase().includes(query))
                );

            if (!filtered.length) {
                log('debug', scriptName, functionName, `⚠️ No matches found in '${inputName}'`);
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
                log('info', scriptName, functionName, `➕ Selected '${fullName}'`, item);
            });

            autocompleteList.appendChild(div);
        });

        autocompleteList.style.display = 'block';
    }

    input.addEventListener('keydown', (e) => {
        const functionName = 'keydown:navigate';
        const items = autocompleteList.querySelectorAll('.autocomplete-item');

        if (e.key === 'ArrowDown') {
            highlightIndex = (highlightIndex + 1) % items.length;
        } else if (e.key === 'ArrowUp') {
            highlightIndex = (highlightIndex - 1 + items.length) % items.length;
        } else if (e.key === 'Enter' || e.key === 'Tab') {
            if (highlightIndex >= 0 && highlightIndex < items.length) {
                e.preventDefault();
                items[highlightIndex].click();
            }
        } else if (e.key === 'Backspace' && input.value === '' && selected.length > 0) {
            const removed = selected.pop();
            renderBadges();
            log('warn', scriptName, functionName, `🗑️ Removed last item`, removed);
        }

        items.forEach((item, i) => {
            item.classList.toggle('highlight', i === highlightIndex);
        });
    });

    document.addEventListener('click', (e) => {
        const functionName = 'document:click';
        if (!container.contains(e.target)) {
            autocompleteList.style.display = 'none';
        }
    });

    function addItem(item) {
        const functionName = 'addItem';
        selected.push(item);
        renderBadges();
        log('debug', scriptName, functionName, `🏷️ Added`, item);
    }

    function removeItem(id) {
        const functionName = 'removeItem';
        selected = selected.filter(i => i.id !== id);
        renderBadges();
        log('debug', scriptName, functionName, `➖ Removed ID ${id}`);
    }

    function renderBadges() {
        const functionName = 'renderBadges';
        badgeContainer.innerHTML = '';

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

        log('debug', scriptName, functionName, `🎯 Updated badges`, selected);
    }
}
