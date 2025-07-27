/**
 * EI Tech Dashboard Charts Component
 * Displays standardized dashboard data for EI Tech unsafe events
 * 12 KPIs with consistent styling patterns
 */

import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Alert,
  alpha,
  Chip
} from '@mui/material';
import {
  Timeline as ActivityIcon,
  Warning as AlertIcon,
  PowerOff as LightningIcon,
  AccessTime as ClockIcon,
  TrendingUp as TrendIcon,
  LocationOn as LocationIcon,
  Assessment as AssessmentIcon,
  Speed as SpeedIcon,
  BarChart as BarChartIcon,
  Schedule as TimeIcon,
  PieChart as PieChartIcon,
  ShowChart as LineChartIcon,
  CalendarToday as CalendarIcon,
  Business as BusinessIcon
} from '@mui/icons-material';
import ReactECharts from 'echarts-for-react';
import { motion } from 'framer-motion';

// Color scheme consistent with other dashboards
const colors = {
  primary: '#1e40af',
  secondary: '#059669',
  success: '#059669',
  warning: '#d97706',
  error: '#dc2626',
  info: '#0284c7',
  purple: '#7c3aed',
  gray: '#6b7280'
};

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 30, scale: 0.9 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.6,
      ease: [0.4, 0, 0.2, 1],
      type: "spring",
      stiffness: 100,
      damping: 15
    }
  }
};

const chartVariants = {
  hidden: { opacity: 0, y: 40, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.8,
      ease: [0.4, 0, 0.2, 1],
      type: "spring",
      stiffness: 80,
      damping: 20
    }
  }
};

