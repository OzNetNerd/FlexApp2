import apiService from '/static/js/services/apiService.js';
import uiService from '/static/js/services/uiService.js';

/**
 * Companies Dashboard Controller
 */
class CompaniesDashboardController {
  constructor() {
    // Get container element
    this.container = document.getElementById('companies-dashboard-container');

    // Get API URLs from data attributes
    this.apiUrls = {
      stats: this.container.dataset.statsUrl,
      segments: this.container.dataset.segmentsUrl,
      topCompanies: this.container.dataset.topCompaniesUrl,
      growth: this.container.dataset.growthUrl
    };

    this.initialized = false;
  }

  /**
   * Initialize the dashboard
   */
  init() {
    if (this.initialized) return;

    this.loadDashboardData();
    this.initialized = true;
  }

  /**
   * Load all dashboard data
   */
  loadDashboardData() {
    const loadingIndicator = uiService.showLoading(null, 'Loading dashboard data...');

    Promise.all([
      this.fetchStats(),
      this.fetchSegments(),
      this.fetchGrowthData()
    ])
    .then(() => {
      loadingIndicator.hide();
    })
    .catch(error => {
      console.error('Error loading dashboard data:', error);
      uiService.showError('Failed to load dashboard data. Please try again later.');
      loadingIndicator.hide();
    });
  }

  /**
   * Fetch dashboard statistics
   */
  fetchStats() {
    return apiService.get(this.apiUrls.stats)
      .then(stats => {
        this.updateStats(stats);
        return stats;
      })
      .catch(error => {
        console.error('Error fetching dashboard stats:', error);
        throw error;
      });
  }

  /**
   * Update statistics on the page
   */
  updateStats(stats) {
    // Update badge values for the large cards
    if (stats.with_opportunities) {
      const badge = document.getElementById('with-opportunities-badge');
      if (badge) badge.textContent = stats.with_opportunities;
    }

    if (stats.with_contacts) {
      const badge = document.getElementById('with-contacts-badge');
      if (badge) badge.textContent = stats.with_contacts;
    }

    // Update total companies count
    const totalCompaniesElement = document.querySelector('.total-companies-count');
    if (totalCompaniesElement && stats.total_companies) {
      totalCompaniesElement.textContent = stats.total_companies;
    }
  }

  /**
   * Fetch segments data
   */
  fetchSegments() {
    return apiService.get(this.apiUrls.segments)
      .then(segments => {
        this.updateSegments(segments);
        return segments;
      })
      .catch(error => {
        console.error('Error fetching segments:', error);
        throw error;
      });
  }

  /**
   * Update segments on the page
   */
  updateSegments(segments) {
    if (!segments || Object.keys(segments).length === 0) {
      // Hide segments section if no data
      const segmentsSection = document.querySelector('.engagement-segments-section');
      if (segmentsSection) {
        segmentsSection.style.display = 'none';
      }
      return;
    }

    // Convert segments object to array
    const segmentsArray = Object.values(segments);

    if (segmentsArray.length < 3) {
      return;
    }

    // Update each segment card
    this.updateSegmentCard('high-engagement', segmentsArray[0]);
    this.updateSegmentCard('medium-engagement', segmentsArray[1]);
    this.updateSegmentCard('no-opportunities', segmentsArray[2]);

    // Show segments section
    const segmentsSection = document.querySelector('.engagement-segments-section');
    if (segmentsSection) {
      segmentsSection.style.display = 'block';
    }
  }

  /**
   * Update a single segment card
   */
  updateSegmentCard(id, segmentData) {
    const card = document.getElementById(id);
    if (!card) return;

    const countElement = card.querySelector('.segment-count');
    if (countElement) {
      countElement.textContent = segmentData.count;
    }

    const percentageElement = card.querySelector('.segment-percentage');
    if (percentageElement) {
      percentageElement.textContent = `${segmentData.percentage}%`;
    }

    const progressBar = card.querySelector('.progress-bar');
    if (progressBar) {
      progressBar.style.width = `${segmentData.percentage}%`;
      progressBar.setAttribute('aria-valuenow', segmentData.percentage);
    }
  }

  /**
   * Fetch growth data for the chart
   */
  fetchGrowthData() {
    return apiService.get(this.apiUrls.growth)
      .then(data => {
        this.initializeChart(data);
        return data;
      })
      .catch(error => {
        console.error('Error fetching growth data:', error);
        throw error;
      });
  }

  /**
   * Initialize the data chart
   */
  initializeChart(growthData) {
    if (!growthData || !growthData.labels || !growthData.new_companies || !growthData.total_companies) {
      console.warn('Growth data not available for chart initialization');
      return;
    }

    const chartData = {
      labels: growthData.labels,
      newItems: growthData.new_companies,
      totalItems: growthData.total_companies
    };

    // Import and use the lineGraph module
    import('/static/js/visuals/lineGraph.js')
      .then(module => {
        // Call the initDataChart function from the imported module
        module.initDataChart('dataChart', chartData);
      })
      .catch(err => console.error('Failed to load lineGraph.js:', err));
  }
}

// Initialize dashboard on DOM load
document.addEventListener('DOMContentLoaded', () => {
  const dashboard = new CompaniesDashboardController();
  dashboard.init();
});