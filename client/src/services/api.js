/**
 * API Service for AI Safety Summarizer
 * Handles all communication with the backend API
 */

import axios from 'axios';
import requestOptimizer from '../utils/requestOptimizer';
import insightsCache from './insightsCache';

//const API_BASE_URL ='http://13.50.248.45:8001';

const API_BASE_URL ='http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // Increased to 2 minutes for large context model processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Response Error:', error);

    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.error || 'Server error occurred';
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error - please check your connection');
    } else {
      // Something else happened
      throw new Error('An unexpected error occurred');
    }
  }
);

// API Service Class
class ApiService {
  // Health check
  async healthCheck() {
    return api.get('/health');
  }

  // Removed unwanted API methods:
  // - getDashboardData (replaced by unified dashboard)
  // - getComprehensiveSummary (not needed for 4-module focus)
  // - getModuleSummary (not needed for 4-module focus)
  // - getPermitSummary (not in required 4 modules)
  // - getIncidentSummary (not in required 4 modules)
  // - getActionSummary (not in required 4 modules)
  // - getInspectionSummary (not in required 4 modules)
  // - getKPIMetrics (replaced by specific KPI endpoints)
  // Only keeping the 4 required KPI endpoints and conversational AI

  // Incident Investigation KPIs - Optimized
  async getIncidentInvestigationKPIs(customerId = null, daysBack = 90) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    // Use optimized request with caching
    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/incident-investigation-kpis`,
      { params }
    );
  }

  // Action Tracking KPIs - Optimized
  async getActionTrackingKPIs(customerId = null, daysBack = 90) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/action-tracking-kpis`,
      { params }
    );
  }

  // Driver Safety Checklist KPIs - Optimized
  async getDriverSafetyChecklistKPIs(customerId = null, daysBack = 90) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/driver-safety-checklist-kpis`,
      { params }
    );
  }

  // Observation Tracker KPIs - Optimized
  async getObservationTrackerKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/observation-tracker-kpis`,
      { params }
    );
  }

  // Equipment Asset KPIs - Optimized
  async getEquipmentAssetKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/equipment-asset-kpis`,
      { params }
    );
  }

  // Risk Assessment KPIs - Optimized
  async getRiskAssessmentKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/risk-assessment-kpis`,
      { params }
    );
  }

  // Employee Training KPIs - Optimized
  async getEmployeeTrainingKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/employee-training-kpis`,
      { params }
    );
  }

  // Fetch all KPIs for the safety dashboard - Optimized
  async getAllKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/all-safety-kpis`,
      { params }
    );
  }

  // Individual Module KPI Endpoints
  async getIncidentInvestigationModuleKPIs(customerId = null, startDate = null, endDate = null, daysBack = 365) {
    // Validate parameters - don't send null daysBack
    const params = { days_back: daysBack || 365 };
    if (customerId) params.customer_id = customerId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    // Skip cache if custom date range is used to ensure fresh data
    const skipCache = startDate && endDate;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/api/modules/incident-investigation/kpis`,
      { params, skipCache }
    );
  }

  async getRiskAssessmentModuleKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/api/modules/risk-assessment/kpis`,
      { params }
    );
  }

  async getActionTrackingModuleKPIs(customerId = null, startDate = null, endDate = null, daysBack = 365) {
    // Validate parameters - don't send null daysBack
    const params = { days_back: daysBack || 365 };
    if (customerId) params.customer_id = customerId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    // Skip cache if custom date range is used to ensure fresh data
    const skipCache = startDate && endDate;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/api/modules/action-tracking/kpis`,
      { params, skipCache }
    );
  }

  async getDriverSafetyModuleKPIs(customerId = null, startDate = null, endDate = null, daysBack = 365) {
    // Validate parameters - don't send null daysBack
    const params = { days_back: daysBack || 365 };
    if (customerId) params.customer_id = customerId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    // Skip cache if custom date range is used to ensure fresh data
    const skipCache = startDate && endDate;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/api/modules/driver-safety/kpis`,
      { params, skipCache }
    );
  }

  async getObservationTrackerModuleKPIs(customerId = null, startDate = null, endDate = null, daysBack = 365) {
    // Validate parameters - don't send null daysBack
    const params = { days_back: daysBack || 365 };
    if (customerId) params.customer_id = customerId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    // Skip cache if custom date range is used to ensure fresh data
    const skipCache = startDate && endDate;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/api/modules/observation-tracker/kpis`,
      { params, skipCache }
    );
  }

  async getEquipmentAssetModuleKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/api/modules/equipment-asset/kpis`,
      { params }
    );
  }

  async getEmployeeTrainingModuleKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/api/modules/employee-training/kpis`,
      { params }
    );
  }

  // Conversational AI Chat Methods - Updated for new ConvBI endpoint
  async startConversation(userId = 'anonymous') {
    // No longer needed for the new conversational BI system
    // Return a mock session for compatibility
    return {
      success: true,
      session_id: `convbi_${Date.now()}`,
      message: "Hello! I'm your SafetyConnect AI assistant. How can I assist you?"
    };
  }

  async sendChatMessage(message, sessionId = null, userId = 'anonymous') {
    // Use the new conversational BI endpoint
    try {
      console.log('Sending message to ConvBI:', message);
      
      const response = await api.post('/api/v1/chat', {
        question: message
      });

      console.log('ConvBI response:', response);

      // Transform the response to match the expected format
      let chartData = null;
      if (response.body?.visualization_data) {
        try {
          // Handle both object and string formats
          const rawChartData = typeof response.body.visualization_data === 'string' 
            ? JSON.parse(response.body.visualization_data)
            : response.body.visualization_data;
          
          // Sanitize the chart data to prevent object rendering issues
          chartData = this.sanitizeChartData(rawChartData);
          console.log('Processed chart data:', chartData);
        } catch (parseError) {
          console.error('Error parsing visualization data:', parseError);
          chartData = null;
        }
      }

      return {
        success: true,
        message: this.extractTextFromResponse(response.body?.final_answer) || 
                 this.extractTextFromResponse(response.body?.error_message) || 
                 'No response available',
        data_context: response.body?.query_result ? JSON.parse(response.body.query_result) : null,
        chart_data: chartData,
        sql_query: response.body?.sql_query || null,
        suggested_actions: [
          "Show me recent incidents by severity",
          "What are the top safety violations this month?",
          "Compare safety metrics across regions",
          "Show training compliance rates"
        ]
      };
    } catch (error) {
      console.error('ConvBI error:', error);
      
      // Return error in expected format
      return {
        success: false,
        message: this.extractTextFromResponse(error.message) || 'Sorry, I encountered an error processing your request. Please try again.',
        error: this.extractTextFromResponse(error.message) || error.toString()
      };
    }
  }

  async getChatHistory(sessionId) {
    // Chat history is not maintained in the new conversational BI system
    // Return empty history for compatibility
    return {
      success: true,
      history: [],
      message: "Chat history is not maintained in the conversational BI system"
    };
  }

  async clearConversation(sessionId) {
    // No conversation state to clear in the new system
    return {
      success: true,
      message: "Conversation cleared"
    };
  }

  async getProactiveInsights(sessionId) {
    // Return some safety-focused proactive insights
    return {
      success: true,
      insights: [
        "Would you like to see recent safety incident trends?",
        "Check current safety performance metrics?",
        "Analyze training completion rates by department?",
        "Review equipment inspection status?"
      ]
    };
  }

  // Module-specific chat methods - Updated to use conversational BI
  async sendModuleChatMessage(moduleName, message, sessionId = null) {
    // Enhance the message with module context for better results
    const contextualMessage = `Regarding ${moduleName} data: ${message}`;
    return this.sendChatMessage(contextualMessage, sessionId);
  }

  // AI Analysis Methods - New endpoints for individual modules
  async getIncidentInvestigationAIAnalysis(customerId = null, daysBack = 90, includeAI = true) {
    const params = { days_back: daysBack, include_ai: includeAI };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/incident-investigation`,
      {
        params,
        skipCache: false,  // Allow caching for better performance
        timeout: 120000    // Increased to 2 minutes for large context model processing
      }
    );
  }

  async getActionTrackingAIAnalysis(customerId = null, daysBack = 90, includeAI = true) {
    const params = { days_back: daysBack, include_ai: includeAI };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/action-tracking`,
      {
        params,
        skipCache: false,  // Allow caching for better performance
        timeout: 120000
      }
    );
  }

  async getDriverSafetyAIAnalysis(customerId = null, daysBack = 90, includeAI = true) {
    const params = { days_back: daysBack, include_ai: includeAI };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/driver-safety-checklists`,
      {
        params,
        skipCache: false,  // Allow caching for better performance
        timeout: 120000
      }
    );
  }

  async getObservationTrackerAIAnalysis(customerId = null, daysBack = 90, includeAI = true) {
    const params = { days_back: daysBack, include_ai: includeAI };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/observation-tracker`,
      {
        params,
        skipCache: false,  // Allow caching for better performance
        timeout: 120000  // Increased to 2 minutes for large context model processing
      }
    );
  }

  async getEquipmentAssetAIAnalysis(customerId = null, daysBack = 90, includeAI = true) {
    const params = { days_back: daysBack, include_ai: includeAI };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/equipment-asset-management`,
      { params, skipCache: true }
    );
  }

  async getRiskAssessmentAIAnalysis(customerId = null, daysBack = 90, includeAI = true) {
    const params = { days_back: daysBack, include_ai: includeAI };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/risk-assessment`,
      { params, skipCache: true }
    );
  }

  async getEmployeeTrainingAIAnalysis(customerId = null, daysBack = 90, includeAI = true) {
    const params = { days_back: daysBack, include_ai: includeAI };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/employee-training-fitness`,
      { params, skipCache: true }
    );
  }

  async getComprehensiveAIAnalysis(customerId = null, daysBack = 90, includeAI = true, modules = 'all') {
    const params = {
      days_back: daysBack,
      include_ai: includeAI,
      modules: modules
    };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/comprehensive`,
      { params }
    );
  }

  async getAIAnalysisStatus() {
    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/status`,
      { params: {} }
    );
  }

  // Submit insight feedback and get additional insights
  async submitInsightFeedback(feedbackData) {
    return api.post('/ai-analysis/feedback', feedbackData);
  }

  // Generate more insights based on feedback and existing insights
  async generateMoreInsights(requestData) {
    const module = requestData.module;
    
    // Route to appropriate endpoint based on module
    switch (module) {
      case 'ei-tech-dashboard':
        console.log('API Request: POST /api/v1/ei_tech/insights/generate-more');
        return api.post('/api/v1/ei_tech/insights/generate-more', requestData);
      case 'srs-dashboard':
        console.log('API Request: POST /api/v1/srs/insights/generate-more');
        return api.post('/api/v1/srs/insights/generate-more', requestData);
      case 'ni-tct-dashboard':
        console.log('API Request: POST /api/v1/ni_tct/insights/generate-more');
        return api.post('/api/v1/ni_tct/insights/generate-more', requestData);
      default:
        // Fallback to original endpoint for other modules
        return api.post('/ai-analysis/generate-more', requestData);
    }
  }

  // Legacy methods for backward compatibility
  async generateAIAnalysis(module, customerId = null, daysBack = 90) {
    // Map to new endpoints
    switch (module) {
      case 'incident_investigation':
        return this.getIncidentInvestigationAIAnalysis(customerId, daysBack, true);
      case 'action_tracking':
        return this.getActionTrackingAIAnalysis(customerId, daysBack, true);
      case 'driver_safety_checklists':
        return this.getDriverSafetyAIAnalysis(customerId, daysBack, true);
      case 'observation_tracker':
        return this.getObservationTrackerAIAnalysis(customerId, daysBack, true);
      case 'equipment_asset_management':
        return this.getEquipmentAssetAIAnalysis(customerId, daysBack, true);
      case 'risk_assessment':
        return this.getRiskAssessmentAIAnalysis(customerId, daysBack, true);
      case 'employee_training_fitness':
        return this.getEmployeeTrainingAIAnalysis(customerId, daysBack, true);
      default:
        throw new Error(`Unknown module: ${module}`);
    }
  }

  async generateComprehensiveAIAnalysis(customerId = null, daysBack = 90, modules = null) {
    const modulesList = modules ? modules.join(',') : 'all';
    return this.getComprehensiveAIAnalysis(customerId, daysBack, true, modulesList);
  }

  // Dashboard Management Methods
  async saveDashboard(dashboardName, charts, userId = 'anonymous') {
    return api.post('/dashboard/save', {
      dashboard_name: dashboardName,
      charts: charts,
      user_id: userId
    });
  }

  async loadDashboard(dashboardId) {
    return api.get(`/dashboard/load/${dashboardId}`);
  }

  async listDashboards(userId = 'anonymous') {
    const params = { user_id: userId };
    return api.get('/dashboard/list', { params });
  }

  // Chart Management Methods
  async addChartToDashboard(chartData, title, source = 'chat', userId = 'anonymous') {
    const response = await api.post('/dashboard/add-chart', {
      chart_data: chartData,
      title: title,
      source: source,
      user_id: userId
    });
    
    // Ensure response has success property for compatibility
    return {
      success: response.status === 'success',
      ...response
    };
  }

  async getUserCharts(userId = 'anonymous') {
    const response = await api.get(`/dashboard/charts/${userId}`);
    
    // Ensure response has success property for compatibility
    return {
      success: response.status === 'success',
      charts: response.charts || [],
      ...response
    };
  }

  async deleteChart(chartId) {
    return api.delete(`/dashboard/charts/${chartId}`);
  }

  async deleteDashboard(dashboardId, userId = 'anonymous') {
    const params = { user_id: userId };
    return api.delete(`/dashboard/dashboard/${dashboardId}`, { params });
  }

  async debugCharts(userId = 'anonymous') {
    return api.get(`/dashboard/debug/charts`, { params: { user_id: userId } });
  }

  // Generic metrics fetcher for real-time updates - Optimized
  async getMetrics(endpoint, customerId = null, daysBack = 90) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/${endpoint}`,
      { params }
    );
  }

  // Optimization utilities
  getOptimizationStats() {
    return requestOptimizer.getStats();
  }

  invalidateCache(pattern) {
    return requestOptimizer.invalidateCache(pattern);
  }

  resetOptimizer() {
    return requestOptimizer.reset();
  }

  // Dashboard endpoints for the 3 safety systems
  async getEITechDashboard(startDate = null, endDate = null, userRole = null, region = null) {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (userRole) params.user_role = userRole;
    if (region) params.region = region;

    return api.get('/dashboard/ei_tech', { params });
  }

  async getSRSDashboard(startDate = null, endDate = null, userRole = null, region = null) {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (userRole) params.user_role = userRole;
    if (region) params.region = region;

    return api.get('/dashboard/srs', { params });
  }

  async getNITCTDashboard(startDate = null, endDate = null, userRole = null, region = null) {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (userRole) params.user_role = userRole;
    if (region) params.region = region;

    return api.get('/dashboard/ni_tct', { params });
  }

  // AI Insights Methods for New Dashboards - Now with caching
  async getEITechInsights(startDate = null, endDate = null) {
    return insightsCache.fetchWithCache('ei-tech-dashboard', startDate, endDate, this);
  }

  async getSRSInsights(startDate = null, endDate = null) {
    return insightsCache.fetchWithCache('srs-dashboard', startDate, endDate, this);
  }

  async getNITCTInsights(startDate = null, endDate = null) {
    return insightsCache.fetchWithCache('ni-tct-dashboard', startDate, endDate, this);
  }

  // Direct API calls for insights (used by cache service)
  async _getEITechInsightsDirect(startDate = null, endDate = null) {
    console.log('API Request: GET /api/v1/ei_tech/insights');
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    return api.get('/api/v1/ei_tech/insights', { params });
  }

  async _getSRSInsightsDirect(startDate = null, endDate = null) {
    console.log('API Request: GET /api/v1/srs/insights');
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    return api.get('/api/v1/srs/insights', { params });
  }

  async _getNITCTInsightsDirect(startDate = null, endDate = null) {
    console.log('API Request: GET /api/v1/ni_tct/insights');
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    return api.get('/api/v1/ni_tct/insights', { params });
  }

  // Dashboard summary endpoints
  async getEITechDashboardSummary(startDate = null, endDate = null, userRole = null, region = null) {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (userRole) params.user_role = userRole;
    if (region) params.region = region;

    return api.get('/dashboard/ei_tech/summary', { params });
  }

  async getSRSDashboardSummary(startDate = null, endDate = null, userRole = null, region = null) {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (userRole) params.user_role = userRole;
    if (region) params.region = region;

    return api.get('/dashboard/srs/summary', { params });
  }

  async getNITCTDashboardSummary(startDate = null, endDate = null, userRole = null, region = null) {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (userRole) params.user_role = userRole;
    if (region) params.region = region;

    return api.get('/dashboard/ni_tct/summary', { params });
  }

  // NI TCT specific time patterns endpoint
  async getNITCTTimePatterns(startDate = null, endDate = null, userRole = null, region = null) {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (userRole) params.user_role = userRole;
    if (region) params.region = region;

    return api.get('/dashboard/ni_tct/time_patterns', { params });
  }

  // Helper to extract text from a response object or string
  extractTextFromResponse(response) {
    if (typeof response === 'string') {
      return response;
    } else if (typeof response === 'object' && response !== null) {
      // Handle various object formats that might contain text
      if ('text' in response) {
        return response.text;
      } else if ('content' in response) {
        return response.content;
      } else if ('message' in response) {
        return response.message;
      }
      // If it's an object without recognizable text property, convert to string
      return JSON.stringify(response);
    }
    return null;
  }

  // Helper to ensure chart data doesn't contain renderable objects
  sanitizeChartData(chartData) {
    if (!chartData || typeof chartData !== 'object') {
      return chartData;
    }

    const sanitized = { ...chartData };
    
    // Ensure title is properly formatted
    if (sanitized.title && typeof sanitized.title === 'object' && sanitized.title.text) {
      // Keep the object structure for ECharts but ensure it's not rendered directly
      sanitized.displayTitle = sanitized.title.text;
    } else if (typeof sanitized.title === 'string') {
      sanitized.displayTitle = sanitized.title;
    }

    console.log('Sanitized chart data:', sanitized);
    return sanitized;
  }

  // Insights Cache Management Methods
  clearInsightsCache(module = null, startDate = null, endDate = null) {
    if (module) {
      insightsCache.clear(module, startDate, endDate);
    } else {
      insightsCache.clearAll();
    }
  }

  getInsightsCacheStats() {
    return insightsCache.getStats();
  }

  // File Upload Methods
  async uploadAndAnalyzeFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/files/upload-analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'File upload failed');
      }

      return await response.json();
    } catch (error) {
      console.error('File upload error:', error);
      throw error;
    }
  }
}

// Create singleton instance
const apiService = new ApiService();

// Add requestOptimizer to window for debugging
if (typeof window !== 'undefined') {
  window.requestOptimizer = requestOptimizer;
}

// Export singleton instance
export default apiService;

// Export individual methods for convenience - all safety KPI endpoints, conversational AI, and AI analysis
export const {
  healthCheck,
  getIncidentInvestigationKPIs,
  getActionTrackingKPIs,
  getDriverSafetyChecklistKPIs,
  getObservationTrackerKPIs,
  getEquipmentAssetKPIs,
  getRiskAssessmentKPIs,
  getEmployeeTrainingKPIs,
  getAllKPIs,
  // Module-specific KPI endpoints
  getIncidentInvestigationModuleKPIs,
  getRiskAssessmentModuleKPIs,
  getActionTrackingModuleKPIs,
  getDriverSafetyModuleKPIs,
  getObservationTrackerModuleKPIs,
  getEquipmentAssetModuleKPIs,
  getEmployeeTrainingModuleKPIs,
  // Chat methods
  startConversation,
  sendChatMessage,
  sendModuleChatMessage,
  getChatHistory,
  clearConversation,
  getProactiveInsights,
  // AI Analysis methods
  generateAIAnalysis,
  generateComprehensiveAIAnalysis,
  getIncidentInvestigationAIAnalysis,
  getActionTrackingAIAnalysis,
  getDriverSafetyAIAnalysis,
  getObservationTrackerAIAnalysis,
  getEquipmentAssetAIAnalysis,
  getRiskAssessmentAIAnalysis,
  getEmployeeTrainingAIAnalysis,
  getComprehensiveAIAnalysis,
  getAIAnalysisStatus,
  // Dashboard methods
  getEITechDashboard,
  getSRSDashboard,
  getNITCTDashboard,
  getEITechDashboardSummary,
  getSRSDashboardSummary,
  getNITCTDashboardSummary,
  getNITCTTimePatterns,
  // AI Insights methods
  getEITechInsights,
  getSRSInsights,
  getNITCTInsights,
  // Insights Cache Management
  clearInsightsCache,
  getInsightsCacheStats,
  // File Upload methods
  uploadAndAnalyzeFile,
} = apiService;

// Additional exports for the new dashboard
export const fetchAllKPIs = (customerId = null, daysBack = 365) =>
  apiService.getAllKPIs(customerId, daysBack);

export const fetchIncidentKPIs = (customerId = null, daysBack = 365) =>
  apiService.getIncidentInvestigationKPIs(customerId, daysBack);

export const fetchDriverSafetyKPIs = (customerId = null, daysBack = 365) =>
  apiService.getDriverSafetyChecklistKPIs(customerId, daysBack);

export const fetchObservationKPIs = (customerId = null, daysBack = 365) =>
  apiService.getObservationTrackerKPIs(customerId, daysBack);

export const fetchActionTrackingKPIs = (customerId = null, daysBack = 365) =>
  apiService.getActionTrackingKPIs(customerId, daysBack);

export const fetchEquipmentAssetKPIs = (customerId = null, daysBack = 365) =>
  apiService.getEquipmentAssetKPIs(customerId, daysBack);

export const fetchRiskAssessmentKPIs = (customerId = null, daysBack = 365) =>
  apiService.getRiskAssessmentKPIs(customerId, daysBack);

export const fetchEmployeeTrainingKPIs = (customerId = null, daysBack = 365) =>
  apiService.getEmployeeTrainingKPIs(customerId, daysBack);
