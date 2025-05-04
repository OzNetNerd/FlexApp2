// Update to sidebar.js
document.addEventListener('DOMContentLoaded', function() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  const collapseBtn = document.getElementById('sidebarCollapseBtn');
  const toggleBtn = document.getElementById('sidebarToggleBtn');
  const body = document.body;
  const submenuToggles = document.querySelectorAll('.submenu-toggle');

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

  // Toggle submenus
  submenuToggles.forEach(toggle => {
    toggle.addEventListener('click', function(e) {
      e.preventDefault();

      // Skip toggle behavior when sidebar is collapsed on desktop
      if (body.classList.contains('sidebar-collapsed') && window.innerWidth >= 992) {
        return;
      }

      const parent = this.parentElement;

      // Close other open submenus on mobile
      if (window.innerWidth < 992) {
        submenuToggles.forEach(otherToggle => {
          const otherParent = otherToggle.parentElement;
          if (otherParent !== parent && otherParent.classList.contains('open')) {
            otherParent.classList.remove('open');
          }
        });
      }

      // Toggle current submenu
      parent.classList.toggle('open');
    });
  });

  // Close sidebar when clicking links on mobile
  const sidebarLinks = document.querySelectorAll('.sidebar-link:not(.submenu-toggle), .submenu-link');
  if (window.innerWidth < 992) {
    sidebarLinks.forEach(link => {
      link.addEventListener('click', function() {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
      });
    });
  }

  // Auto-open submenu if a child is active
  document.querySelectorAll('.submenu-item.active').forEach(item => {
    const parentSubmenu = item.closest('.has-submenu');
    if (parentSubmenu) {
      parentSubmenu.classList.add('open');
    }
  });
});