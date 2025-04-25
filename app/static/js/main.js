import log from '/static/js/core/logger.js';
import moduleSystem from '/static/js/core/module.js';

/**
 * Main application entry point
 */
(function() {
  // Application namespace
  window.App = window.App || {};
  
  // Import core modules
  import('/static/js/core/config.js');
  import('/static/js/core/events.js');
  
  // Import services
  import('/static/js/services/apiService.js');
  import('/static/js/services/uiService.js');
  import('/static/js/services/notificationService.js');
  
  // Import page modules
  import('/static/js/pages/common.js');
  
  // Set up logging
  const initLogger = () => {
    log('info', 'main.js', 'init', '🚀 Application initializing');
    
    // Determine environment based on URL or other factors
    const isDevelopment = window.location.hostname === 'localhost' || 
      window.location.hostname === '127.0.0.1' ||
      window.location.hostname.includes('dev.');
    
    // Enable nested logging in development
    if (isDevelopment && typeof setNestedLogging === 'function') {
      setNestedLogging(true);
      log('info', 'main.js', 'logger', 'Nested logging enabled for development');
    }
    
    // Log browser and platform info
    log('info', 'main.js', 'environment', `Browser: ${navigator.userAgent}`);
    log('debug', 'main.js', 'environment', `Viewport: ${window.innerWidth}x${window.innerHeight}`);
  };
  
  // Detect page type and load appropriate modules
  const initPageModules = () => {
    // Get the current path
    const path = window.location.pathname;
    
    // Determine page type based on URL pattern
    let pageType = null;
    
    if (path.endsWith('/create') || path.includes('/edit/')) {
      pageType = 'edit';
      log('info', 'main.js', 'pageDetection', `Detected edit page: ${path}`);
      
      // Load edit page module
      import('/static/js/pages/entityEdit.js').catch(error => {
        log('error', 'main.js', 'moduleLoad', `Failed to load entity edit module: ${error.message}`);
      });
    } else if (path.endsWith('/') || path.includes('/index')) {
      pageType = 'list';
      log('info', 'main.js', 'pageDetection', `Detected list page: ${path}`);
      
      // Load list page module
      import('/static/js/pages/entityList.js').catch(error => {
        log('error', 'main.js', 'moduleLoad', `Failed to load entity list module: ${error.message}`);
      });
    } else if (path.includes('/view/')) {
      pageType = 'view';
      log('info', 'main.js', 'pageDetection', `Detected view page: ${path}`);
      
      // Load view page module
      import('/static/js/pages/entityView.js').catch(error => {
        log('error', 'main.js', 'moduleLoad', `Failed to load entity view module: ${error.message}`);
      });
    } else {
      log('info', 'main.js', 'pageDetection', `Unknown page type: ${path}`);
    }
    
    // Store page type in the App namespace
    window.App.pageType = pageType;
  };
  
  // Initialize application
  const initApp = () => {
    log('info', 'main.js', 'init', '✅ Application initialized');
    
    // Tell the module system to initialize any modules that are ready
    moduleSystem.initReadyModules();
  };
  
  // Set up hooks for module loading
  document.addEventListener('DOMContentLoaded', () => {
    log('info', 'main.js', 'DOMContentLoaded', 'DOM content loaded');
  });
  
  // Initialize application
  initLogger();
  initPageModules();
  initApp();
})();