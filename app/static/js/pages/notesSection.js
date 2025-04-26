import log from '/static/js/core/logger.js';
import eventSystem from '/static/js/core/events.js';
import apiService from '/static/js/services/apiService.js';

/**
 * Unified Notes Component
 * Handles all notes functionality including tabbed interfaces
 * Combines functionality from previous notes.js and notesSection.js
 */
class NotesComponent {
  constructor() {
    this.instances = new Map();
    log('info', 'notesSection.js', 'constructor', 'Unified Notes component created');

    // Initialize on DOMContentLoaded
    document.addEventListener('DOMContentLoaded', () => {
      log("info", "notesSection.js", "DOMContentLoaded", "DOM content loaded. Initializing Notes");

      // Auto-initialize any notes containers found in the DOM
      const notesDataContainers = document.querySelectorAll('[id^="notesData"]');
      notesDataContainers.forEach(container => {
        this.initNotes(container.id);
      });
    });
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
      log('error', 'notesSection.js', functionName, `Notes data container not found: ${containerId}`);
      return null;
    }

    // Check if already initialized
    if (this.instances.has(containerId)) {
      log('warn', 'notesSection.js', functionName, `Notes already initialized for container: ${containerId}`);
      return this.instances.get(containerId);
    }

    // Extract configuration from data attributes
    const notableType = notesData.dataset.notableType;
    const notableId = notesData.dataset.notableId;
    const currentUserId = notesData.dataset.userId;
    const currentUsername = notesData.dataset.username;
    const scriptName = 'notesSection'; // Unified script name

    log('info', scriptName, functionName, 'Initializing Notes Section', {
      notableType,
      notableId,
      currentUserId
    });

    // Get references to essential UI elements
    const notesTabPane = document.getElementById('tab-notes');
    const notesTabButton = document.getElementById('tab-notes-tab');
    const notesList = document.getElementById('notesList');
    const notesLoading = document.getElementById('notesLoading');
    const newNoteForm = document.getElementById('newNoteForm');
    const noteContentField = document.getElementById('content');

    // Date filter elements
    const noteFilterSelect = document.getElementById('noteFilterSelect');
    const dateRangeSelectors = document.getElementById('dateRangeSelectors');
    const dateFrom = document.getElementById('dateFrom');
    const dateTo = document.getElementById('dateTo');
    const applyDateRange = document.getElementById('applyDateRange');
    const noteSearchInput = document.getElementById('noteSearchInput');

    // Optional UI check warning
    if (!notesList || !notesLoading || !newNoteForm || !noteContentField) {
      log("warn", scriptName, functionName, "One or more UI elements are missing. Limited functionality available.");
    }

    // Create and insert status message area dynamically
    const statusMessage = document.createElement('div');
    statusMessage.className = 'alert mt-3 d-none';
    statusMessage.setAttribute('role', 'alert');
    if (newNoteForm) {
      newNoteForm.insertAdjacentElement('afterend', statusMessage);
    } else if (notesTabPane) {
      notesTabPane.appendChild(statusMessage);
    }

    // State
    const state = {
      notes: [],
      isLoading: false,
      currentFilters: { days: '0' }, // Default to 'All notes'
      searchTerm: '',
      notesLoadedForCurrentView: false
    };

    // Set default dates for date pickers
    function setDefaultDates() {
      if (dateFrom && dateTo) {
        const today = new Date();
        const weekAgo = new Date();
        weekAgo.setDate(today.getDate() - 7);

        dateFrom.value = formatDateForInput(weekAgo);
        dateTo.value = formatDateForInput(today);
      }
    }

    // Format date for date input field (YYYY-MM-DD)
    function formatDateForInput(date) {
      return date.toISOString().split('T')[0];
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
      log("debug", scriptName, statusFunctionName, `Showing status message: ${message}`, { type });

      statusMessage.className = `alert alert-${type} mt-3`;
      statusMessage.textContent = message;
      statusMessage.classList.remove('d-none');

      // Auto-hide after 5 seconds
      setTimeout(() => {
        statusMessage.classList.add('d-none');
        log("debug", scriptName, statusFunctionName, "Status message hidden");
      }, 5000);
    }

