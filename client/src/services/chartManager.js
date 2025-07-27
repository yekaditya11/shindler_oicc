/**
 * Global Chart Manager
 * Manages chart addition to dashboard from anywhere in the app
 */

import ApiService from './api';

class ChartManager {
  constructor() {
    this.charts = [];
    this.listeners = [];
    this.isLoading = false; // Prevent infinite loops
    this.loadCharts();
  }

  // Load charts from localStorage and API
  async loadCharts() {
    if (this.isLoading) {
      console.log('🔄 ChartManager: Already loading charts, skipping...');
      return;
    }
    
    this.isLoading = true;
    
    try {
      // Try API first
      try {
        const response = await ApiService.getUserCharts('anonymous');
        if (response.success && response.charts) {
          console.log('📊 ChartManager: Loaded charts from API:', response.charts.map(c => ({ 
            id: c.id, 
            chart_id: c.chart_id, 
            chartId: c.chartId,
            title: c.title 
          })));
          this.charts = response.charts;
          this.notifyListeners();
          return;
        }
      } catch (apiError) {
        console.warn('API load failed, using localStorage:', apiError);
      }

      // Fallback to localStorage
      const saved = localStorage.getItem('customDashboardCharts');
      if (saved) {
        this.charts = JSON.parse(saved);
        
        // Fix charts that don't have proper IDs
        let chartsFixed = false;
        this.charts = this.charts.map((chart, index) => {
          if (!chart.id && !chart.chart_id) {
            console.log(`🔧 ChartManager: Fixing chart ${index} without ID:`, chart.title);
            chartsFixed = true;
            const timestamp = Math.floor(Date.now() / 1000); // Use Unix timestamp like server
            return {
              ...chart,
              id: `chart_${timestamp}`,
              chart_id: `chart_${timestamp}`,
              chartId: `chart_${timestamp}`
            };
          }
          return chart;
        });
        
        // Save fixed charts back to localStorage (but don't trigger listeners again)
        if (chartsFixed) {
          console.log('🔧 ChartManager: Fixed charts without IDs, saving to localStorage');
          this.saveToLocalStorage(true); // Skip notification to prevent infinite loop
        }
        
        console.log('📊 ChartManager: Loaded charts from localStorage:', this.charts.map(c => ({ 
          id: c.id, 
          chart_id: c.chart_id, 
          chartId: c.chartId,
          title: c.title 
        })));
        this.notifyListeners();
      }
    } catch (error) {
      console.error('Error loading charts:', error);
    } finally {
      this.isLoading = false;
    }
  }

