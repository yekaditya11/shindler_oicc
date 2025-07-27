/**
 * Insights Cache Service
 * Simple caching for AI insights to avoid regenerating them every time
 */

class InsightsCacheService {
  constructor() {
    this.cache = new Map();
    this.cacheExpiry = 30 * 60 * 1000; // 30 minutes in milliseconds
    this.maxCacheSize = 20; // Maximum number of cached insights
  }

  /**
   * Generate cache key for insights
   */
  generateCacheKey(module, startDate, endDate) {
    const dateKey = startDate && endDate ? `${startDate}_${endDate}` : 'default';
    return `${module}_insights_${dateKey}`;
  }

  /**
   * Get cached insights if available and not expired
   */
  get(module, startDate, endDate) {
    const key = this.generateCacheKey(module, startDate, endDate);
    const cachedItem = this.cache.get(key);
    
    if (!cachedItem) {
      console.log('🤖 Insights cache miss for:', key);
      return null;
    }

    const now = Date.now();
    if (now - cachedItem.timestamp > this.cacheExpiry) {
      console.log('🤖 Insights cache expired for:', key);
      this.cache.delete(key);
      return null;
    }

    console.log('🤖 Insights cache hit for:', key);
    return cachedItem.data;
  }

  /**
   * Store insights in cache with timestamp
   */
  set(module, startDate, endDate, data) {
    const key = this.generateCacheKey(module, startDate, endDate);
    
    // Check cache size and remove oldest items if needed
    if (this.cache.size >= this.maxCacheSize) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
      console.log('🤖 Removed oldest insights cache entry:', oldestKey);
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
    
    console.log('🤖 Cached insights for:', key);
  }

  /**
   * Clear specific insights cache entry
   */
  clear(module, startDate, endDate) {
    const key = this.generateCacheKey(module, startDate, endDate);
    this.cache.delete(key);
    console.log('🤖 Cleared insights cache for:', key);
  }

  /**
   * Clear all insights cache
   */
  clearAll() {
    this.cache.clear();
    console.log('🤖 Cleared all insights cache');
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxCacheSize,
      expiryMinutes: this.cacheExpiry / (60 * 1000)
    };
  }

  /**
   * Fetch insights with caching
   */
  async fetchWithCache(module, startDate, endDate, apiService) {
    // Check cache first
    const cachedData = this.get(module, startDate, endDate);
    if (cachedData) {
      return cachedData;
    }

    // Fetch from API
    let insightsData;
    switch (module) {
      case 'ei-tech-dashboard':
        insightsData = await apiService._getEITechInsightsDirect(startDate, endDate);
        break;
      case 'srs-dashboard':
        insightsData = await apiService._getSRSInsightsDirect(startDate, endDate);
        break;
      case 'ni-tct-dashboard':
        insightsData = await apiService._getNITCTInsightsDirect(startDate, endDate);
        break;
      default:
        throw new Error(`Unknown module: ${module}`);
    }

    // Cache the result
    this.set(module, startDate, endDate, insightsData);

    return insightsData;
  }
}

// Create singleton instance
const insightsCache = new InsightsCacheService();

export default insightsCache; 