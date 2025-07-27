/**
 * PlotlyChart Component
 * Renders Plotly charts within the chatbot interface
 * Version: 2024-12-07 - Fixed hover values visibility
 */

import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Typography,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Fullscreen as FullscreenIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

// Dynamically import Plotly to avoid SSR issues
let Plot = null;
if (typeof window !== 'undefined') {
  import('react-plotly.js').then((module) => {
    Plot = module.default;
  }).catch((error) => {
    console.error('Failed to load Plotly:', error);
  });
}

const PlotlyChart = ({ chartData, isFullscreen = false }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [plotlyLoaded, setPlotlyLoaded] = useState(false);
  const plotRef = useRef(null);

  // Debug logging
  console.log('PlotlyChart received chartData:', chartData);

  useEffect(() => {
    // Check if Plotly is loaded
    const checkPlotly = async () => {
      try {
        if (typeof window !== 'undefined') {
          const module = await import('react-plotly.js');
          Plot = module.default;
          setPlotlyLoaded(true);
        }
      } catch (err) {
        console.error('Error loading Plotly:', err);
        setError('Failed to load chart library');
      } finally {
        setIsLoading(false);
      }
    };

    checkPlotly();
  }, []);

  // Handle chart resize when fullscreen mode changes
  useEffect(() => {
    if (plotRef.current && plotlyLoaded) {
      // Small delay to allow for layout changes
      const timer = setTimeout(() => {
        if (plotRef.current && plotRef.current.resizeHandler) {
          plotRef.current.resizeHandler();
        }
      }, 300);

      return () => clearTimeout(timer);
    }
  }, [isFullscreen, plotlyLoaded]);

  // Add resize observer to handle container size changes
  useEffect(() => {
    if (!plotRef.current || !plotlyLoaded) return;

    const resizeObserver = new ResizeObserver(() => {
      if (plotRef.current && plotRef.current.resizeHandler) {
        // Small delay to ensure layout is stable
        setTimeout(() => {
          plotRef.current.resizeHandler();
        }, 100);
      }
    });

    const chartContainer = plotRef.current;
    resizeObserver.observe(chartContainer);

    return () => {
      resizeObserver.disconnect();
    };
  }, [plotlyLoaded]);

  // Enhanced automatic resize handling for dashboard integration
  useEffect(() => {
    if (!plotlyLoaded || !plotRef.current) return;

    const handleChartResize = () => {
      console.log('PlotlyChart: Handling automatic resize');
      
      // Multiple resize attempts to ensure proper sizing
      const resizeAttempts = [50, 150, 300, 500];
      
      resizeAttempts.forEach((delay, index) => {
        setTimeout(() => {
          if (plotRef.current) {
            console.log(`PlotlyChart: Resize attempt ${index + 1} after ${delay}ms`);
            
            // Try different resize methods
            try {
              // Method 1: Use Plotly's resize method
              if (plotRef.current.resizeHandler) {
                plotRef.current.resizeHandler();
              }
              
              // Method 2: Use Plotly's relayout method
              if (window.Plotly && plotRef.current.el) {
                window.Plotly.relayout(plotRef.current.el, {});
              }
              
              // Method 3: Force resize by triggering window resize
              window.dispatchEvent(new Event('resize'));
            } catch (error) {
              console.warn('PlotlyChart resize error:', error);
            }
          }
        }, delay);
      });
    };

    // Listen for chart addition events
    const handleChartAddition = () => {
      console.log('PlotlyChart: Chart addition detected');
      handleChartResize();
    };

    // Listen for dashboard update events
    const handleDashboardUpdate = () => {
      console.log('PlotlyChart: Dashboard update detected');
      handleChartResize();
    };

    // Add event listeners
    window.addEventListener('chart-added', handleChartAddition);
    window.addEventListener('dashboard-update', handleDashboardUpdate);
    window.addEventListener('resize', handleChartResize);

    // Initial resize after component mounts
    handleChartResize();

    return () => {
      window.removeEventListener('chart-added', handleChartAddition);
      window.removeEventListener('dashboard-update', handleDashboardUpdate);
      window.removeEventListener('resize', handleChartResize);
    };
  }, [plotlyLoaded, chartData]); // Added chartData dependency to trigger on data changes

  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: 200,
          gap: 2,
        }}
      >
        <CircularProgress size={24} />
        <Typography variant="body2" color="text.secondary">
          Loading chart...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ my: 2 }}>
        {error}
        <Typography variant="body2" sx={{ mt: 1, fontSize: '0.75rem' }}>
          Debug: Chart data = {JSON.stringify(chartData, null, 2)}
        </Typography>
      </Alert>
    );
  }

  if (!chartData) {
    console.log('PlotlyChart: No chart data provided');
    return (
      <Alert severity="info" sx={{ my: 2 }}>
        No chart data provided
        <Typography variant="body2" sx={{ mt: 1, fontSize: '0.75rem' }}>
          Debug: chartData is {typeof chartData}: {JSON.stringify(chartData)}
        </Typography>
      </Alert>
    );
  }

  if (!plotlyLoaded || !Plot) {
    return (
      <Alert severity="warning" sx={{ my: 2 }}>
        Chart library not loaded (plotlyLoaded: {plotlyLoaded.toString()}, Plot: {Plot ? 'available' : 'null'})
        <Typography variant="body2" sx={{ mt: 1, fontSize: '0.75rem' }}>
          Chart data: {JSON.stringify(chartData, null, 2)}
        </Typography>
      </Alert>
    );
  }

  // Process chart data based on type
  const processChartData = () => {
    try {
      console.log('Processing chart data:', chartData);

      // If chartData has Plotly config, use it directly
      if (chartData.config) {
        console.log('Using Plotly config directly:', chartData.config);
        // The config contains the full Plotly figure with data and layout
        const plotlyConfig = chartData.config;
        return {
          data: plotlyConfig.data || [],
          layout: plotlyConfig.layout || {},
          config: { displayModeBar: false, responsive: true }
        };
      }

      // If chartData type is 'plotly' and has config, use it
      if (chartData.type === 'plotly' && chartData.config) {
        console.log('Using Plotly config from type plotly:', chartData.config);
        const plotlyConfig = chartData.config;
        return {
          data: plotlyConfig.data || [],
          layout: plotlyConfig.layout || {},
          config: { displayModeBar: false, responsive: true }
        };
      }

      // Handle simple chart data formats from server or AI-generated charts
      const chartType = chartData.type || 'bar';
      const chartTitle = chartData.title || 'Chart';
      const chartDataArray = chartData.data || [];

      if (!chartDataArray || chartDataArray.length === 0) {
        throw new Error(`No data provided for chart. Chart type: ${chartType}, Data: ${JSON.stringify(chartDataArray)}`);
      }

      // Validate data structure
      const validData = chartDataArray.filter(item =>
        item &&
        typeof item === 'object' &&
        (item.name || item.label || item.x) &&
        (typeof item.value === 'number' || typeof item.y === 'number' || !isNaN(Number(item.value || item.y)))
      );

      if (validData.length === 0) {
        throw new Error(`No valid data items found. Chart type: ${chartType}, Original data: ${JSON.stringify(chartDataArray)}`);
      }

      console.log(`Processing simple chart - Type: ${chartType}, Title: ${chartTitle}, Valid data length: ${validData.length}/${chartDataArray.length}`);

      // Create enhanced Plotly configuration with better value display
      let plotData;

      if (chartType === 'donut' || chartType === 'pie') {
        // Truncate long labels to prevent legend overflow
        const truncateLabel = (label, maxLength = 15) => {
          const str = String(label);
          return str.length > maxLength ? str.substring(0, maxLength) + '...' : str;
        };
        
        const labels = validData.map(item => truncateLabel(item.name || item.label || item.x || 'Unknown'));
        const values = validData.map(item => Number(item.value || item.y || 0));

        // Generate better colors
        const colors = [
          '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ];

        plotData = [{
          labels: labels,
          values: values,
          type: 'pie',
          hole: chartType === 'donut' ? 0.4 : 0,
          // Adjust pie chart size based on container
          domain: {
            x: [0.1, 0.9],
            y: [0.1, 0.75] // Reduced from 0.8 to give more space for legend
          },
          marker: {
            colors: validData.map((item, index) => item.color || colors[index % colors.length]),
            line: {
              color: '#ffffff',
              width: 2
            }
          },
          textinfo: 'percent',
          textposition: 'inside',
          textfont: {
            size: isFullscreen ? 12 : 10,
            color: '#ffffff'
          },
          // Remove external labels to prevent overlap
          texttemplate: '%{percent:.1%}',
          hovertemplate: '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent:.1%}<extra></extra>'
        }];

        console.log('Pie/Donut chart data:', { labels, values, validData });
      } else if (chartType === 'heatmap') {
        // Handle heatmap charts
        const names = chartDataArray.map(item => item.name || item.label || item.x || 'Unknown');
        const values = chartDataArray.map(item => item.value || item.y || 0);

        plotData = [{
          z: [values], // Single row heatmap
          x: names,
          y: ['Value'],
          type: 'heatmap',
          colorscale: 'RdYlBu_r',
          hoverongaps: false,
          hovertemplate: '<b>%{x}</b><br>Value: %{z}<extra></extra>',
          showscale: true
        }];
      } else {
        const xData = validData.map(item => String(item.name || item.label || item.x || 'Unknown'));
        const yData = validData.map(item => Number(item.value || item.y || 0));

        // Generate better colors for bar charts
        const colors = [
          '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ];

        // Create a simple, reliable trace configuration
        const trace = {
          x: xData,
          y: yData,
          type: chartType === 'line' ? 'scatter' : chartType,
          name: 'Count',
          text: yData.map(val => `${val}`),
          textposition: 'outside',
          textfont: {
            size: 12,
            color: '#000'
          },
          showlegend: false
        };

        // Add mode for line charts
        if (chartType === 'line') {
          trace.mode = 'lines+markers';
          trace.line = {
            color: '#1976d2',
            width: 3
          };
          trace.marker = {
            color: '#1976d2',
            size: 8
          };
        } else {
          // Add marker configuration for bar/scatter charts
          trace.marker = {
            color: validData.map((item, index) => item.color || colors[index % colors.length]),
            line: {
              color: 'rgba(255,255,255,0.6)',
              width: 1
            },
            opacity: 0.8
          };

          if (chartType === 'scatter') {
            trace.marker.size = 10;
          }

          // Ensure hover works properly for bars
          if (chartType === 'bar') {
            // Let hovertemplate handle the display
          }
        }

        // Keep it simple - let Plotly handle hover automatically

        plotData = [trace];
        console.log('Bar/Line/Scatter chart data:', {
          chartType,
          xData,
          yData,
          validData,
          trace: trace
        });
      }

      // Truncate chart title if too long
      const truncateTitle = (title, maxLength = 40) => {
        const str = String(title);
        return str.length > maxLength ? str.substring(0, maxLength) + '...' : str;
      };

      // Create responsive layout configuration based on fullscreen mode and container size
      const layout = {
        title: {
          text: truncateTitle(chartTitle),
          font: { size: isFullscreen ? 18 : 13, color: '#092f57' },
          x: 0.5,
          pad: { t: isFullscreen ? 30 : 20 }, // Increased top padding for more space between title and chart
          // Improve title display for long titles
          xref: 'paper',
          yref: 'paper',
          xanchor: 'center',
          yanchor: 'top'
        },
        margin: {
          l: chartType === 'donut' || chartType === 'pie' ? (isFullscreen ? 80 : 40) : (isFullscreen ? 100 : 60),
          r: chartType === 'donut' || chartType === 'pie' ? (isFullscreen ? 80 : 40) : (isFullscreen ? 80 : 40),
          t: isFullscreen ? 100 : 60, // Increased top margin for more space between title and chart
          b: chartType === 'donut' || chartType === 'pie' ? (isFullscreen ? 60 : 40) : (isFullscreen ? 60 : 40) // Reduced bottom margin to reduce space between chart and description
        },
        autosize: true,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Roboto, sans-serif', size: isFullscreen ? 14 : 11 }
      };

      // Add legend for pie/donut charts with responsive sizing
      if (chartType === 'donut' || chartType === 'pie') {
        layout.showlegend = true;
        layout.legend = {
          orientation: 'h', // Always horizontal for better space utilization
          x: 0.5,
          xanchor: 'center',
          y: -0.1, // Move legend even closer to chart to reduce bottom space
          yanchor: 'top',
          font: { size: isFullscreen ? 11 : 9 },
          bgcolor: 'rgba(255,255,255,0.95)',
          bordercolor: 'rgba(0,0,0,0.1)',
          borderwidth: 1,
          // More compact legend layout
          itemsizing: 'constant',
          itemwidth: 15,
          itemheight: 12,
          // Better legend text handling
          traceorder: 'normal',
          itemclick: false,
          itemdoubleclick: false
        };
      } else {
        layout.showlegend = false;
      }

      // Add axes for non-pie charts with responsive sizing
      if (chartType !== 'donut' && chartType !== 'pie') {
        layout.xaxis = {
          showgrid: true,
          gridcolor: 'rgba(0,0,0,0.1)',
          tickfont: { size: isFullscreen ? 12 : 9 },
          tickangle: -45,
          automargin: true,
          title: {
            text: '',
            font: { size: isFullscreen ? 14 : 11 }
          }
        };
        layout.yaxis = {
          showgrid: true,
          gridcolor: 'rgba(0,0,0,0.1)',
          tickfont: { size: isFullscreen ? 12 : 9 },
          automargin: true,
          title: {
            text: 'Count',
            font: { size: isFullscreen ? 14 : 11 }
          }
        };
      }

      // Disable hover completely
      layout.hovermode = false;

      // Add donut center annotation
      if (chartType === 'donut') {
        layout.annotations = [{
          text: `<b>Total</b><br>${validData.reduce((sum, item) => sum + (item.value || 0), 0)}`,
          x: 0.5,
          y: 0.5,
          xref: 'paper',
          yref: 'paper',
          showarrow: false,
          font: { size: 14, color: '#333' },
          align: 'center'
        }];
      }

      const config = {
        displayModeBar: false,
        responsive: true,
        showTips: false,
        showAxisDragHandles: false,
        showAxisRangeEntryBoxes: false,
        doubleClick: 'reset',
        staticPlot: false,
        scrollZoom: false,
        editable: false,
        autosizable: true
      };

      return { data: plotData, layout, config };
    } catch (err) {
      console.error('Error processing chart data:', err);
      throw new Error('Failed to process chart data');
    }
  };

  const handleDownload = () => {
    if (plotRef.current) {
      // Use Plotly's built-in download functionality
      const plotElement = plotRef.current.el;
      if (plotElement && window.Plotly) {
        window.Plotly.downloadImage(plotElement, {
          format: 'png',
          width: 800,
          height: 600,
          filename: 'safety-chart'
        });
      }
    }
  };

  const handleFullscreen = () => {
    // Implement fullscreen functionality
    console.log('Fullscreen chart');
  };

  try {
    const { data, layout, config } = processChartData();

    console.log('Final chart data for rendering:', {
      dataLength: data?.length,
      layoutTitle: layout?.title?.text,
      chartType: chartData.type,
      hasConfig: !!chartData.config
    });

    // Dynamic sizing based on fullscreen mode and container context
    const chartHeight = isFullscreen ? '500px' : '100%';
    const containerMinHeight = isFullscreen ? '500px' : '300px';

    return (
      <Box sx={{
        position: 'relative',
        width: '100%',
        minHeight: containerMinHeight,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 2, // Changed to 2 for very subtle rounded corners
        '& .plotly': {
          width: '100% !important',
          height: '100% !important',
          flex: 1,
          borderRadius: 2, // Changed to 2 for very subtle rounded corners
        },
        '& .plotly .main-svg': {
          overflow: 'visible !important',
          borderRadius: 2, // Changed to 2 for very subtle rounded corners
        },
        '& .hoverlayer': {
          pointerEvents: 'none !important'
        },
        '& *': {
          borderRadius: 2, // Changed to 2 for very subtle rounded corners
        }
      }}>
        {/* Chart Controls */}
        <Box
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            zIndex: 10,
            display: 'flex',
            gap: 0.5,
          }}
        >
          <Tooltip title="Download chart">
            <IconButton
              size="small"
              onClick={handleDownload}
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.8)',
                '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.9)' },
              }}
            >
              <DownloadIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Fullscreen">
            <IconButton
              size="small"
              onClick={handleFullscreen}
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.8)',
                '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.9)' },
              }}
            >
              <FullscreenIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Plotly Chart */}
        <Plot
          ref={plotRef}
          data={data}
          layout={layout}
          config={{
            ...config,
            displayModeBar: false,
            responsive: true,
            toImageButtonOptions: {
              format: 'png',
              filename: 'chart',
              height: isFullscreen ? 600 : 400,
              width: isFullscreen ? 900 : 600,
              scale: 1
            }
          }}
          style={{
            width: '100%',
            height: chartHeight,
            minHeight: containerMinHeight,
            minWidth: 0, // Allow chart to shrink properly
            flex: 1,
            padding: '8px 0', // Reduced padding to center chart better
            borderRadius: 2, // Changed to 2 for very subtle rounded corners
          }}
          useResizeHandler={true}
          onInitialized={() => console.log('Plotly chart initialized successfully')}
          onError={(err) => console.error('Plotly chart error:', err)}
          onUpdate={(figure) => {
            // Ensure chart resizes properly after updates
            if (plotRef.current) {
              plotRef.current.resize();
            }
          }}
        />

        {/* Chart Info */}
        {chartData.title && (
          <Typography
            variant="caption"
            sx={{
              display: 'block',
              textAlign: 'center',
              mt: 0.25, // Further reduced margin top to bring description closer to chart
              color: '#64748b',
              fontStyle: 'italic',
              wordBreak: 'break-word',
              overflowWrap: 'break-word',
              maxWidth: '100%',
              px: 1,
              flexShrink: 0
            }}
          >
            {chartData.title}
          </Typography>
        )}
      </Box>
    );
  } catch (err) {
    console.error('Error rendering chart:', err);
    console.error('Chart data that caused error:', chartData);
    return (
      <Alert severity="error" sx={{ my: 2 }}>
        Failed to render chart: {err.message}
        <Typography variant="body2" sx={{ mt: 1, fontSize: '0.75rem' }}>
          Debug: {JSON.stringify(chartData, null, 2)}
        </Typography>
      </Alert>
    );
  }
};

export default PlotlyChart;
