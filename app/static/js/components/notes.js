import log from '/static/js/core/logger.js';
import eventSystem from '/static/js/core/events.js';
import apiService from '/static/js/services/apiService.js';

/**
 * Notes component for displaying and managing notes
 */
class NotesComponent {
  constructor() {
    this.instances = new Map();
    log('info', 'notes.js', 'constructor', 'Notes component created');
  }

  /**
   * Initialize a notes section
   * @param {string} containerId - Container element ID (defaults to 'notesData')
   * @returns {Object} - Notes controller
   */
  initNotes(containerId = 'notesData') {
    const functionName = 'initNotes';

    // Check if already initialized
    if (this.instances.has(containerId)) {
      log('warn', 'notes.js', functionName, `Notes already initialized for container: ${containerId}`);
      return this.instances.get(containerId);
    }

    // Get data attributes from the notesData div
    const notesData = document.getElementById(containerId);
    if (!notesData) {
      log('error', 'notes.js', functionName, `Notes data container not found: ${containerId}`);
      return null;
    }

    const notableType = notesData.dataset.notableType;
    const notableId = notesData.dataset.notableId;
    const currentUserId = notesData.dataset.userId;
    const currentUsername = notesData.dataset.username;
    const scriptName = notesData.dataset.scriptName || 'notes_module';

    log('info', scriptName, functionName, 'Initializing Notes Section module', {
      notableType,
      notableId,
      currentUserId
    });

    // UI Elements
    const notesList = document.getElementById('notesList');
    const notesLoading = document.getElementById('notesLoading');
    const statusMessage = document.createElement('div');
    statusMessage.className = 'alert mt-3 d-none';

    // Add status message container after the form
    const newNoteForm = document.getElementById('newNoteForm');
    if (newNoteForm) {
      newNoteForm.insertAdjacentElement('afterend', statusMessage);
    }

    // State
    const state = {
      notes: [],
      isLoading: false,
      currentFilter: null,
      searchTerm: ''
    };

    /**
     * Load notes with optional filters
     * @param {Object} filters - Optional filters
     */
    function loadNotes(filters = {}) {
      const loadFunctionName = "loadNotes";
      log("info", scriptName, loadFunctionName, "Loading notes with filters", filters);

      state.isLoading = true;
      state.currentFilter = filters;

      if (notesLoading) {
        notesLoading.style.display = 'block';
      }

      // Build query string
      let queryParams = new URLSearchParams();
      queryParams.append('notable_type', notableType);
      queryParams.append('notable_id', notableId);

      // Add additional filters if provided
      for (const [key, value] of Object.entries(filters)) {
        queryParams.append(key, value);
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

          // Publish notes loaded event
          eventSystem.publish('notes.loaded', {
            notableType,
            notableId,
            notes: state.notes,
            filters
          });
        })
        .catch(error => {
          state.isLoading = false;

          if (notesLoading) {
            notesLoading.style.display = 'none';
          }

          if (notesList) {
            notesList.innerHTML = `<div class="alert alert-danger">Error loading notes: ${error.message}</div>`;
          }

          log("error", scriptName, loadFunctionName, "Error loading notes", {
            url: endpoint,
            error: error
          });

          // Publish notes error event
          eventSystem.publish('notes.error', {
            notableType,
            notableId,
            error,
            filters
          });
        });
    }

