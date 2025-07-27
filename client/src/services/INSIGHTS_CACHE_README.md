# Insights Caching System

## Overview

The Insights Caching System is a simple and efficient way to cache AI-generated insights to avoid regenerating them every time. This improves performance and reduces API calls to the AI service.

## Features

- **Simple Caching**: Cache insights for 30 minutes by default
- **Module-Specific**: Each module (EI Tech, SRS, NI TCT) has separate cache entries
- **Date Range Aware**: Different date ranges create separate cache entries
- **Cache Management**: View cache stats and clear cache when needed
- **Visual Indicators**: Shows when insights are loaded from cache vs fresh generation

## How It Works

### Cache Key Generation
Cache keys are generated based on:
- Module name (e.g., 'ei-tech-dashboard', 'srs-dashboard', 'ni-tct-dashboard')
- Date range (start date and end date)

Example cache keys:
- `ei-tech-dashboard_insights_2024-01-01_2024-01-31`
- `srs-dashboard_insights_2024-02-01_2024-02-28`

### Cache Expiry
- Default expiry: 30 minutes
- Maximum cache size: 20 entries
- LRU (Least Recently Used) eviction when cache is full

## Usage

### Automatic Caching
The caching is automatic - when you call the insights API methods, they will:
1. Check if data exists in cache
2. If cached and not expired, return cached data
3. If not cached or expired, fetch from API and cache the result

```javascript
// These methods now automatically use caching
const insights = await ApiService.getEITechInsights('2024-01-01', '2024-01-31');
const insights = await ApiService.getSRSInsights('2024-01-01', '2024-01-31');
const insights = await ApiService.getNITCTInsights('2024-01-01', '2024-01-31');
```

### Cache Management

```javascript
// Get cache statistics
const stats = ApiService.getInsightsCacheStats();
console.log(stats);
// Output: { size: 5, maxSize: 20, expiryMinutes: 30 }

// Clear specific cache entry
ApiService.clearInsightsCache('ei-tech-dashboard', '2024-01-01', '2024-01-31');

// Clear all cache
ApiService.clearInsightsCache();
```

### Visual Indicators

The insights panel shows:
- **"Cached" chip**: When insights are loaded from cache
- **Cache management button**: Storage icon in the header
- **Cache statistics panel**: Shows cache size and expiry time

## Benefits

1. **Performance**: Faster loading of previously generated insights
2. **Cost Savings**: Reduces AI API calls and associated costs
3. **Better UX**: Instant display of cached insights
4. **Reduced Server Load**: Less strain on the AI service
5. **Offline Resilience**: Cached data available even with network issues

## Configuration

Cache settings can be modified in `insightsCache.js`:

```javascript
this.cacheExpiry = 30 * 60 * 1000; // 30 minutes
this.maxCacheSize = 20; // Maximum cached entries
```

## Testing

Run the test function in browser console:

```javascript
// Import and run the test
import { testInsightsCache } from './test/InsightsCacheTest.js';
testInsightsCache();
```

## Troubleshooting

### Cache Not Working
1. Check browser console for cache-related logs
2. Verify cache key generation
3. Check if cache is being cleared unexpectedly

### Force Fresh Data
To force fresh insights generation:
1. Click the storage icon in insights panel
2. Click the clear cache button
3. Or use `ApiService.clearInsightsCache()` in console

### Cache Stats
Monitor cache performance:
```javascript
console.log(ApiService.getInsightsCacheStats());
```

## Integration

The caching system integrates seamlessly with:
- Unified Safety Dashboard
- AI Insights Panel
- All three safety modules (EI Tech, SRS, NI TCT)
- Date range filtering
- Module switching 