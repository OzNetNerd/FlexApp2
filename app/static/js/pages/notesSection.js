import log from '/static/js/core/logger.js';
import eventSystem from '/static/js/core/events.js';
import apiService from '/static/js/services/apiService.js';

/**
 * Unified Notes Component
 * Handles all notes functionality including tabbed interfaces
 */
class NotesComponent {
  constructor() {
    this.instances = new Map();
    this.initialized = false;
    log('info', 'notesSection.js', 'constructor', '🔄 Unified Notes component created');

    document.addEventListener('DOMContentLoaded', () => {
      if (this.initialized) {
        log('warn', 'notesSection.js', 'DOMContentLoaded', '⚠️ DOMContentLoaded fired again, but NotesComponent already initialized.');
        return;
      }
      this.initialized = true;
      window.notesScriptLoaded = true;
      log('info', 'notesSection.js', 'DOMContentLoaded', '✅ DOMContentLoaded - Initializing Notes Components.');


      // Initialize each notesData container
      document.querySelectorAll('[id^="notesData"]').forEach(container => {
        log('debug', 'notesSection.js', 'DOMContentLoaded', '🔎 Found notesData container', {containerId: container.id});
        const ctrl = this.initNotes(container.id);
        // Assuming there's only one primary notesController for now, or the last one initialized takes precedence
        window.notesController = ctrl;
      });

      // Listen for our custom tabs.change event
      eventSystem.subscribe('tabs.change', ({containerId, activeTab}) => {
        log('debug', 'notesSection.js', 'tabs.change', '📬 Received tabs.change event', {containerId, activeTab});
        // This check assumes the notes section is within a container with id 'formTabs' and the tab name is 'Notes'
        if (containerId === 'formTabs' && this.normalizeTabName(activeTab) === 'notes') {
          log('info', 'notesSection.js', 'tabs.change', '➡️ Notes tab activated via event system');
          const ctrl = window.notesController; // Or use this.getNotes(containerId) if supporting multiple distinct notes components per page
          if (ctrl) {
            ctrl.showTab(); // Explicitly ensure tab is marked as active
            ctrl.loadNotes(ctrl.getState().currentFilters, true); // Force reload
          } else {
             log('error', 'notesSection.js', 'tabs.change', '❌ notesController not found for active tab.');
          }
        }
      });
       log('info', 'notesSection.js', 'DOMContentLoaded', '✅ DOMContentLoaded - Initialization complete.');
    });
  }

  /**
   * Normalize tab name for case-insensitive comparison
   * @param {string} name - Tab name to normalize
   * @returns {string} - Normalized tab name
   */
  normalizeTabName(name) {
    return (name || '').toLowerCase().trim();
  }


