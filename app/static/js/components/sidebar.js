// Update to sidebar.js
document.addEventListener('DOMContentLoaded', function() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  const collapseBtn = document.getElementById('sidebarCollapseBtn');
  const toggleBtn = document.getElementById('sidebarToggleBtn');
  const body = document.body;

  // Toggle mobile sidebar
  toggleBtn?.addEventListener('click', function() {
    sidebar.classList.toggle('show');
    overlay.classList.toggle('show');
  });

  // Collapse sidebar (desktop)
  collapseBtn?.addEventListener('click', function() {
    body.classList.toggle('sidebar-collapsed');
  });

  // Close sidebar when clicking overlay
  overlay?.addEventListener('click', function() {
    sidebar.classList.remove('show');
    overlay.classList.remove('show');
  });

  // Close sidebar when clicking links on mobile
  const sidebarLinks = document.querySelectorAll('.sidebar-link');
  if (window.innerWidth < 992) {
    sidebarLinks.forEach(link => {
      link.addEventListener('click', function() {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
      });
    });
  }
});