  // Save charts to localStorage
  saveToLocalStorage(skipNotification = false) {
    try {
      localStorage.setItem('customDashboardCharts', JSON.stringify(this.charts));
      if (!skipNotification) {
        this.notifyListeners();
      }
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  }

  // Add chart from chatbot
  async addChart(chartConfig) {
    try {
      console.log('ChartManager: Adding chart', chartConfig);

      // Try API first
      try {
        const response = await ApiService.addChartToDashboard(
          chartConfig.chartData,
          chartConfig.title || 'AI Generated Chart',
          chartConfig.source || 'chat',
          'anonymous'
        );
        
        if (response.success) {
          console.log('✅ ChartManager: Chart added via API with response:', response);
          // Reload charts from API
          await this.loadCharts();
          this.showNotification('Chart added to dashboard successfully!', 'success');
          
          // Trigger automatic resize events
          this.triggerChartResizeEvents();
          
          return response;
        }
      } catch (apiError) {
        console.warn('API add failed, using localStorage:', apiError);
        
        // Fallback to localStorage - use server-compatible ID format
        const timestamp = Math.floor(Date.now() / 1000); // Use Unix timestamp like server
        const newChart = {
          id: `chart_${timestamp}`,
          chart_id: `chart_${timestamp}`,
          title: chartConfig.title || 'AI Generated Chart',
          chart_data: chartConfig.chartData,
          chartData: chartConfig.chartData, // Keep both for compatibility
          source: chartConfig.source || 'chat',
          created_at: chartConfig.timestamp || new Date().toISOString(),
          size: 6,
          position: this.charts.length
        };

        this.charts.push(newChart);
        this.saveToLocalStorage(true); // Skip notification since we call it manually
        this.notifyListeners();
        this.showNotification('Chart added to dashboard (saved locally)!', 'success');
        
        // Trigger automatic resize events
        this.triggerChartResizeEvents();
        
        return newChart;
      }
    } catch (error) {
      console.error('Error adding chart:', error);
      this.showNotification('Failed to add chart to dashboard', 'error');
      throw error;
    }
  }

  // Delete chart
  async deleteChart(chartId) {
    try {
      console.log('🗑️ ChartManager: Deleting chart with ID:', chartId);
      console.log('🗑️ ChartManager: Current charts before deletion:', this.charts.map(c => ({ 
        id: c.id, 
        chart_id: c.chart_id, 
        chartId: c.chartId,
        title: c.title 
      })));
      
      // Try API first
      try {
        await ApiService.deleteChart(chartId);
        await this.loadCharts();
        this.showNotification('Chart removed from dashboard', 'info');
        console.log('✅ ChartManager: Chart deleted via API');
      } catch (apiError) {
        console.warn('API delete failed, using localStorage:', apiError);
        
        // Fallback to localStorage
        const beforeCount = this.charts.length;
        this.charts = this.charts.filter(chart => 
          chart.id !== chartId && 
          chart.chart_id !== chartId &&
          chart.chartId !== chartId &&
          (chart.id && chart.id.toString() !== chartId.toString()) &&
          (chart.chart_id && chart.chart_id.toString() !== chartId.toString())
        );
        const afterCount = this.charts.length;
        
        console.log(`🗑️ ChartManager: Local deletion - before: ${beforeCount}, after: ${afterCount}`);
        
        if (beforeCount === afterCount) {
          console.warn('⚠️ ChartManager: No chart was found to delete locally');
        } else {
          console.log('✅ ChartManager: Chart deleted locally');
        }
        
        this.saveToLocalStorage(true); // Skip notification since we call it manually
        this.notifyListeners();
        this.showNotification('Chart removed from dashboard (local only)', 'info');
      }
    } catch (error) {
      console.error('❌ ChartManager: Error deleting chart:', error);
      this.showNotification('Error removing chart', 'error');
      throw error; // Re-throw to let calling code handle the error
    }
  }

  // Update charts (for reordering)
  updateCharts(updatedCharts) {
    this.charts = updatedCharts;
    this.saveToLocalStorage(true); // Skip notification since we call it manually
    this.notifyListeners();
  }

  // Get all charts
  getCharts() {
    return this.charts;
  }

  // Add listener for chart updates
  addListener(callback) {
    this.listeners.push(callback);
  }

  // Remove listener
  removeListener(callback) {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  // Notify all listeners
  notifyListeners() {
    this.listeners.forEach(callback => {
      try {
        callback(this.charts);
      } catch (error) {
        console.error('Error in chart listener:', error);
      }
    });
  }

  // Show notification (can be overridden by UI components)
  showNotification(message, severity = 'success') {
    console.log(`[${severity.toUpperCase()}] ${message}`);

    // Try to show browser notification if available
    if (window.showNotification) {
      window.showNotification(message, severity);
    } else {
      // Create a custom notification element instead of alert
      this.createCustomNotification(message, severity);
    }
  }

  // Create custom notification when UI notification system is not available
  createCustomNotification(message, severity = 'success') {
    // Remove any existing notifications
    const existingNotification = document.getElementById('chart-manager-notification');
    if (existingNotification) {
      existingNotification.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.id = 'chart-manager-notification';
    notification.style.cssText = `
      position: fixed;
      top: 24px;
      right: 24px;
      z-index: 10000;
      padding: 16px 20px;
      border-radius: 12px;
      color: white;
      font-family: "Roboto", "Helvetica", "Arial", sans-serif;
      font-size: 14px;
      font-weight: 500;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
      transform: translateX(100%);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      max-width: 420px;
      min-width: 300px;
      word-wrap: break-word;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      cursor: pointer;
    `;

    // Set background color based on severity with Material-UI colors
    const colors = {
      success: '#2e7d32',
      error: '#d32f2f',
      warning: '#ed6c02',
      info: '#0288d1'
    };
    notification.style.backgroundColor = colors[severity] || colors.success;

    // Add icon based on severity
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️'
    };
    const icon = icons[severity] || icons.success;

    // Create notification content with close button
    notification.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px;">
        <div style="display: flex; align-items: center; gap: 8px; flex: 1;">
          <span style="font-size: 16px;">${icon}</span>
          <span>${message}</span>
        </div>
        <button
          onclick="this.parentElement.parentElement.click()"
          style="
            background: none;
            border: none;
            color: rgba(255, 255, 255, 0.8);
            cursor: pointer;
            font-size: 18px;
            padding: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: background-color 0.2s ease;
          "
          onmouseover="this.style.backgroundColor='rgba(255, 255, 255, 0.1)'"
          onmouseout="this.style.backgroundColor='transparent'"
        >×</button>
      </div>
    `;

    // Add to document
    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
    }, 100);

    // Auto-hide functionality with pause on hover
    let autoHideTimeout;
    const startAutoHide = () => {
      autoHideTimeout = setTimeout(() => {
        hideNotification();
      }, 5000); // 5 seconds
    };

    const hideNotification = () => {
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    };

    // Start auto-hide timer
    startAutoHide();

    // Pause auto-hide on hover
    notification.addEventListener('mouseenter', () => {
      if (autoHideTimeout) {
        clearTimeout(autoHideTimeout);
      }
    });

    // Resume auto-hide when mouse leaves
    notification.addEventListener('mouseleave', () => {
      startAutoHide();
    });

    // Allow manual close on click
    notification.addEventListener('click', () => {
      if (autoHideTimeout) {
        clearTimeout(autoHideTimeout);
      }
      hideNotification();
    });
  }

  // Trigger automatic chart resize events
  triggerChartResizeEvents() {
    console.log('Triggering chart resize events');
    
    // Dispatch custom events for chart addition
    if (typeof window !== 'undefined') {
      // Event for chart addition
      window.dispatchEvent(new CustomEvent('chart-added', {
        detail: { timestamp: Date.now() }
      }));
      
      // Event for dashboard update
      window.dispatchEvent(new CustomEvent('dashboard-update', {
        detail: { timestamp: Date.now() }
      }));
      
      // Trigger window resize event for responsive components
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
      }, 100);
      
      // Additional resize events with delays
      [300, 500, 800].forEach(delay => {
        setTimeout(() => {
          window.dispatchEvent(new Event('resize'));
        }, delay);
      });
    }
  }
}

// Create global instance
const chartManager = new ChartManager();

// Expose globally for chatbot integration
window.addChartToDashboard = (chartConfig) => chartManager.addChart(chartConfig);
window.chartManager = chartManager;

// Add utility function to clear localStorage for testing
window.clearChartStorage = () => {
  localStorage.removeItem('customDashboardCharts');
  chartManager.charts = [];
  chartManager.notifyListeners();
  console.log('🗑️ Chart storage cleared');
};

// Add utility function to fix chart IDs
window.fixChartIds = () => {
  chartManager.loadCharts();
  console.log('🔧 Chart IDs fixed');
};

// Add utility function to test deletion
window.testChartDeletion = (chartIndex = 0) => {
  const charts = chartManager.getCharts();
  if (charts.length > chartIndex) {
    const chart = charts[chartIndex];
    const deleteId = chart.id || chart.chart_id || chart.chartId;
    console.log(`🗑️ Testing deletion of chart ${chartIndex}:`, chart.title, 'with ID:', deleteId);
    console.log('🗑️ Full chart object:', chart);
    chartManager.deleteChart(deleteId);
  } else {
    console.log('❌ No chart found at index:', chartIndex);
  }
};

// Add utility function to inspect charts
window.inspectCharts = () => {
  const charts = chartManager.getCharts();
  console.log('📊 All charts:', charts.map((chart, index) => ({
    index,
    id: chart.id,
    chart_id: chart.chart_id,
    chartId: chart.chartId,
    title: chart.title,
    created_at: chart.created_at,
    timestamp: chart.timestamp
  })));
};

// Add utility function to check server charts
window.checkServerCharts = async () => {
  try {
    const response = await ApiService.getUserCharts('anonymous');
    console.log('📊 Server charts:', response);
    if (response.charts) {
      console.log('📊 Server chart IDs:', response.charts.map(c => ({
        id: c.id,
        chart_id: c.chart_id,
        title: c.title
      })));
    }
  } catch (error) {
    console.error('❌ Error checking server charts:', error);
  }
};

// Add utility function to sync with server
window.syncWithServer = async () => {
  try {
    console.log('🔄 Syncing charts with server...');
    await chartManager.loadCharts();
    console.log('✅ Sync complete');
  } catch (error) {
    console.error('❌ Error syncing with server:', error);
  }
};

// Add utility function to inspect localStorage
window.inspectLocalStorage = () => {
  try {
    const saved = localStorage.getItem('customDashboardCharts');
    if (saved) {
      const charts = JSON.parse(saved);
      console.log('📊 localStorage charts:', charts);
      console.log('📊 localStorage chart IDs:', charts.map((chart, index) => ({
        index,
        id: chart.id,
        chart_id: chart.chart_id,
        chartId: chart.chartId,
        title: chart.title,
        created_at: chart.created_at,
        timestamp: chart.timestamp,
        timestampType: typeof chart.timestamp
      })));
    } else {
      console.log('📊 No charts in localStorage');
    }
  } catch (error) {
    console.error('❌ Error inspecting localStorage:', error);
  }
};

// Add utility function to fix NaN IDs
window.fixNaNIds = () => {
  try {
    const saved = localStorage.getItem('customDashboardCharts');
    if (saved) {
      const charts = JSON.parse(saved);
      let fixed = false;
      
      const fixedCharts = charts.map((chart, index) => {
        if (chart.id && chart.id.includes('NaN') || 
            chart.chart_id && chart.chart_id.includes('NaN') ||
            chart.chartId && chart.chartId.includes('NaN')) {
          console.log(`🔧 Fixing NaN ID for chart ${index}:`, chart.title);
          fixed = true;
          const timestamp = Math.floor(Date.now() / 1000);
          return {
            ...chart,
            id: `chart_${timestamp}_${index}`,
            chart_id: `chart_${timestamp}_${index}`,
            chartId: `chart_${timestamp}_${index}`
          };
        }
        return chart;
      });
      
      if (fixed) {
        localStorage.setItem('customDashboardCharts', JSON.stringify(fixedCharts));
        chartManager.charts = fixedCharts;
        chartManager.notifyListeners();
        console.log('✅ Fixed NaN IDs');
      } else {
        console.log('✅ No NaN IDs found');
      }
    }
  } catch (error) {
    console.error('❌ Error fixing NaN IDs:', error);
  }
};

// Add utility function to show chart JSON structure
window.showChartJSON = (chartIndex = 0) => {
  try {
    const charts = chartManager.getCharts();
    if (charts.length > chartIndex) {
      const chart = charts[chartIndex];
      console.log(`📊 Chart ${chartIndex} JSON structure:`, JSON.stringify(chart, null, 2));
      console.log(`📊 Chart ${chartIndex} ID fields:`, {
        id: chart.id,
        chart_id: chart.chart_id,
        chartId: chart.chartId,
        title: chart.title,
        created_at: chart.created_at,
        timestamp: chart.timestamp
      });
    } else {
      console.log('❌ No chart found at index:', chartIndex);
    }
  } catch (error) {
    console.error('❌ Error showing chart JSON:', error);
  }
};

// Add utility function to debug server charts
window.debugServerCharts = async () => {
  try {
    const response = await ApiService.debugCharts('anonymous');
    console.log('🔍 Server chart files:', response);
    return response;
  } catch (error) {
    console.error('❌ Error debugging server charts:', error);
  }
};

export default chartManager;
