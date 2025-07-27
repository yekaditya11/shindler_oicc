/**
 * Dashboard Manager Component
 * Manages custom dashboards and chart integration from chatbot
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Alert,
  Snackbar,
  CircularProgress,
  Tabs,
  Tab,
  Paper
} from '@mui/material';
import CustomDashboard from './CustomDashboard';
import SavedDashboards from './SavedDashboards';
import chartManager from '../../services/chartManager';
import ApiService from '../../services/api';

const DashboardManager = () => {
  const [savedCharts, setSavedCharts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [activeTab, setActiveTab] = useState(0);
  const [currentDashboard, setCurrentDashboard] = useState(null);

  // Load charts from global chart manager
  useEffect(() => {
    // Get initial charts
    setSavedCharts(chartManager.getCharts());

    // Listen for chart updates
    const handleChartsUpdate = (charts) => {
      setSavedCharts(charts);
    };

    chartManager.addListener(handleChartsUpdate);

    // Override global notification function
    if (typeof window !== 'undefined') {
      // eslint-disable-next-line no-undef
      window['showNotification'] = showNotification;
    }

    return () => {
      chartManager.removeListener(handleChartsUpdate);
    };
  }, []);

  // Delete chart using global chart manager
  const deleteChart = async (chartId) => {
    await chartManager.deleteChart(chartId);
  };

  // Update dashboard (for reordering)
  const updateDashboard = (updatedCharts) => {
    chartManager.updateCharts(updatedCharts);
  };

  // Save dashboard configuration
  const saveDashboard = async (dashboardConfig) => {
    try {
      setLoading(true);
      
      // Save to backend if API is available
      try {
        await ApiService.saveDashboard(
          dashboardConfig.name,
          dashboardConfig.charts,
          'anonymous'
        );
        showNotification(`Dashboard "${dashboardConfig.name}" saved successfully!`, 'success');
        
        // Switch to saved dashboards tab to show the new dashboard
        setActiveTab(1);
      } catch (apiError) {
        console.warn('Backend save failed, using local storage:', apiError);
        // Fallback to localStorage
        const savedDashboards = JSON.parse(localStorage.getItem('savedDashboards') || '[]');
        savedDashboards.push({
          ...dashboardConfig,
          id: `dashboard_${Date.now()}`
        });
        localStorage.setItem('savedDashboards', JSON.stringify(savedDashboards));
        showNotification(`Dashboard "${dashboardConfig.name}" saved locally!`, 'success');
      }
    } catch (error) {
      console.error('Error saving dashboard:', error);
      showNotification('Failed to save dashboard', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Load saved dashboard
  const handleLoadDashboard = (dashboard) => {
    setCurrentDashboard(dashboard);
    setSavedCharts(dashboard.charts || []);
    setActiveTab(0); // Switch to custom dashboard tab
    showNotification(`Dashboard "${dashboard.name}" loaded successfully!`, 'success');
  };

  // Handle refresh
  const handleRefresh = () => {
    // Reload charts from global chart manager
    setSavedCharts(chartManager.getCharts());
  };

  // Show notification
  const showNotification = (message, severity = 'success') => {
    setNotification({ open: true, message, severity });
  };

  // Close notification
  const closeNotification = () => {
    setNotification({ ...notification, open: false });
  };

  // Debug: Log when component mounts
  useEffect(() => {
    console.log('DashboardManager mounted');
    console.log('Current saved charts:', savedCharts);
  }, [savedCharts]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', overflow: 'hidden' }}>
      {/* Tab Navigation */}
      <Paper sx={{ mb: 2 }}>
        <Tabs 
          value={activeTab} 
          onChange={(e, newValue) => setActiveTab(newValue)}
          sx={{ 
            borderBottom: 1, 
            borderColor: 'divider',
            '& .MuiTab-root': {
              textTransform: 'none',
              fontWeight: 500
            }
          }}
        >
          <Tab 
            label="Custom Dashboard" 
            sx={{ 
              color: activeTab === 0 ? '#3b82f6' : 'text.secondary',
              '&.Mui-selected': { color: '#3b82f6' }
            }}
          />
          <Tab 
            label="Saved Dashboards" 
            sx={{ 
              color: activeTab === 1 ? '#3b82f6' : 'text.secondary',
              '&.Mui-selected': { color: '#3b82f6' }
            }}
          />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {activeTab === 0 && (
        <CustomDashboard
          savedCharts={savedCharts}
          onSaveChart={saveDashboard}
          onDeleteChart={deleteChart}
          onUpdateDashboard={updateDashboard}
        />
      )}

      {activeTab === 1 && (
        <SavedDashboards
          onLoadDashboard={handleLoadDashboard}
          onRefresh={handleRefresh}
        />
      )}

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={4000}
        onClose={closeNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={closeNotification} 
          severity={notification.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DashboardManager;
