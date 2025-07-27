/**
 * Custom Dashboard Component
 * Allows users to create custom dashboards with AI-generated charts from chatbot
 * Supports drag-and-drop, resizing, and chart management
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip,
  Tooltip,
  Menu,
  MenuItem,
  Fab
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Dashboard as DashboardIcon,
  DragIndicator as DragIcon,
  Fullscreen as FullscreenIcon,
  MoreVert as MoreIcon,
  GridView as GridIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

// Import chart components
import EChartsChart from '../chatbot/EChartsChart';
import PlotlyChart from '../chatbot/PlotlyChart';

// Import chart resize handler
import { ChartResizeHandler } from '../../utils/chartResizeHandler';

const CustomDashboard = ({ savedCharts = [], onSaveChart, onDeleteChart, onUpdateDashboard }) => {
  const [charts, setCharts] = useState(savedCharts);
  const [isEditMode, setIsEditMode] = useState(false);
  const [selectedChart, setSelectedChart] = useState(null);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [dashboardName, setDashboardName] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [gridSize, setGridSize] = useState(12); // Default grid size
  const [dragState, setDragState] = useState({
    isDragging: false,
    draggedIndex: null,
    dragOverIndex: null
  });
  const [isMouseDown, setIsMouseDown] = useState(false);
  const [mouseStartPos, setMouseStartPos] = useState({ x: 0, y: 0 });
  const dragRef = useRef(null);
  const resizeHandlerRef = useRef(null);

  useEffect(() => {
    setCharts(savedCharts);
  }, [savedCharts]);

  // Simple mouse-based drag and drop
  const handleMouseDown = useCallback((e, index) => {
    if (!isEditMode) return;
    
    console.log('🔄 Mouse down on chart:', index);
    setIsMouseDown(true);
    setMouseStartPos({ x: e.clientX, y: e.clientY });
    setDragState(prev => ({
      ...prev,
      isDragging: false,
      draggedIndex: index
    }));
  }, [isEditMode]);

  const handleMouseMove = useCallback((e) => {
    if (!isMouseDown || !isEditMode) return;
    
    const deltaX = Math.abs(e.clientX - mouseStartPos.x);
    const deltaY = Math.abs(e.clientY - mouseStartPos.y);
    
    // Start dragging after moving 5px
    if ((deltaX > 5 || deltaY > 5) && !dragState.isDragging) {
      console.log('🔄 Starting drag');
      setDragState(prev => ({
        ...prev,
        isDragging: true
      }));
      document.body.style.cursor = 'grabbing';
      document.body.classList.add('dragging'); // Add dragging class for CSS rules
      // Don't disable user-select as it can interfere with chart rendering
      // document.body.style.userSelect = 'none';
    }
    
    // Update drag over state for visual feedback
    if (dragState.isDragging) {
      const elements = document.elementsFromPoint(e.clientX, e.clientY);
      let dropIndex = null;
      
      for (const element of elements) {
        const index = element.getAttribute('data-chart-index');
        if (index !== null) {
          dropIndex = parseInt(index);
          break;
        }
      }
      
      if (dropIndex !== null && dropIndex !== dragState.draggedIndex) {
        setDragState(prev => ({
          ...prev,
          dragOverIndex: dropIndex
        }));
      } else {
        setDragState(prev => ({
          ...prev,
          dragOverIndex: null
        }));
      }
    }
  }, [isMouseDown, isEditMode, mouseStartPos, dragState.isDragging, dragState.draggedIndex]);

  const handleMouseUp = useCallback((e) => {
    if (!isMouseDown || !isEditMode) return;
    
    console.log('🔄 Mouse up');
    setIsMouseDown(false);
    document.body.style.cursor = '';
    document.body.classList.remove('dragging'); // Remove dragging class
    // document.body.style.userSelect = '';
    
    if (dragState.isDragging) {
      const dragIndex = dragState.draggedIndex;
      const dropIndex = dragState.dragOverIndex;
      
      console.log('🔄 Drop detection:', { dragIndex, dropIndex });
      
      if (dropIndex !== null && dropIndex !== dragIndex) {
        console.log('🔄 Reordering from', dragIndex, 'to', dropIndex);
        
        const newCharts = [...charts];
        const [draggedItem] = newCharts.splice(dragIndex, 1);
        
        // Insert at the correct position
        let insertIndex = dropIndex;
        if (dragIndex < dropIndex) {
          // When dragging from left to right, insert at the target position
          insertIndex = dropIndex;
        } else {
          // When dragging from right to left, insert at the target position
          insertIndex = dropIndex;
        }
        
        newCharts.splice(insertIndex, 0, draggedItem);
        
        console.log('🔄 Final reorder:', { from: dragIndex, to: insertIndex, totalCharts: newCharts.length });
        
        setCharts(newCharts);
        if (onUpdateDashboard) {
          onUpdateDashboard(newCharts);
        }
      } else {
        console.log('🔄 No valid drop target found');
      }
    }
    
    setDragState({
      isDragging: false,
      draggedIndex: null,
      dragOverIndex: null
    });
  }, [isMouseDown, isEditMode, dragState, charts, onUpdateDashboard]);

  // Add global mouse event listeners
  useEffect(() => {
    if (isEditMode) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
    }
  }, [isEditMode, handleMouseMove, handleMouseUp]);

  // Handle chart resizing when grid layout changes
  useEffect(() => {
    // Initialize resize handler
    if (!resizeHandlerRef.current) {
      resizeHandlerRef.current = new ChartResizeHandler();
    }

    const resizeCharts = () => {
      // Small delay to ensure layout is stable
      setTimeout(() => {
        if (resizeHandlerRef.current) {
          resizeHandlerRef.current.resizeDashboardCharts();
        }
      }, 300);
    };

    // Resize charts when charts array changes
    if (charts.length > 0) {
      resizeCharts();
    }
  }, [charts, gridSize]);

  // Enhanced automatic chart resizing when new charts are added
  useEffect(() => {
    if (!resizeHandlerRef.current) {
      resizeHandlerRef.current = new ChartResizeHandler();
    }

    // Function to handle automatic chart resizing
    const handleChartResize = () => {
      console.log('Auto-resizing charts after chart addition/change');
      
      // Multiple resize attempts with different delays to ensure all charts are properly sized
      const resizeAttempts = [100, 300, 500, 800];
      
      resizeAttempts.forEach((delay, index) => {
        setTimeout(() => {
          if (resizeHandlerRef.current) {
            console.log(`Resize attempt ${index + 1} after ${delay}ms`);
            resizeHandlerRef.current.resizeDashboardCharts();
            
            // Additional Plotly-specific resize
            if (typeof window !== 'undefined' && window.Plotly) {
              try {
                window.Plotly.Plots.resize();
              } catch (error) {
                console.warn('Plotly resize error:', error);
              }
            }
            
            // Force ECharts resize
            const echartsContainers = document.querySelectorAll('.echarts-for-react');
            echartsContainers.forEach(container => {
              if (container.__echarts__) {
                try {
                  container.__echarts__.resize();
                } catch (error) {
                  console.warn('ECharts resize error:', error);
                }
              }
            });
          }
        }, delay);
      });
    };

    // Trigger resize when charts change
    if (charts.length > 0) {
      handleChartResize();
    }

    // Setup resize observer for container changes
    const resizeObserver = resizeHandlerRef.current.setupDashboardResizeObserver();
    
    return () => {
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
    };
  }, [charts.length, charts]); // Added charts dependency to trigger on chart content changes

  // Add global event listener for chart additions
  useEffect(() => {
    const handleChartAddition = () => {
      console.log('Chart addition detected, triggering resize');
      setTimeout(() => {
        if (resizeHandlerRef.current) {
          resizeHandlerRef.current.resizeDashboardCharts();
        }
      }, 200);
    };

    // Listen for custom chart addition events
    window.addEventListener('chart-added', handleChartAddition);
    window.addEventListener('dashboard-update', handleChartAddition);

    return () => {
      window.removeEventListener('chart-added', handleChartAddition);
      window.removeEventListener('dashboard-update', handleChartAddition);
    };
  }, []);

  // Handle chart deletion
  const handleDeleteChart = (chartId) => {
    const updatedCharts = charts.filter(chart =>
      chart.id !== chartId && chart.chart_id !== chartId
    );
    setCharts(updatedCharts);
    if (onDeleteChart) {
      onDeleteChart(chartId);
    }
  };

  // Handle saving dashboard
  const handleSaveDashboard = () => {
    if (!dashboardName.trim()) return;
    
    const dashboardConfig = {
      name: dashboardName,
      charts: charts,
      gridSize: gridSize,
      createdAt: new Date().toISOString()
    };

    if (onSaveChart) {
      onSaveChart(dashboardConfig);
    }
    
    setShowSaveDialog(false);
    setDashboardName('');
  };

  // Render individual chart
  const renderChart = (chart, index) => {
    const chartSize = chart.size || 6; // Default to half width
    const chartId = chart.chart_id || chart.id || `chart_${index}`;
    const isBeingDragged = dragState.isDragging && dragState.draggedIndex === index;
    const isDragOver = dragState.isDragging && dragState.dragOverIndex === index;
    
    // Debug logging for chart rendering
    console.log(`Rendering chart ${index}:`, { 
      isBeingDragged, 
      isDragOver, 
      chartId, 
      chartType: chart.chartData?.type || chart.chart_data?.type 
    });

    // Calculate dynamic height based on chart size and type
    const getChartHeight = () => {
      const baseHeight = 450; // Reduced base height to give more balanced spacing
      const sizeMultiplier = chartSize <= 6 ? 1 : chartSize <= 8 ? 1.2 : 1.4; // Adjust height based on grid size
      return Math.round(baseHeight * sizeMultiplier);
    };

    const chartHeight = getChartHeight();

    return (
      <Grid 
        item 
        xs={12} 
        md={chartSize}
        key={chartId}
        data-chart-index={index}
        sx={{
          opacity: isBeingDragged ? 0.8 : 1, // Increased opacity to keep charts more visible
          transform: isBeingDragged ? 'rotate(2deg) scale(0.98)' : 'none', // Reduced transform to keep charts more visible
          transition: 'all 0.2s ease',
          position: 'relative',
          cursor: isEditMode ? 'grab' : 'default',
          '&:active': {
            cursor: isEditMode ? 'grabbing' : 'default',
          },
          border: isDragOver ? '2px dashed #3b82f6' : 'none', // Add drop target indicator
          boxShadow: isDragOver ? '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)' : 'none', // Add drop target shadow
        }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          transition={{ duration: 0.3 }}
          style={{
            transform: isBeingDragged ? 'rotate(2deg)' : 'none', // Reduced rotation to keep charts more visible
            zIndex: isBeingDragged ? 1000 : 1,
          }}
        >
          <Card
            sx={{
              height: chartHeight, // Dynamic height based on chart size
              position: 'relative',
              border: isEditMode ? '2px dashed #e0e7ff' : '1px solid #e5e7eb',
              borderColor: isBeingDragged ? '#3b82f6' : undefined,
              borderRadius: 2, // Changed to 2 for very subtle rounded corners
              boxShadow: isBeingDragged 
                ? '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
                : '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              transition: 'all 0.3s ease',
              cursor: isEditMode ? 'grab' : 'default',
              '&:hover': {
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                transform: isEditMode ? 'translateY(-2px)' : 'none',
              },
              '&:active': {
                cursor: isEditMode ? 'grabbing' : 'default',
              }
            }}
            onMouseDown={(e) => handleMouseDown(e, index)}
          >
            {/* Floating Delete Button - Only visible in edit mode */}
            {isEditMode && (
              <Box
                sx={{
                  position: 'absolute',
                  top: 8,
                  right: 8,
                  zIndex: 10,
                  bgcolor: 'rgba(255, 255, 255, 0.9)',
                  borderRadius: '50%',
                  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
                  '&:hover': {
                    bgcolor: 'rgba(255, 255, 255, 1)',
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
                  }
                }}
              >
                <Tooltip title="Delete chart">
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation(); // Prevent triggering drag
                      handleDeleteChart(chartId);
                    }}
                    sx={{
                      color: '#dc2626',
                      '&:hover': { 
                        bgcolor: 'rgba(220, 38, 38, 0.1)',
                        color: '#b91c1c'
                      }
                    }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            )}

            {/* Chart Content - No header, just the chart */}
            <CardContent sx={{ 
              p: 0.5, // Further reduced padding to give more space to charts
              height: '100%', // Use full height since no header
              pb: 0.5, // Reduced bottom padding
              display: 'flex',
              flexDirection: 'column',
              borderRadius: 2 // Changed to 2 for very subtle rounded corners
            }}>
              <Box sx={{ 
                width: '100%', 
                height: '100%',
                minWidth: 0, // Allow container to shrink
                minHeight: 0, // Allow container to shrink
                overflow: 'hidden', // Prevent overflow issues
                pointerEvents: isEditMode ? 'auto' : 'auto', // Keep pointer events enabled for chart visibility
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                borderRadius: 2 // Changed to 2 for very subtle rounded corners
              }}>
                {(() => {
                  // Handle both chartData and chart_data properties
                  const chartData = chart.chartData || chart.chart_data;

                  if (!chartData) {
                    return (
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          height: '100%',
                          color: '#6b7280',
                          flex: 1
                        }}
                      >
                        <Typography>Chart data not available</Typography>
                      </Box>
                    );
                  }

                  // Auto-detect chart type for conversational BI charts
                  let chartType = chartData.type;
                  
                  // If no type specified, detect from data structure
                  if (!chartType) {
                    if (chartData.series && Array.isArray(chartData.series)) {
                      // ECharts format - has series array
                      chartType = 'echarts';
                    } else if (chartData.data && chartData.layout) {
                      // Plotly format - has data and layout
                      chartType = 'plotly';
                    } else if (chartData.data || chartData.datasets) {
                      // Chart.js format - has data or datasets
                      chartType = 'echarts'; // Default to echarts for safety
                    } else {
                      // Unknown format, try echarts as default
                      chartType = 'echarts';
                    }
                  }

                  console.log('Chart type detected:', chartType, 'for chart data:', chartData);

                  // Create responsive chart wrapper
                  const ChartWrapper = ({ children }) => (
                    <Box sx={{
                      width: '100%',
                      height: '100%',
                      minHeight: 0,
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center', // Center the chart vertically
                      alignItems: 'center', // Center the chart horizontally
                      borderRadius: 2, // Changed to 2 for very subtle rounded corners
                      '& > *': {
                        width: '100%',
                        maxHeight: '85%', // Limit chart height to leave space for title/description
                        minHeight: 0,
                        borderRadius: 2, // Changed to 2 for very subtle rounded corners for chart components
                      },
                      '& *': {
                        borderRadius: 2, // Changed to 2 for very subtle rounded corners for all child elements
                      }
                    }}>
                      {children}
                    </Box>
                  );

                  if (chartType === 'echarts') {
                    return (
                      <ChartWrapper>
                        <EChartsChart
                          chartData={chartData}
                          isFullscreen={false}
                          key={`echarts-${chartId}`} // Stable key to prevent unnecessary re-renders
                        />
                      </ChartWrapper>
                    );
                  } else if (chartType === 'plotly') {
                    return (
                      <ChartWrapper>
                        <PlotlyChart
                          chartData={chartData}
                          isFullscreen={false}
                          key={`plotly-${chartId}`} // Stable key to prevent unnecessary re-renders
                        />
                      </ChartWrapper>
                    );
                  } else {
                    return (
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          height: '100%',
                          color: '#6b7280',
                          flex: 1
                        }}
                      >
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography>Unsupported chart type: {chartType}</Typography>
                          <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
                            Chart data: {JSON.stringify(Object.keys(chartData))}
                          </Typography>
                        </Box>
                      </Box>
                    );
                  }
                })()}
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      </Grid>
    );
  };

  return (
    <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 2,
        flexWrap: 'wrap',
        gap: 2
      }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 600, color: '#092f57' }}>
            Custom Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Click 'Edit Mode' to drag and drop AI-generated charts to create your custom dashboard.
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Button
            variant={isEditMode ? "contained" : "outlined"}
            startIcon={<EditIcon />}
            onClick={() => setIsEditMode(!isEditMode)}
            sx={{ 
              bgcolor: isEditMode ? '#3b82f6' : 'transparent',
              color: isEditMode ? 'white' : '#3b82f6',
              borderColor: '#3b82f6',
              '&:hover': {
                bgcolor: isEditMode ? '#2563eb' : 'rgba(59, 130, 246, 0.1)',
              }
            }}
          >
            {isEditMode ? 'Exit Edit Mode' : 'Edit Mode'}
          </Button>

          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={() => setShowSaveDialog(true)}
            disabled={charts.length === 0}
            sx={{ 
              bgcolor: '#10b981',
              '&:hover': { bgcolor: '#059669' },
              '&:disabled': { bgcolor: '#d1d5db' }
            }}
          >
            Save Dashboard
          </Button>
        </Box>
      </Box>

      {/* Dashboard Container */}
      <Box 
        data-dashboard-container="true"
        sx={{ 
          minHeight: 'calc(100vh - 200px)',
          position: 'relative'
        }}
      >
        {charts.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: 400,
              border: '2px dashed #e5e7eb',
              borderRadius: 2,
              bgcolor: '#f8fafc'
            }}
          >
            <DashboardIcon sx={{ fontSize: 64, color: '#9ca3af', mb: 2 }} />
            <Typography variant="h6" color="textSecondary" gutterBottom>
              No charts added yet
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ textAlign: 'center', maxWidth: 400 }}>
              Start a conversation with the AI chatbot and add generated charts to your custom dashboard using the "+" button on each chart.
            </Typography>
          </Box>
        ) : (
          <Grid container spacing={2}>
            <AnimatePresence>
              {charts.map((chart, index) => renderChart(chart, index))}
            </AnimatePresence>
            
            {/* Drop zone indicator */}
            {dragState.isDragging && dragState.dragOverIndex !== null && (
              <Grid 
                item 
                xs={12} 
                sx={{
                  height: 4,
                  bgcolor: '#3b82f6',
                  borderRadius: 2,
                  opacity: 0.8,
                  animation: 'pulse 1s infinite',
                  '@keyframes pulse': {
                    '0%, 100%': { opacity: 0.8 },
                    '50%': { opacity: 0.4 }
                  }
                }}
              />
            )}
          </Grid>
        )}
      </Box>

      {/* Save Dashboard Dialog */}
      <Dialog open={showSaveDialog} onClose={() => setShowSaveDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Save Custom Dashboard</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Dashboard Name"
            fullWidth
            variant="outlined"
            value={dashboardName}
            onChange={(e) => setDashboardName(e.target.value)}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSaveDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleSaveDashboard}
            variant="contained"
            disabled={!dashboardName.trim()}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CustomDashboard;