    /**
     * Load notes with optional filters
     * @param {Object} filters - Optional filters
     * @param {boolean} forceReload - Force reload even if already loaded
     */
    function loadNotes(filters = {}, forceReload = false) {
      const loadFunctionName = "loadNotes";

      // Update state
      state.currentFilters = filters;

      // Check if notes are already loaded for current view
      if (state.notesLoadedForCurrentView && !forceReload) {
        log("debug", scriptName, loadFunctionName, "Skipping load: Notes already loaded for current view");
        return;
      }

      log("info", scriptName, loadFunctionName, "Loading notes with filters", {
        filters,
        searchTerm: state.searchTerm
      });

      state.isLoading = true;

      if (notesLoading) {
        notesLoading.style.display = 'block';
      }

      if (notesList) {
        notesList.innerHTML = '<div class="text-center py-3"><div class="spinner-border text-primary spinner-border-sm me-2" role="status"></div>Connecting to notes service...</div>';
      }

      // Build query string
      let queryParams = new URLSearchParams();
      queryParams.append('notable_type', notableType);
      queryParams.append('notable_id', notableId);

      // Add additional filters if provided
      for (const [key, value] of Object.entries(filters)) {
        queryParams.append(key, value);
      }

      // Add search term if present
      if (state.searchTerm) {
        queryParams.append('q', state.searchTerm);
      }

      const endpoint = `/api/notes/query?${queryParams.toString()}`;
      log("debug", scriptName, loadFunctionName, "Built query URL", endpoint);

      apiService.get(endpoint)
        .then(data => {
          state.isLoading = false;

          if (notesLoading) {
            notesLoading.style.display = 'none';
          }

          log("debug", scriptName, loadFunctionName, "Response payload received", {
            url: endpoint,
            payload: data
          });

          state.notes = data.data || [];
          renderNotes(state.notes);
          state.notesLoadedForCurrentView = true;

          // Publish notes loaded event
          eventSystem.publish('notes.loaded', {
            containerId,
            notableType,
            notableId,
            notes: state.notes,
            filters: state.currentFilters,
            searchTerm: state.searchTerm
          });
        })
        .catch(error => {
          state.isLoading = false;
          state.notesLoadedForCurrentView = false;

          if (notesLoading) {
            notesLoading.style.display = 'none';
          }

          if (notesList) {
            notesList.innerHTML = `
              <div class="alert alert-danger" role="alert">
                <h5>Error loading notes</h5>
                <p>${error.message}</p>
                <p>Possible causes:</p>
                <ul>
                  <li>API server is not running or unreachable</li>
                  <li>Endpoint configuration is incorrect</li>
                  <li>Server error occurred while processing the request</li>
                </ul>
                <button class="btn btn-sm btn-primary mt-2" onclick="window.notesController.refresh()">
                  <i class="fas fa-sync-alt me-1"></i> Retry
                </button>
              </div>`;
          }

          log("error", scriptName, loadFunctionName, "Error loading notes", {
            url: endpoint,
            error: error
          });

          // Publish notes error event
          eventSystem.publish('notes.error', {
            containerId,
            notableType,
            notableId,
            error,
            filters: state.currentFilters,
            searchTerm: state.searchTerm
          });
        });
    }