// StatCard component with small icon and text
const StatCard = ({ title, value, icon, color = 'primary', subtitle = null }) => (
  <motion.div
    variants={itemVariants}
    whileHover={{
      scale: 1.02,
      y: -4,
      transition: { duration: 0.2 }
    }}
  >
    <Card sx={{
      height: 100,
      bgcolor: alpha(colors[color], 0.05),
      borderRadius: 2, // Changed to 2 for very subtle rounded corners
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      borderLeft: `4px solid ${colors[color]}`,
      '&:hover': {
        bgcolor: alpha(colors[color], 0.08),
        boxShadow: `0 8px 32px ${alpha(colors[color], 0.12)}`,
      }
    }}>
      <CardContent sx={{ height: '100%', p: 1.5, '&:last-child': { pb: 1.5 } }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
          {React.cloneElement(icon, { 
            sx: { fontSize: 16, color: colors[color], mr: 1 }
          })}
          <Typography 
            variant="body2" 
            sx={{ 
              color: 'text.secondary',
              fontSize: '0.75rem',
              fontWeight: 500,
              lineHeight: 1.2
            }}
          >
            {title}
          </Typography>
        </Box>
        <Typography 
          variant="h5" 
          sx={{ 
            fontWeight: 700, 
            color: colors[color],
            fontSize: '1.25rem',
            lineHeight: 1.2,
            mb: 0.5
          }}
        >
          {value}
        </Typography>
        {subtitle && (
          <Typography 
            variant="caption" 
            sx={{ 
              color: 'text.disabled',
              fontSize: '0.65rem'
            }}
          >
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  </motion.div>
);

// Chart wrapper component
const ChartCard = ({ title, children, height = 400, icon = null }) => (
  <motion.div variants={chartVariants}>
    <Card sx={{
      borderRadius: 2, // Changed to 2 for very subtle rounded corners
      bgcolor: 'background.paper',
      border: '1px solid',
      borderColor: 'divider',
      '&:hover': {
        borderColor: 'primary.main',
        boxShadow: (theme) => `0 4px 20px ${alpha(theme.palette.primary.main, 0.08)}`
      },
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
    }}>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          {icon && (
            <Box sx={{ mr: 1.5, display: 'flex', alignItems: 'center' }}>
              {React.cloneElement(icon, { 
                sx: { 
                  fontSize: 20, 
                  color: '#1e40af' 
                } 
              })}
            </Box>
          )}
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 600,
              color: 'text.primary',
              fontSize: '1.125rem'
            }}
          >
            {title}
          </Typography>
        </Box>
        <Box sx={{ height: height }}>
          {children}
        </Box>
      </CardContent>
    </Card>
  </motion.div>
);

const EITechDashboardCharts = ({ data }) => {
  // Handle loading or empty data state
  if (!data || !data.dashboard_data) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <Alert severity="info" sx={{ borderRadius: 2 }}>
          Loading EI Tech dashboard data...
        </Alert>
      </motion.div>
    );
  }

  const dashboardData = data.dashboard_data;

  // Helper function to format numbers
  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num?.toString() || '0';
  };

  // Helper function to format percentage
  const formatPercentage = (num) => {
    return `${num?.toFixed(1) || '0'}%`;
  };

  // Monthly trends chart - Multi-line chart
  const monthlyTrendsChart = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: colors.primary,
      borderWidth: 1,
      textStyle: { color: '#333' },
      formatter: function(params) {
        let tooltip = `<strong>${params[0].axisValue}</strong><br/>`;
        params.forEach(param => {
          tooltip += `${param.marker} ${param.seriesName}: ${param.value}<br/>`;
        });
        return tooltip;
      }
    },
    legend: {
      data: ['Total Events', 'Serious Events', 'Work Stoppages'],
      bottom: 0,
      textStyle: { color: '#666' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dashboardData.monthly_trends?.map(item => item.month) || [],
      axisLabel: { color: '#666' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#666' }
    },
    series: [
      {
        name: 'Total Events',
        data: dashboardData.monthly_trends?.map(item => item.event_count) || [],
        type: 'line',
        smooth: true,
        lineStyle: { color: colors.primary, width: 3 },
        itemStyle: { color: colors.primary }
      },
      {
        name: 'Serious Events',
        data: dashboardData.monthly_trends?.map(item => item.serious_count) || [],
        type: 'line',
        smooth: true,
        lineStyle: { color: colors.warning, width: 3 },
        itemStyle: { color: colors.warning }
      },
      {
        name: 'Work Stoppages',
        data: dashboardData.monthly_trends?.map(item => item.work_stopped_count) || [],
        type: 'line',
        smooth: true,
        lineStyle: { color: colors.error, width: 3 },
        itemStyle: { color: colors.error }
      }
    ]
  };

  // Event type distribution chart - Doughnut Chart
  const eventTypeChart = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: 0,
      textStyle: { color: '#666' }
    },
    series: [{
      name: 'Event Types',
      type: 'pie',
      radius: ['50%', '80%'],
      center: ['50%', '45%'],
      data: dashboardData.event_type_distribution?.map(item => ({
        value: item.event_count,
        name: item.event_type
      })) || [],
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        color: '#666',
        formatter: '{d}%'
      },
      labelLine: {
        show: true
      }
    }]
  };

  // Top 5 Branches - Multi-Bar Chart
  const top5BranchesChart = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['Total Incidents', 'Serious Incidents', 'Work Stoppages'],
      bottom: 0,
      textStyle: { color: '#666' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dashboardData.branch_performance_analysis?.map(item => item.branch) || [],
      axisLabel: { 
        color: '#666',
        rotate: 30,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#666' }
    },
    series: [
      {
        name: 'Total Incidents',
        type: 'bar',
        data: dashboardData.branch_performance_analysis?.map(item => item.total_incidents) || [],
        itemStyle: { color: colors.primary },
        barWidth: '20%'
      },
      {
        name: 'Serious Incidents',
        type: 'bar',
        data: dashboardData.branch_performance_analysis?.map(item => item.serious_incidents) || [],
        itemStyle: { color: colors.warning },
        barWidth: '20%'
      },
      {
        name: 'Work Stoppages',
        type: 'bar',
        data: dashboardData.branch_performance_analysis?.map(item => item.work_stoppages) || [],
        itemStyle: { color: colors.error },
        barWidth: '20%'
      }
    ]
  };

  // Weekly Pattern - Line Chart
  const weeklyPatternChart = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c} events'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dashboardData.time_based_analysis?.day_of_week_analysis?.map(item => 
        item.day_of_week?.trim().substring(0, 3)
      ) || [],
      axisLabel: { color: '#666' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#666' }
    },
    series: [{
      data: dashboardData.time_based_analysis?.day_of_week_analysis?.map(item => item.incident_count) || [],
      type: 'line',
      smooth: true,
      lineStyle: { color: colors.primary, width: 3 },
      itemStyle: { 
        color: colors.primary,
        borderWidth: 2,
        borderColor: '#fff'
      },
      symbol: 'circle',
      symbolSize: 8
    }]
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Box sx={{ p: 0 }}>
        {/* Header */}


        {/* Key Metrics */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Events"
              value={formatNumber(dashboardData.total_events?.count?.total_events)}
              subtitle={`${formatNumber(dashboardData.total_events?.count?.unique_events)} unique`}
              icon={<ActivityIcon />}
              color="primary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Serious Events"
              value={formatNumber(dashboardData.serious_near_miss_rate?.count?.serious_near_miss_count)}
              subtitle={`${dashboardData.serious_near_miss_rate?.count?.serious_near_miss_percentage || '0'}% rate`}
              icon={<AlertIcon />}
              color="warning"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Work Stoppages"
              value={formatNumber(dashboardData.work_stoppage_rate?.count)}
              subtitle={`${dashboardData.work_stoppage_rate?.rate?.toFixed(2) || '0'}% rate`}
              icon={<LightningIcon />}
              color="error"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Avg Response Time"
              value={dashboardData.response_time_analysis?.average_response_time || 'N/A'}
              subtitle={`${formatNumber(dashboardData.response_time_analysis?.events_analyzed)} events analyzed`}
              icon={<ClockIcon />}
              color="info"
            />
          </Grid>
        </Grid>

        {/* Charts */}
        <Grid container spacing={3}>
          {/* Row 1: Monthly Trends & Event Types */}
          <Grid item xs={12} md={6}>
            <ChartCard title="Monthly Trends" height={350} icon={<LineChartIcon />}>
              <ReactECharts option={monthlyTrendsChart} style={{ height: '100%' }} />
            </ChartCard>
          </Grid>
          <Grid item xs={12} md={6}>
            <ChartCard title="Event Types" height={350} icon={<PieChartIcon />}>
              <ReactECharts option={eventTypeChart} style={{ height: '100%' }} />
            </ChartCard>
          </Grid>

          {/* Row 2: Severity Levels & Weekly Pattern */}
          <Grid item xs={12} md={6}>
            <ChartCard title="Severity Levels" height={350} icon={<AssessmentIcon />}>
              <ReactECharts option={{
                tooltip: {
                  trigger: 'item',
                  formatter: '{a} <br/>{b}: {c} ({d}%)'
                },
                legend: {
                  orient: 'horizontal',
                  bottom: 0,
                  textStyle: { color: '#666' }
                },
                series: [{
                  name: 'Severity Levels',
                  type: 'pie',
                  radius: '70%',
                  center: ['50%', '45%'],
                  data: dashboardData.incident_severity_distribution?.map(item => ({
                    value: item.incident_count,
                    name: item.severity_level,
                    itemStyle: {
                      color: item.severity_level === 'High' ? colors.error :
                             item.severity_level === 'Medium' ? colors.warning : colors.success
                    }
                  })) || [],
                  label: {
                    color: '#666',
                    formatter: '{b}: {d}%'
                  }
                }]
              }} style={{ height: '100%' }} />
            </ChartCard>
          </Grid>
          <Grid item xs={12} md={6}>
            <ChartCard title="Weekly Pattern" height={350} icon={<CalendarIcon />}>
              <ReactECharts option={weeklyPatternChart} style={{ height: '100%' }} />
            </ChartCard>
          </Grid>

          {/* Row 3: Branch Analysis - Full Width */}
          <Grid item xs={12}>
            <ChartCard title="Branch Analysis" height={400} icon={<BusinessIcon />}>
              <ReactECharts option={top5BranchesChart} style={{ height: '100%' }} />
            </ChartCard>
          </Grid>
        </Grid>
      </Box>
    </motion.div>
  );
};

export default EITechDashboardCharts; 