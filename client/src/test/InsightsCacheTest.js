/**
 * Simple test for Insights Cache functionality
 * Run this in browser console to test caching
 */

import insightsCache from '../services/insightsCache';
import ApiService from '../services/api';

// Mock API service for testing
const mockApiService = {
  _getEITechInsightsDirect: async (startDate, endDate) => {
    console.log('🔍 Mock API call for EI Tech insights');
    return {
      status: 'success',
      insights: [
        'Test insight 1',
        'Test insight 2',
        'Test insight 3'
      ],
      metadata: {
        generated_at: new Date().toISOString(),
        data_period: `${startDate} to ${endDate}`
      }
    };
  }
};

// Test function
export const testInsightsCache = async () => {
  console.log('🧪 Starting Insights Cache Test...');
  
  try {
    // Test 1: First call (should hit API)
    console.log('\n📞 Test 1: First API call');
    const result1 = await insightsCache.fetchWithCache('ei-tech-dashboard', '2024-01-01', '2024-01-31', mockApiService);
    console.log('Result 1:', result1);
    console.log('From cache:', result1.fromCache);
    
    // Test 2: Second call (should hit cache)
    console.log('\n📞 Test 2: Second call (should be cached)');
    const result2 = await insightsCache.fetchWithCache('ei-tech-dashboard', '2024-01-01', '2024-01-31', mockApiService);
    console.log('Result 2:', result2);
    console.log('From cache:', result2.fromCache);
    
    // Test 3: Different date range (should hit API)
    console.log('\n📞 Test 3: Different date range');
    const result3 = await insightsCache.fetchWithCache('ei-tech-dashboard', '2024-02-01', '2024-02-28', mockApiService);
    console.log('Result 3:', result3);
    console.log('From cache:', result3.fromCache);
    
    // Test 4: Cache stats
    console.log('\n📊 Cache Stats:');
    console.log(insightsCache.getStats());
    
    // Test 5: Clear cache
    console.log('\n🗑️ Clearing cache...');
    insightsCache.clearAll();
    console.log('Cache cleared');
    
    // Test 6: Call after clearing (should hit API)
    console.log('\n📞 Test 6: Call after clearing cache');
    const result6 = await insightsCache.fetchWithCache('ei-tech-dashboard', '2024-01-01', '2024-01-31', mockApiService);
    console.log('Result 6:', result6);
    console.log('From cache:', result6.fromCache);
    
    console.log('\n✅ Insights Cache Test completed successfully!');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
};

// Export for use in browser console
if (typeof window !== 'undefined') {
  window.testInsightsCache = testInsightsCache;
} 