/**
 * js/visuals/lineGraph.js
 * Handles the initialization and rendering of the data chart
 */

// Define script name at the top
const scriptName = 'data-chart.js';

// Import the logger module
import log from '/static/js/core/logger.js';

/**
 * Initialize and render the data chart
 * @param {Object} chartData - The data for the chart with labels, newItems, and totalItems
 */
function initDataChart(chartData) {
  log('info', scriptName, 'initDataChart', 'Initializing data chart...');

  // Check if Chart.js is loaded
  if (typeof Chart === 'undefined') {
    log('error', scriptName, 'initDataChart', 'Chart.js is not loaded properly');
    return;
  }

  // Check if the canvas element exists
  const chartCanvas = document.getElementById('dataChart');
  if (!chartCanvas) {
    log('error', scriptName, 'initDataChart', 'Data chart canvas element not found');
    return;
  }

  log('info', scriptName, 'initDataChart', 'Found chart canvas, creating chart context');
  const ctx = chartCanvas.getContext('2d');

  // Create gradient fills for better visualization
  log('debug', scriptName, 'initDataChart', 'Creating gradient fills for chart');
  const newItemsGradient = ctx.createLinearGradient(0, 0, 0, 300);
  newItemsGradient.addColorStop(0, 'rgba(40, 167, 69, 0.4)');
  newItemsGradient.addColorStop(1, 'rgba(40, 167, 69, 0.05)');

  const totalItemsGradient = ctx.createLinearGradient(0, 0, 0, 300);
  totalItemsGradient.addColorStop(0, 'rgba(0, 123, 255, 0.4)');
  totalItemsGradient.addColorStop(1, 'rgba(0, 123, 255, 0.05)');

  // Get labels and data
  const { labels, newItems, totalItems } = chartData;

  log('info', scriptName, 'initDataChart', 'Preparing chart with data', {
    labels,
    newItems,
    totalItems
  });

  // Create the chart
  log('info', scriptName, 'initDataChart', 'Creating new Chart.js instance');
  try {
    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'New Items',
            backgroundColor: newItemsGradient,
            borderColor: 'rgba(40, 167, 69, 1)',
            borderWidth: 2,
            pointBackgroundColor: 'rgba(40, 167, 69, 1)',
            pointRadius: 4,
            pointHoverRadius: 6,
            fill: true,
            tension: 0.3,
            data: newItems
          },
          {
            label: 'Total Items',
            backgroundColor: totalItemsGradient,
            borderColor: 'rgba(0, 123, 255, 1)',
            borderWidth: 2,
            pointBackgroundColor: 'rgba(0, 123, 255, 1)',
            pointRadius: 4,
            pointHoverRadius: 6,
            fill: true,
            tension: 0.3,
            data: totalItems
          }
        ]
      },
      options: {
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
      }
    });

    log('info', scriptName, 'initDataChart', 'Data chart initialized successfully');
    return chart;
  } catch (error) {
    log('error', scriptName, 'initDataChart', 'Error initializing data chart:', error);
    return null;
  }
}

/**
 * Initialize the chart when the DOM is fully loaded
 */
function initializeOnLoad() {
  log('debug', scriptName, 'initializeOnLoad', 'Setting up DOMContentLoaded event listener');

  document.addEventListener('DOMContentLoaded', function() {
    log('info', scriptName, 'DOMContentLoaded', 'DOM fully loaded, attempting to initialize chart');

    try {
      // Try to get chart data from the window object (populated by template)
      if (window.chartData) {
        log('info', scriptName, 'DOMContentLoaded', 'Found chart data in window object', window.chartData);
        initDataChart(window.chartData);
      } else {
        log('warn', scriptName, 'DOMContentLoaded', 'Chart data not found in window object');
      }
    } catch (error) {
      log('error', scriptName, 'DOMContentLoaded', 'Error during chart initialization:', error);
    }
  });
}

// Start the initialization process
initializeOnLoad();

// Export the function for potential reuse
export default initDataChart;