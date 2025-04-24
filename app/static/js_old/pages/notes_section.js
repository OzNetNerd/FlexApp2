import log from '/static/js/logger.js';

/**
 * Notes Section JavaScript
 * Handles loading, displaying, filtering, and adding notes
 */
document.addEventListener('DOMContentLoaded', function() {
  // Get data attributes from the notesData div
  const notesData = document.getElementById('notesData');
  const notableType = notesData.dataset.notableType;
  const notableId = notesData.dataset.notableId;
  const currentUserId = notesData.dataset.userId;
  const currentUsername = notesData.dataset.username;
  const scriptName = notesData.dataset.scriptName || 'notes_module';

  // Log module initialization
  log("info", scriptName, "init", "Initializing Notes Section module");

  // UI Elements
  const notesList = document.getElementById('notesList');
  const notesLoading = document.getElementById('notesLoading');
  const statusMessage = document.createElement('div');
  statusMessage.className = 'alert mt-3 d-none';

  // Add status message container after the form
  document.getElementById('newNoteForm').insertAdjacentElement('afterend', statusMessage);

  // Initial notes load
  loadNotes();

  /**
   * Load notes with optional filters.
   */
  function loadNotes(filters = {}) {
    const functionName = "loadNotes";
    log("info", scriptName, functionName, "Loading notes with filters", filters);
    notesLoading.style.display = 'block';

    // Build query string
    let queryParams = new URLSearchParams();
    queryParams.append('notable_type', notableType);
    queryParams.append('notable_id', notableId);

    // Add additional filters if provided
    for (const [key, value] of Object.entries(filters)) {
      queryParams.append(key, value);
    }

    const endpoint = `/api/notes/query?${queryParams.toString()}`;
    log("debug", scriptName, functionName, "Built query URL", endpoint);

    fetch(endpoint)
      .then(response => {
        log("debug", scriptName, functionName, "Received response", {
          status: response.status,
          statusText: response.statusText,
          url: endpoint
        });
        if (!response.ok) {
          return response.text().then(text => {
            log("error", scriptName, functionName, "Error response text", {
              url: endpoint,
              text: text
            });
            try {
              const errorData = JSON.parse(text);
              throw new Error(`API responded with status: ${response.status}: ${JSON.stringify(errorData)}`);
            } catch (parseError) {
              throw new Error(`API responded with status: ${response.status}: ${text}`);
            }
          });
        }
        return response.json();
      })
      .then(data => {
        notesLoading.style.display = 'none';
        log("debug", scriptName, functionName, "Response payload received", {
          url: endpoint,
          payload: data
        });
        renderNotes(data.data);
      })
      .catch(error => {
        notesLoading.style.display = 'none';
        notesList.innerHTML = `<div class="alert alert-danger">Error loading notes: ${error.message}</div>`;
        log("error", scriptName, functionName, "Error loading notes", {
          url: endpoint,
          error: error
        });
        console.error('Notes loading error:', error);
      });
  }

  /**
   * Render notes in the UI.
   */
  function renderNotes(notes) {
    const functionName = "renderNotes";
    log("debug", scriptName, functionName, `Rendering ${notes ? notes.length : 0} notes`);
    if (!notes || notes.length === 0) {
      notesList.innerHTML = '<div class="text-center py-3 text-muted">No notes found</div>';
      return;
    }

    let html = '';
    notes.forEach(note => {
      const date = new Date(note.created_at).toLocaleString();
      log("debug", scriptName, functionName, "Processing note", {
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
    log("info", scriptName, "renderNotes", "Notes rendered successfully");
  }

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
      const functionName = "notesSearchForm_submit";
      const searchTerm = document.getElementById('noteSearchInput').value.trim();
      log("info", scriptName, functionName, "Search submitted", { searchTerm });
      if (searchTerm) {
        loadNotes({ q: searchTerm });
      }
    });
  }

  /**
   * Show status message.
   */
  function showStatus(message, type = 'success') {
    const functionName = "showStatus";
    log("debug", scriptName, functionName, `Showing status message: ${message}`, { type });
    statusMessage.className = `alert alert-${type} mt-3`;
    statusMessage.textContent = message;
    statusMessage.classList.remove('d-none');

    // Auto-hide after 5 seconds
    setTimeout(() => {
      statusMessage.classList.add('d-none');
      log("debug", scriptName, functionName, "Status message hidden");
    }, 5000);
  }

  /**
   * Add new note.
   */
  const newNoteForm = document.getElementById('newNoteForm');
  if (newNoteForm) {
    newNoteForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const functionName = "newNoteForm_submit";

      // Basic validation
      const contentField = document.getElementById('content');
      if (!contentField || !contentField.value.trim()) {
        log("warn", scriptName, functionName, "Note content is empty. Aborting submission.");
        showStatus('Please enter a note.', 'danger');
        return;
      }

      // Disable submit button during submission
      const submitBtn = newNoteForm.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Submitting...';

      // Use dataset values instead of relying on form inputs for these fields
      const cleanedData = {
        content: contentField.value,
        notable_type: notableType,
        notable_id: notableId,
        user_id: currentUserId
      };

      const postEndpoint = "/api/notes/";
      log("debug", scriptName, functionName, "Preparing POST request", {
        url: postEndpoint,
        method: "POST",
        payload: cleanedData
      });

      fetch(postEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cleanedData)
      })
      .then(response => {
        log("debug", scriptName, functionName, "Received response for POST", {
          status: response.status,
          statusText: response.statusText,
          url: postEndpoint
        });
        if (!response.ok) {
          return response.text().then(text => {
            log("error", scriptName, functionName, "Error response text for POST", {
              url: postEndpoint,
              text: text
            });
            try {
              const errorData = JSON.parse(text);
              throw new Error(`API responded with status: ${response.status}: ${JSON.stringify(errorData)}`);
            } catch (parseError) {
              throw new Error(`API responded with status: ${response.status}: ${text}`);
            }
          });
        }
        return response.json();
      })
      .then(data => {
        log("debug", scriptName, functionName, "Response payload received for POST", {
          url: postEndpoint,
          payload: data
        });
        if (data.error) {
          throw new Error(data.error.message);
        }
        newNoteForm.reset();
        loadNotes();
        showStatus('Note added successfully!');
        log("info", scriptName, functionName, "Note added successfully");
      })
      .catch(error => {
        showStatus(`Error adding note: ${error.message}`, 'danger');
        log("error", scriptName, functionName, "Error adding note", {
          url: postEndpoint,
          error: error
        });
        console.error('Error adding note:', error);
      })
      .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-plus me-1"></i> Add Note';
      });
    });
  }
});
