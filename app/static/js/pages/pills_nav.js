// static/js/pills_nav.js

document.addEventListener('DOMContentLoaded', () => {
  // Log events through debug panel if available
  if (window.debugLogger && window.debugLogger.pills) {
    if (document.querySelector('#tab-pills')) {
      window.debugLogger.pills.info('Tab navigation initialized');

      document.querySelectorAll('#tab-pills .nav-link').forEach(pill => {
        pill.addEventListener('click', () => {
          window.debugLogger.pills.info(`Tab switched to: ${pill.textContent.trim()}`);
        });
      });
    } else {
      window.debugLogger.pills.error('UI configuration missing');

      const url = new URL(window.location.href);
      const pathParts = url.pathname.split('/').filter(part => part.length > 0);

      window.debugLogger.pills.debug('URL analysis', {
        url: url.toString(),
        pathParts: pathParts,
        potentialItemType: pathParts.length > 0 ? pathParts[0] : null
      });
    }
  }
});
