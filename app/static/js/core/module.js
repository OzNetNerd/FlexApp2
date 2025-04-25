import log from '/static/js/core/logger.js';

/**
 * Simple module system for handling dependencies and initialization.
 */
class ModuleSystem {
  constructor() {
    this.modules = new Map();
    this.initialized = new Set();
    this.domReady = false;

    log('info', 'module.js', 'constructor', 'Module system created');

    // Set up DOM ready event
    document.addEventListener('DOMContentLoaded', () => {
      this.domReady = true;
      log('info', 'module.js', 'DOMContentLoaded', 'DOM is ready, initializing modules');
      this.initReadyModules();
    });
  }

  /**
   * Register a module with the system
   * @param {string} name - Module name
   * @param {Function} initFn - Initialization function
   * @param {Array<string>} dependencies - Array of module dependencies
   * @param {boolean} requiresDom - Whether module requires DOM to be ready
   */
  register(name, initFn, dependencies = [], requiresDom = true) {
    log('debug', 'module.js', 'register', `Registering module: ${name}`, { dependencies, requiresDom });

    this.modules.set(name, {
      name,
      initFn,
      dependencies,
      requiresDom
    });

    // Initialize immediately if no dependencies and doesn't require DOM (or DOM is ready)
    if (dependencies.length === 0 && (!requiresDom || this.domReady)) {
      this.initModule(name);
    }

    return this;
  }

  /**
   * Initialize a specific module and its dependencies
   * @param {string} name - Module name
   */
  initModule(name) {
    // Skip if already initialized
    if (this.initialized.has(name)) return;

    const module = this.modules.get(name);
    if (!module) {
      log('warn', 'module.js', 'initModule', `Module not found: ${name}`);
      return;
    }

    log('debug', 'module.js', 'initModule', `Initializing module: ${name}`);

    // Check if module requires DOM but DOM is not ready
    if (module.requiresDom && !this.domReady) {
      log('debug', 'module.js', 'initModule', `Module ${name} requires DOM, deferring initialization`);
      return;
    }

    // Initialize dependencies first
    module.dependencies.forEach(dep => {
      this.initModule(dep);
    });

    // Initialize the module
    try {
      module.initFn();
      this.initialized.add(name);
      log('info', 'module.js', 'initModule', `Module initialized: ${name}`);
    } catch (error) {
      log('error', 'module.js', 'initModule', `Error initializing module ${name}:`, error);
    }
  }

  /**
   * Initialize all modules that are ready to be initialized
   */
  initReadyModules() {
    this.modules.forEach((module, name) => {
      // Skip if already initialized
      if (this.initialized.has(name)) return;

      // Check if all dependencies are initialized
      const depsReady = module.dependencies.every(dep => this.initialized.has(dep));

      // Initialize if dependencies are ready and DOM requirements are met
      if (depsReady && (!module.requiresDom || this.domReady)) {
        this.initModule(name);
      }
    });
  }
}

// Create singleton instance
const moduleSystem = new ModuleSystem();
export default moduleSystem;
