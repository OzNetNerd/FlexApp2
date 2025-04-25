import log from '/static/js/core/logger.js';

/**
 * Notes Section JavaScript - Fixed Version
 * Handles loading, displaying, filtering, adding notes, and initial load.
 */
document.addEventListener('DOMContentLoaded', function() {
  // --- Configuration and Element Selection ---

  const notesData = document.getElementById('notesData');
  if (!notesData) {
    console.error('Critical Error: Notes data configuration element (#notesData) not found.');
    return; // Stop execution if config is missing
  }

  // Extract configuration from data attributes
  const notableType = notesData.dataset.notableType;
  const notableId = notesData.dataset.notableId;
  const currentUserId = notesData.dataset.userId;
  const currentUsername = notesData.dataset.username;
  // Use provided scriptName or default for logging context
  const scriptName = notesData.dataset.scriptName || 'notes_section';

  log("info", scriptName, "init", "Initializing Notes Section module", { notableType, notableId });

  // Get references to essential UI elements
  const notesTabPane = document.getElementById('tab-notes');
  const notesTabButton = document.getElementById('tab-notes-tab');
  const notesList = document.getElementById('notesList');
  const notesLoading = document.getElementById('notesLoading');
  const newNoteForm = document.getElementById('newNoteForm');
  const notesFilterLinks = document.querySelectorAll('.note-filter');
  const notesSearchForm = document.getElementById('notesSearchForm');
  const noteContentField = document.getElementById('content'); // Specific field for validation/reset

  // Check if essential elements exist
  if (!notesTabPane || !notesList || !notesLoading || !newNoteForm || !noteContentField) {
      log("error", scriptName, "init", "One or more essential UI elements are missing. Functionality may be impaired.", {
          notesTabPaneExists: !!notesTabPane,
          notesListExists: !!notesList,
          notesLoadingExists: !!notesLoading,
          newNoteFormExists: !!newNoteForm,
          noteContentFieldExists: !!noteContentField
      });
      // Depending on severity, you might want to return here or display a user message.
  }


  // Create and insert status message area dynamically
  const statusMessage = document.createElement('div');
  statusMessage.className = 'alert mt-3 d-none'; // Start hidden
  statusMessage.setAttribute('role', 'alert');
  if (newNoteForm) {
    // Insert right after the form for context
    newNoteForm.insertAdjacentElement('afterend', statusMessage);
  } else {
      // Fallback: append to the notes tab pane if form is missing
      notesTabPane?.appendChild(statusMessage);
  }

  // State variable to track if notes have been loaded successfully
  let notesLoaded = false;
  // Store current filters to potentially avoid reload if filters haven't changed (optional optimization)
  let currentFilters = {};

  // --- Core Functions ---

  /**
   * Fetches notes from the API based on current entity and filters.
   * @param {object} filters - Key-value pairs for filtering (e.g., { days: 7, q: 'search' }).
   * @param {boolean} forceReload - If true, bypass the notesLoaded check.
   */
  function loadNotes(filters = {}, forceReload = false) {
    const functionName = "loadNotes";

    // Prevent reload if notes are already loaded and filters haven't changed, unless forced
    if (notesLoaded && !forceReload && JSON.stringify(filters) === JSON.stringify(currentFilters)) {
        log("debug", scriptName, functionName, "Skipping load: Notes already loaded and filters unchanged.");
        return;
    }

    log("info", scriptName, functionName, "Attempting to load notes", { filters, forceReload });
    currentFilters = filters; // Update current filters

    if (notesLoading) {
      notesLoading.style.display = 'block'; // Show loading spinner
    }
    if (notesList) {
       // Optionally clear previous notes or show loading text
       notesList.innerHTML = '';
    }

    // Build query parameters
    const queryParams = new URLSearchParams({
        notable_type: notableType,
        notable_id: notableId,
        ...filters // Spread filter object into params
    });

    const endpoint = `/api/notes/query?${queryParams.toString()}`;
    log("debug", scriptName, functionName, "Fetching notes from endpoint", { url: endpoint });

    fetch(endpoint)
      .then(response => {
        log("debug", scriptName, functionName, "Received fetch response", { status: response.status, ok: response.ok, url: endpoint });
        if (!response.ok) {
          // Attempt to get more detailed error from response body
          return response.text().then(text => {
            let errorMsg = `API error: Status ${response.status}`;
            try {
              const errorData = JSON.parse(text);
              // Use a more specific error message if available (adjust key based on your API)
              errorMsg += `: ${errorData.message || errorData.detail || text}`;
            } catch (e) {
              errorMsg += `: ${text}`; // Fallback to raw text if JSON parsing fails
            }
            log("error", scriptName, functionName, "API response not OK", { status: response.status, responseBody: text, url: endpoint });
            throw new Error(errorMsg); // Throw an error to be caught below
          });
        }
        return response.json(); // Parse JSON if response is OK
      })
      .then(data => {
        log("debug", scriptName, functionName, "Successfully parsed API response", { data });
        if (notesLoading) {
          notesLoading.style.display = 'none'; // Hide loading spinner
        }
        // Assuming API returns data in a 'data' property, adjust if needed
        renderNotes(data.data || []);
        notesLoaded = true; // Mark notes as successfully loaded
      })
      .catch(error => {
        log("error", scriptName, functionName, "Error during note loading or processing", { error: error.message, url: endpoint });
        if (notesLoading) {
          notesLoading.style.display = 'none';
        }
        if (notesList) {
          // Display error message in the notes list area
          notesList.innerHTML = `<div class="alert alert-danger" role="alert">Error loading notes: ${error.message}. Please try again later.</div>`;
        }
        notesLoaded = false; // Mark as not loaded due to error
        console.error('Notes loading error:', error);
      });
  }

  /**
   * Renders the notes array into the notesList element.
   * @param {Array} notes - Array of note objects from the API.
   */
  function renderNotes(notes) {
    const functionName = "renderNotes";
    if (!notesList) {
        log("error", scriptName, functionName, "notesList element not found, cannot render.");
        return;
    }

    log("debug", scriptName, functionName, `Rendering ${notes ? notes.length : 0} notes.`);

    if (!notes || notes.length === 0) {
      notesList.innerHTML = '<div class="text-center py-3 text-muted">No notes found matching the criteria.</div>';
      return;
    }

    // Build HTML string for notes
    const notesHtml = notes.map(note => {
      const noteDate = new Date(note.created_at || Date.now()); // Fallback if created_at is missing
      const formattedDate = noteDate.toLocaleString(undefined, { // Use locale default formatting
          dateStyle: 'medium',
          timeStyle: 'short'
      });

      // Determine display username with fallbacks
      let displayUsername = 'Unknown User';
       if (note.user_id && currentUserId && note.user_id.toString() === currentUserId.toString()) {
          displayUsername = currentUsername || 'You'; // Use configured username or 'You'
      } else if (note.user && typeof note.user === 'object') {
          // Check common properties for username
          displayUsername = note.user.username || note.user.name || note.user.email || displayUsername;
      } else if (note.user && typeof note.user === 'string') {
          displayUsername = note.user; // If user is just a string ID/name
      } else if (note.username) {
          displayUsername = note.username; // Fallback to a direct username property
      }

      // Use processed_content if available (e.g., Markdown rendered to HTML), else raw content
      const noteBody = note.processed_content || note.content || '(No content)';

      // Return HTML structure for a single note item
      return `
        <div class="note-item mb-3 p-3 border rounded shadow-sm">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <strong class="text-primary">${displayUsername}</strong>
            <small class="text-muted">${formattedDate}</small>
          </div>
          <div class="note-content">
            ${noteBody}
          </div>
        </div>
      `;
    }).join(''); // Join all note HTML strings

    notesList.innerHTML = notesHtml;
    log("info", scriptName, functionName, `Successfully rendered ${notes.length} notes.`);
  }

  /**
   * Displays a status message to the user (e.g., success or error).
   * @param {string} message - The text message to display.
   * @param {string} type - The alert type ('success', 'danger', 'warning', 'info'). Defaults to 'success'.
   */
  function showStatus(message, type = 'success') {
    const functionName = "showStatus";
    log("debug", scriptName, functionName, `Displaying status: "${message}"`, { type });

    if (!statusMessage) {
        log("error", scriptName, functionName, "statusMessage element not found, cannot show status.");
        return;
    }

    statusMessage.className = `alert alert-${type} mt-3`; // Set alert type class
    statusMessage.textContent = message;
    statusMessage.classList.remove('d-none'); // Make it visible

    // Optional: Auto-hide the message after a delay
    setTimeout(() => {
      statusMessage.classList.add('d-none');
      log("debug", scriptName, functionName, "Status message hidden automatically.");
    }, 5000); // Hide after 5 seconds
  }


  // --- Event Listeners ---

  // Handle clicking filter links (e.g., Last 7 days)
  notesFilterLinks.forEach(filter => {
    filter.addEventListener('click', function(e) {
      e.preventDefault(); // Prevent default link behavior
      const days = this.dataset.days;
      log("info", scriptName, "filterClick", `Filter applied: ${days} days`);
      notesLoaded = false; // Force reload when filter changes
      loadNotes({ days: days }, true); // Pass filter and force reload
    });
  });

  // Handle search form submission
  if (notesSearchForm) {
    notesSearchForm.addEventListener('submit', function(e) {
      e.preventDefault(); // Prevent form submission
      const functionName = "notesSearchForm_submit";
      const searchInput = document.getElementById('noteSearchInput');
      const searchTerm = searchInput ? searchInput.value.trim() : '';

      log("info", scriptName, functionName, "Search submitted", { searchTerm });
      notesLoaded = false; // Force reload on search
      // Load notes with the search query 'q', pass empty filter if term is empty to show all
      loadNotes(searchTerm ? { q: searchTerm } : {}, true);
    });
  } else {
       log("warn", scriptName, "init", "Notes search form not found.");
  }

  // Handle adding a new note
  if (newNoteForm) {
    newNoteForm.addEventListener('submit', function(e) {
      e.preventDefault(); // Prevent standard form submission
      const functionName = "newNoteForm_submit";

      const content = noteContentField.value.trim();
      if (!content) {
        log("warn", scriptName, functionName, "Note content is empty. Aborting submission.");
        showStatus('Please enter text for the note.', 'warning');
        noteContentField.focus(); // Focus the content field
        return;
      }

      // Disable submit button and show loading state
      const submitBtn = newNoteForm.querySelector('button[type="submit"]');
      const originalButtonHtml = submitBtn.innerHTML; // Store original button content
      if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Adding...';
      }

      // Data payload for the API
      const noteData = {
        content: content,
        notable_type: notableType,
        notable_id: notableId,
        // Send user_id if available, API should handle associating the note
        user_id: currentUserId || null
      };

      const postEndpoint = "/api/notes/"; // API endpoint for creating notes
      log("debug", scriptName, functionName, "Submitting new note", { url: postEndpoint, data: noteData });

      fetch(postEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Include CSRF token header if needed by your backend framework
          // 'X-CSRFToken': getCookie('csrftoken') // Example for Django
        },
        body: JSON.stringify(noteData)
      })
      .then(response => {
         log("debug", scriptName, functionName, "Received POST response", { status: response.status, ok: response.ok, url: postEndpoint });
         if (!response.ok) {
             // Handle API errors similarly to the GET request
             return response.text().then(text => {
                let errorMsg = `API error: Status ${response.status}`;
                 try {
                     const errorData = JSON.parse(text);
                     errorMsg += `: ${errorData.message || errorData.detail || text}`;
                 } catch (e) {
                     errorMsg += `: ${text}`;
                 }
                log("error", scriptName, functionName, "API response not OK for POST", { status: response.status, responseBody: text, url: postEndpoint });
                throw new Error(errorMsg);
            });
         }
         return response.json(); // Assuming API returns the created note or success status
      })
      .then(data => {
        log("info", scriptName, functionName, "Note added successfully via API", { responseData: data });
        newNoteForm.reset(); // Clear the form fields
        showStatus('Note added successfully!', 'success');
        notesLoaded = false; // Mark notes as needing refresh
        loadNotes(currentFilters, true); // Reload notes to show the new one, maintaining current filters
      })
      .catch(error => {
        log("error", scriptName, functionName, "Error adding note", { error: error.message, url: postEndpoint });
        showStatus(`Error adding note: ${error.message}`, 'danger');
        console.error('Error adding note:', error);
      })
      .finally(() => {
        // Always re-enable the submit button and restore its content
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalButtonHtml;
        }
      });
    });
   } else {
        log("warn", scriptName, "init", "New note form not found.");
   }

  // --- Initial Load Logic ---

  /**
   * Checks if the notes tab is currently active/visible and loads notes if needed.
   * This specifically handles the initial page load scenario.
   */
  function performInitialLoadCheck() {
    const functionName = "performInitialLoadCheck";
    // Check using classList.contains('active') on the tab pane - more direct for Bootstrap
    if (notesTabPane && notesTabPane.classList.contains('active')) {
      log("info", scriptName, functionName, "Notes tab is active on initial page load. Triggering load.");
      loadNotes({}, true); // Load notes with empty filters, force load
    } else {
      log("debug", scriptName, functionName, "Notes tab is not active on initial load. Notes will load on tab activation.");
       if (notesLoading) {
            notesLoading.style.display = 'none'; // Ensure loading indicator is hidden if tab isn't active
       }
    }
  }

  // Execute the initial check after setting everything up
  performInitialLoadCheck();

  // Listener for Bootstrap tab change events to load notes when the tab becomes visible
   if (notesTabButton) {
       notesTabButton.addEventListener('shown.bs.tab', function(event) {
           // event.target is the tab button that was clicked (notesTabButton)
           // event.relatedTarget is the previous active tab button
           log("info", scriptName, "tabShown", "Notes tab 'shown.bs.tab' event triggered.");
           // Load notes only if they haven't been loaded yet or if filters changed (handled in loadNotes)
           // The forceReload = false here prevents unnecessary reloads if already loaded and filters are same.
           loadNotes(currentFilters, false);
       });
   } else {
       log("warn", scriptName, "init", "Notes tab button (#tab-notes-tab) not found. Tab switching might not load notes.");
   }

}); // End DOMContentLoaded