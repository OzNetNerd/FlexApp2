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

  // UI Elements
  const notesList = document.getElementById('notesList');
  const notesLoading = document.getElementById('notesLoading');
  const statusMessage = document.createElement('div');
  statusMessage.className = 'alert mt-3 d-none';

  // Add status message container after the form
  document.getElementById('newNoteForm').insertAdjacentElement('afterend', statusMessage);

  // Initial notes load
  loadNotes();

  // Load notes with optional filters
  function loadNotes(filters = {}) {
    notesLoading.style.display = 'block';

    // Build query string
    let queryParams = new URLSearchParams();
    queryParams.append('notable_type', notableType);
    queryParams.append('notable_id', notableId);

    // Add additional filters
    for (const [key, value] of Object.entries(filters)) {
      queryParams.append(key, value);
    }

    // Fetch notes
    fetch(`/api/notes/query?${queryParams.toString()}`)
      .then(response => {
        if (!response.ok) {
          return response.json().then(errorData => {
            throw new Error(`API responded with status: ${response.status}: ${JSON.stringify(errorData)}`);
          }).catch(e => {
            throw new Error(`API responded with status: ${response.status}`);
          });
        }
        return response.json();
      })
      .then(data => {
        notesLoading.style.display = 'none';
        renderNotes(data.data);
      })
      .catch(error => {
        notesLoading.style.display = 'none';
        notesList.innerHTML = `<div class="alert alert-danger">Error loading notes: ${error.message}</div>`;
        console.error('Notes loading error:', error);
      });
  }

  // Render notes
  function renderNotes(notes) {
    if (!notes || notes.length === 0) {
      notesList.innerHTML = '<div class="text-center py-3 text-muted">No notes found</div>';
      return;
    }

    let html = '';
    notes.forEach(note => {
      const date = new Date(note.created_at).toLocaleString();

      // Debug log to see what user data we're getting
      console.log('Note user data:', note.user, 'user_id:', note.user_id);

      // Use current username when displaying user's own notes
      let username = 'Unknown User';

      if (note.user_id && note.user_id.toString() === currentUserId) {
        username = currentUsername || 'You';
      }
      else if (note.user) {
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
  }

  // Filter by days
  document.querySelectorAll('.note-filter').forEach(filter => {
    filter.addEventListener('click', function(e) {
      e.preventDefault();
      const days = this.dataset.days;
      loadNotes({days: days});
    });
  });

  // Search form
  const searchForm = document.getElementById('notesSearchForm');
  if (searchForm) {
    searchForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const searchTerm = document.getElementById('noteSearchInput').value.trim();
      if (searchTerm) {
        loadNotes({q: searchTerm});
      }
    });
  }

  // Show status message
  function showStatus(message, type = 'success') {
    statusMessage.className = `alert alert-${type} mt-3`;
    statusMessage.textContent = message;
    statusMessage.classList.remove('d-none');

    // Auto-hide after 5 seconds
    setTimeout(() => {
      statusMessage.classList.add('d-none');
    }, 5000);
  }

  // Add new note with improved feedback
  const newNoteForm = document.getElementById('newNoteForm');
  if (newNoteForm) {
    newNoteForm.addEventListener('submit', function(e) {
      e.preventDefault();

      // Basic validation
      const contentField = document.getElementById('content');
      if (!contentField || !contentField.value.trim()) {
        showStatus('Please enter a note.', 'danger');
        return;
      }

      // Disable submit button during submission
      const submitBtn = newNoteForm.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Submitting...';

      const formData = new FormData(newNoteForm);
      const noteData = Object.fromEntries(formData.entries());

      // Only keep the expected fields to avoid 500 errors
      const cleanedData = {
        content: noteData.content,
        notable_type: noteData.notable_type,
        notable_id: noteData.notable_id,
        user_id: noteData.user_id
      };

      console.log('Submitting note with data:', cleanedData);

      fetch('/api/notes/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cleanedData)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`API responded with status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (data.error) {
          throw new Error(data.error.message);
        }
        newNoteForm.reset();
        loadNotes();
        showStatus('Note added successfully!');
      })
      .catch(error => {
        showStatus(`Error adding note: ${error.message}`, 'danger');
        console.error('Error adding note:', error);
      })
      .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-plus me-1"></i> Add Note';
      });
    });
  }
});