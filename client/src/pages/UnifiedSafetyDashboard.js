/**
 * Unified Safety Dashboard
 * Single dashboard with module dropdown, AI analysis toggle, and integrated chatbot
 */

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Typography,
  FormControl,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import AIIcon from '@mui/icons-material/Psychology';
import RefreshIcon from '@mui/icons-material/Refresh';
import SecurityIcon from '@mui/icons-material/Security';
import VisibilityIcon from '@mui/icons-material/Visibility';
import DashboardIcon from '@mui/icons-material/Dashboard';
import UploadIcon from '@mui/icons-material/CloudUpload';
import AssessmentIcon from '@mui/icons-material/Assessment';
import StorageIcon from '@mui/icons-material/Storage';
import { motion, AnimatePresence } from 'framer-motion';

// Import components
import ErrorBoundary from '../components/common/ErrorBoundary';
import DatePickerFilter from '../components/filters/DatePickerFilter';
import SafetyConnectLayout from '../components/layout/SafetyConnectLayout';

// Import chart components (removed unused ones)

// Import custom dashboard
import DashboardManager from '../components/dashboard/DashboardManager';

// Import new dashboard components
import EITechDashboardCharts from '../components/charts/EITechDashboardCharts';
import SRSDashboardCharts from '../components/charts/SRSDashboardCharts';
import NITCTDashboardCharts from '../components/charts/NITCTDashboardCharts';

// Import unified insights panel
import UnifiedInsightsPanel from '../components/insights/UnifiedInsightsPanel';

// Import floating AI assistant
import FloatingAIAssistant from '../components/common/FloatingAIAssistant';



// Import chart resize handler
import { ChartResizeHandler } from '../utils/chartResizeHandler';

// Import API service
import ApiService from '../services/api';

// Import dashboard cache service
import dashboardCache from '../services/dashboardCache';

// All available modules
const ALL_SAFETY_MODULES = [
  {
    id: 'ei-tech-dashboard',
    label: 'Safety Dashboard',
    icon: SecurityIcon,
    color: '#1e40af'
  },
  {
    id: 'srs-dashboard',
    label: 'Safety Dashboard',
    icon: SecurityIcon,
    color: '#7c3aed'
  },
  {
    id: 'ni-tct-dashboard',
    label: 'Safety Dashboard',
    icon: VisibilityIcon,
    color: '#0284c7'
  },
  {
    id: 'custom-dashboard',
    label: 'Custom Dashboard',
    icon: DashboardIcon,
    color: '#7c3aed'
  }
];

// Function to get available modules based on file analysis
const getAvailableModules = (availableDashboards = null) => {
  console.log('🔍 getAvailableModules called with:', availableDashboards);
  
  if (!availableDashboards) {
    // If no file analysis, show all modules
    console.log('📋 No availableDashboards provided, showing all modules');
    return ALL_SAFETY_MODULES;
  }
  
  // Filter modules based on available dashboards from file analysis
  const filteredModules = ALL_SAFETY_MODULES.filter(module => 
    availableDashboards.includes(module.id)
  );
  
  console.log('📋 Filtered modules:', filteredModules.map(m => m.id));
  return filteredModules;
};

