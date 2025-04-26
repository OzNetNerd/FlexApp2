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
    this.initialized = false;
    log('info', this.scriptName, 'constructor', '🔄 Tabs component created');
  }

  /**
   * Normalize tab name for case-insensitive comparison
   * @param {string} name - Tab name to normalize
   * @returns {string} - Normalized tab name
   */
  normalizeTabName(name) {
    return (name || '').toLowerCase().trim();
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

    // Global initialization guard
    if (!this.initialized) {
      this.initialized = true;
      log('info', this.scriptName, 'globalInit', '🔄 First tabs initialization');
    }

    // Check if already initialized
    if (this.instances.has(tabsContainerId)) {
      log('warn', this.scriptName, functionName, `⚠️ Tabs already initialized for container: ${tabsContainerId}`);
      return this.instances.get(tabsContainerId);
    }

    // Get the tabs container
    const tabsContainer = document.getElementById(tabsContainerId);
    if (!tabsContainer) {
      log('error', this.scriptName, functionName, `❌ Tabs container not found: ${tabsContainerId}`);
      return null;
    }

    // Get configuration from data attributes
    const config = {
      tabNames: JSON.parse(tabsContainer.dataset.tabNames || '[]'),
      activeTab: tabsContainer.dataset.activeTab || null,
      readOnly: false,
      ...options
    };

    log('info', this.scriptName, functionName, `🔄 Initializing tabs: ${tabsContainerId}`, config);

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
      })),
      tabsConfig: config
    };

    // Log the initial active tab
    log('info', this.scriptName, functionName, `📌 Initial active tab: ${state.activeTab}`);

    /**
     * Switch to a specific tab
     * @param {string} tabName - Tab name to switch to
     * @returns {boolean} - Whether the tab was switched successfully
     */
    function switchTab(tabName) {
      const switchFunctionName = 'switchTab';

      // Find the tab
      const normalizedTabName = self.normalizeTabName(tabName);
      const tab = state.tabs.find(t => self.normalizeTabName(t.name) === normalizedTabName);

      if (!tab) {
        log('warn', self.scriptName, switchFunctionName, `⚠️ Tab not found: ${tabName}`);
        return false;
      }

      // Check if the tab is enabled
      if (!tab.enabled || !tab.visible) {
        log('warn', self.scriptName, switchFunctionName, `⚠️ Tab is disabled or hidden: ${tabName}`);
        return false;
      }

      log('info', self.scriptName, switchFunctionName, `🔄 Switching to tab: ${tabName} (from ${state.activeTab})`);

      // Update active tab - use the original case from the tab object
      state.activeTab = tab.name;

      // Update UI
      updateTabUI();

      log('info', self.scriptName, switchFunctionName, `✅ Switched to tab: ${tabName}`);

      // Publish tab change event
      eventSystem.publish('tabs.change', {
        containerId: tabsContainerId,
        activeTab: tab.name
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

      // Log tab details for debugging
      log("debug", self.scriptName, updateFunctionName, `📌 Updating UI with active tab: ${state.activeTab}`);
      log("debug", self.scriptName, updateFunctionName, `📌 Found ${navLinks.length} nav links and ${tabPanes.length} tab panes`);

      // Update nav links
      navLinks.forEach(link => {
        const tabName = link.dataset.tabName || link.textContent.trim();
        const normalizedTabName = self.normalizeTabName(tabName);
        const tab = state.tabs.find(t => self.normalizeTabName(t.name) === normalizedTabName);

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

        // Update active state - Compare normalized names
        if (self.normalizeTabName(tabName) === self.normalizeTabName(state.activeTab)) {
          link.classList.add('active');
          link.setAttribute('aria-selected', 'true');
          log("debug", self.scriptName, updateFunctionName, `📌 Set nav link active: ${tabName}`);
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

        // Log current pane state before changes
        const wasActive = pane.classList.contains('active') && pane.classList.contains('show');

        // Update visibility - Compare normalized names
        if (self.normalizeTabName(tabName) === self.normalizeTabName(state.activeTab)) {
          pane.classList.add('active', 'show');
          log("debug", self.scriptName, updateFunctionName, `📌 Set tab pane active: ${tabName} (was ${wasActive ? 'already active' : 'inactive'})`);
        } else {
          pane.classList.remove('active', 'show');
          if (wasActive) {
            log("debug", self.scriptName, updateFunctionName, `📌 Set tab pane inactive: ${tabName}`);
          }
        }
      });

      log('debug', self.scriptName, updateFunctionName, `✅ Updated tab UI for ${tabsContainerId}, active tab: ${state.activeTab}`);
    };

    // Set up event listeners
    const navLinks = tabsContainer.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      // Check if we've already attached a listener to avoid duplicates
      if (link._tabsComponentListenerAttached) {
        log("warn", self.scriptName, "eventSetup", `⚠️ Tab link already has a listener: ${link.dataset.tabName || link.textContent.trim()}`);
        return;
      }

      const tabClickListener = (e) => {
        e.preventDefault();

        // Skip if the tab is disabled
        if (link.classList.contains('disabled')) {
          return;
        }

        // Get the tab name
        const tabName = link.dataset.tabName || link.textContent.trim();
        log("info", self.scriptName, "tabClick", `🖱️ Tab link clicked: ${tabName}`);

        // Switch to the tab
        switchTab(tabName);
      };

      link.addEventListener('click', tabClickListener);

      // Mark as having a listener attached
      link._tabsComponentListenerAttached = true;

      // Store the listener function for potential cleanup
      link._tabsComponentListener = tabClickListener;

      log("debug", self.scriptName, "eventSetup", `✅ Attached click listener to tab: ${link.dataset.tabName || link.textContent.trim()}`);
    });

    // Initial UI update - force after a short delay to ensure DOM is ready
    setTimeout(() => {
      log("info", self.scriptName, "initialUpdate", `🔄 Performing initial UI update for tabs`);
      updateTabUI();
    }, 50);

    // Log tab information
    log("debug", self.scriptName, "config", "📌 Tab names:", config.tabNames);

    /**
     * Set tab enabled state
     * @param {string} tabName - Tab name
     * @param {boolean} enabled - Enabled state
     * @returns {boolean} - Success
     */
    function setTabEnabled(tabName, enabled = true) {
      const normalizedTabName = self.normalizeTabName(tabName);
      const tab = state.tabs.find(t => self.normalizeTabName(t.name) === normalizedTabName);

      if (!tab) {
        log('warn', self.scriptName, 'setTabEnabled', `⚠️ Tab not found: ${tabName}`);
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
      const normalizedTabName = self.normalizeTabName(tabName);
      const tab = state.tabs.find(t => self.normalizeTabName(t.name) === normalizedTabName);

      if (!tab) {
        log('warn', self.scriptName, 'setTabVisible', `⚠️ Tab not found: ${tabName}`);
        return false;
      }

      tab.visible = visible;
      updateTabUI();
      return true;
    }

    /**
     * Force restore active tab - useful in case of conflicts
     */
    function forceRestoreActiveTab() {
      log("warn", self.scriptName, "forceRestoreActiveTab", `🔧 Forcing active tab restoration: ${state.activeTab}`);
      updateTabUI();
    }

    // Tabs controller object
    const controller = {
      switchTab,
      getActiveTab: () => state.activeTab,
      getTabs: () => [...state.tabs],
      setTabEnabled,
      setTabVisible,
      refresh: () => updateTabUI(),
      forceRestoreActiveTab,
      getState: () => ({ ...state })
    };

    // Store the controller
    this.instances.set(tabsContainerId, controller);

    // Listen for potential conflicts with other tab managers
    eventSystem.subscribe('tabs.conflict', (data) => {
      if (data.containerId === tabsContainerId) {
        log("warn", self.scriptName, "conflict", `⚠️ Tab conflict detected, enforcing state`);
        forceRestoreActiveTab();
      }
    });

    // Monitor document for external tab changes
    const observer = new MutationObserver((mutations) => {
      // Check if our active tab has been deactivated by something else
      mutations.forEach(mutation => {
        if (mutation.type === 'attributes' &&
            mutation.attributeName === 'class' &&
            mutation.target.classList &&
            mutation.target.id &&
            mutation.target.id.startsWith('tab-')) {

          // Get the tab name
          const tabName = mutation.target.id.replace('tab-', '');
          const isActive = mutation.target.classList.contains('active');

          // If this is our active tab and it's been deactivated, restore it
          if (self.normalizeTabName(tabName) === self.normalizeTabName(state.activeTab) && !isActive) {
            log("warn", self.scriptName, "mutationObserver", `⚠️ Tab '${tabName}' was deactivated externally, restoring`);
            // Small delay to let other scripts finish
            setTimeout(() => {
              updateTabUI();
            }, 10);
          }
        }
      });
    });

    // Start observing tab panes for class changes
    document.querySelectorAll('.tab-pane').forEach(pane => {
      observer.observe(pane, { attributes: true });
    });

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
      log('warn', this.scriptName, functionName, '⚠️ Template data element not found');
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
    log("info", this.scriptName, functionName, `📌 Received variables: ${received.join(', ') || 'None'}`);

    if (missing.length > 0) {
      log("warn", this.scriptName, functionName, `❌ Missing variables: ${missing.join(', ')}`);
    } else {
      log("info", this.scriptName, functionName, `✅ All expected variables present`);
    }

    // Log tab render info if tabs exist
    const formTabs = document.getElementById('formTabs');
    if (formTabs) {
      const tabRenderFuncName = 'template_render';
      const tabNames = JSON.parse(formTabs.dataset.tabNames || '[]');
      log("info", this.scriptName, tabRenderFuncName, "🧩 Tabs rendered:", tabNames);

      // Log sections for each tab
      document.querySelectorAll('.tab-pane').forEach((tabPane, index) => {
        const sectionNames = JSON.parse(tabPane.dataset.sectionNames || '[]');
        log("debug", this.scriptName, tabRenderFuncName, `📁 Sections in tab '${tabNames[index] || index}':`, sectionNames);
      });
    }
  }
}

// Create singleton instance
const tabsComponent = new TabsComponent();
export default tabsComponent;