    /**
     * Render notes in the UI
     * @param {Array} notes - Notes to render
     */
    function renderNotes(notes) {
      const renderFunctionName = "renderNotes";
      log("debug", scriptName, renderFunctionName, `Rendering ${notes ? notes.length : 0} notes`);

      if (!notesList) {
        log("warn", scriptName, renderFunctionName, "Notes list element not found");
        return;
      }

      if (!notes || notes.length === 0) {
        notesList.innerHTML = '<div class="text-center py-3 text-muted">No notes found</div>';
        return;
      }

      let html = '';
      notes.forEach(note => {
        const date = new Date(note.created_at).toLocaleString();
        log("debug", scriptName, renderFunctionName, "Processing note", {
          noteId: note.id,
          user: note.user,
          user_id: note.user_id
        });

        let username = 'Unknown User';
        if (note.user_id && note.user_id.toString() === currentUserId) {
          username = currentUsername || 'You';
        } else if (note.user) {
          if (typeof note.user === 'object') {
            username = note.user.username || note.user.name || note.user.email || 'Unknown User';
          } else if (typeof note.user === 'string') {
            username = note.user;
          }
        } else if (note.username) {
          username = note.username;
        }

        html += `
          <div class="note-item mb-3 p-3 border rounded">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <strong>${username}</strong>
              <small class="text-muted">${date}</small>
            </div>
            <div class="note-content">
              ${note.processed_content || note.content}
            </div>
          </div>
        `;
      });

      notesList.innerHTML = html;
      log("info", scriptName, renderFunctionName, "Notes rendered successfully");
    }

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
     * Add a new note
     * @param {string} content - Note content
     * @returns {Promise} - Promise that resolves when the note is added
     */
    function addNote(content) {
      const addFunctionName = "addNote";

      if (!content || content.trim() === '') {
        log("warn", scriptName, addFunctionName, "Note content is empty. Aborting submission.");
        showStatus('Please enter a note.', 'danger');
        return Promise.reject(new Error('Note content is empty'));
      }

      log("info", scriptName, addFunctionName, "Adding new note");

      // Disable submit button during submission
      const submitBtn = newNoteForm?.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Submitting...';
      }

      // Prepare data
      const noteData = {
        content,
        notable_type: notableType,
        notable_id: notableId,
        user_id: currentUserId
      };

      const postEndpoint = "/api/notes/";
      log("debug", scriptName, addFunctionName, "Preparing POST request", {
        url: postEndpoint,
        method: "POST",
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
          }

          loadNotes(state.currentFilter);
          showStatus('Note added successfully!');

          log("info", scriptName, addFunctionName, "Note added successfully");

          // Publish note added event
          eventSystem.publish('notes.added', {
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
            submitBtn.innerHTML = '<i class="fas fa-plus me-1"></i> Add Note';
          }
        });
    }

    // Set up event listeners

    // Filter by days
    document.querySelectorAll('.note-filter').forEach(filter => {
      filter.addEventListener('click', function(e) {
        e.preventDefault();
        const days = this.dataset.days;
        log("info", scriptName, "filterClick", `Filter clicked for ${days} days`);
        loadNotes({ days: days });
      });
    });

    // Search form submission
    const searchForm = document.getElementById('notesSearchForm');
    if (searchForm) {
      searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const searchFunctionName = "notesSearchForm_submit";
        const searchTerm = document.getElementById('noteSearchInput').value.trim();
        log("info", scriptName, searchFunctionName, "Search submitted", { searchTerm });
        state.searchTerm = searchTerm;
        if (searchTerm) {
          loadNotes({ q: searchTerm });
        }
      });
    }

    // New note form submission
    if (newNoteForm) {
      newNoteForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const submitFunctionName = "newNoteForm_submit";

        // Get content
        const contentField = document.getElementById('content');
        if (!contentField || !contentField.value.trim()) {
          log("warn", scriptName, submitFunctionName, "Note content is empty. Aborting submission.");
          showStatus('Please enter a note.', 'danger');
          return;
        }

        addNote(contentField.value);
      });
    }

    // Initialize the notes section
    loadNotes();

    // Notes controller object
    const controller = {
      loadNotes,
      addNote,
      refresh: () => loadNotes(state.currentFilter),
      getState: () => ({ ...state }),
      search: (searchTerm) => {
        state.searchTerm = searchTerm;
        loadNotes({ q: searchTerm });
      },
      filter: (days) => {
        loadNotes({ days });
      },
      showStatus
    };

    // Store the controller
    this.instances.set(containerId, controller);

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