const UnifiedSafetyDashboard = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Get file analysis data from location state
  const fileAnalysis = location.state?.fileAnalysis;
  const availableDashboards = location.state?.availableDashboards;

  console.log('🏠 UnifiedSafetyDashboard - Location state:', {
    fileAnalysis: !!fileAnalysis,
    fileType: fileAnalysis?.file_type,
    availableDashboards: availableDashboards,
    fullFileAnalysis: fileAnalysis
  });

  // Fallback: Try to get availableDashboards from localStorage if not in location state
  const getAvailableDashboards = () => {
    if (availableDashboards) {
      // Store in localStorage for future use
      localStorage.setItem('availableDashboards', JSON.stringify(availableDashboards));
      return availableDashboards;
    }
    
    // Try to get from localStorage
    const stored = localStorage.getItem('availableDashboards');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        console.log('📦 Retrieved availableDashboards from localStorage:', parsed);
        return parsed;
      } catch (e) {
        console.warn('Failed to parse availableDashboards from localStorage:', e);
      }
    }
    
    return null;
  };

  const finalAvailableDashboards = getAvailableDashboards();

  // Get available modules based on file analysis
  const SAFETY_MODULES = getAvailableModules(finalAvailableDashboards);

  // State management
  const [selectedModule, setSelectedModule] = useState(
    SAFETY_MODULES.length > 0 ? SAFETY_MODULES[0].id : 'ei-tech-dashboard'
  );
  const [aiAnalysisEnabled, setAiAnalysisEnabled] = useState(false);
  const [moduleData, setModuleData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dateRange, setDateRange] = useState({
    startDate: null,
    endDate: null,
    daysBack: 365
  });

  // AI Analysis state
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState(null);

  // Feedback state - tracks feedback for each insight by index
  const [insightFeedback, setInsightFeedback] = useState({});

  // State for generating more insights
  const [loadingMoreInsights, setLoadingMoreInsights] = useState(false);

  // State for insights panel expansion
  const [insightsPanelExpanded, setInsightsPanelExpanded] = useState(false);

  // State to force chart re-render when AI panel toggles
  const [chartRenderKey, setChartRenderKey] = useState(0);



  // Chart resize handler reference
  const chartResizeHandlerRef = useRef(null);

  // Effect to handle changes in availableDashboards and update selectedModule accordingly
  useEffect(() => {
    console.log('🔄 useEffect: availableDashboards changed:', finalAvailableDashboards);
    const currentModules = getAvailableModules(finalAvailableDashboards);
    
    // If current selected module is not in available modules, select the first available one
    if (currentModules.length > 0 && !currentModules.find(m => m.id === selectedModule)) {
      console.log('🔄 Updating selectedModule from', selectedModule, 'to', currentModules[0].id);
      setSelectedModule(currentModules[0].id);
    }
  }, [finalAvailableDashboards, selectedModule]);

  // Effect to handle direct dashboard access (no file upload)
  useEffect(() => {
    // If no file analysis and no stored dashboards, this is a direct access
    if (!fileAnalysis && !finalAvailableDashboards) {
      console.log('🚀 Direct dashboard access detected - showing all available dashboards');
      // Store all available dashboards in localStorage for consistency
      const allDashboards = ['ei-tech-dashboard', 'srs-dashboard', 'ni-tct-dashboard', 'custom-dashboard'];
      localStorage.setItem('availableDashboards', JSON.stringify(allDashboards));
    }
    
    // If we have file analysis with a specific type, ensure we only show relevant dashboards
    if (fileAnalysis && fileAnalysis.file_type && fileAnalysis.file_type !== 'unknown') {
      console.log('📁 File analysis detected:', fileAnalysis.file_type);
      console.log('📁 Available dashboards from analysis:', fileAnalysis.available_dashboards);
      
      // Store the specific dashboards for this file type
      if (fileAnalysis.available_dashboards) {
        localStorage.setItem('availableDashboards', JSON.stringify(fileAnalysis.available_dashboards));
        console.log('📁 Stored specific dashboards for file type:', fileAnalysis.file_type);
      }
    }
  }, [fileAnalysis, finalAvailableDashboards]);

  // Initialize chart resize handler and global event listeners
  useEffect(() => {
    // Initialize chart resize handler
    if (!chartResizeHandlerRef.current) {
      chartResizeHandlerRef.current = new ChartResizeHandler();
    }

    // Global event listeners for chart resizing
    const handleChartAddition = () => {
      console.log('UnifiedSafetyDashboard: Chart addition detected, triggering resize');
      setTimeout(() => {
        if (chartResizeHandlerRef.current) {
          chartResizeHandlerRef.current.resizeDashboardCharts();
        }
      }, 200);
    };

    const handleDashboardUpdate = () => {
      console.log('UnifiedSafetyDashboard: Dashboard update detected, triggering resize');
      setTimeout(() => {
        if (chartResizeHandlerRef.current) {
          chartResizeHandlerRef.current.resizeDashboardCharts();
        }
      }, 200);
    };

    // Add global event listeners
    window.addEventListener('chart-added', handleChartAddition);
    window.addEventListener('dashboard-update', handleDashboardUpdate);

    // Initial chart resize after page load
    setTimeout(() => {
      if (chartResizeHandlerRef.current) {
        chartResizeHandlerRef.current.resizeDashboardCharts();
      }
    }, 500);

    return () => {
      window.removeEventListener('chart-added', handleChartAddition);
      window.removeEventListener('dashboard-update', handleDashboardUpdate);
    };
  }, []);

  // Get current module info
  const currentModule = SAFETY_MODULES.find(m => m.id === selectedModule);



  // Fetch module data with caching
  const fetchModuleData = async (moduleId, dateParams) => {
    console.log('🔄 Fetching data for module:', moduleId, 'with date params:', dateParams);
    
    // Custom dashboard doesn't need data fetching
    if (moduleId === 'custom-dashboard') {
      setLoading(false);
      setModuleData({}); // Set empty data to indicate loaded
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Use cache service to fetch data
      const data = await dashboardCache.fetchWithCache(moduleId, dateParams, ApiService);
      
      // Check if this is still the current module (prevent race conditions)
      if (moduleId === selectedModule) {
        setModuleData(data?.data || data);
        console.log('✅ Data fetched successfully for', moduleId, '- Data received:', data ? 'Yes' : 'No');
      } else {
        console.log('🔄 Ignoring data for', moduleId, '- module changed to', selectedModule);
      }
    } catch (err) {
      console.error(`❌ Error fetching ${moduleId} data:`, err);
      if (moduleId === selectedModule) {
        setError(`Failed to load ${currentModule?.label || moduleId} data. Please try again.`);
      }
    } finally {
      if (moduleId === selectedModule) {
        setLoading(false);
      }
    }
  };



  // Load data when module or date range changes
  useEffect(() => {
    console.log('🔄 useEffect triggered - Module:', selectedModule, 'DateRange:', dateRange);
    
    // Add a cleanup flag to prevent race conditions
    let isCancelled = false;
    
    const loadData = async () => {
      if (isCancelled) return;
      await fetchModuleData(selectedModule, dateRange);
    };
    
    loadData();
    
    // Cleanup function to cancel if effect runs again
    return () => {
      isCancelled = true;
    };
  }, [selectedModule, dateRange]);

  // Preload cache for other modules in background - DISABLED to prevent unnecessary API calls
  useEffect(() => {
    // Configuration: Set to false to disable preloading entirely
    const ENABLE_PRELOADING = false;
    
    if (!ENABLE_PRELOADING) {
      console.log('📦 Preloading disabled by configuration');
      return;
    }
    
    // Only preload if we have file analysis and multiple available dashboards
    if (!fileAnalysis || !finalAvailableDashboards || finalAvailableDashboards.length <= 1) {
      console.log('📦 Skipping preload - no file analysis or single dashboard only');
      return;
    }

    const preloadOtherModules = async () => {
      // Only preload modules that are actually available based on file analysis
      const availableModules = finalAvailableDashboards.filter(dashboard => 
        dashboard !== 'custom-dashboard' && dashboard !== selectedModule
      );
      
      console.log('📦 Preloading cache for available modules only:', availableModules);
      
      for (const moduleId of availableModules) {
        try {
          await dashboardCache.preloadCommonData(moduleId, ApiService);
        } catch (error) {
          console.warn(`📦 Failed to preload ${moduleId}:`, error);
        }
      }
    };

    // Preload after a short delay to not interfere with current module loading
    const timeoutId = setTimeout(preloadOtherModules, 2000);
    
    return () => clearTimeout(timeoutId);
  }, [selectedModule, fileAnalysis, finalAvailableDashboards]);

  // Fetch AI analysis when module data changes and AI is enabled
  useEffect(() => {
    console.log('🤖 AI useEffect triggered:', { aiAnalysisEnabled, hasModuleData: !!moduleData, selectedModule });
    if (aiAnalysisEnabled && moduleData) {
      console.log('🤖 Auto-fetching AI analysis due to data change');
      fetchAIAnalysis(selectedModule, moduleData);
    }
  }, [moduleData, aiAnalysisEnabled]); // Removed selectedModule to prevent duplicate calls

  // Handle chart resizing when insights panel toggles
  useEffect(() => {
    // Optimized resize handling with proper timing
    const triggerResize = () => {
      // Immediate notification for layout change start
      requestAnimationFrame(() => {
        window.dispatchEvent(new CustomEvent('ai-panel-toggle', {
          detail: {
            insightsPanelOpen: aiAnalysisEnabled,
            phase: 'start'
          }
        }));
      });

      // Resize during animation (mid-point)
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
        window.dispatchEvent(new CustomEvent('ai-panel-toggle', {
          detail: {
            insightsPanelOpen: aiAnalysisEnabled,
            phase: 'mid'
          }
        }));
      }, 200); // Half of animation duration

      // Final resize after animation completes
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
        window.dispatchEvent(new CustomEvent('ai-panel-toggle', {
          detail: {
            insightsPanelOpen: aiAnalysisEnabled,
            phase: 'complete'
          }
        }));
      }, 450); // Slightly after animation duration (400ms)
    };

    triggerResize();
  }, [aiAnalysisEnabled]);

  // Handle module change
  const handleModuleChange = (event) => {
    const newModule = event.target.value;
    setSelectedModule(newModule);
    setModuleData(null);
    // Reset feedback and loading states when module changes
    setInsightFeedback({});
    setLoadingMoreInsights(false);
  };

  // Handle AI toggle - Show/hide AI insights card inline
  const handleAIToggle = (eventOrBoolean) => {
    // Handle both event (from switch) and boolean (from floating button)
    const isEnabled = typeof eventOrBoolean === 'boolean'
      ? eventOrBoolean
      : eventOrBoolean.target.checked;

    console.log('🤖 AI Toggle clicked:', isEnabled);
    console.log('🤖 Current moduleData:', moduleData ? 'Available' : 'Not available');
    console.log('🤖 Current selectedModule:', selectedModule);

    setAiAnalysisEnabled(isEnabled);

    // Force chart re-render by updating key
    setChartRenderKey(prev => prev + 1);

    // If enabling AI, fetch AI analysis for current module
    if (isEnabled && moduleData) {
      console.log('🤖 Fetching AI analysis...');
      fetchAIAnalysis(selectedModule, moduleData);
    } else if (isEnabled && !moduleData) {
      console.log('🤖 AI enabled but no module data available yet');
    }

    // Improved event dispatch for layout changes
    requestAnimationFrame(() => {
      // Notify about AI panel toggle with detailed information
      const responsiveWidth = isEnabled ? '40%' : '0%';
      window.dispatchEvent(new CustomEvent('ai-panel-toggle', {
        detail: {
          insightsPanelOpen: isEnabled,
          phase: 'start',
          panelWidth: responsiveWidth
        }
      }));

      // Also dispatch legacy event for backward compatibility
      window.dispatchEvent(new CustomEvent('chatbot-toggle', {
        detail: { insightsPanelOpen: isEnabled }
      }));
    });
  };

  // Handle date range change
  const handleDateRangeChange = (newDateRange) => {
    console.log('📅 Date Range Changed:', newDateRange);
    setDateRange(newDateRange);
  };

  // Track last AI analysis call to prevent duplicates
  const lastAiCallRef = useRef({ moduleId: null, timestamp: 0 });

  // Fetch AI Analysis for current module
  const fetchAIAnalysis = async (moduleId, data) => {
    console.log('🤖 fetchAIAnalysis called:', { moduleId, hasData: !!data });
    
    // Prevent duplicate calls within 2 seconds for the same module
    const now = Date.now();
    const timeSinceLastCall = now - lastAiCallRef.current.timestamp;
    
    if (lastAiCallRef.current.moduleId === moduleId && timeSinceLastCall < 2000) {
      console.log('🤖 Skipping duplicate AI call for', moduleId, '(called', timeSinceLastCall, 'ms ago)');
      return;
    }
    
    // Update last call tracking
    lastAiCallRef.current = { moduleId, timestamp: now };
    
    setAiLoading(true);
    setAiError(null);
    // Reset feedback and loading states when fetching new analysis
    setInsightFeedback({});
    setLoadingMoreInsights(false);

    try {
      const { startDate, endDate, daysBack } = dateRange;
      
      // Calculate actual dates for AI insights API
      let apiStartDate, apiEndDate;
      
      if (startDate && endDate) {
        // Custom date range - use provided dates
        apiStartDate = startDate.toISOString().split('T')[0];
        apiEndDate = endDate.toISOString().split('T')[0];
      } else if (daysBack) {
        // Quick date range - calculate dates from daysBack
        const endDateCalc = new Date();
        const startDateCalc = new Date();
        startDateCalc.setDate(endDateCalc.getDate() - daysBack);
        
        apiStartDate = startDateCalc.toISOString().split('T')[0];
        apiEndDate = endDateCalc.toISOString().split('T')[0];
      } else {
        // Default to last year if no dates provided
        const endDateCalc = new Date();
        const startDateCalc = new Date();
        startDateCalc.setDate(endDateCalc.getDate() - 365);
        
        apiStartDate = startDateCalc.toISOString().split('T')[0];
        apiEndDate = endDateCalc.toISOString().split('T')[0];
      }
      
      console.log('🤖 AI API call parameters:', { moduleId, apiStartDate, apiEndDate });

      let aiData;
      switch (moduleId) {
        case 'ei-tech-dashboard':
          aiData = await ApiService.getEITechInsights(apiStartDate, apiEndDate);
          break;
        case 'srs-dashboard':
          aiData = await ApiService.getSRSInsights(apiStartDate, apiEndDate);
          break;
        case 'ni-tct-dashboard':
          aiData = await ApiService.getNITCTInsights(apiStartDate, apiEndDate);
          break;
        case 'global-dashboard':
          const apiDaysBack = daysBack || 365;
          aiData = await ApiService.generateComprehensiveAIAnalysis(null, apiDaysBack);
          break;
        case 'incident-investigation':
          const apiDaysBack2 = daysBack || 365;
          aiData = await ApiService.getIncidentInvestigationAIAnalysis(null, apiDaysBack2, true);
          break;
        case 'action-tracking':
          const apiDaysBack3 = daysBack || 365;
          aiData = await ApiService.getActionTrackingAIAnalysis(null, apiDaysBack3, true);
          break;
        case 'driver-safety':
          const apiDaysBack4 = daysBack || 365;
          aiData = await ApiService.getDriverSafetyAIAnalysis(null, apiDaysBack4, true);
          break;
        case 'observation-tracker':
          const apiDaysBack5 = daysBack || 365;
          aiData = await ApiService.getObservationTrackerAIAnalysis(null, apiDaysBack5, true);
          break;
        case 'equipment-asset':
          const apiDaysBack6 = daysBack || 365;
          aiData = await ApiService.getEquipmentAssetAIAnalysis(null, apiDaysBack6, true);
          break;
        case 'employee-training':
          const apiDaysBack7 = daysBack || 365;
          aiData = await ApiService.getEmployeeTrainingAIAnalysis(null, apiDaysBack7, true);
          break;
        case 'risk-assessment':
          const apiDaysBack8 = daysBack || 365;
          aiData = await ApiService.getRiskAssessmentAIAnalysis(null, apiDaysBack8, true);
          break;
        default:
          throw new Error(`AI analysis not available for module: ${moduleId}`);
      }

      console.log('🤖 AI API response:', aiData);
      const analysisData = aiData?.data || aiData?.ai_analysis || aiData;
      console.log('🤖 Setting AI analysis:', analysisData);
      
      setAiAnalysis(analysisData);
    } catch (err) {
      console.error(`🤖 Error fetching AI analysis for ${moduleId}:`, err);
      setAiError(`Failed to load AI insights. Please try again.`);
    } finally {
      setAiLoading(false);
    }
  };

  // Handle refresh
  const handleRefresh = () => {
    // Clear cache for current module and date range
    dashboardCache.clear(selectedModule, dateRange);
    console.log('🔄 Cache cleared for module:', selectedModule);
    
    fetchModuleData(selectedModule, dateRange);
    if (aiAnalysisEnabled) {
      fetchAIAnalysis(selectedModule, moduleData);
    }
  };

  // Handle insight feedback
  const handleInsightFeedback = async (insightIndex, feedbackType, event) => {
    try {
      // Prevent event bubbling to avoid triggering other handlers
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }

      // Update local state immediately for responsive UI
      setInsightFeedback(prev => ({
        ...prev,
        [insightIndex]: feedbackType
      }));

      // Get the insight text for the API call
      const insight = aiAnalysis?.insights?.[insightIndex];
      
      // Comprehensive safety check for insight text
      let insightText = '';
      if (typeof insight === 'string') {
        insightText = insight;
      } else if (insight && typeof insight === 'object') {
        if (typeof insight.text === 'string') {
          insightText = insight.text;
        } else if (insight.text && typeof insight.text === 'object') {
          // Handle nested objects
          insightText = JSON.stringify(insight.text);
        } else {
          insightText = JSON.stringify(insight);
        }
      } else {
        insightText = String(insight || 'No insight available');
      }

      if (!insightText) {
        console.error('No insight text found for index:', insightIndex);
        return;
      }

      // Send feedback to backend
      const feedbackData = {
        module: selectedModule,
        insight_index: insightIndex,
        insight_text: insightText,
        feedback_type: feedbackType,
        timestamp: new Date().toISOString()
      };

      console.log('📝 Sending insight feedback:', feedbackData);
      console.log('📝 Current loading state before feedback:', loading);
      console.log('📝 Current aiLoading state before feedback:', aiLoading);

      // Call API to submit feedback and potentially get more insights
      const response = await ApiService.submitInsightFeedback(feedbackData);

      console.log('📝 Feedback response received:', response);
      console.log('📝 Current loading state after feedback:', loading);
      console.log('📝 Current aiLoading state after feedback:', aiLoading);

      if (response?.additional_insights) {
        // If the API returns additional insights based on feedback, update the analysis
        setAiAnalysis(prev => ({
          ...prev,
          insights: [...(prev?.insights || []), ...response.additional_insights]
        }));
        console.log('✨ Added additional insights based on feedback:', response.additional_insights);
      }

    } catch (error) {
      console.error('Error submitting insight feedback:', error);
      // Revert the feedback state on error
      setInsightFeedback(prev => {
        const newState = { ...prev };
        delete newState[insightIndex];
        return newState;
      });
    }
  };

  // Handle generating more insights based on feedback
  const handleGenerateMoreInsights = async (event) => {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }

    if (!aiAnalysis?.insights || loadingMoreInsights) return;

    setLoadingMoreInsights(true);

    try {
      console.log('🔄 Generating more insights based on feedback...');

      // Get positive feedback insights to use as examples
      const positiveInsights = aiAnalysis.insights
        .map((insight, index) => {
          // Safe text extraction
          let text = '';
          if (typeof insight === 'string') {
            text = insight;
          } else if (insight && typeof insight === 'object') {
            if (typeof insight.text === 'string') {
              text = insight.text;
            } else {
              text = JSON.stringify(insight.text || insight);
            }
          } else {
            text = String(insight || '');
          }
          
          return {
            text,
            feedback: insightFeedback[index],
            index
          };
        })
        .filter(item => item.feedback === 'positive')
        .map(item => item.text);

      // Get all existing insights to avoid duplicates
      const existingInsights = aiAnalysis.insights.map(insight => {
        if (typeof insight === 'string') {
          return insight;
        } else if (insight && typeof insight === 'object') {
          if (typeof insight.text === 'string') {
            return insight.text;
          } else {
            return JSON.stringify(insight.text || insight);
          }
        } else {
          return String(insight || '');
        }
      });

      // Calculate dates for consistent analysis period
      const { startDate, endDate, daysBack } = dateRange;
      let apiStartDate, apiEndDate;
      
      if (startDate && endDate) {
        // Custom date range - use provided dates
        apiStartDate = startDate.toISOString().split('T')[0];
        apiEndDate = endDate.toISOString().split('T')[0];
      } else if (daysBack) {
        // Quick date range - calculate dates from daysBack
        const endDateCalc = new Date();
        const startDateCalc = new Date();
        startDateCalc.setDate(endDateCalc.getDate() - daysBack);
        
        apiStartDate = startDateCalc.toISOString().split('T')[0];
        apiEndDate = endDateCalc.toISOString().split('T')[0];
      } else {
        // Default to last year if no dates provided
        const endDateCalc = new Date();
        const startDateCalc = new Date();
        startDateCalc.setDate(endDateCalc.getDate() - 365);
        
        apiStartDate = startDateCalc.toISOString().split('T')[0];
        apiEndDate = endDateCalc.toISOString().split('T')[0];
      }

      // Call API to generate more data-driven insights
      const response = await ApiService.generateMoreInsights({
        module: selectedModule,
        existing_insights: existingInsights,
        positive_examples: positiveInsights,
        count: 5,
        data_driven: true, // Request data-driven insights, not recommendations
        start_date: apiStartDate,
        end_date: apiEndDate
      });

      if (response?.additional_insights && response.additional_insights.length > 0) {
        // Add new insights to existing ones with animation
        setAiAnalysis(prev => ({
          ...prev,
          insights: [...(prev?.insights || []), ...response.additional_insights]
        }));

        console.log(`✨ Added ${response.additional_insights.length} new insights based on feedback`);

        // Show success message briefly
        setTimeout(() => {
          console.log('🎉 New insights successfully integrated');
        }, 500);
      } else {
        console.log('⚠️ No additional insights generated');
        setAiError('No new insights could be generated. Try providing more feedback first.');
      }

    } catch (error) {
      console.error('Error generating more insights:', error);
      setAiError('Failed to generate more insights. Please try again.');
    } finally {
      setLoadingMoreInsights(false);
    }
  };

  // Handle removing insights
  const handleRemoveInsight = (insightIndex) => {
    console.log(`Removing insight ${insightIndex}`);

    if (aiAnalysis && aiAnalysis.insights) {
      const updatedInsights = aiAnalysis.insights.filter((_, index) => index !== insightIndex);
      setAiAnalysis(prev => ({
        ...prev,
        insights: updatedInsights
      }));

      // Update feedback state to remove the deleted insight and adjust indices
      setInsightFeedback(prev => {
        const newFeedback = {};
        Object.keys(prev).forEach(key => {
          const index = parseInt(key);
          if (index < insightIndex) {
            newFeedback[index] = prev[key];
          } else if (index > insightIndex) {
            newFeedback[index - 1] = prev[key];
          }
          // Skip the deleted insight (index === insightIndex)
        });
        return newFeedback;
      });
    }
  };

  // Render module charts
  const renderModuleCharts = () => {
    // Custom dashboard doesn't need moduleData
    if (selectedModule === 'custom-dashboard') {
      return <DashboardManager />;
    }

    if (!moduleData) return null;

    switch (selectedModule) {
      case 'ei-tech-dashboard':
        return <EITechDashboardCharts data={moduleData} />;
      case 'srs-dashboard':
        return <SRSDashboardCharts data={moduleData} />;
      case 'ni-tct-dashboard':
        return <NITCTDashboardCharts data={moduleData} />;
      default:
        return <Alert severity="warning">Module charts not implemented yet.</Alert>;
    }
  };

  // Clean header actions - minimal (empty for center)
  const headerActions = (
    <>
      {/* Center area is empty - upload button moved to right side */}
    </>
  );

  // Header right actions - upload button and data health
  const headerRightActions = (
    <>
      {/* Data Health Button */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <IconButton
          onClick={() => navigate('/data-health')}
          sx={{
            color: 'white',
            '&:hover': {
              bgcolor: 'rgba(255, 255, 255, 0.1)',
              transform: 'scale(1.05)',
            },
            transition: 'all 0.2s ease',
            p: 0.5,
          }}
          title="Data Health Assessment"
        >
          <img 
            src="/database_health.png" 
            alt="Data Health" 
            style={{ 
              width: 24, 
              height: 24, 
              borderRadius: '4px',
              objectFit: 'cover',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              filter: 'brightness(0.8) contrast(1.2) invert(1)' // Makes it darker and white
            }} 
          />
        </IconButton>
      </motion.div>

      {/* Upload Button */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <IconButton
          onClick={() => navigate('/')}
          sx={{
            color: 'white',
            '&:hover': {
              bgcolor: 'rgba(255, 255, 255, 0.1)',
              transform: 'scale(1.05)',
            },
            transition: 'all 0.2s ease',
          }}
          title="Upload New Data File"
        >
          <UploadIcon />
        </IconButton>
      </motion.div>
    </>
  );

  return (
    <ErrorBoundary>
      <SafetyConnectLayout
        headerActions={headerActions}
        headerRightActions={headerRightActions}
      >

        <Box sx={{ px: 1.5, py: 2 }}> {/* Reduced padding from 3 to 1.5 for more width */}
          {/* Simplified Clean Header */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            {/* Clean Controls Row - Module Dropdown Left, Date Picker & Reload Right */}
            <Box sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              mb: 3,
              py: 2,
              borderBottom: '1px solid #e5e7eb'
            }}>
              {/* Beautiful Module Dropdown with Animations */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
              >
                <FormControl size="small" sx={{ minWidth: 280 }}>
                  <Select
                    value={selectedModule}
                    onChange={handleModuleChange}
                    displayEmpty
                    sx={{
                      bgcolor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: 0.5, // Reduced border radius
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      '& .MuiOutlinedInput-notchedOutline': {
                        border: 'none',
                      },
                      '&:hover': {
                        bgcolor: '#f8fafc',
                        boxShadow: '0 4px 12px 0 rgba(0, 0, 0, 0.1)',
                        transform: 'translateY(-1px)',
                      },
                      '& .MuiSelect-select': {
                        py: 1.5,
                        px: 2,
                      }
                    }}
                  >
                    {SAFETY_MODULES.map((module, index) => {
                      const IconComponent = module.icon;
                      return (
                        <MenuItem
                          key={module.id}
                          value={module.id}
                          sx={{
                            borderRadius: 0.25, // Reduced border radius
                            mx: 1,
                            my: 0.5,
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              backgroundColor: `${module.color}15`,
                              transform: 'translateX(4px)',
                            },
                          }}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <motion.div
                              whileHover={{ scale: 1.1, rotate: 5 }}
                              transition={{ duration: 0.2 }}
                            >
                              <IconComponent sx={{ fontSize: 20, color: module.color }} />
                            </motion.div>
                            <Typography sx={{ fontWeight: 500 }}>{module.label}</Typography>
                          </Box>
                        </MenuItem>
                      );
                    })}
                  </Select>
                </FormControl>
              </motion.div>

              {/* Right side - Date Picker & Reload */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>

                {/* Compact Date Picker */}
                <DatePickerFilter
                  dateRange={dateRange}
                  onDateRangeChange={handleDateRangeChange}
                  showDaysBackOption={true}
                  compact={true}
                />

                {/* Reload Button */}
                <Tooltip title="Refresh Data">
                  <IconButton
                    onClick={handleRefresh}
                    disabled={loading}
                    sx={{
                      bgcolor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: 1.5,
                      p: 1.5,
                      '&:hover': {
                        bgcolor: '#f8fafc',
                      },
                      '&:disabled': {
                        bgcolor: '#f1f5f9',
                      }
                    }}
                  >
                    <RefreshIcon sx={{ fontSize: 20, color: loading ? '#94a3b8' : '#092f57' }} />
                  </IconButton>
                </Tooltip>





                {/* Cosmic AI Assistant in header */}
                <Box sx={{ ml: 1, display: 'flex', alignItems: 'center' }}>
                  <FloatingAIAssistant
                    isActive={aiAnalysisEnabled}
                    onToggle={() => handleAIToggle(!aiAnalysisEnabled)}
                    isLoading={aiLoading}
                    hasNewInsights={aiAnalysis?.insights && aiAnalysis.insights.length > 0}
                  />
                </Box>
              </Box>
            </Box>


          </motion.div>

          {/* Error Display */}
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              <Alert severity="error" sx={{ mb: 3, border: '1px solid #fecaca' }}>
                {error}
              </Alert>
            </motion.div>
          )}

          {/* Main Content Area - Responsive Layout */}
          <Box sx={{
            display: 'flex',
            gap: 2, // Reduced gap from 3 to 2 for more space utilization
            minHeight: '600px',
            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            overflow: 'hidden', // Prevent layout shifts during animation
            position: 'relative'
          }}>
            {/* Dashboard Content - Adjusts width based on insights panel */}
            <Box sx={{
              flex: aiAnalysisEnabled ? '1 1 60%' : '1 1 100%',
              transition: 'flex 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              minWidth: 0, // Prevents flex item from overflowing
              maxWidth: aiAnalysisEnabled ? '60%' : '100%',
              overflow: 'hidden' // Ensure content doesn't overflow during transition
            }}>
              <AnimatePresence mode="wait">
                <motion.div
                  key={selectedModule}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                {/* Module Card - Clean Design */}
                <Card
                  sx={{
                    minHeight: 600,
                    bgcolor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: 2,
                    overflow: 'hidden',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    height: '100%'
                  }}
                >
                  <CardContent sx={{ p: 3, height: '100%' }}>
                    {loading ? (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.3 }}
                      >
                        <Box sx={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          justifyContent: 'center',
                          py: 8,
                          gap: 2
                        }}>
                          {/* Beautiful Loading Animation with Module Icon */}
                          <motion.div
                            animate={{
                              rotate: [0, 10, -10, 0],
                              y: [0, -5, 5, 0],
                              scale: [1, 1.1, 0.9, 1]
                            }}
                            transition={{
                              duration: 2,
                              repeat: Infinity,
                              ease: "easeInOut"
                            }}
                          >
                            {(() => {
                              const currentModule = SAFETY_MODULES.find(m => m.id === selectedModule);
                              const IconComponent = currentModule?.icon || CircularProgress;
                              return currentModule ? (
                                <IconComponent
                                  sx={{
                                    fontSize: 48,
                                    color: currentModule.color,
                                    filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1))'
                                  }}
                                />
                              ) : (
                                <CircularProgress size={48} sx={{ color: '#092f57' }} />
                              );
                            })()}
                          </motion.div>
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                          >
                            <Typography
                              variant="h6"
                              sx={{
                                color: '#6b7280',
                                fontWeight: 500,
                                textAlign: 'center'
                              }}
                            >
                              Loading {SAFETY_MODULES.find(m => m.id === selectedModule)?.label}...
                            </Typography>
                          </motion.div>
                        </Box>
                      </motion.div>
                    ) : (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.3 }}
                      >
                        <Box
                          key={`charts-${chartRenderKey}-${aiAnalysisEnabled ? 'with-ai' : 'without-ai'}`}
                          sx={{
                            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                            width: '100%',
                            overflow: 'hidden'
                          }}
                        >
                          {/* Module Charts - Clean Display */}
                          {renderModuleCharts()}
                        </Box>
                      </motion.div>
                    )}
                  </CardContent>
                </Card>
                </motion.div>
              </AnimatePresence>
            </Box>

            {/* Unified Insights Panel - Slides in from right */}
            <AnimatePresence>
              {aiAnalysisEnabled && (
                <motion.div
                  initial={{ opacity: 0, x: 300, width: 0 }}
                  animate={{
                    opacity: 1,
                    x: 0,
                    width: '40%'
                  }}
                  exit={{ opacity: 0, x: 300, width: 0 }}
                  transition={{
                    duration: 0.4,
                    ease: [0.4, 0, 0.2, 1]
                  }}
                  style={{
                    flex: '0 0 40%',
                    minWidth: '420px',
                    maxWidth: 'none' // Remove max width constraint to use full 40%
                  }}
                >
                  <UnifiedInsightsPanel
                    aiAnalysis={aiAnalysis}
                    aiLoading={aiLoading}
                    aiError={aiError}
                    insightFeedback={insightFeedback}
                    loadingMoreInsights={loadingMoreInsights}
                    selectedModule={selectedModule}
                    onClose={() => {
                      setAiAnalysisEnabled(false);
                      // Improved event dispatch for panel close
                      requestAnimationFrame(() => {
                        window.dispatchEvent(new CustomEvent('ai-panel-toggle', {
                          detail: {
                            insightsPanelOpen: false,
                            phase: 'start',
                            panelWidth: '0%'
                          }
                        }));

                        // Legacy event for backward compatibility
                        window.dispatchEvent(new CustomEvent('chatbot-toggle', {
                          detail: { insightsPanelOpen: false }
                        }));
                      });
                    }}
                    onFeedback={handleInsightFeedback}
                    onGenerateMore={handleGenerateMoreInsights}
                    onRemoveInsight={handleRemoveInsight}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </Box>
        </Box>



      </SafetyConnectLayout>
    </ErrorBoundary>
  );
};

export default UnifiedSafetyDashboard;
