/**
  js/logger.js
 * Logger Module
 * Centralized logging utility for consistent logging across the application
 */

  const levelColors = {
    debug: '#808080', // Gray
    info: '#4682B4',  // Steel blue
    warn: '#FFA500',  // Orange/Yellow
    error: '#FF0000'  // Red
};

/**
 * Logs a message at the specified level.
 * @param {string} level - The log level (`debug`, `info`, `warn`, `error`).
 * @param {string} scriptName - The script where the log originates.
 * @param {string} functionName - The function where the log originates.
 * @param {string} message - The log message.
 * @param {any} [data] - Optional additional data to log.
 */
export default function log(level, scriptName, functionName, message, data) {
    const timestamp = new Date().toISOString();
    const contextLabel = `[${scriptName}:${functionName}]`;

    // Format the message with colored level
    const coloredLevel = `%c${level.toUpperCase()}%c`;
    const levelStyle = `color: ${levelColors[level]}; font-weight: bold;`;
    const resetStyle = 'color: inherit; font-weight: normal;';

    const baseMessage = `${timestamp} ${coloredLevel} ${contextLabel}: ${message}`;

    if (data === undefined) {
        console[level](baseMessage, levelStyle, resetStyle);
    } else if (data === null) {
        console[level](`${baseMessage} (null)`, levelStyle, resetStyle);
    } else if (typeof data === 'object') {
        try {
            // Handle special DOM objects
            const processedData = data instanceof DOMStringMap ? Object.fromEntries(Object.entries(data)) : data;

            // Check if this is a string-like object (with numeric keys)
            const hasNumericKeys = typeof processedData === 'object' &&
                                  processedData !== null &&
                                  !Array.isArray(processedData) &&
                                  Object.keys(processedData).length > 0 &&
                                  Object.keys(processedData).every(k => !isNaN(parseInt(k)));

            if (hasNumericKeys) {
                // Handle string-like objects by converting to actual string
                const strValue = Object.values(processedData).join('');
                console[level](`${baseMessage} ${strValue}`, levelStyle, resetStyle);
            } else {
                console[level](baseMessage, levelStyle, resetStyle, processedData);
            }
        } catch (error) {
            console[level](`${baseMessage} (Unprintable object)`, levelStyle, resetStyle);
        }
    } else {
        console[level](baseMessage, levelStyle, resetStyle, data);
    }
}