    /**
     * Render notes in the UI
     * @param {Array} notes - Notes to render
     */
    function renderNotes(notes) {
      const renderFunctionName = "renderNotes";

      if (!notesList) {
        log("warn", scriptName, renderFunctionName, "Notes list element not found");
        return;
      }

      log("debug", scriptName, renderFunctionName, `Rendering ${notes ? notes.length : 0} notes`);

      if (!notes || notes.length === 0) {
        notesList.innerHTML = '<div class="text-center py-3 text-muted">No notes found matching the criteria.</div>';
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
      log("info", scriptName, renderFunctionName, "Notes rendered successfully");
    }

    /**
     * Add a new note
     * @param {string} content - Note content
     * @returns {Promise} - Promise that resolves when the note is added
     */
    function addNote(content) {
      const addFunctionName = "addNote";

      if (!content || content.trim() === '') {
        log("warn", scriptName, addFunctionName, "Note content is empty. Aborting submission.");
        showStatus('Please enter a note.', 'warning');
        if (noteContentField) noteContentField.focus();
        return Promise.reject(new Error('Note content is empty'));
      }

      log("info", scriptName, addFunctionName, "Adding new note");

      // Disable submit button during submission
      const submitBtn = newNoteForm?.querySelector('button[type="submit"]');
      const originalButtonHtml = submitBtn ? submitBtn.innerHTML : '';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Adding...';
      }

      // Prepare data
      const noteData = {
        content: content.trim(),
        notable_type: notableType,
        notable_id: notableId,
        user_id: currentUserId || null
      };

      const postEndpoint = "/api/notes/";
      log("debug", scriptName, addFunctionName, "Preparing POST request", {
        url: postEndpoint,
        payload: noteData
      });

      return apiService.post(postEndpoint, noteData)
        .then(data => {
          log("debug", scriptName, addFunctionName, "Response payload received for POST", {
            url: postEndpoint,
            payload: data
          });

          if (newNoteForm) {
            newNoteForm.reset();
            if (noteContentField) noteContentField.focus();
          }

          state.notesLoadedForCurrentView = false; // Invalidate current view
          loadNotes(state.currentFilters, true); // Force reload with current filters
          showStatus('Note added successfully!');

          log("info", scriptName, addFunctionName, "Note added successfully");

          // Publish note added event
          eventSystem.publish('notes.added', {
            containerId,
            notableType,
            notableId,
            note: data.data || data
          });

          return data;
        })
        .catch(error => {
          showStatus(`Error adding note: ${error.message}`, 'danger');

          log("error", scriptName, addFunctionName, "Error adding note", {
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

          throw error;
        })
        .finally(() => {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalButtonHtml || '<i class="fas fa-plus me-1"></i> Add Note';
          }
        });
    }

    // Set up event listeners for tabbed interface
    if (notesTabButton) {
      notesTabButton.addEventListener('shown.bs.tab', function(event) {
        log("info", scriptName, "tabShown", "Notes tab 'shown.bs.tab' event triggered");
        loadNotes(state.currentFilters, !state.notesLoadedForCurrentView);
      });
    }

    // Filter by days dropdown
    if (noteFilterSelect) {
      noteFilterSelect.addEventListener('change', function(e) {
        const functionName = "noteFilterSelect_change";
        const value = this.value;

        log("info", scriptName, functionName, `Filter changed: ${value}`);

        // Toggle date range selectors visibility
        if (value === 'custom' && dateRangeSelectors) {
          dateRangeSelectors.classList.remove('d-none');
          state.notesLoadedForCurrentView = false;
          if (notesList) notesList.innerHTML = '<div class="text-center py-3 text-muted">Select a date range and click "Apply".</div>';
          if (notesLoading) notesLoading.style.display = 'none';
          return;
        } else if (dateRangeSelectors) {
          dateRangeSelectors.classList.add('d-none');
        }

        // For predefined filters (7, 30, All)
        state.currentFilters = { days: value };
        state.notesLoadedForCurrentView = false;
        loadNotes(state.currentFilters, true);
      });
    }

    // Handle Apply Date Range button click
    if (applyDateRange) {
      applyDateRange.addEventListener('click', function(e) {
        const functionName = "applyDateRange_click";

        if (!dateFrom || !dateTo) {
          log("error", scriptName, functionName, "Date range inputs not found");
          showStatus('Date range inputs are missing.', 'danger');
          return;
        }

        const fromValue = dateFrom.value;
        const toValue = dateTo.value;

        if (!fromValue || !toValue) {
          showStatus('Please select both From and To dates', 'warning');
          return;
        }

        const fromDate = new Date(fromValue);
        const toDate = new Date(toValue);
        toDate.setHours(23, 59, 59, 999); // Set to end of day for inclusivity

        if (fromDate > toDate) {
          showStatus('From date must be before or the same as To date', 'warning');
          return;
        }

        log("info", scriptName, functionName, "Custom date range applied", {
          fromDate: fromValue,
          toDate: toValue
        });

        state.currentFilters = {
          from_date: fromValue,
          to_date: toValue,
          custom: true
        };
        state.notesLoadedForCurrentView = false;
        loadNotes(state.currentFilters, true);
      });
    }

    // Handle Search input changes
    if (noteSearchInput) {
      noteSearchInput.addEventListener('input', function(e) {
        const functionName = "noteSearchInput_input";
        const searchTerm = this.value.trim();
        log("debug", scriptName, functionName, "Search input changed", { searchTerm });

        state.searchTerm = searchTerm;
        state.notesLoadedForCurrentView = false;
        loadNotes(state.currentFilters, true);
      });
    }

    // Handle adding a new note form submission
    if (newNoteForm) {
      newNoteForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const functionName = "newNoteForm_submit";

        addNote(noteContentField ? noteContentField.value : '')
          .then(() => {
            // Success handled within addNote
          })
          .catch(error => {
            log("error", scriptName, functionName, "Add note promise rejected", error);
          });
      });
    }

    // Notes controller object
    const controller = {
      loadNotes: (filters = {}, forceReload = false) => loadNotes(filters, forceReload),
      addNote,
      refresh: () => loadNotes(state.currentFilters, true),
      getState: () => ({ ...state }),
      search: (searchTerm) => {
        if (noteSearchInput) noteSearchInput.value = searchTerm;
        state.searchTerm = searchTerm;
        state.notesLoadedForCurrentView = false;
        loadNotes(state.currentFilters, true);
      },
      filter: (filters) => {
        state.currentFilters = filters;
        state.notesLoadedForCurrentView = false;
        loadNotes(filters, true);
      },
      showStatus
    };

    // Store the controller instance
    this.instances.set(containerId, controller);

    // Expose controller globally for external access
    window.notesController = controller;
    log("debug", scriptName, functionName, "Notes controller exposed globally");

    // Ensure loading indicator is hidden if tab isn't active initially
    if (notesLoading) {
      notesLoading.style.display = 'none';
    }

    // Only show the "Select tab" message if the notes tab is NOT initially active
    if (notesList && notesTabPane && !(notesTabPane.classList.contains('active') || notesTabPane.classList.contains('show'))) {
      notesList.innerHTML = '<div class="text-center py-3 text-muted">Select the "Notes" tab to load notes.</div>';
    } else {
      // If no tab interface or tab is active, load notes immediately
      loadNotes();
    }

    log('info', scriptName, functionName, 'Notes initialization complete for', containerId);
    return controller;
  }

  /**
   * Get a notes controller by container ID
   * @param {string} containerId - Container ID
   * @returns {Object|null} - Notes controller or null if not found
   */
  getNotes(containerId = 'notesData') {
    return this.instances.get(containerId) || null;
  }
}

// Create singleton instance
const notesComponent = new NotesComponent();
export default notesComponent;