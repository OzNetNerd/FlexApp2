import log from '/static/js/core/logger.js';
import moduleSystem from '/static/js/core/module.js';
import eventSystem from '/static/js/core/events.js';
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
    // Modified: Removed explicit initialization of notesComponent here
    // The notesSection.js script should handle its own initialization based on DOM and tab visibility.
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
   * This method now only checks for the notes section element.
   * The actual initialization and tab handling for notes should be done by notesSection.js.
   */
  initNotes() {
    const functionName = 'initNotes';

    // Check if the notes section exists
    const notesData = document.getElementById('notesData');
    if (!notesData) {
      log('debug', 'entityView.js', functionName, 'Notes section not found');
      return;
    }

    log('debug', 'entityView.js', functionName, 'Notes section element found. Assuming notesSection.js will handle initialization.');

    // Removed: notesComponent.initNotes('notesData');
    // Removed: Event listeners that were likely intended for notesComponent

    // Listen for notes added event (assuming eventSystem is used by notesSection.js or related)
    eventSystem.subscribe('notes.added', (data) => {
      log('info', 'entityView.js', 'notesAdded', 'Note added successfully (event received)');
    });

    // Listen for notes error event (assuming eventSystem is used by notesSection.js or related)
    eventSystem.subscribe('notes.error', (data) => {
      log('error', 'entityView.js', 'notesError', 'Error with notes (event received):', data.error);
    });
  }
}

// Create instance and register with the module system
// The module system should ensure entityView.js is initialized once.
const entityViewPage = new EntityViewPage();
moduleSystem.register('entityView', () => entityViewPage.init(), ['common'], true);

export default entityViewPage;