  /**
   * Initialize a notes section
   * @param {string} containerId - Container element ID (defaults to 'notesData')
   * @returns {Object} - Notes controller or null if initialization failed
   */
  initNotes(containerId = 'notesData') {
    const functionName = 'initNotes';

    // Get data attributes from the notesData div
    const notesData = document.getElementById(containerId);
    if (!notesData) {
      log('error', 'notesSection.js', functionName, `❌ Notes data container not found: ${containerId}`);
      return null;
    }

    // Check if already initialized
    if (this.instances.has(containerId)) {
      log('warn', 'notesSection.js', functionName, `⚠️ Notes already initialized for container: ${containerId}`);
      return this.instances.get(containerId);
    }

    // Extract configuration from data attributes
    const notableType = notesData.dataset.notableType;
    const notableId = notesData.dataset.notableId;
    const currentUserId = notesData.dataset.userId;
    const currentUsername = notesData.dataset.username;
    const scriptName = 'notesSection'; // Unified script name

    log('info', scriptName, functionName, '🔄 Initializing Notes Section', {
      notableType,
      notableId,
      currentUserId,
      containerId
    });

    // Get references to essential UI elements
    const notesTabPane = document.getElementById('tab-notes');
    const notesTabButton = document.getElementById('tab-notes-tab'); // The button/link that activates the tab pane
    const notesList = document.getElementById('notesList');
    const notesLoading = document.getElementById('notesLoading');
    const newNoteForm = document.getElementById('newNoteForm');
    const noteContentField = document.getElementById('content');

    log('debug', scriptName, functionName, '📌 UI elements status', {
      notesTabPane: notesTabPane ? '✅ Found #tab-notes' : '❌ Missing #tab-notes',
      notesTabButton: notesTabButton ? '✅ Found #tab-notes-tab' : '❌ Missing #tab-notes-tab',
      notesList: notesList ? '✅ Found #notesList' : '❌ Missing #notesList',
      notesLoading: notesLoading ? '✅ Found #notesLoading' : '❌ Missing #notesLoading',
      newNoteForm: newNoteForm ? '✅ Found #newNoteForm' : '❌ Missing #newNoteForm',
      noteContentField: noteContentField ? '✅ Found #content' : '❌ Missing #content'
    });

    // Date filter elements
    const noteFilterSelect = document.getElementById('noteFilterSelect');
    const dateRangeSelectors = document.getElementById('dateRangeSelectors');
    const dateFrom = document.getElementById('dateFrom');
    const dateTo = document.getElementById('dateTo');
    const applyDateRange = document.getElementById('applyDateRange');
    const noteSearchInput = document.getElementById('noteSearchInput');

     log('debug', scriptName, functionName, '📌 Filter UI elements status', {
      noteFilterSelect: noteFilterSelect ? '✅ Found #noteFilterSelect' : '❌ Missing #noteFilterSelect',
      dateRangeSelectors: dateRangeSelectors ? '✅ Found #dateRangeSelectors' : '❌ Missing #dateRangeSelectors',
      dateFrom: dateFrom ? '✅ Found #dateFrom' : '❌ Missing #dateFrom',
      dateTo: dateTo ? '✅ Found #dateTo' : '❌ Missing #dateTo',
      applyDateRange: applyDateRange ? '✅ Found #applyDateRange' : '❌ Missing #applyDateRange',
      noteSearchInput: noteSearchInput ? '✅ Found #noteSearchInput' : '❌ Missing #noteSearchInput'
    });


    // Optional UI check warning
    if (!notesList || !notesLoading || !newNoteForm || !noteContentField) {
      log("warn", scriptName, functionName, "⚠️ One or more core UI elements are missing. Limited functionality available.");
    }

    // Check initial tab state
    const isTabInitiallyActive = notesTabPane && (notesTabPane.classList.contains('active') || notesTabPane.classList.contains('show'));
    log("info", scriptName, functionName, `📌 Initial tab active status (#tab-notes): ${isTabInitiallyActive ? 'Active' : 'Inactive'}`);


    // Create and insert status message area dynamically
    const statusMessage = document.createElement('div');
    statusMessage.className = 'alert mt-3 d-none';
    statusMessage.setAttribute('role', 'alert');
    if (newNoteForm) {
      newNoteForm.insertAdjacentElement('afterend', statusMessage);
      log('debug', scriptName, functionName, '✅ Status message element added after newNoteForm.');
    } else if (notesTabPane) {
      notesTabPane.appendChild(statusMessage);
       log('debug', scriptName, functionName, '✅ Status message element added inside notesTabPane.');
    } else {
       log('warn', scriptName, functionName, '⚠️ Could not find location to insert status message element.');
    }


    // State
    const state = {
      notes: [],
      isLoading: false,
      currentFilters: { days: '0' }, // Default to 'All notes'
      searchTerm: '',
      notesLoadedForCurrentView: false // Track if notes have been loaded for the current filters/search
    };

    log('debug', scriptName, functionName, '✅ Initial state set', state);


    // Set default dates for date pickers
    function setDefaultDates() {
      const setDefaultFunctionName = "setDefaultDates";
      if (dateFrom && dateTo) {
        const today = new Date();
        const weekAgo = new Date();
        weekAgo.setDate(today.getDate() - 7);

        dateFrom.value = formatDateForInput(weekAgo);
        dateTo.value = formatDateForInput(today);
        log('debug', scriptName, setDefaultFunctionName, '✅ Default dates set for inputs.');
      } else {
        log('debug', scriptName, setDefaultFunctionName, '⚠️ Date inputs not found, skipping default date setting.');
      }
    }

    // Format date for date input field (YYYY-MM-DD)
    function formatDateForInput(date) {
       const formatFunctionName = "formatDateForInput";
       const formatted = date.toISOString().split('T')[0];
       log('debug', scriptName, formatFunctionName, `Formatted date: ${formatted}`, {originalDate: date});
       return formatted;
    }

    // Initialize date pickers with default values
    setDefaultDates();

    /**
     * Show status message
     * @param {string} message - Message to show
     * @param {string} type - Message type (success, danger, warning, info)
     */
    function showStatus(message, type = 'success') {
      const statusFunctionName = "showStatus";
      log("debug", scriptName, statusFunctionName, `Showing status message: "${message}"`, { type });

      if (statusMessage) {
        statusMessage.className = `alert alert-${type} mt-3`;
        statusMessage.textContent = message;
        statusMessage.classList.remove('d-none');

        // Auto-hide after 5 seconds
        setTimeout(() => {
          if (statusMessage) {
             statusMessage.classList.add('d-none');
             log("debug", scriptName, statusFunctionName, "Status message hidden after timeout.");
          }
        }, 5000);
         log('debug', scriptName, statusFunctionName, '✅ Status message element updated and shown.');
      } else {
         log('warn', scriptName, statusFunctionName, '⚠️ Status message element not found, cannot show message.');
      }
    }

    /**
     * Load notes with optional filters
     * @param {Object} filters - Optional filters
     * @param {boolean} forceReload - Force reload even if already loaded
     */
    function loadNotes(filters = {}, forceReload = false) {
      const loadFunctionName = "loadNotes";
      log("info", scriptName, loadFunctionName, "➡️ Attempting to load notes.", {
        currentState: {...state}, // Clone to avoid logging reactivity issues
        requestedFilters: filters,
        forceReload: forceReload
      });


      // Update state
      state.currentFilters = filters;

      // Check if notes are already loaded for current view unless forceReload is true
      if (state.notesLoadedForCurrentView && !forceReload) {
        log("debug", scriptName, loadFunctionName, "⏩ Skipping load: Notes already loaded for current view and forceReload is false.");
        return;
      }

      log("info", scriptName, loadFunctionName, "🔄 Loading notes with filters", {
        filters,
        searchTerm: state.searchTerm
      });

      state.isLoading = true;

      if (notesLoading) {
        notesLoading.style.display = 'block';
        log('debug', scriptName, loadFunctionName, '✅ notesLoading element shown.');
      } else {
         log('warn', scriptName, loadFunctionName, '⚠️ notesLoading element not found.');
      }


      if (notesList) {
        notesList.innerHTML = '<div class="text-center py-3"><div class="spinner-border text-primary spinner-border-sm me-2" role="status"></div>Connecting to notes service...</div>';
        log('debug', scriptName, loadFunctionName, '✅ notesList innerHTML set to connecting message.');
      } else {
        log('warn', scriptName, loadFunctionName, '⚠️ notesList element not found.');
      }


      // Build query string
      let queryParams = new URLSearchParams();
      queryParams.append('notable_type', notableType);
      queryParams.append('notable_id', notableId);

      // Add additional filters if provided
      for (const [key, value] of Object.entries(filters)) {
        if (value !== null && value !== undefined && value !== '') { // Only append non-empty values
           queryParams.append(key, value);
        }
      }

      // Add search term if present
      if (state.searchTerm) {
        queryParams.append('q', state.searchTerm);
      }

      const endpoint = `/api/notes/query?${queryParams.toString()}`;
      log("debug", scriptName, loadFunctionName, "Built query URL", endpoint);

      log("debug", scriptName, loadFunctionName, "➡️ Making API GET request to notes endpoint."); // Added log
      apiService.get(endpoint)
        .then(data => {
          log("debug", scriptName, loadFunctionName, "✅ API GET request successful."); // Added log
          state.isLoading = false;
          log("debug", scriptName, loadFunctionName, "✅ API request successful.", {url: endpoint, data});

          if (notesLoading) {
            notesLoading.style.display = 'none';
             log('debug', scriptName, loadFunctionName, '✅ notesLoading element hidden on success.');
          }


          log("debug", scriptName, loadFunctionName, "✅ Response payload received", {
            url: endpoint,
            payload: data
          });

          state.notes = data.data || [];
          renderNotes(state.notes);
          state.notesLoadedForCurrentView = true; // Mark as loaded for the current view

          log("info", scriptName, loadFunctionName, "✅ Notes loaded and rendered successfully.");

          // Publish notes loaded event
          eventSystem.publish('notes.loaded', {
            containerId,
            notableType,
            notableId,
            notes: state.notes,
            filters: state.currentFilters,
            searchTerm: state.searchTerm
          });
           log('debug', scriptName, loadFunctionName, '✅ "notes.loaded" event published.');
        })
        .catch(error => {
          log("error", scriptName, loadFunctionName, "❌ API GET request failed."); // Added log
          state.isLoading = false;
          state.notesLoadedForCurrentView = false; // Loading failed, so reset this flag

          log("error", scriptName, loadFunctionName, "❌ Error loading notes from API", {
            url: endpoint,
            error: error
          });


          if (notesLoading) {
            notesLoading.style.display = 'none';
             log('debug', scriptName, loadFunctionName, '✅ notesLoading element hidden on error.');
          }

          if (notesList) {
            notesList.innerHTML = `
              <div class="alert alert-danger" role="alert">
                <h5>Error loading notes</h5>
                <p>${error.message || 'An unknown error occurred'}</p>
                <p>Please check:</p>
                <ul>
                  <li>If the API server is running and reachable.</li>
                  <li>The network connection.</li>
                  <li>The browser console for more details.</li>
                </ul>
                <button class="btn btn-sm btn-primary mt-2" onclick="window.notesController.refresh()">
                  <i class="fas fa-sync-alt me-1"></i> Retry
                </button>
              </div>`;
             log('debug', scriptName, loadFunctionName, '✅ notesList innerHTML set to error message.');
          } else {
             log('warn', scriptName, loadFunctionName, '⚠️ notesList element not found to display error message.');
          }


          showStatus(`Failed to load notes: ${error.message || 'Unknown error'}`, 'danger');


          // Publish notes error event
          eventSystem.publish('notes.error', {
            containerId,
            notableType,
            notableId,
            error,
            filters: state.currentFilters,
            searchTerm: state.searchTerm,
            action: 'load'
          });
           log('debug', scriptName, loadFunctionName, '✅ "notes.error" event published.');
        });
    }

    /**
     * Render notes in the UI
     * @param {Array} notes - Notes to render
     */
    function renderNotes(notes) {
      const renderFunctionName = "renderNotes";
       log("info", scriptName, renderFunctionName, `➡️ Attempting to render ${notes ? notes.length : 0} notes.`);


      if (!notesList) {
        log("warn", scriptName, renderFunctionName, "❌ Notes list element not found (#notesList). Cannot render.");
        return;
      }

      log("debug", scriptName, renderFunctionName, `📝 Rendering ${notes ? notes.length : 0} notes`);

      if (!notes || notes.length === 0) {
        notesList.innerHTML = '<div class="text-center py-3 text-muted">No notes found matching the criteria.</div>';
        log("info", scriptName, renderFunctionName, "✅ No notes found, displayed message.");
        return;
      }

      let html = '';
      notes.forEach(note => {
        const noteDate = new Date(note.created_at || Date.now());
        const formattedDate = noteDate.toLocaleString(undefined, {
          dateStyle: 'medium',
          timeStyle: 'short'
        });

        // Determine display username with fallbacks
        let displayUsername = 'Unknown User';
        if (note.user_id && currentUserId && note.user_id.toString() === currentUserId.toString()) {
          displayUsername = currentUsername || 'You';
        } else if (note.user && typeof note.user === 'object') {
          displayUsername = note.user.username || note.user.name || note.user.email || displayUsername;
        } else if (note.user && typeof note.user === 'string') {
          displayUsername = note.user;
        } else if (note.username) {
          displayUsername = note.username;
        }
         log('debug', scriptName, renderFunctionName, 'Processing note for rendering', {noteId: note.id, displayUsername, created_at: note.created_at});


        html += `
          <div class="note-item mb-3 p-3 border rounded shadow-sm">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <strong class="text-primary">${displayUsername}</strong>
              <small class="text-muted">${formattedDate}</small>
            </div>
            <div class="note-content">
              ${note.processed_content || note.content || '(No content)'}
            </div>
          </div>
        `;
      });

      notesList.innerHTML = html;
      log("info", scriptName, renderFunctionName, "✅ Notes rendered successfully.");
    }

    /**
     * Add a new note
     * @param {string} content - Note content
     * @returns {Promise} - Promise that resolves when the note is added
     */
    function addNote(content) {
      const addFunctionName = "addNote";
       log("info", scriptName, addFunctionName, "➡️ Attempting to add new note.");

      if (!content || content.trim() === '') {
        log("warn", scriptName, addFunctionName, "⚠️ Note content is empty. Aborting submission.");
        showStatus('Please enter a note.', 'warning');
        if (noteContentField) noteContentField.focus();
        return Promise.reject(new Error('Note content is empty'));
      }

      log("info", scriptName, addFunctionName, "➕ Adding new note");

      // Disable submit button during submission
      const submitBtn = newNoteForm?.querySelector('button[type="submit"]');
      const originalButtonHtml = submitBtn ? submitBtn.innerHTML : '';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Adding...';
         log('debug', scriptName, addFunctionName, '✅ Submit button disabled and text changed.');
      } else {
         log('warn', scriptName, addFunctionName, '⚠️ Submit button not found.');
      }


      // Prepare data
      const noteData = {
        content: content.trim(),
        notable_type: notableType,
        notable_id: notableId,
        user_id: currentUserId || null // Send null if currentUserId is not available
      };

      const postEndpoint = "/api/notes/";
      log("debug", scriptName, addFunctionName, "Preparing POST request", {
        url: postEndpoint,
        payload: noteData
      });

      log("debug", scriptName, addFunctionName, "➡️ Making API POST request to add note."); // Added log
      return apiService.post(postEndpoint, noteData)
        .then(data => {
          log("debug", scriptName, addFunctionName, "✅ API POST request successful."); // Added log

          log("debug", scriptName, addFunctionName, "✅ Response payload received for POST", {
            url: postEndpoint,
            payload: data
          });

          if (newNoteForm) {
            newNoteForm.reset();
            if (noteContentField) noteContentField.focus();
             log('debug', scriptName, addFunctionName, '✅ New note form reset and focus set.');
          }


          state.notesLoadedForCurrentView = false; // Invalidate current view
          log('debug', scriptName, addFunctionName, '🔄 Resetting notesLoadedForCurrentView flag.');
          loadNotes(state.currentFilters, true); // Force reload with current filters
          showStatus('Note added successfully!');

          log("info", scriptName, addFunctionName, "✅ Note added successfully");

          // Publish note added event
          eventSystem.publish('notes.added', {
            containerId,
            notableType,
            notableId,
            note: data.data || data // Use data.data if available, otherwise the raw data
          });
           log('debug', scriptName, addFunctionName, '✅ "notes.added" event published.');

          return data; // Resolve with the response data
        })
        .catch(error => {
           log("error", scriptName, addFunctionName, "❌ API POST request failed."); // Added log
          showStatus(`Error adding note: ${error.message || 'Unknown error'}`, 'danger');

          log("error", scriptName, addFunctionName, "❌ Error adding note via API", {
            url: postEndpoint,
            error: error
          });

          // Publish note error event
          eventSystem.publish('notes.error', {
            containerId,
            notableType,
            notableId,
            error,
            action: 'add'
          });
           log('debug', scriptName, addFunctionName, '✅ "notes.error" event published.');


          throw error; // Re-throw the error so the promise chain can handle it
        })
        .finally(() => {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalButtonHtml || '<i class="fas fa-plus me-1"></i> Add Note';
             log('debug', scriptName, addFunctionName, '✅ Submit button re-enabled and text restored.');
          }
        });
    }

    // Set up event listeners for tabbed interface
    if (notesTabButton) {
      // IMPORTANT: Check if listener already attached to avoid duplicates
      if (!notesTabButton._notesTabListenerAttached) {
        log("info", scriptName, "tabEvents", "🔄 Setting up notes tab 'shown.bs.tab' event listener.");

        notesTabButton.addEventListener('shown.bs.tab', function(event) {
          log("info", scriptName, "tabShown", "🚀 Notes tab 'shown.bs.tab' event triggered.");

          // Force tab to stay visible - prevents hiding issues in some complex layouts
          if (notesTabPane) {
            notesTabPane.classList.add('active', 'show');
            log("info", scriptName, "tabShown", "📌 Enforced notes tab visibility.");
          } else {
             log("warn", scriptName, "tabShown", "⚠️ notesTabPane element not found, cannot enforce visibility.");
          }


          // Load notes when the tab is shown. Force reload if notes haven't been loaded for the current view.
          log("debug", scriptName, "tabShown", "➡️ Calling loadNotes from 'shown.bs.tab' handler."); // Added log
          loadNotes(state.currentFilters, !state.notesLoadedForCurrentView);
        });

        // Also listen for 'hide' events to debug tab hiding - useful for diagnosing conflicts
        notesTabButton.addEventListener('hide.bs.tab', function(event) {
          log("warn", scriptName, "tabHide", "⚠️ Notes tab 'hide.bs.tab' event triggered - this may indicate a conflict or unexpected behavior.");
        });

        notesTabButton._notesTabListenerAttached = true; // Mark as attached
        log("debug", scriptName, "tabEvents", "✅ 'shown.bs.tab' and 'hide.bs.tab' listeners attached to #tab-notes-tab.");
      } else {
        log("warn", scriptName, "tabEvents", "⚠️ Tab listener already attached to #tab-notes-tab, skipping.");
      }
    } else {
       log("warn", scriptName, "tabEvents", "❌ Notes tab button element (#tab-notes-tab) not found. Tab activation might not work as expected.");
    }


    // Filter by days dropdown
    if (noteFilterSelect) {
      noteFilterSelect.addEventListener('change', function(e) {
        const functionName = "noteFilterSelect_change";
        const value = this.value;

        log("info", scriptName, functionName, `📅 Filter changed: ${value}`);

        // Toggle date range selectors visibility
        if (value === 'custom' && dateRangeSelectors) {
          dateRangeSelectors.classList.remove('d-none');
          state.notesLoadedForCurrentView = false; // Invalidate for custom range
          if (notesList) notesList.innerHTML = '<div class="text-center py-3 text-muted">Select a date range and click "Apply".</div>';
          if (notesLoading) notesLoading.style.display = 'none';
          log('debug', scriptName, functionName, '✅ Custom date range selected, showing date selectors.');
          return; // Stop here, wait for 'Apply'
        } else if (dateRangeSelectors) {
          dateRangeSelectors.classList.add('d-none');
          log('debug', scriptName, functionName, '✅ Non-custom filter selected, hiding date selectors.');
        }

        // For predefined filters (7, 30, All)
        state.currentFilters = { days: value };
        state.notesLoadedForCurrentView = false; // Invalidate for new filter
        log('debug', scriptName, functionName, '🔄 Resetting notesLoadedForCurrentView flag for predefined filter.');
        log("debug", scriptName, functionName, "➡️ Calling loadNotes from filter change handler."); // Added log
        loadNotes(state.currentFilters, true); // Force reload with new filter
      });
       log('debug', scriptName, 'filterEvents', '✅ Change listener attached to #noteFilterSelect.');
    } else {
        log('warn', scriptName, 'filterEvents', '⚠️ Filter select element (#noteFilterSelect) not found.');
    }


    // Handle Apply Date Range button click
    if (applyDateRange) {
      applyDateRange.addEventListener('click', function(e) {
        const functionName = "applyDateRange_click";
        log("info", scriptName, functionName, "➡️ Apply Date Range button clicked.");

        if (!dateFrom || !dateTo) {
          log("error", scriptName, functionName, "❌ Date range inputs not found. Cannot apply filter.");
          showStatus('Date range inputs are missing.', 'danger');
          return;
        }

        const fromValue = dateFrom.value;
        const toValue = dateTo.value;

        if (!fromValue || !toValue) {
          showStatus('Please select both From and To dates', 'warning');
          log("warn", scriptName, functionName, "⚠️ From or To date is missing.");
          return;
        }

        const fromDate = new Date(fromValue);
        const toDate = new Date(toValue);
        toDate.setHours(23, 59, 59, 999); // Set to end of day for inclusivity

        if (fromDate > toDate) {
          showStatus('From date must be before or the same as To date', 'warning');
          log("warn", scriptName, functionName, "⚠️ From date is after To date.");
          return;
        }

        log("info", scriptName, functionName, "📅 Custom date range applied", {
          fromDate: fromValue,
          toDate: toValue
        });

        state.currentFilters = {
          from_date: fromValue,
          to_date: toValue,
          custom: true // Indicate custom range
        };
        state.notesLoadedForCurrentView = false; // Invalidate for custom range
        log('debug', scriptName, functionName, '🔄 Resetting notesLoadedForCurrentView flag for custom range.');
        log("debug", scriptName, functionName, "➡️ Calling loadNotes from date range apply handler."); // Added log
        loadNotes(state.currentFilters, true); // Force reload with custom range
      });
       log('debug', scriptName, 'filterEvents', '✅ Click listener attached to #applyDateRange.');
    } else {
        log('warn', scriptName, 'filterEvents', '⚠️ Apply Date Range button (#applyDateRange) not found.');
    }


    // Handle Search input changes
    if (noteSearchInput) {
      // Using 'input' event for immediate feedback while typing
      noteSearchInput.addEventListener('input', debounce(function(e) {
         const functionName = "noteSearchInput_input";
        const searchTerm = this.value.trim();
        log("debug", scriptName, functionName, "🔍 Search input changed (debounced)", { searchTerm });

        // Only trigger search if term is not empty or if it became empty (to clear search)
        if (searchTerm !== state.searchTerm) {
            state.searchTerm = searchTerm;
            state.notesLoadedForCurrentView = false; // Invalidate for new search term
            log('debug', scriptName, functionName, '🔄 Resetting notesLoadedForCurrentView flag for new search term.');
             log("debug", scriptName, functionName, "➡️ Calling loadNotes from search input handler."); // Added log
            loadNotes(state.currentFilters, true); // Force reload with new search term
        } else {
             log("debug", scriptName, functionName, "🔍 Search term unchanged, skipping load.");
        }
      }, 300)); // Debounce with 300ms delay
       log('debug', scriptName, 'searchEvents', '✅ Input listener attached to #noteSearchInput with debounce.');
    } else {
       log('warn', scriptName, 'searchEvents', '⚠️ Search input element (#noteSearchInput) not found.');
    }


    // Debounce function to limit how often a function is called
    function debounce(func, delay) {
        let timeoutId;
        return function(...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                func.apply(this, args);
            }, delay);
        };
    }


    // Handle adding a new note form submission
    if (newNoteForm) {
      // Remove any existing listeners first to prevent duplicates on re-initialization
      if (newNoteForm._hasSubmitListener) {
        log("warn", scriptName, "formEvents", "⚠️ Form already has submit listener, removing old one.");
        const oldListener = newNoteForm._submitListener;
        if (oldListener) {
          newNoteForm.removeEventListener('submit', oldListener);
        }
      }

      // Add new listener
      const submitListener = function(e) {
        e.preventDefault(); // Prevent default form submission
        const functionName = "newNoteForm_submit";
        log("info", scriptName, functionName, "📝 Note form submitted.");

        const noteContent = noteContentField ? noteContentField.value : '';
        addNote(noteContent)
          .then(() => {
            // Success handled within addNote, no need to do anything here
            log("debug", scriptName, functionName, "✅ addNote promise resolved successfully.");
          })
          .catch(error => {
            log("error", scriptName, functionName, "❌ addNote promise rejected.", error);
            // Error handled within addNote, but we could add more here if needed
          });
      };

      newNoteForm.addEventListener('submit', submitListener);
      newNoteForm._submitListener = submitListener; // Store reference to remove later
      newNoteForm._hasSubmitListener = true; // Mark as having a listener
       log('debug', scriptName, 'formEvents', '✅ Submit listener attached to #newNoteForm.');

    } else {
       log('warn', scriptName, 'formEvents', '⚠️ New note form element (#newNoteForm) not found.');
    }


    // Notes controller object - provides an interface for external interaction
    const controller = {
      loadNotes: (filters = state.currentFilters, forceReload = true) => { // Default to current filters, force reload true
        log("info", scriptName, "controller.loadNotes", "➡️ Controller method loadNotes called.", {filters, forceReload});
        loadNotes(filters, forceReload);
      },
      addNote: (content) => {
         log("info", scriptName, "controller.addNote", "➡️ Controller method addNote called.");
         return addNote(content); // Return the promise
      },
      refresh: () => {
        log("info", scriptName, "controller.refresh", "➡️ Controller method refresh called.");
        loadNotes(state.currentFilters, true); // Force reload with current filters
      },
      getState: () => {
         log("debug", scriptName, "controller.getState", "➡️ Controller method getState called.");
         return { ...state }; // Return a copy of the state
      },
      search: (searchTerm) => {
        const controllerFunctionName = "controller.search";
        log("info", scriptName, controllerFunctionName, "➡️ Controller method search called.", {searchTerm});
        if (noteSearchInput) {
          noteSearchInput.value = searchTerm; // Update input field
           log('debug', scriptName, controllerFunctionName, '✅ #noteSearchInput value updated.');
        } else {
           log('warn', scriptName, controllerFunctionName, '⚠️ #noteSearchInput not found, cannot update value.');
        }

        // Manually trigger the search logic (bypassing debounce for immediate controller calls if needed)
        // Or call the debounced function directly if you want the delay
        const searchTermTrimmed = (searchTerm || '').trim();
        if (searchTermTrimmed !== state.searchTerm) {
            state.searchTerm = searchTermTrimmed;
            state.notesLoadedForCurrentView = false; // Invalidate
            log('debug', scriptName, controllerFunctionName, '🔄 Resetting notesLoadedForCurrentView flag for search.');
             log("debug", scriptName, controllerFunctionName, "➡️ Calling loadNotes from controller search method."); // Added log
             loadNotes(state.currentFilters, true); // Force reload with new search term
        } else {
            log("debug", scriptName, controllerFunctionName, "🔍 Search term unchanged, skipping load.");
        }
      },
      filter: (filters) => {
        const controllerFunctionName = "controller.filter";
         log("info", scriptName, controllerFunctionName, "➡️ Controller method filter called.", {filters});

        // Update the filter select/date inputs in the UI to reflect the applied filter
        if (noteFilterSelect && filters.days !== undefined) {
            noteFilterSelect.value = filters.days;
             log('debug', scriptName, controllerFunctionName, '✅ #noteFilterSelect value updated.');
            // Also handle showing/hiding custom date selectors based on the new filter value
            if (filters.days === 'custom' && dateRangeSelectors) {
                 dateRangeSelectors.classList.remove('d-none');
                 // Potentially set date input values if filters include from_date/to_date
                 if(filters.from_date && dateFrom) dateFrom.value = filters.from_date;
                 if(filters.to_date && dateTo) dateTo.value = filters.to_date;
                  log('debug', scriptName, controllerFunctionName, '✅ Custom date range shown and inputs updated.');
            } else if (dateRangeSelectors) {
                 dateRangeSelectors.classList.add('d-none');
                  log('debug', scriptName, controllerFunctionName, '✅ Custom date range hidden.');
            }
        } else if (dateRangeSelectors && filters.custom && filters.from_date && filters.to_date) {
             // Case where only custom date range is provided without a 'days' value in filters
             if (dateRangeSelectors) dateRangeSelectors.classList.remove('d-none');
             if(dateFrom) dateFrom.value = filters.from_date;
             if(dateTo) dateTo.value = filters.to_date;
             if (noteFilterSelect) noteFilterSelect.value = 'custom'; // Update dropdown to 'custom'
              log('debug', scriptName, controllerFunctionName, '✅ Custom date range applied via filter method.');
        } else {
             log('warn', scriptName, controllerFunctionName, '⚠️ Filter UI elements not found or filter format unexpected.');
        }


        state.currentFilters = filters;
        state.notesLoadedForCurrentView = false; // Invalidate for new filters
        log('debug', scriptName, controllerFunctionName, '🔄 Resetting notesLoadedForCurrentView flag for filter.');
        log("debug", scriptName, controllerFunctionName, "➡️ Calling loadNotes from controller filter method."); // Added log
        loadNotes(filters, true); // Force reload with new filters
      },
      showStatus, // Expose the showStatus utility
      // Add method to force tab visibility - useful for external components
      showTab: () => {
         const controllerFunctionName = "controller.showTab";
        if (notesTabPane) {
          notesTabPane.classList.add('active', 'show');
          log("info", scriptName, controllerFunctionName, "📌 Manually forced tab visibility.");
          // Potentially trigger a load here if it's critical that showing the tab loads notes
          // loadNotes(state.currentFilters, !state.notesLoadedForCurrentView); // Decide if showing tab should force a load
          return true;
        }
        log("warn", scriptName, controllerFunctionName, "⚠️ notesTabPane element not found, cannot force tab visibility.");
        return false;
      }
    };

    // Store the controller instance for potential later retrieval by container ID
    this.instances.set(containerId, controller);
    log("debug", scriptName, functionName, `✅ Notes controller instance stored for container: ${containerId}`);


    // Expose the primary controller globally for ease of access (if only one notes component)
    // If multiple notes components are on the page, this should be managed differently (e.g., using getNotes)
    if (containerId === 'notesData') { // Assuming 'notesData' is the main one
        window.notesController = controller;
        log("debug", scriptName, functionName, "🌎 Primary Notes controller exposed globally as window.notesController");
    }


    // Ensure loading indicator is hidden if tab isn't active initially
    if (notesLoading && !isTabInitiallyActive) {
       notesLoading.style.display = 'none';
       log("debug", scriptName, functionName, "✅ notesLoading hidden because tab is not initially active.");
    } else if (notesLoading && isTabInitiallyActive) {
       log("debug", scriptName, functionName, "✅ notesLoading remains visible because tab is initially active, loadNotes will handle hiding.");
    }


    // Check if tab is ready - this is crucial for initial load behavior
    // If the tab is not initially active, display a message prompting the user to select it.
    // If the tab IS initially active, or if there is no tab interface (notesTabPane is null),
    // proceed with loading notes immediately.
    if (notesList && notesTabPane && !isTabInitiallyActive) {
      notesList.innerHTML = '<div class="text-center py-3 text-muted">Select the "Notes" tab to load notes.</div>';
      log("info", scriptName, functionName, "💬 Displayed 'Select the Notes tab' message.");
    } else {
      // If no tab interface or tab is active, load notes immediately
      log("info", scriptName, functionName, "➡️ Entering block to potentially call loadNotes immediately."); // Added log
      if (notesList && notesLoading) { // Add a check for essential elements before attempting load
          log("info", scriptName, functionName, "🔄 Tab is active or notesTabPane not found, attempting to load notes immediately.");
          log("debug", scriptName, functionName, "➡️ Calling loadNotes immediately after initialization."); // Added log
          loadNotes(); // Initial load
          log("debug", scriptName, functionName, "✅ loadNotes called immediately after initialization."); // Added log
      } else {
           log("error", scriptName, functionName, "❌ Cannot load notes immediately, essential UI elements missing."); // Added log
            if (notesLoading) notesLoading.style.display = 'none'; // Hide loading if elements are missing
            if (notesList) notesList.innerHTML = '<div class="text-center py-3 text-danger">Error initializing notes UI elements.</div>';
      }

    }

    log('info', scriptName, functionName, '✅ Notes initialization complete for', containerId);
    return controller; // Return the created controller
  }

  /**
   * Get a notes controller by container ID
   * @param {string} containerId - Container ID
   * @returns {Object|null} - Notes controller or null if not found
   */
  getNotes(containerId = 'notesData') {
     log('info', 'notesSection.js', 'getNotes', `➡️ Attempting to get controller for container: ${containerId}`);
     const controller = this.instances.get(containerId) || null;
     if (controller) {
         log('debug', 'notesSection.js', 'getNotes', `✅ Found controller for ${containerId}.`);
     } else {
         log('warn', 'notesSection.js', 'getNotes', `⚠️ No controller found for ${containerId}.`);
     }
     return controller;
  }
}

const notesComponent = new NotesComponent();
window.notesScriptLoaded = true; // Legacy flag, consider removing if not needed elsewhere
log('info', 'notesSection.js', 'global', '✅ notesSection script loaded and component instantiated.');

// Export the component instance if using ES modules
export default notesComponent;