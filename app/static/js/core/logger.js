/**
 * js/core/logger.js
 * Logger Module – supports optional nested (file & function) grouping.
 */

// Toggle this to enable/disable nested grouping
export let nestedLoggingEnabled = false;

// Color map for levels
const levelColors = {
  debug: '#808080',
  info: '#4682B4',
  warn: '#FFA500',
  error: '#FF0000'
};

// Track open file groups: { functionCount, currentFunction }
const fileGroups = new Map();

// Close all open groups (file + nested function)
function closeAllFileGroups() {
  if (!nestedLoggingEnabled) return;
  fileGroups.forEach((group) => {
    if (group.currentFunction) {
      console.groupEnd(); // close the function group
    }
    console.groupEnd(); // close the file group
  });
  fileGroups.clear();
}

/**
 * Main log function.
 *
 * @param {string} level         One of 'debug'|'info'|'warn'|'error'
 * @param {string} scriptName    Name of the JS file/module
 * @param {string} functionName  Name of the function or context
 * @param {string} message       The message to log
 * @param {any}    [data]        Optional extra data object
 */
export default function log(level, scriptName, functionName, message, data) {
  // if user passed e.g. 4 args and message is an array/object, shift it into data
  if (data === undefined && typeof message !== 'string') {
    data    = message;
    message = '';
  }

  const timestamp = new Date().toISOString();
  const coloredLevel = `%c${level.toUpperCase()}%c`;
  const levelStyle = `color: ${levelColors[level]}; font-weight: bold;`;
  const resetStyle = 'color: inherit; font-weight: normal;';
  const baseMessage = `${timestamp} ${coloredLevel} [${scriptName}:${functionName}]: ${message}`;

  // If nested grouping is off, just output a flat log
  if (!nestedLoggingEnabled) {
    if (data === undefined) {
      console[level](baseMessage, levelStyle, resetStyle);
    } else {
      // Use console.log with label first, then object separately
      console[level](baseMessage, levelStyle, resetStyle);
      // Use separate console call for object to make it inspectable
      console[level](data);
    }
    return;
  }

  // --- nested grouping logic ---
  // Ensure only one file group is open at a time
  if (!fileGroups.has(scriptName)) {
    closeAllFileGroups();
    console.groupCollapsed(`${scriptName} (0)`);
    fileGroups.set(scriptName, {
      functionCount: 0,
      currentFunction: null
    });
  }

  const fileGroup = fileGroups.get(scriptName);

  // Switch function groups if needed
  if (fileGroup.currentFunction !== functionName) {
    if (fileGroup.currentFunction !== null) {
      console.groupEnd(); // close previous function group
    }
    fileGroup.functionCount++;
    console.groupCollapsed(functionName);
    fileGroup.currentFunction = functionName;
  }

  // Finally log inside the innermost group
  if (data === undefined) {
    console[level](baseMessage, levelStyle, resetStyle);
  } else {
    // Separate calls for message and data
    console[level](baseMessage, levelStyle, resetStyle);
    console[level](data);
  }
}

/**
 * Force-close all groups immediately.
 */
export function resetGroups() {
  closeAllFileGroups();
}

/**
 * Helper to change nested-logging behavior at runtime.
 * Passing false will also close any currently open groups.
 *
 * @param {boolean} enabled
 */
export function setNestedLogging(enabled) {
  nestedLoggingEnabled = enabled;
  if (!enabled) {
    closeAllFileGroups();
  }
}