/**
 * js/visuals/lineGraph.js
 * Flexible chart initialization module with unified configuration
 */

// Define script name at the top
const scriptName = 'line-graph.js';

// Import the logger module
import log from '/static/js/core/logger.js';

/**
 * Creates a flat color or gradient fill for chart datasets
 * @param {CanvasRenderingContext2D} ctx - The canvas context
 * @param {string} color - The base color in rgba format
 * @param {number} alpha1 - The alpha value for the first color stop (0-1)
 * @param {number} alpha2 - The alpha value for the second color stop (0-1)
 * @param {number} height - The height of the gradient
 * @returns {string|CanvasGradient} The color or gradient
 */
function createGradient(ctx, color, alpha1 = 0.2, alpha2 = 0.2, height = 300) {
  log('debug', scriptName, 'createGradient', 'Creating color fill');

  // Extract color components from rgba
  const colorBase = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);

  if (!colorBase) {
    log('warn', scriptName, 'createGradient', 'Invalid color format, using original color');
    return color;
  }

  const [_, r, g, b] = colorBase;

  // Return flat color with standard transparency
  return `rgba(${r}, ${g}, ${b}, ${alpha1})`;
}

/**
 * Helper function to deep merge objects
 * @param {Object} target - The target object
 * @param {Object} source - The source object
 * @returns {Object} The merged object
 */
function mergeDeep(target, source) {
  const output = Object.assign({}, target);

  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach(key => {
      if (isObject(source[key])) {
        if (!(key in target)) {
          Object.assign(output, { [key]: source[key] });
        } else {
          output[key] = mergeDeep(target[key], source[key]);
        }
      } else {
        Object.assign(output, { [key]: source[key] });
      }
    });
  }

  return output;
}

/**
 * Helper function to check if value is an object
 * @param {*} item - The item to check
 * @returns {boolean} Whether the item is an object
 */
function isObject(item) {
  return (item && typeof item === 'object' && !Array.isArray(item));
}

/**
 * Get default chart options
 * @returns {Object} Default chart options
 */
function getDefaultOptions() {
  return {
    type: 'line',
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 1000,
      easing: 'easeOutQuart'
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          font: {
            size: 11
          },
          color: '#6c757d'
        }
      },
      y: {
        beginAtZero: true,
        grace: '5%',
        title: {
          display: true,
          text: 'Number of Items',
          font: {
            size: 13,
            weight: 'bold'
          }
        },
        ticks: {
          precision: 0,
          font: {
            size: 11
          },
          color: '#6c757d'
        }
      }
    },
    plugins: {
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        padding: 10,
        cornerRadius: 4
      },
      legend: {
        position: 'top',
        labels: {
          padding: 20,
          boxWidth: 15,
          usePointStyle: true
        }
      }
    }
  };
}

/**
 * Get the predefined chart type configurations
 * @param {string} chartType - The type of chart
 * @returns {Object} The chart type configuration
 */
function getChartTypeConfig(chartType) {
  const types = {
    // Data chart (original from first example)
    'data': {
      dataMapping: (rawData) => {
        const { labels, newItems, totalItems } = rawData;
        return {
          labels: labels,
          datasets: [
            {
              label: 'New Items',
              backgroundColor: 'rgba(40, 167, 69, 0.2)',
              borderColor: 'rgba(40, 167, 69, 1)',
              borderWidth: 2,
              pointBackgroundColor: 'rgba(40, 167, 69, 1)',
              pointRadius: 4,
              fill: true,
              data: newItems
            },
            {
              label: 'Total Items',
              backgroundColor: 'rgba(0, 123, 255, 0.2)',
              borderColor: 'rgba(0, 123, 255, 1)',
              borderWidth: 2,
              pointBackgroundColor: 'rgba(0, 123, 255, 1)',
              pointRadius: 4,
              fill: true,
              data: totalItems
            }
          ]
        };
      },
      options: {
        scales: {
          y: {
            title: {
              text: 'Number of Items'
            }
          }
        }
      }
    },

    // Contact growth chart (from second example)
    'contact': {
      dataMapping: (rawData) => {
        const { labels, newContacts, totalContacts } = rawData;
        return {
          labels: labels,
          datasets: [
            {
              label: 'New Contacts',
              backgroundColor: 'rgba(40, 167, 69, 0.2)',
              borderColor: 'rgba(40, 167, 69, 1)',
              borderWidth: 2,
              pointBackgroundColor: 'rgba(40, 167, 69, 1)',
              pointRadius: 4,
              fill: true,
              data: newContacts
            },
            {
              label: 'Total Contacts',
              backgroundColor: 'rgba(0, 123, 255, 0.2)',
              borderColor: 'rgba(0, 123, 255, 1)',
              borderWidth: 2,
              pointBackgroundColor: 'rgba(0, 123, 255, 1)',
              pointRadius: 4,
              fill: true,
              data: totalContacts
            }
          ]
        };
      },
      options: {
        scales: {
          y: {
            title: {
              text: 'Number of Contacts'
            }
          }
        }
      }
    },

    // Revenue chart (example of another chart type)
    'revenue': {
      dataMapping: (rawData) => {
        const { labels, actual, target } = rawData;
        return {
          labels: labels,
          datasets: [
            {
              label: 'Actual Revenue',
              backgroundColor: 'rgba(255, 193, 7, 0.2)',
              borderColor: 'rgba(255, 193, 7, 1)',
              borderWidth: 2,
              pointBackgroundColor: 'rgba(255, 193, 7, 1)',
              pointRadius: 4,
              fill: true,
              data: actual
            },
            {
              label: 'Target Revenue',
              backgroundColor: 'rgba(220, 53, 69, 0.2)',
              borderColor: 'rgba(220, 53, 69, 1)',
              borderWidth: 2,
              pointBackgroundColor: 'rgba(220, 53, 69, 1)',
              pointRadius: 4,
              fill: true,
              data: target
            }
          ]
        };
      },
      options: {
        scales: {
          y: {
            title: {
              text: 'Revenue Amount'
            },
            ticks: {
              callback: function(value) {
                return '$' + value.toLocaleString();
              }
            }
          }
        }
      }
    },

    // Default/generic chart (allows any custom configuration)
    'generic': {
      dataMapping: (rawData) => rawData,
      options: {}
    }
  };

  return types[chartType] || types.generic;
}

