// Script to manage modal visibility
function openDeleteModal() {
  const modal = new bootstrap.Modal(document.getElementById('deleteConfirmationModal'));
  modal.show();
}

function closeDeleteModal() {
  const modal = bootstrap.Modal.getInstance(document.getElementById('deleteConfirmationModal'));
  if (modal) modal.hide();
}
