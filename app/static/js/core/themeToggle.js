// Export the initialization function
export function initThemeToggle() {
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

  // Function to set theme
  const setTheme = (theme) => {
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);

    // Update toggle button icon
    if (themeToggleBtn) {
      const icon = themeToggleBtn.querySelector('i');
      if (icon) {
        if (theme === 'dark') {
          icon.className = 'fas fa-sun';
        } else {
          icon.className = 'fas fa-moon';
        }
      }
    }

    console.info(`Theme set to: ${theme}`);
  };

  // Check for theme preference
  const savedTheme = localStorage.getItem('theme');
  let currentTheme;

  if (savedTheme) {
    currentTheme = savedTheme;
  } else if (prefersDarkScheme.matches) {
    currentTheme = 'dark';
  } else {
    currentTheme = 'light';
  }
  
  // Set the initial theme
  setTheme(currentTheme);

  // Theme toggle handler
  window.toggleTheme = function() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
  };

  // Add event listener to theme toggle button
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', window.toggleTheme);
  }

  // Listen for system preference changes
  prefersDarkScheme.addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      setTheme(e.matches ? 'dark' : 'light');
    }
  });
}