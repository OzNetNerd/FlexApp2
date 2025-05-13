import log from '/static/js/core/logger.js';
import { getDatasetVariables, getDatasetValue } from '/static/js/core/utils.js';

/**
 * API service for making HTTP requests
 */
class ApiService {
  constructor() {
    this.baseUrl = '';
    this.defaultHeaders = {
      'Content-Type': 'application/json'
    };
    log('info', 'apiService.js', 'constructor', 'API service created');
  }

  /**
   * Set the base URL for API requests
   * @param {string} url - Base URL
   */
  setBaseUrl(url) {
    this.baseUrl = url;
    log('debug', 'apiService.js', 'setBaseUrl', `Base URL set to: ${url}`);
  }

  /**
   * Add a default header for API requests
   * @param {string} name - Header name
   * @param {string} value - Header value
   */
  addDefaultHeader(name, value) {
    this.defaultHeaders[name] = value;
    log('debug', 'apiService.js', 'addDefaultHeader', `Added default header: ${name}`);
  }

  /**
   * Make a generic request
   * @param {string} method - HTTP method
   * @param {string} url - Request URL
   * @param {Object} data - Request data
   * @param {Object} headers - Additional headers
   * @param {Object} options - Additional fetch options
   * @returns {Promise} - Promise that resolves with the response data
   */
  request(method, url, data = null, headers = {}, options = {}) {
    const functionName = 'request';

    // Prepend base URL if the URL doesn't start with http or /
    const fullUrl = (url.startsWith('http') || url.startsWith('/'))
      ? url
      : `${this.baseUrl}/${url}`;

    // Merge default headers with provided headers
    const mergedHeaders = {
      ...this.defaultHeaders,
      ...headers
    };

    // Create fetch options
    const fetchOptions = {
      method,
      headers: mergedHeaders,
      ...options
    };

    // Add body if data is provided
    if (data !== null) {
      if (mergedHeaders['Content-Type'] === 'application/json') {
        fetchOptions.body = JSON.stringify(data);
      } else if (data instanceof FormData) {
        fetchOptions.body = data;
        // Let the browser set the boundary
        delete fetchOptions.headers['Content-Type'];
      } else {
        fetchOptions.body = data;
      }
    }

    log('debug', 'apiService.js', functionName, `Making ${method} request to ${fullUrl}`, {
      headers: mergedHeaders,
      data: data
    });

    return fetch(fullUrl, fetchOptions)
      .then(response => {
        log('debug', 'apiService.js', functionName, `Received response from ${fullUrl}`, {
          status: response.status,
          statusText: response.statusText
        });

        // Check if the response is OK
        if (!response.ok) {
          return response.text().then(text => {
            log('error', 'apiService.js', functionName, `Error response from ${fullUrl}`, {
              status: response.status,
              text: text
            });

            try {
              const errorData = JSON.parse(text);
              throw new Error(`API responded with status: ${response.status}: ${JSON.stringify(errorData)}`);
            } catch (parseError) {
              throw new Error(`API responded with status: ${response.status}: ${text}`);
            }
          });
        }

        // Check if the response is empty
        const contentType = response.headers.get('content-type');
        if (!contentType || (!contentType.includes('application/json') && response.status !== 204)) {
          return response.text();
        }

        return response.json();
      })
      .then(data => {
        log('debug', 'apiService.js', functionName, `Processed response from ${fullUrl}`, {
          data: data
        });

        return data;
      })
      .catch(error => {
        log('error', 'apiService.js', functionName, `Error in ${method} request to ${fullUrl}:`, error);
        throw error;
      });
  }

  /**
   * Make a GET request
   * @param {string} url - Request URL
   * @param {Object} headers - Additional headers
   * @param {Object} options - Additional fetch options
   * @returns {Promise} - Promise that resolves with the response data
   */
  get(url, headers = {}, options = {}) {
    return this.request('GET', url, null, headers, options);
  }

  /**
   * Make a POST request
   * @param {string} url - Request URL
   * @param {Object} data - Request data
   * @param {Object} headers - Additional headers
   * @param {Object} options - Additional fetch options
   * @returns {Promise} - Promise that resolves with the response data
   */
  post(url, data, headers = {}, options = {}) {
    return this.request('POST', url, data, headers, options);
  }

