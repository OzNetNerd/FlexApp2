import apiService from '/static/js/services/apiService.js';
import uiService from '/static/js/services/uiService.js';
import eventSystem from '/static/js/core/events.js';
import log from '/static/js/core/logger.js';

/**
 * Companies Dashboard Controller - Responsible for data operations only
 */
class CompaniesDashboardController {
  constructor() {
    this.container = document.getElementById('companies-dashboard-container');
    this.apiUrls = {
      stats: this.container.dataset.statsUrl,
      segments: this.container.dataset.segmentsUrl,
      topCompanies: this.container.dataset.topCompaniesUrl,
      growth: this.container.dataset.growthUrl
    };
    this.initialized = false;
  }

  init() {
    if (this.initialized) return;
    this.loadDashboardData();
    this.initialized = true;
  }

  loadDashboardData() {
    eventSystem.publish('dashboard:loading:start', { message: 'Loading dashboard data...' });

    Promise.all([
      this.fetchStats(),
      this.fetchSegments(),
      this.fetchGrowthData()
    ])
    .then(() => {
      eventSystem.publish('dashboard:loading:complete');
    })
    .catch(error => {
      console.error('Error loading dashboard data:', error);
      eventSystem.publish('dashboard:loading:error', {
        message: 'Failed to load dashboard data. Please try again later.'
      });
    });
  }

  fetchStats() {
    return apiService.get(this.apiUrls.stats)
      .then(stats => {
        eventSystem.publish('dashboard:stats:updated', stats);
        return stats;
      })
      .catch(error => {
        console.error('Error fetching dashboard stats:', error);
        throw error;
      });
  }

  fetchSegments() {
    return apiService.get(this.apiUrls.segments)
      .then(segments => {
        eventSystem.publish('dashboard:segments:updated', segments);
        return segments;
      })
      .catch(error => {
        console.error('Error fetching segments:', error);
        throw error;
      });
  }

  fetchGrowthData() {
    return apiService.get(this.apiUrls.growth)
      .then(data => {
        eventSystem.publish('dashboard:growth:updated', data);
        return data;
      })
      .catch(error => {
        console.error('Error fetching growth data:', error);
        throw error;
      });
  }
}

// UI Updates Module - Handles all UI updates based on events
const DashboardUIUpdates = {
  init() {
    eventSystem.subscribe('dashboard:loading:start', this.handleLoadingStart);
    eventSystem.subscribe('dashboard:loading:complete', this.handleLoadingComplete);
    eventSystem.subscribe('dashboard:loading:error', this.handleLoadingError);

    eventSystem.subscribe('dashboard:stats:updated', this.updateStats);
    eventSystem.subscribe('dashboard:segments:updated', this.updateSegments);
    eventSystem.subscribe('dashboard:growth:updated', this.initializeChart);

    log('info', 'dashboard.js', 'DashboardUIUpdates.init', 'UI update event listeners initialized');
  },

  handleLoadingStart(data) {
    window.currentLoadingIndicator = uiService.showLoading(null, data.message);
  },

  handleLoadingComplete() {
    if (window.currentLoadingIndicator) {
      window.currentLoadingIndicator.hide();
      window.currentLoadingIndicator = null;
    }
  },

  handleLoadingError(data) {
    if (window.currentLoadingIndicator) {
      window.currentLoadingIndicator.hide();
      window.currentLoadingIndicator = null;
    }
    uiService.showError(data.message);
  },

  updateStats(stats) {
    if (stats.with_opportunities) {
      const badge = document.getElementById('with-opportunities-badge');
      if (badge) badge.textContent = stats.with_opportunities;
    }

    if (stats.with_contacts) {
      const badge = document.getElementById('with-contacts-badge');
      if (badge) badge.textContent = stats.with_contacts;
    }

    const totalCompaniesElement = document.querySelector('.total-companies-count');
    if (totalCompaniesElement && stats.total_companies) {
      totalCompaniesElement.textContent = stats.total_companies;
    }

    log('debug', 'dashboard.js', 'updateStats', 'Statistics updated');
  },

  updateSegments(segments) {
    if (!segments || Object.keys(segments).length === 0) return;

    const segmentsArray = Object.values(segments);
    if (segmentsArray.length < 3) return;

    DashboardUIUpdates.updateSegmentCard('high-engagement', segmentsArray[0]);
    DashboardUIUpdates.updateSegmentCard('medium-engagement', segmentsArray[1]);
    DashboardUIUpdates.updateSegmentCard('no-opportunities', segmentsArray[2]);

    const segmentsSection = document.querySelector('.engagement-segments-section');
    if (segmentsSection) {
      segmentsSection.style.display = 'block';
    }

    log('debug', 'dashboard.js', 'updateSegments', 'Segment cards updated');
  },

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
  },

  initializeChart(growthData) {
    if (!growthData || !growthData.labels || !growthData.new_companies || !growthData.total_companies) {
      log('warn', 'dashboard.js', 'initializeChart', 'Growth data not available');
      return;
    }

    const chartData = {
      labels: growthData.labels,
      newItems: growthData.new_companies,
      totalItems: growthData.total_companies
    };

    import('/static/js/visuals/lineGraph.js')
      .then(module => {
        module.initDataChart('dataChart', chartData);
        log('info', 'dashboard.js', 'initializeChart', 'Data chart initialized');
      })
      .catch(err => {
        log('error', 'dashboard.js', 'initializeChart', 'Failed to load lineGraph.js', err);
      });
  }
};

// Initialize dashboard on DOM load
document.addEventListener('DOMContentLoaded', () => {
  log('info', 'dashboard.js', 'DOMContentLoaded', 'Initializing dashboard');
  DashboardUIUpdates.init();
  const dashboard = new CompaniesDashboardController();
  dashboard.init();
});