/**
 * Main function to create any type of chart with a unified configuration
 * @param {Object} config - Complete chart configuration object
 * @param {string} config.canvasId - The ID of the canvas element
 * @param {string} config.type - The type of chart ('data', 'contact', 'revenue', 'generic')
 * @param {Object} config.data - The data for the chart (format depends on chart type)
 * @param {Object} config.options - Additional chart options (optional)
 * @param {boolean} config.useGradients - Whether to use gradient fills (optional, default: true)
 * @returns {Chart|null} The created Chart instance or null on failure
 */
function createChart(config) {
  const {
    canvasId,
    type = 'generic',
    data,
    options = {},
    useGradients = true
  } = config;

  log('info', scriptName, 'createChart', `Initializing ${type} chart for canvas ID: ${canvasId}`);

  // Check if Chart.js is loaded
  if (typeof Chart === 'undefined') {
    log('error', scriptName, 'createChart', 'Chart.js is not loaded properly');
    return null;
  }

  // Check if the canvas element exists
  const chartCanvas = document.getElementById(canvasId);
  if (!chartCanvas) {
    log('error', scriptName, 'createChart', `Canvas element with ID ${canvasId} not found`);
    return null;
  }

  const ctx = chartCanvas.getContext('2d');

  // Get the chart type configuration
  const typeConfig = getChartTypeConfig(type);

  // Apply the data mapping function to get the chart-ready data structure
  const mappedData = typeConfig.dataMapping(data);

  // Apply flat colors if requested
  if (useGradients) {
    if (mappedData.datasets) {
      mappedData.datasets = mappedData.datasets.map(dataset => {
        if (dataset.backgroundColor) {
          dataset.backgroundColor = createGradient(ctx, dataset.backgroundColor);
        }
        return dataset;
      });
    }
  }

  // Merge all options: default options + type-specific options + custom options
  const defaultOptions = getDefaultOptions();
  const mergedOptions = mergeDeep(
    mergeDeep(defaultOptions, typeConfig.options),
    options
  );

  // Create the chart
  log('info', scriptName, 'createChart', 'Creating new Chart.js instance');
  try {
    const chart = new Chart(ctx, {
      type: mergedOptions.type || 'line',
      data: mappedData,
      options: mergedOptions
    });

    log('info', scriptName, 'createChart', 'Chart initialized successfully');
    return chart;
  } catch (error) {
    log('error', scriptName, 'createChart', 'Error initializing chart:', error);
    return null;
  }
}

/**
 * Initialize chart when the DOM is fully loaded
 * @param {Object} config - Chart configuration object
 */
function initializeOnLoad(config) {
  log('debug', scriptName, 'initializeOnLoad', 'Setting up DOMContentLoaded event listener');

  document.addEventListener('DOMContentLoaded', function() {
    log('info', scriptName, 'DOMContentLoaded', 'DOM fully loaded, attempting to initialize chart');

    try {
      createChart(config);
    } catch (error) {
      log('error', scriptName, 'DOMContentLoaded', 'Error during chart initialization:', error);
    }
  });
}

// Export functions
export {
  createChart,
  initializeOnLoad
};

// For backward compatibility with the original function
export function initDataChart(canvasId, chartData, options = {}) {
  return createChart({
    canvasId: canvasId,
    type: 'data',
    data: chartData,
    options: options
  });
}

// Default export for backward compatibility
export default createChart;