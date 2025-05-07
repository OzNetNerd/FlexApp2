/**
 * Bar Graph visualization module
 * Creates stacked bar charts with configurable datasets
 */

/**
 * Initialize a stacked bar chart
 * @param {string} chartId - The ID of the canvas element
 * @param {Object} data - Chart data containing labels and datasets
 * @param {Object} options - Additional chart options (optional)
 */
export function initBarChart(chartId, data, options = {}) {
  const ctx = document.getElementById(chartId).getContext('2d');

  // Default configuration
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        stacked: true,
        grid: {
          display: false
        }
      },
      y: {
        stacked: true,
        beginAtZero: true,
        title: {
          display: true,
          text: options.yAxisTitle || 'Amount'
        }
      }
    },
    plugins: {
      tooltip: {
        mode: 'index',
        intersect: false
      },
      legend: {
        position: 'top'
      }
    }
  };

  // Default colors if not provided
  const defaultColors = [
    'rgba(40, 167, 69, 0.8)',   // green
    'rgba(0, 123, 255, 0.8)',   // blue
    'rgba(108, 117, 125, 0.8)', // gray
    'rgba(255, 193, 7, 0.8)',   // yellow
    'rgba(220, 53, 69, 0.8)'    // red
  ];

  // Prepare datasets with colors if not provided
  const datasets = Array.isArray(data.datasets)
    ? data.datasets
    : Object.keys(data).filter(key => key !== 'labels').map((key, index) => ({
        label: key,
        backgroundColor: defaultColors[index % defaultColors.length],
        data: data[key]
      }));

  // Create and return the chart instance
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.labels,
      datasets: datasets
    },
    options: {...defaultOptions, ...options}
  });
}

/**
 * Initialize a sales forecast chart with preset categories
 * @param {string} chartId - The ID of the canvas element
 * @param {Object} forecastData - Data containing labels, closed_won, forecast, pipeline
 * @param {string} currencySymbol - Currency symbol to display (optional)
 */
export function initSalesForecastChart(chartId, forecastData, currencySymbol = '$') {
  const options = {
    yAxisTitle: `Amount (${currencySymbol})`
  };

  // Convert to format expected by initBarChart if needed
  const chartData = {
    labels: forecastData.labels,
    datasets: [
      {
        label: 'Closed Won',
        backgroundColor: 'rgba(40, 167, 69, 0.8)',
        data: forecastData.closed_won
      },
      {
        label: 'Forecast',
        backgroundColor: 'rgba(0, 123, 255, 0.8)',
        data: forecastData.forecast
      },
      {
        label: 'Pipeline',
        backgroundColor: 'rgba(108, 117, 125, 0.8)',
        data: forecastData.pipeline
      }
    ]
  };

  return initBarChart(chartId, chartData, options);
}