// Updated sidebar.js with localStorage for state persistence
document.addEventListener('DOMContentLoaded', function() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  const collapseBtn = document.getElementById('sidebarCollapseBtn');
  const toggleBtn = document.getElementById('sidebarToggleBtn');
  const body = document.body;
  const submenuToggles = document.querySelectorAll('.submenu-toggle');

  // Restore sidebar collapsed state
  if (localStorage.getItem('sidebarCollapsed') === 'true') {
    body.classList.add('sidebar-collapsed');
  }

  // Toggle mobile sidebar
  toggleBtn?.addEventListener('click', function() {
    sidebar.classList.toggle('show');
    overlay.classList.toggle('show');
  });

  // Collapse sidebar (desktop) and save state
  collapseBtn?.addEventListener('click', function() {
    body.classList.toggle('sidebar-collapsed');
    // Save sidebar collapsed state
    localStorage.setItem('sidebarCollapsed', body.classList.contains('sidebar-collapsed'));
  });

  // Close sidebar when clicking overlay
  overlay?.addEventListener('click', function() {
    sidebar.classList.remove('show');
    overlay.classList.remove('show');
  });

  // Assign unique identifiers to submenus for tracking
  document.querySelectorAll('.has-submenu').forEach((submenu, index) => {
    // Try to get text from first link or use index as fallback
    const linkText = submenu.querySelector('.sidebar-link')?.textContent.trim() || `submenu-${index}`;
    submenu.dataset.submenuId = linkText.replace(/\s+/g, '-').toLowerCase();
  });

  // Restore open submenus
  document.querySelectorAll('.has-submenu').forEach(submenu => {
    const submenuId = submenu.dataset.submenuId;
    if (localStorage.getItem('submenu_' + submenuId) === 'open') {
      submenu.classList.add('open');
    }
  });

  // Toggle submenus and save state
  submenuToggles.forEach(toggle => {
    toggle.addEventListener('click', function(e) {
      e.stopPropagation(); // Prevent event bubbling

      // Skip toggle behavior when sidebar is collapsed on desktop
      if (body.classList.contains('sidebar-collapsed') && window.innerWidth >= 992) {
        return;
      }

      const parent = this.closest('.has-submenu');
      const submenuId = parent.dataset.submenuId;

      // Close other open submenus on mobile
      if (window.innerWidth < 992) {
        submenuToggles.forEach(otherToggle => {
          const otherParent = otherToggle.closest('.has-submenu');
          if (otherParent !== parent && otherParent.classList.contains('open')) {
            otherParent.classList.remove('open');

            // Save closed state for other submenu
            const otherId = otherParent.dataset.submenuId;
            localStorage.removeItem('submenu_' + otherId);
          }
        });
      }

      // Toggle current submenu
      parent.classList.toggle('open');

      // Save submenu state
      if (parent.classList.contains('open')) {
        localStorage.setItem('submenu_' + submenuId, 'open');
      } else {
        localStorage.removeItem('submenu_' + submenuId);
      }
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

  // Auto-open submenu if a child is active (and save that state)
  document.querySelectorAll('.submenu-item.active').forEach(item => {
    const parentSubmenu = item.closest('.has-submenu');
    if (parentSubmenu) {
      parentSubmenu.classList.add('open');

      // Save this submenu as open
      const submenuId = parentSubmenu.dataset.submenuId;
      localStorage.setItem('submenu_' + submenuId, 'open');
    }
  });
});