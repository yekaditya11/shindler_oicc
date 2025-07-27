# Dashboard Caching System

This directory contains the caching implementation for the dashboard to improve performance and reduce API calls.

## Overview

The caching system is designed to:
- Cache dashboard data to avoid repeated API calls
- Improve user experience when navigating between pages
- Reduce server load
- Provide cache management tools

## Components

### 1. Dashboard Cache Service (`dashboardCache.js`)

A singleton service that manages caching for dashboard data.

**Features:**
- Automatic cache key generation based on module ID and date parameters
- 5-minute cache expiry
- Maximum 50 cached entries with LRU eviction
- Preloading of common date ranges
- Cache statistics and management

**Key Methods:**
- `fetchWithCache(moduleId, dateParams, apiService)` - Fetch data with caching
- `get(moduleId, dateParams)` - Get cached data
- `set(moduleId, dateParams, data)` - Cache data
- `clear(moduleId, dateParams)` - Clear specific cache entry
- `clearAll()` - Clear all cache
- `getStats()` - Get cache statistics
- `preloadCommonData(moduleId, apiService)` - Preload common date ranges

### 2. Cache Manager Component (`CacheManager.js`)

A React component that provides a UI for cache management.

**Features:**
- View cache statistics
- Clear all cache
- Clear expired entries
- Cache entry list (future enhancement)

## Usage

### In Dashboard Components

```javascript
import dashboardCache from '../services/dashboardCache';

// Fetch data with caching
const data = await dashboardCache.fetchWithCache(moduleId, dateParams, ApiService);

// Clear cache for specific module/date range
dashboardCache.clear(moduleId, dateParams);

// Get cache statistics
const stats = dashboardCache.getStats();
```

### Cache Status Indicator

The dashboard includes a cache status indicator that shows whether data was loaded from cache or server:

- **Green "Cached"** - Data loaded from cache
- **Yellow "Live"** - Data loaded from server

### Cache Manager

Access the cache manager via the storage icon button in the dashboard header to:
- View cache statistics
- Clear cache entries
- Monitor cache usage

## Cache Keys

Cache keys are generated based on:
- Module ID (e.g., 'ei-tech-dashboard', 'srs-dashboard')
- Date parameters (startDate, endDate, daysBack)

Examples:
- `ei-tech-dashboard_days_30` - EI Tech dashboard for last 30 days
- `srs-dashboard_2024-01-01_2024-01-31` - SRS dashboard for specific date range

## Configuration

Cache settings can be modified in `dashboardCache.js`:

```javascript
this.cacheExpiry = 5 * 60 * 1000; // 5 minutes
this.maxCacheSize = 50; // Maximum cached entries
```

## Benefits

1. **Performance**: Faster page loads when navigating between dashboards
2. **Reduced API Calls**: Less server load and network traffic
3. **Better UX**: Instant data display for cached content
4. **Cost Savings**: Reduced API usage costs
5. **Offline Resilience**: Cached data available even with network issues

## Future Enhancements

- Cache entry list with individual management
- Cache persistence across browser sessions
- Cache warming strategies
- Cache invalidation based on data freshness
- Cache analytics and monitoring 