// static/js/pages/notesSection.js
import log from '/static/js/core/logger.js';
import eventSystem from '/static/js/core/events.js';
import apiService from '/static/js/services/apiService.js';

class NotesComponent {
  constructor() {
    this.instances = new Map();
    this.initialized = false;
    log('info', 'notesSection.js', 'constructor', '🔄 Unified Notes component created');
    document.addEventListener('DOMContentLoaded', () => this._onDOMContentLoaded());
  }

  _onDOMContentLoaded() {
    if (this.initialized) return;
    this.initialized = true;
    window.notesScriptLoaded = true;
    log('info', 'notesSection.js', 'DOMContentLoaded', '✅ Initializing Notes Components.');

    document.querySelectorAll('[id^="notesData"]').forEach(container => {
      const ctrl = this.initNotes(container.id);
      window.notesController = ctrl;
    });

    eventSystem.subscribe('tabs.change', ({containerId, activeTab}) => {
      if (containerId === 'formTabs' && activeTab.toLowerCase() === 'notes') {
        window.notesController?.showTab();
        window.notesController?.loadNotes(window.notesController.getState().currentFilters, true);
      }
    });
  }

  initNotes(containerId = 'notesData') {
    const fn = 'initNotes';
    const notesData = document.getElementById(containerId);
    if (!notesData) {
      log('error', 'notesSection.js', fn, `❌ Notes data container not found: ${containerId}`);
      return null;
    }
    if (this.instances.has(containerId)) return this.instances.get(containerId);

    const notableType = notesData.dataset.notableType;
    const notableId = notesData.dataset.notableId;
    const currentUserId = notesData.dataset.userId;
    const currentUsername = notesData.dataset.username;
    const scriptName = 'notesSection';

    log('info', scriptName, fn, '🔄 Initializing Notes Section', {notableType, notableId, currentUserId});

    // UI elements
    const notesTabPane      = document.getElementById('tab-notes');
    const notesTabButton    = document.getElementById('tab-notes-tab');
    const notesList         = document.getElementById('notesList');
    const notesLoading      = document.getElementById('notesLoading');
    const noteContentField  = document.getElementById('content');
    const noteFilterSelect  = document.getElementById('noteFilterSelect');
    const dateRangeSelectors= document.getElementById('dateRangeSelectors');
    const dateFrom          = document.getElementById('dateFrom');
    const dateTo            = document.getElementById('dateTo');
    const applyDateRange    = document.getElementById('applyDateRange');
    const noteSearchInput   = document.getElementById('noteSearchInput');
    const submitBtn         = document.getElementById('newNoteSubmit');

    // Insert status message
    const statusMessage = document.createElement('div');
    statusMessage.className = 'alert mt-3 d-none';
    statusMessage.setAttribute('role', 'alert');
    if (noteContentField) noteContentField.insertAdjacentElement('afterend', statusMessage);

    // State
    const state = {
      notes: [],
      isLoading: false,
      currentFilters: { days: '0' },
      searchTerm: '',
      notesLoadedForCurrentView: false
    };

    // Date setup
    const setDefaultDates = () => {
      if (!dateFrom || !dateTo) return;
      const today = new Date();
      const weekAgo = new Date();
      weekAgo.setDate(today.getDate() - 7);
      dateFrom.value = weekAgo.toISOString().split('T')[0];
      dateTo.value   = today.toISOString().split('T')[0];
    };
    setDefaultDates();

    // Helpers: showStatus, loadNotes, renderNotes, addNote, debounce
    const showStatus = (msg, type='success') => {
      statusMessage.className = `alert alert-${type} mt-3`;
      statusMessage.textContent = msg;
      statusMessage.classList.remove('d-none');
      setTimeout(() => statusMessage.classList.add('d-none'), 5000);
    };

    const loadNotes = (filters={}, force=false) => {
      if (state.notesLoadedForCurrentView && !force) return;
      state.currentFilters = filters;
      state.isLoading = true;
      notesLoading && (notesLoading.style.display = 'block');
      notesList && (notesList.innerHTML = '<div class="text-center py-3"><div class="spinner-border spinner-border-sm me-2" role="status"></div>Connecting to notes service...</div>');

      let qs = new URLSearchParams({ notable_type: notableType, notable_id: notableId });
      Object.entries(filters).forEach(([k,v]) => v!='' && qs.append(k, v));
      state.searchTerm && qs.append('q', state.searchTerm);
      const url = `/api/notes/query?${qs}`;
      apiService.get(url)
        .then(data => {
          state.isLoading = false;
          notesLoading && (notesLoading.style.display = 'none');
          state.notes = data.data || [];
          renderNotes(state.notes);
          state.notesLoadedForCurrentView = true;
        })
        .catch(err => {
          state.isLoading = false;
          state.notesLoadedForCurrentView = false;
          notesLoading && (notesLoading.style.display = 'none');
          notesList && (notesList.innerHTML = `<div class="alert alert-danger">Error loading notes: ${err.message}</div>`);
          showStatus(`Failed to load notes: ${err.message}`, 'danger');
        });
    };

    const renderNotes = (notes) => {
      if (!notesList) return;
      if (!notes.length) {
        notesList.innerHTML = '<div class="text-center py-3 text-muted">No notes found.</div>';
        return;
      }
      notesList.innerHTML = notes.map(n => {
        const date = new Date(n.created_at || Date.now()).toLocaleString();
        const user = (n.user?.username || n.username || 'Unknown');
        return `
          <div class="note-item mb-3 p-3 border rounded shadow-sm">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <strong class="text-primary">${user}</strong>
              <small class="text-muted">${date}</small>
            </div>
            <div class="note-content">${n.processed_content||n.content||'(No content)'}</div>
          </div>`;
      }).join('');
    };

    const addNote = (content) => {
      if (!content.trim()) {
        showStatus('Please enter a note.', 'warning');
        return Promise.reject(new Error('Empty'));
      }
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Adding…';
      return apiService.post('/api/notes/', {
        content: content.trim(),
        notable_type: notableType,
        notable_id: notableId,
        user_id: currentUserId
      })
      .then(res => {
        noteContentField.value = '';
        state.notesLoadedForCurrentView = false;
        loadNotes(state.currentFilters, true);
        showStatus('Note added successfully!');
      })
      .catch(err => {
        showStatus(`Error adding note: ${err.message}`, 'danger');
        throw err;
      })
      .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-plus me-1"></i> Add Note';
      });
    };

    // Attach click handler instead of form submit
    if (submitBtn) {
      submitBtn.addEventListener('click', e => {
        e.preventDefault();
        addNote(noteContentField.value).catch(() => {/* already handled */});
      });
    }

    // Immediately load if pane active (or no tabs)
    const isActive = notesTabPane?.classList.contains('active') || !notesTabPane;
    if (isActive) loadNotes();
    else notesList && (notesList.innerHTML = '<div class="text-center py-3 text-muted">Select the "Notes" tab to load notes.</div>');

    const controller = { loadNotes, addNote, showTab: ()=>{notesTabPane?.classList.add('active','show');}, getState:()=>({...state}) };
    this.instances.set(containerId, controller);
    return controller;
  }
}

const notesComponent = new NotesComponent();
export default notesComponent;
