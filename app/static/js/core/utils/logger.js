/**
 * core/utils/logger.js
 * Logger Module – Supports file and function grouping for better debugging
 */

const levelColors = {
  debug: '#808080',
  info: '#4682B4',
  warn: '#FFA500',
  error: '#FF0000'
};

// Map to track open file groups. Each entry holds the function count and current function name.
const fileGroups = new Map();

// Helper to close all open groups (both file and nested function groups)
function closeAllFileGroups() {
  fileGroups.forEach((group) => {
    if (group.currentFunction) {
      console.groupEnd(); // close the function group
    }
    console.groupEnd(); // close the file group
  });
  fileGroups.clear();
}

export default function log(level, scriptName, functionName, message, data) {
  const timestamp = new Date().toISOString();
  const coloredLevel = `%c${level.toUpperCase()}%c`;
  const levelStyle = `color: ${levelColors[level]}; font-weight: bold;`;
  const resetStyle = 'color: inherit; font-weight: normal;';
  const baseMessage = `${timestamp} ${coloredLevel} [${scriptName}:${functionName}]: ${message}`;

  // If we haven't opened a file group for this script, close any existing groups and open a new file group.
  if (!fileGroups.has(scriptName)) {
    closeAllFileGroups();
    // We open the file group with an initial count (here shown as 0).
    // (Due to console API limits, updating this count later isn't directly possible.)
    console.groupCollapsed(`${scriptName} (0)`);
    fileGroups.set(scriptName, {
      functionCount: 0,
      currentFunction: null
    });
  }

  const fileGroup = fileGroups.get(scriptName);

  // If the current function group isn't the one for this log, close the old function group (if any)
  // and start a new one.
  if (fileGroup.currentFunction !== functionName) {
    if (fileGroup.currentFunction !== null) {
      console.groupEnd(); // close previous function group
    }
    fileGroup.functionCount++;
    // Ideally we would update the file group header to reflect the new function count,
    // but the console API does not allow updating an already-opened group header.
    console.groupCollapsed(functionName);
    fileGroup.currentFunction = functionName;
  }

  // Log the message inside the current function group.
  if (data === undefined) {
    console[level](baseMessage, levelStyle, resetStyle);
  } else {
    console[level](baseMessage, levelStyle, resetStyle, data);
  }
}

export function resetGroups() {
  closeAllFileGroups();
}