import log from '/static/js/core/logger.js';
import moduleSystem from '/static/js/core/module.js';
import eventSystem from '/static/js/core/events.js';
import formManager from '/static/js/components/form.js';
import tabsComponent from '/static/js/components/tabs.js';
import notificationService from '/static/js/services/notificationService.js';

/**
 * Common page functionality shared across different page types
 */
class CommonPageModule {
  constructor() {
    log('info', 'common.js', 'constructor', 'Common page module created');
  }

  /**
   * Initialize common page functionality
   */
  init() {
    const functionName = 'init';
    log('info', 'common.js', functionName, 'Initializing common page functionality');

    // Set up global event listeners
    this.setupGlobalEventListeners();

    // Set up tooltips and popovers if Bootstrap is available
    this.setupBootstrapComponents();

    // Validate tabs template if it exists
    if (document.getElementById('template-data')) {
      tabsComponent.validateTabsTemplate();
    }

    // Initialize tabs if they exist
    const formTabs = document.getElementById('formTabs');
    if (formTabs) {
      tabsComponent.initTabs('formTabs');
    }

    // Set up debug logging in UI if in development
    this.setupDebugLogging();

    log('info', 'common.js', functionName, 'Common page initialization complete');
  }

  /**
   * Set up global event listeners
   */
  setupGlobalEventListeners() {
    const functionName = 'setupGlobalEventListeners';
    log('debug', 'common.js', functionName, 'Setting up global event listeners');

    // Track page load time
    const pageLoadStart = window.performance?.timing?.navigationStart || Date.now();

    // Page fully loaded
    window.addEventListener('load', () => {
      const loadTime = Date.now() - pageLoadStart;
      log('info', 'common.js', 'pageLoad', `Page fully loaded in ${loadTime}ms`);

      // Publish page loaded event
      eventSystem.publish('page.loaded', {
        url: window.location.href,
        loadTime: loadTime
      });

      // Automatically hide any page loading indicators
      const loadingIndicators = document.querySelectorAll('.page-loading');
      loadingIndicators.forEach(indicator => {
        indicator.style.display = 'none';
      });
    });

    // Page visibility change
    document.addEventListener('visibilitychange', () => {
      const isVisible = document.visibilityState === 'visible';
      log('debug', 'common.js', 'visibilityChange', `Page visibility changed: ${isVisible ? 'visible' : 'hidden'}`);

      // Publish visibility event
      eventSystem.publish('page.visibility', {
        isVisible: isVisible
      });
    });

    // Before page unload
    window.addEventListener('beforeunload', (event) => {
      log('debug', 'common.js', 'beforeUnload', 'Page about to unload');

      // Publish before unload event
      eventSystem.publish('page.beforeUnload', {});
    });
  }

  /**
   * Set up Bootstrap components if available
   */
  setupBootstrapComponents() {
    const functionName = 'setupBootstrapComponents';

    if (typeof bootstrap === 'undefined') {
      log('warn', 'common.js', functionName, 'Bootstrap is not available');
      return;
    }

    // Enable tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
      const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => {
        return new bootstrap.Tooltip(tooltipTriggerEl);
      });

      log('debug', 'common.js', functionName, `Initialized ${tooltipList.length} tooltips`);
    }

    // Enable popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length > 0) {
      const popoverList = [...popoverTriggerList].map(popoverTriggerEl => {
        return new bootstrap.Popover(popoverTriggerEl);
      });

      log('debug', 'common.js', functionName, `Initialized ${popoverList.length} popovers`);
    }
  }

  /**
   * Set up debug logging in UI if in development
   */
  setupDebugLogging() {
    const functionName = 'setupDebugLogging';

    // Check if the debug panel element exists
    const debugPanel = document.getElementById('debug-panel');
    if (!debugPanel) {
      return;
    }

    log('debug', 'common.js', functionName, 'Setting up debug logging panel');

    // Create debug logger if not already exists
    if (!window.debugLogger) {
      window.debugLogger = {};
    }

    // Add debug log methods for various modules
    const modules = ['edit', 'view', 'pills', 'table', 'form', 'api'];

    modules.forEach(module => {
      if (!window.debugLogger[module]) {
        window.debugLogger[module] = {
          info: (message, data) => {
            log('info', `${module}.js`, 'debug', message, data);
            this.appendToDebugPanel(`[INFO] [${module}] ${message}`, data);
          },
          warn: (message, data) => {
            log('warn', `${module}.js`, 'debug', message, data);
            this.appendToDebugPanel(`[WARN] [${module}] ${message}`, data, 'warning');
          },
          error: (message, data) => {
            log('error', `${module}.js`, 'debug', message, data);
            this.appendToDebugPanel(`[ERROR] [${module}] ${message}`, data, 'danger');
          },
          debug: (message, data) => {
            log('debug', `${module}.js`, 'debug', message, data);
            this.appendToDebugPanel(`[DEBUG] [${module}] ${message}`, data, 'secondary');
          }
        };
      }
    });
  }

  /**
   * Append a message to the debug panel
   * @param {string} message - Debug message
   * @param {any} data - Optional data object
   * @param {string} type - Message type (primary, secondary, success, danger, warning, info)
   */
  appendToDebugPanel(message, data, type = 'primary') {
    const debugPanel = document.getElementById('debug-panel');
    if (!debugPanel) {
      return;
    }

    const debugLog = debugPanel.querySelector('.debug-log');
    if (!debugLog) {
      return;
    }

    // Create log entry
    const entry = document.createElement('div');
    entry.className = `debug-entry text-${type} mb-1`;

    // Add timestamp
    const timestamp = new Date().toISOString().split('T')[1].split('.')[0];

    // Format message
    entry.innerHTML = `<span class="debug-time">${timestamp}</span> ${message}`;

    // Add data if provided
    if (data !== undefined) {
      const dataStr = JSON.stringify(data, null, 2);

      if (dataStr !== '{}' && dataStr !== '[]') {
        const dataElement = document.createElement('pre');
        dataElement.className = 'debug-data mt-1 p-1 border';
        dataElement.textContent = dataStr;
        entry.appendChild(dataElement);
      }
    }

    // Add to log, at the top
    debugLog.insertBefore(entry, debugLog.firstChild);

    // Trim log if too many entries
    const maxEntries = 50;
    const entries = debugLog.querySelectorAll('.debug-entry');
    if (entries.length > maxEntries) {
      for (let i = maxEntries; i < entries.length; i++) {
        debugLog.removeChild(entries[i]);
      }
    }
  }
}

// Create instance and register with the module system
const commonPageModule = new CommonPageModule();
moduleSystem.register('common', () => commonPageModule.init(), [], true);

export default commonPageModule;