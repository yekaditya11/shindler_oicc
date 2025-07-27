/**
 * Dashboard Test Component
 * Test the drag-and-drop dashboard functionality
 */

import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Card,
  CardContent,
  Grid,
  Alert,
  Chip
} from '@mui/material';
import { Add as AddIcon, DragIndicator as DragIcon } from '@mui/icons-material';
import DashboardManager from '../dashboard/DashboardManager';
import chartManager from '../../services/chartManager';

const DashboardTest = () => {
  const [testCharts] = useState([
    {
      id: 'test_chart_1',
      chart_id: 'test_chart_1',
      title: 'Sample Incident Trends',
      chart_data: {
        type: 'echarts',
        echarts_config: {
          title: { text: 'Incident Trends' },
          xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May'] },
          yAxis: { type: 'value' },
          series: [{
            data: [5, 3, 8, 2, 6],
            type: 'line',
            smooth: true
          }]
        }
      },
      source: 'test',
      created_at: new Date().toISOString(),
      size: 6
    },
    {
      id: 'test_chart_2',
      chart_id: 'test_chart_2',
      title: 'Action Status Distribution',
      chart_data: {
        type: 'echarts',
        echarts_config: {
          title: { text: 'Action Status' },
          series: [{
            type: 'pie',
            data: [
              { value: 15, name: 'Open' },
              { value: 25, name: 'In Progress' },
              { value: 35, name: 'Completed' }
            ]
          }]
        }
      },
      source: 'test',
      created_at: new Date().toISOString(),
      size: 6
    },
    {
      id: 'test_chart_3',
      chart_id: 'test_chart_3',
      title: 'Safety Performance Metrics',
      chart_data: {
        type: 'plotly',
        config: {
          data: [{
            x: ['Q1', 'Q2', 'Q3', 'Q4'],
            y: [85, 92, 78, 95],
            type: 'bar',
            marker: { color: '#3b82f6' }
          }],
          layout: {
            title: 'Quarterly Safety Performance',
            xaxis: { title: 'Quarter' },
            yaxis: { title: 'Performance Score (%)' }
          }
        }
      },
      source: 'test',
      created_at: new Date().toISOString(),
      size: 12
    }
  ]);

  const addTestChart = () => {
    const randomChart = testCharts[Math.floor(Math.random() * testCharts.length)];
    const chartWithId = {
      ...randomChart,
      id: `test_chart_${Date.now()}`,
      chart_id: `test_chart_${Date.now()}`,
      title: `${randomChart.title} (${new Date().toLocaleTimeString()})`
    };
    
    chartManager.addChart(chartWithId);
  };

  const clearAllCharts = () => {
    const charts = chartManager.getCharts();
    charts.forEach(chart => {
      chartManager.deleteChart(chart.id || chart.chart_id);
    });
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard Test Page
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 3 }}>
        This page demonstrates the drag-and-drop dashboard functionality.
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Test Chart Addition
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                Click the button below to add a test chart to your custom dashboard.
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={addTestChart}
                sx={{ bgcolor: '#3b82f6', mr: 2 }}
              >
                Add Test Chart
              </Button>
              <Button
                variant="outlined"
                onClick={clearAllCharts}
                sx={{ borderColor: '#dc2626', color: '#dc2626' }}
              >
                Clear All
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Drag & Drop Instructions
              </Typography>
              <Typography variant="body2" component="div" sx={{ mb: 2 }}>
                <ol>
                  <li>Add some test charts using the button above</li>
                  <li>Navigate to the "Custom Dashboard" module</li>
                  <li>Click "Edit Mode" to enable drag and drop</li>
                  <li>Drag charts by clicking and holding on the chart area</li>
                  <li>Drop charts in new positions to reorder them</li>
                  <li>Use the drag handle icon for easier dragging</li>
                </ol>
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <DragIcon fontSize="small" color="action" />
                <Typography variant="caption" color="textSecondary">
                  Look for this icon when in edit mode
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Note:</strong> The drag and drop functionality uses HTML5 drag and drop API. 
          Make sure you're in "Edit Mode" to drag charts. Charts can be dragged from anywhere 
          on the chart card when in edit mode.
        </Typography>
      </Alert>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          Custom Dashboard
        </Typography>
        <DashboardManager />
      </Box>
    </Box>
  );
};

export default DashboardTest;
