// Track form changes
let formChanged = false;

document.addEventListener('DOMContentLoaded', function() {
  const formElements = document.querySelectorAll('#edit-form input, #edit-form select, #edit-form textarea');

  formElements.forEach(element => {
    element.addEventListener('change', () => {
      formChanged = true;

      // Use debug logger if available
      if (window.debugLogger && window.debugLogger.edit) {
        window.debugLogger.edit.info("Form state changed - unsaved changes detected", {
          element: element.name || element.id,
          type: element.type,
          value: element.value
        });
      }
    });
  });

  // Unsaved changes modal handling
  // Find the cancel button
  const cancelButton = document.querySelector('.d-flex.justify-content-end.mt-4 a.btn-secondary');

  if (cancelButton) {
    cancelButton.addEventListener('click', function(event) {
      if (formChanged) {
        event.preventDefault();
        const modal = new bootstrap.Modal(document.getElementById('unsavedChangesModal'));
        modal.show();
      }
    });
  }

  const confirmLeaveBtn = document.getElementById('confirmLeaveBtn');
  if (confirmLeaveBtn) {
    confirmLeaveBtn.addEventListener('click', function() {
      // Get the current URL and build the appropriate return URL
      const currentPath = window.location.pathname;
      const isEdit = currentPath.includes('/edit/');
      const hasId = /\/\d+\//.test(currentPath);

      let redirectUrl;
      if (hasId) {
        // If editing an existing item, go to view page
        redirectUrl = currentPath.replace('/edit/', '/view/');
      } else {
        // If creating a new item, go to index page
        redirectUrl = currentPath.split('/create')[0];
      }

      window.location.href = redirectUrl;
    });
  }

  // Add form submit handler
  const form = document.getElementById('edit-form');
  if (form) {
    form.addEventListener('submit', function() {
      formChanged = false; // Reset after submission
    });
  }
});

// Add window unload handler for unsaved changes
window.addEventListener('beforeunload', function(e) {
  if (formChanged) {
    e.preventDefault();
    e.returnValue = '';
    return '';
  }
});
