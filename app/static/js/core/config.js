import log from '/static/js/core/logger.js';

/**
 * Configuration management system for retrieving values from data attributes
 */
class ConfigManager {
  constructor() {
    this.cache = new Map();
    log('info', 'config.js', 'constructor', 'Configuration manager created');
  }

  /**
   * Get configuration from data attributes on an element
   * @param {string} elementId - Element ID to look for
   * @param {Object} defaults - Default values
   * @param {boolean} useCache - Whether to use cached values
   * @returns {Object} - Configuration object
   */
  fromElement(elementId, defaults = {}, useCache = true) {
    const functionName = 'fromElement';

    // Check cache first
    if (useCache && this.cache.has(elementId)) {
      log('debug', 'config.js', functionName, `Using cached config for ${elementId}`);
      return this.cache.get(elementId);
    }

    const element = document.getElementById(elementId);
    if (!element) {
      log('warn', 'config.js', functionName, `Element not found: ${elementId}`, defaults);
      return defaults;
    }

    log('debug', 'config.js', functionName, `Reading config from element: ${elementId}`);

    const config = { ...defaults };

    // Process all data attributes
    for (const [key, value] of Object.entries(element.dataset)) {
      try {
        // Try to parse JSON values
        config[key] = JSON.parse(value);
      } catch (e) {
        // Use as string if not valid JSON
        config[key] = value;
      }
    }

    log('debug', 'config.js', functionName, `Parsed config for ${elementId}:`, config);

    // Cache the result
    if (useCache) {
      this.cache.set(elementId, config);
    }

    return config;
  }

  /**
   * Get configuration from multiple data elements
   * @param {Array<{id: string, defaults: Object}>} elements - Elements to process
   * @returns {Object} - Combined configuration
   */
  fromElements(elements, useCache = true) {
    const config = {};

    elements.forEach(({ id, defaults = {} }) => {
      config[id] = this.fromElement(id, defaults, useCache);
    });

    return config;
  }

  /**
   * Clear cached configurations
   * @param {string} [elementId] - Specific element ID to clear, or all if not specified
   */
  clearCache(elementId) {
    if (elementId) {
      this.cache.delete(elementId);
      log('debug', 'config.js', 'clearCache', `Cleared cache for ${elementId}`);
    } else {
      this.cache.clear();
      log('debug', 'config.js', 'clearCache', 'Cleared all configuration cache');
    }
  }
}

// Create singleton instance
const configManager = new ConfigManager();
export default configManager;