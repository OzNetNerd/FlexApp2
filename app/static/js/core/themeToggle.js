document.addEventListener('DOMContentLoaded', () => {
  // Check for theme preference in localStorage
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    document.body.setAttribute('data-theme', savedTheme);
    console.debug(`Applied saved theme: ${savedTheme}`);
  }

  // Theme toggle handler for both navbar and sidebar
  window.toggleTheme = function() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    console.info(`Theme switched to: ${newTheme}`);
  }

  // Add event listener to theme toggle button
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', window.toggleTheme);
    console.debug("Theme toggle button initialized");
  }
});