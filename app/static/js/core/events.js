import log from '/static/js/core/logger.js';

/**
 * Simple pub/sub event system for cross-component communication
 */
class EventSystem {
  constructor() {
    this.events = {};
    log('info', 'events.js', 'constructor', 'Event system created');
  }

  /**
   * Subscribe to an event
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   * @returns {Object} - Subscription object with unsubscribe method
   */
  subscribe(event, callback) {
    const functionName = 'subscribe';

    // Create event array if it doesn't exist
    if (!this.events[event]) {
      this.events[event] = [];
    }

    // Add callback to event array
    this.events[event].push(callback);

    log('debug', 'events.js', functionName, `Subscribed to event: ${event}`);

    // Return subscription object with unsubscribe method
    return {
      unsubscribe: () => {
        this.events[event] = this.events[event].filter(cb => cb !== callback);
        log('debug', 'events.js', 'unsubscribe', `Unsubscribed from event: ${event}`);

        // Clean up empty event arrays
        if (this.events[event].length === 0) {
          delete this.events[event];
        }
      }
    };
  }

  /**
   * Publish an event with data
   * @param {string} event - Event name
   * @param {any} data - Event data
   */
  publish(event, data) {
    const functionName = 'publish';

    if (!this.events[event]) {
      log('debug', 'events.js', functionName, `No subscribers for event: ${event}`);
      return;
    }

    log('debug', 'events.js', functionName, `Publishing event: ${event}`, data);

    this.events[event].forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        log('error', 'events.js', functionName, `Error in event handler for ${event}:`, error);
      }
    });
  }

  /**
   * Clear all subscribers for an event
   * @param {string} [event] - Event name, or all events if not specified
   */
  clear(event) {
    if (event) {
      delete this.events[event];
      log('debug', 'events.js', 'clear', `Cleared subscribers for event: ${event}`);
    } else {
      this.events = {};
      log('debug', 'events.js', 'clear', 'Cleared all event subscribers');
    }
  }
}

// Create singleton instance
const eventSystem = new EventSystem();
export default eventSystem;