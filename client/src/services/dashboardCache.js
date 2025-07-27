/**
 * Dashboard Cache Service
 * Caches dashboard data to avoid repeated API calls when navigating between pages
 */

class DashboardCacheService {
  constructor() {
    this.cache = new Map();
    this.cacheExpiry = 5 * 60 * 1000; // 5 minutes in milliseconds
    this.maxCacheSize = 50; // Maximum number of cached items
  }

  /**
   * Generate a cache key based on module ID and date parameters
   */
  generateCacheKey(moduleId, dateParams) {
    const { startDate, endDate, daysBack } = dateParams;
    
    if (startDate && endDate) {
      return `${moduleId}_${startDate.toISOString().split('T')[0]}_${endDate.toISOString().split('T')[0]}`;
    } else if (daysBack) {
      return `${moduleId}_days_${daysBack}`;
    } else {
      return `${moduleId}_default`;
    }
  }

  /**
   * Check if data exists in cache and is not expired
   */
  get(moduleId, dateParams) {
    const key = this.generateCacheKey(moduleId, dateParams);
    const cachedItem = this.cache.get(key);
    
    if (!cachedItem) {
      console.log('📦 Cache miss for key:', key);
      return null;
    }

    const now = Date.now();
    if (now - cachedItem.timestamp > this.cacheExpiry) {
      console.log('📦 Cache expired for key:', key);
      this.cache.delete(key);
      return null;
    }

    console.log('📦 Cache hit for key:', key);
    return cachedItem.data;
  }

  /**
   * Store data in cache with timestamp
   */
  set(moduleId, dateParams, data) {
    const key = this.generateCacheKey(moduleId, dateParams);
    
    // Check cache size and remove oldest items if needed
    if (this.cache.size >= this.maxCacheSize) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
      console.log('📦 Removed oldest cache entry:', oldestKey);
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
    
    console.log('📦 Cached data for key:', key);
  }

  /**
   * Clear specific cache entry
   */
  clear(moduleId, dateParams) {
    const key = this.generateCacheKey(moduleId, dateParams);
    this.cache.delete(key);
    console.log('📦 Cleared cache for key:', key);
  }

  /**
   * Clear all cache
   */
  clearAll() {
    this.cache.clear();
    console.log('📦 Cleared all cache');
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxCacheSize,
      expiryTime: this.cacheExpiry
    };
  }

  /**
   * Preload data for common date ranges
   */
  async preloadCommonData(moduleId, apiService) {
    const commonRanges = [
      { daysBack: 30, label: 'Last 30 days' },
      { daysBack: 90, label: 'Last 90 days' },
      { daysBack: 365, label: 'Last year' }
    ];

    console.log('📦 Preloading common data for module:', moduleId);
    
    for (const range of commonRanges) {
      try {
        const data = await this.fetchWithCache(moduleId, { daysBack: range.daysBack }, apiService);
        console.log(`📦 Preloaded ${range.label} data for ${moduleId}`);
      } catch (error) {
        console.warn(`📦 Failed to preload ${range.label} data for ${moduleId}:`, error);
      }
    }
  }

  /**
   * Fetch data with caching
   */
  async fetchWithCache(moduleId, dateParams, apiService) {
    // Check cache first
    const cachedData = this.get(moduleId, dateParams);
    if (cachedData) {
      return cachedData;
    }

    // Fetch from API
    console.log('📦 Fetching fresh data for module:', moduleId);
    let data;
    
    try {
      const { startDate, endDate, daysBack } = dateParams;
      
      // Calculate actual dates for API call
      let apiStartDate, apiEndDate;
      
      if (startDate && endDate) {
        apiStartDate = startDate.toISOString().split('T')[0];
        apiEndDate = endDate.toISOString().split('T')[0];
      } else if (daysBack) {
        const endDateCalc = new Date();
        const startDateCalc = new Date();
        startDateCalc.setDate(endDateCalc.getDate() - daysBack);
        
        apiStartDate = startDateCalc.toISOString().split('T')[0];
        apiEndDate = endDateCalc.toISOString().split('T')[0];
      } else {
        // Default to last year
        const endDateCalc = new Date();
        const startDateCalc = new Date();
        startDateCalc.setDate(endDateCalc.getDate() - 365);
        
        apiStartDate = startDateCalc.toISOString().split('T')[0];
        apiEndDate = endDateCalc.toISOString().split('T')[0];
      }

      // Call appropriate API based on module
      switch (moduleId) {
        case 'ei-tech-dashboard':
          data = await apiService.getEITechDashboard(apiStartDate, apiEndDate);
          break;
        case 'srs-dashboard':
          data = await apiService.getSRSDashboard(apiStartDate, apiEndDate);
          break;
        case 'ni-tct-dashboard':
          data = await apiService.getNITCTDashboard(apiStartDate, apiEndDate);
          break;
        case 'custom-dashboard':
          data = {}; // Custom dashboard doesn't need data fetching
          break;
        default:
          throw new Error(`Unknown module: ${moduleId}`);
      }

      // Cache the data
      this.set(moduleId, dateParams, data);
      return data;
      
    } catch (error) {
      console.error('📦 Error fetching data for module:', moduleId, error);
      throw error;
    }
  }
}

// Create singleton instance
const dashboardCache = new DashboardCacheService();

export default dashboardCache; 