import log from '/static/js/core/logger.js';
import eventSystem from '/static/js/core/events.js';
import configManager from '/static/js/core/config.js';

/**
 * Tab navigation component
 */
class TabsComponent {
  constructor() {
    this.instances = new Map();
    this.scriptName = 'tabs.js'; // Default value for scriptName
    log('info', this.scriptName, 'constructor', 'Tabs component created');
  }

  /**
   * Initialize tabs
   * @param {string} tabsContainerId - Tabs container ID
   * @param {Object} options - Tab options
   * @returns {Object} - Tabs controller
   */
  initTabs(tabsContainerId = 'formTabs', options = {}) {
    const functionName = 'initTabs';
    const self = this; // Store reference to 'this'

    // Check if already initialized
    if (this.instances.has(tabsContainerId)) {
      log('warn', this.scriptName, functionName, `Tabs already initialized for container: ${tabsContainerId}`);
      return this.instances.get(tabsContainerId);
    }

    // Get the tabs container
    const tabsContainer = document.getElementById(tabsContainerId);
    if (!tabsContainer) {
      log('error', this.scriptName, functionName, `Tabs container not found: ${tabsContainerId}`);
      return null;
    }

    // Get configuration from data attributes
    const config = {
      tabNames: JSON.parse(tabsContainer.dataset.tabNames || '[]'),
      activeTab: tabsContainer.dataset.activeTab || null,
      readOnly: false,
      ...options
    };

    log('info', this.scriptName, functionName, `Initializing tabs: ${tabsContainerId}`, config);

    // Get template data if available
    const templateData = document.getElementById('template-data');
    if (templateData) {
      this.scriptName = templateData.dataset.scriptName || this.scriptName; // Ensure scriptName is properly set
      if (templateData.dataset.readOnlyDefined) {
        config.readOnly = JSON.parse(templateData.dataset.readOnlyDefined);
      }
    }

    // State
    const state = {
      activeTab: config.activeTab || (config.tabNames.length > 0 ? config.tabNames[0] : null),
      tabs: config.tabNames.map(name => ({
        name,
        enabled: true,
        visible: true
      }))
    };

    /**
     * Switch to a specific tab
     * @param {string} tabName - Tab name to switch to
     * @returns {boolean} - Whether the tab was switched successfully
     */
    function switchTab(tabName) {
      const switchFunctionName = 'switchTab';

      // Find the tab
      const tab = state.tabs.find(t => t.name === tabName);
      if (!tab) {
        log('warn', self.scriptName, switchFunctionName, `Tab not found: ${tabName}`);
        return false;
      }

      // Check if the tab is enabled
      if (!tab.enabled || !tab.visible) {
        log('warn', self.scriptName, switchFunctionName, `Tab is disabled or hidden: ${tabName}`);
        return false;
      }

      // Update active tab
      state.activeTab = tabName;

      // Update UI
      updateTabUI();

      log('info', self.scriptName, switchFunctionName, `Switched to tab: ${tabName}`);

      // Publish tab change event
      eventSystem.publish('tabs.change', {
        containerId: tabsContainerId,
        activeTab: tabName
      });

      return true;
    }

    /**
     * Update the tab UI
     */
    const updateTabUI = () => {
      const updateFunctionName = 'updateTabUI';

      // Get all nav links
      const navLinks = tabsContainer.querySelectorAll('.nav-link');

      // Get all tab panes
      const tabPanes = document.querySelectorAll('.tab-pane');

      // Update nav links
      navLinks.forEach(link => {
        const tabName = link.dataset.tabName || link.textContent.trim();
        const tab = state.tabs.find(t => t.name === tabName);

        // Skip if the tab is not found
        if (!tab) return;

        // Update visibility
        if (!tab.visible) {
          link.parentElement.style.display = 'none';
        } else {
          link.parentElement.style.display = '';
        }

        // Update enabled state
        if (!tab.enabled) {
          link.classList.add('disabled');
          link.setAttribute('aria-disabled', 'true');
          link.setAttribute('tabindex', '-1');
        } else {
          link.classList.remove('disabled');
          link.removeAttribute('aria-disabled');
          link.removeAttribute('tabindex');
        }

        // Update active state
        if (tabName === state.activeTab) {
          link.classList.add('active');
          link.setAttribute('aria-selected', 'true');
        } else {
          link.classList.remove('active');
          link.setAttribute('aria-selected', 'false');
        }
      });

      // Update tab panes
      tabPanes.forEach(pane => {
        // Extract tab name from pane ID or data attribute
        let tabName = pane.dataset.tabName;
        if (!tabName && pane.id.startsWith('tab-')) {
          tabName = pane.id.replace('tab-', '');
        }

        // Skip if the tab name is not found
        if (!tabName) return;

        // Update visibility
        if (tabName === state.activeTab) {
          pane.classList.add('active', 'show');
        } else {
          pane.classList.remove('active', 'show');
        }
      });

      log('debug', self.scriptName, updateFunctionName, `Updated tab UI for ${tabsContainerId}, active tab: ${state.activeTab}`);
    };

    // Set up event listeners
    const navLinks = tabsContainer.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();

        // Skip if the tab is disabled
        if (link.classList.contains('disabled')) {
          return;
        }

        // Get the tab name
        const tabName = link.dataset.tabName || link.textContent.trim();

        // Switch to the tab
        switchTab(tabName);

        log('debug', self.scriptName, 'navLinkClick', `Tab link clicked: ${tabName}`);
      });
    });

    // Initial UI update
    updateTabUI();

    // Log tab information
    log("debug", self.scriptName, "config", "Tab names:", config.tabNames);

    /**
     * Set tab enabled state
     * @param {string} tabName - Tab name
     * @param {boolean} enabled - Enabled state
     * @returns {boolean} - Success
     */
    function setTabEnabled(tabName, enabled = true) {
      const tab = state.tabs.find(t => t.name === tabName);
      if (!tab) {
        log('warn', self.scriptName, 'setTabEnabled', `Tab not found: ${tabName}`);
        return false;
      }

      tab.enabled = enabled;
      updateTabUI();
      return true;
    }

    /**
     * Set tab visibility
     * @param {string} tabName - Tab name
     * @param {boolean} visible - Visibility state
     * @returns {boolean} - Success
     */
    function setTabVisible(tabName, visible = true) {
      const tab = state.tabs.find(t => t.name === tabName);
      if (!tab) {
        log('warn', self.scriptName, 'setTabVisible', `Tab not found: ${tabName}`);
        return false;
      }

      tab.visible = visible;
      updateTabUI();
      return true;
    }

    // Tabs controller object
    const controller = {
      switchTab,
      getActiveTab: () => state.activeTab,
      getTabs: () => [...state.tabs],
      setTabEnabled, // Added setTabEnabled method
      setTabVisible,
      refresh: () => updateTabUI()
    };

    // Store the controller
    this.instances.set(tabsContainerId, controller);

    return controller;
  }

  /**
   * Get a tabs controller by container ID
   * @param {string} containerId - Container ID
   * @returns {Object|null} - Tabs controller or null if not found
   */
  getTabs(containerId = 'formTabs') {
    return this.instances.get(containerId) || null;
  }

  /**
   * Validate tabs template
   */
  validateTabsTemplate() {
    const functionName = 'validateTabsTemplate';
    const self = this; // Store reference to 'this'

    const templateData = document.getElementById('template-data');
    if (!templateData) {
      log('warn', this.scriptName, functionName, 'Template data element not found');
      return;
    }

    const scriptName = templateData.dataset.scriptName;

    // Log initialization info
    const expected = ['tabs', 'read_only'];
    const received = [];
    const missing = [];

    if (JSON.parse(templateData.dataset.tabsDefined)) received.push('tabs'); else missing.push('tabs');
    if (JSON.parse(templateData.dataset.readOnlyDefined)) received.push('readOnly'); else missing.push('readOnly');

    log("info", this.scriptName, functionName, `🔍 Expecting variables: ${expected.join(', ')}`);
    log("info", this.scriptName, functionName, `Received variables: ${received.join(', ') || 'None'}`);

    if (missing.length > 0) {
      log("warn", this.scriptName, functionName, `❌ Missing variables: ${missing.join(', ')}`);
    } else {
      log("info", this.scriptName, functionName, `✅ All expected variables present`);
    }

    // Log tab render info if tabs exist
    const formTabs = document.getElementById('formTabs');
    if (formTabs) {
      const tabRenderFuncName = 'template_render';
      const tabNames = JSON.parse(formTabs.dataset.tabNames);
      log("info", this.scriptName, tabRenderFuncName, "🧩 Tabs rendered:", tabNames);

      // Log sections for each tab
      document.querySelectorAll('.tab-pane').forEach((tabPane, index) => {
        const sectionNames = JSON.parse(tabPane.dataset.sectionNames || '[]');
        log("debug", this.scriptName, tabRenderFuncName, `📁 Sections in tab '${tabNames[index]}':`, sectionNames);
      });
    }
  }
}

// Create singleton instance
const tabsComponent = new TabsComponent();
export default tabsComponent;