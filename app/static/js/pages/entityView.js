import log from '/static/js/core/logger.js';
import moduleSystem from '/static/js/core/module.js';
import eventSystem from '/static/js/core/events.js';
import notesComponent from '/static/js/components/notes.js';
import buttonsComponent from '/static/js/components/buttons.js';

/**
 * Entity view page functionality
 */
class EntityViewPage {
  constructor() {
    log('info', 'entityView.js', 'constructor', 'Entity view page module created');
  }

  /**
   * Initialize view page functionality
   */
  init() {
    const functionName = 'init';
    log('info', 'entityView.js', functionName, 'Initializing entity view page');

    // Initialize header buttons
    this.initButtons();

    // Initialize notes section if it exists
    this.initNotes();

    log('info', 'entityView.js', functionName, 'Entity view page initialization complete');
  }

  /**
   * Initialize header buttons
   */
  initButtons() {
    const functionName = 'initButtons';
    log('debug', 'entityView.js', functionName, 'Initializing header buttons');

    // Init header buttons
    buttonsComponent.initHeaderButtons();

    // Find edit button and track clicks
    const editButton = document.querySelector('a[href$="/edit"]');
    if (editButton) {
      editButton.addEventListener('click', () => {
        log('info', 'entityView.js', 'editClick', 'Edit button clicked');
      });
    }
  }

  /**
   * Initialize notes section if it exists
   */
  initNotes() {
    const functionName = 'initNotes';

    // Check if the notes section exists
    const notesData = document.getElementById('notesData');
    if (!notesData) {
      log('debug', 'entityView.js', functionName, 'Notes section not found');
      return;
    }

    log('debug', 'entityView.js', functionName, 'Initializing notes section');

    // Initialize notes with the notes component
    const notesController = notesComponent.initNotes('notesData');

    // Listen for notes added event
    eventSystem.subscribe('notes.added', (data) => {
      log('info', 'entityView.js', 'notesAdded', 'Note added successfully');
    });

    // Listen for notes error event
    eventSystem.subscribe('notes.error', (data) => {
      log('error', 'entityView.js', 'notesError', 'Error with notes:', data.error);
    });
  }
}

// Create instance and register with the module system
const entityViewPage = new EntityViewPage();
moduleSystem.register('entityView', () => entityViewPage.init(), ['common'], true);

export default entityViewPage;