  /**
   * Make a PUT request
   * @param {string} url - Request URL
   * @param {Object} data - Request data
   * @param {Object} headers - Additional headers
   * @param {Object} options - Additional fetch options
   * @returns {Promise} - Promise that resolves with the response data
   */
  put(url, data, headers = {}, options = {}) {
    return this.request('PUT', url, data, headers, options);
  }

  /**
   * Make a PATCH request
   * @param {string} url - Request URL
   * @param {Object} data - Request data
   * @param {Object} headers - Additional headers
   * @param {Object} options - Additional fetch options
   * @returns {Promise} - Promise that resolves with the response data
   */
  patch(url, data, headers = {}, options = {}) {
    return this.request('PATCH', url, data, headers, options);
  }

  /**
   * Make a DELETE request
   * @param {string} url - Request URL
   * @param {Object} headers - Additional headers
   * @param {Object} options - Additional fetch options
   * @returns {Promise} - Promise that resolves with the response data
   */
  delete(url, headers = {}, options = {}) {
    return this.request('DELETE', url, null, headers, options);
  }

  /**
   * Upload a file
   * @param {string} url - Request URL
   * @param {File} file - File to upload
   * @param {string} fieldName - Field name for the file
   * @param {Object} additionalData - Additional form data
   * @param {Object} headers - Additional headers
   * @param {Object} options - Additional fetch options
   * @returns {Promise} - Promise that resolves with the response data
   */
  uploadFile(url, file, fieldName = 'file', additionalData = {}, headers = {}, options = {}) {
    const functionName = 'uploadFile';

    const formData = new FormData();
    formData.append(fieldName, file);

    // Add additional data
    for (const [key, value] of Object.entries(additionalData)) {
      formData.append(key, value);
    }

    log('debug', 'apiService.js', functionName, `Uploading file to ${url}`, {
      fileName: file.name,
      fileSize: file.size,
      fileType: file.type,
      fieldName: fieldName
    });

    return this.request('POST', url, formData, headers, options);
  }
}

// Create singleton instance
const apiService = new ApiService();
export default apiService;

/**
 * Fetches data from an API endpoint using the dataset variables on a container element
 * @param {string} containerId - The ID of the container element with dataset attributes
 * @returns {Promise<Array|Object>} - The data fetched from the API
 */
export async function fetchApiDataFromContainer(containerId) {
  const functionName = "fetchApiDataFromContainer";
  const container = document.getElementById(containerId);

  if (!container) {
    throw new Error(`Container with ID '${containerId}' not found`);
  }

  const apiUrl = container.dataset.apiUrl || container.getAttribute('data-api-url');

  if (!apiUrl) {
    log("error", "apiService.js", functionName, "API URL is null or empty");
    throw new Error("Missing API URL. Check data-api-url attribute on container.");
  }

  log("info", "apiService.js", functionName, `API URL Retrieved: ${apiUrl}`);

  try {
    return await apiService.get(apiUrl);
  } catch (error) {
    log("error", "apiService.js", functionName, "Failed to fetch data from API", error);
    throw error;
  }
}

/**
 * Normalizes data structure from various API response formats
 * @param {Array|Object} data - The raw data from the API
 * @returns {Array} - Normalized data array
 */
export function normalizeData(data) {
  // Handle potential error responses
  if (data && data.data && data.data.error) {
    throw new Error(data.data.error.message || "Unknown API error");
  }

  // Handle both data structures: data = [{...}] or data = {data: [{...}]}
  if (Array.isArray(data)) {
    return data;
  } else if (data && typeof data === 'object') {
    if (data.data && Array.isArray(data.data)) {
      return data.data;
    } else if (data.data && typeof data.data === 'object' && !data.data.error) {
      return [data.data];
    } else if (Object.keys(data).length > 0 && !('data' in data)) {
      return [data];
    }
  }

  // Fallback to empty array
  return [];
}

/**
 * Formats a string for use as a column header or display text
 * @param {string} text - Raw text to format
 * @returns {string} - Formatted text
 */
export function formatDisplayText(text) {
  return text
    .replace(/_/g, ' ') // Replace underscores with spaces
    .replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()) // Capitalize first letter
    .replace(/\bId\b/g, 'ID') // Make "Id" into "ID"
    .replace(/\bAt\b/g, 'at'); // Make "At" into "at"
}