// Improved sidebar.js with flicker prevention

document.addEventListener('DOMContentLoaded', function() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  const collapseBtn = document.getElementById('sidebarCollapseBtn');
  const toggleBtn = document.getElementById('sidebarToggleBtn');
  const body = document.body;
  const submenuToggles = document.querySelectorAll('.submenu-toggle');

  // We no longer need to set the initial state here as it's now handled
  // by the inline script in the head of base.html

  // Assign unique identifiers to submenus for tracking
  document.querySelectorAll('.has-submenu').forEach((submenu, index) => {
    const linkText = submenu.querySelector('.sidebar-link')?.textContent.trim() || `submenu-${index}`;
    submenu.dataset.submenuId = linkText.replace(/\s+/g, '-').toLowerCase();
  });

  // Auto-open submenu if a child is active
  document.querySelectorAll('.submenu-item.active').forEach(item => {
    const parentSubmenu = item.closest('.has-submenu');
    if (parentSubmenu) {
      parentSubmenu.classList.add('open');
      const submenuId = parentSubmenu.dataset.submenuId;
      localStorage.setItem('submenu_' + submenuId, 'open');
    }
  });

  // Restore open submenus from localStorage
  document.querySelectorAll('.has-submenu').forEach(submenu => {
    const submenuId = submenu.dataset.submenuId;
    if (localStorage.getItem('submenu_' + submenuId) === 'open') {
      submenu.classList.add('open');
    }
  });

  // Toggle mobile sidebar
  toggleBtn?.addEventListener('click', function() {
    sidebar.classList.toggle('show');
    overlay.classList.toggle('show');
  });

  // Collapse sidebar (desktop) and save state
  collapseBtn?.addEventListener('click', function() {
    document.documentElement.classList.toggle('sidebar-collapsed');
    body.classList.toggle('sidebar-collapsed');

    // Save sidebar collapsed state
    const isCollapsed = document.documentElement.classList.contains('sidebar-collapsed');
    localStorage.setItem('sidebarCollapsed', isCollapsed);

    // Set cookie for server-side rendering
    document.cookie = `sidebarCollapsed=${isCollapsed}; path=/; max-age=31536000; SameSite=Lax`;
  });

  // Close sidebar when clicking overlay
  overlay?.addEventListener('click', function() {
    sidebar.classList.remove('show');
    overlay.classList.remove('show');
  });

  // Toggle submenus and save state
  submenuToggles.forEach(toggle => {
    toggle.addEventListener('click', function(e) {
      e.stopPropagation(); // Prevent event bubbling

      // Skip toggle behavior when sidebar is collapsed on desktop
      if (document.documentElement.classList.contains('sidebar-collapsed') && window.innerWidth >= 992) {
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

  // Handle link clicks - preserve state during navigation
  const sidebarLinks = document.querySelectorAll('.sidebar-link:not(.submenu-toggle), .submenu-link');
  sidebarLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      // Close sidebar on mobile
      if (window.innerWidth < 992) {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
      }

      // Store current sidebar state for the next page
      const currentState = {
        collapsed: document.documentElement.classList.contains('sidebar-collapsed'),
        openSubmenus: Array.from(document.querySelectorAll('.has-submenu.open'))
          .map(el => el.dataset.submenuId)
      };

      // Store path-specific state in cookie for server-side access
      const pathStateStr = JSON.stringify({
        path: link.getAttribute('href'),
        state: currentState
      });

      document.cookie = `sidebarPathState=${encodeURIComponent(pathStateStr)}; path=/; max-age=31536000; SameSite=Lax`;
      sessionStorage.setItem('sidebarPathState', pathStateStr);
    });
  });
});