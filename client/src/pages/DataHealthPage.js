/**
 * Data Health Page
 * Simplified data health assessment with hardcoded values and 5-dimensional analysis
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  Chip,
  IconButton,
  Paper,
  Alert,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import InfoIcon from '@mui/icons-material/Info';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import StorageIcon from '@mui/icons-material/Storage';
import SecurityIcon from '@mui/icons-material/Security';
import ScheduleIcon from '@mui/icons-material/Schedule';
import VerifiedIcon from '@mui/icons-material/Verified';
import AssessmentIcon from '@mui/icons-material/Assessment';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import { motion } from 'framer-motion';

// Hardcoded data health values
const HEALTH_DATA = {
  overall_health: {
    score: 78,
    grade: "Good",
    timestamp: new Date().toISOString()
  },
  dimensions: {
    completeness: {
      score: 85,
      columns_assessed: 12
    },
    uniqueness: {
      score: 92,
      columns_assessed: 8
    },
    consistency: {
      score: 73,
      columns_assessed: 15
    },
    validity: {
      score: 81,
      columns_assessed: 10
    },
    timeliness: {
      score: 65,
      columns_assessed: 6
    }
  },
  column_analysis: {
    // Column 1-6: Core identification
    "event_id": {
      overall_column_score: 98,
      priority: "critical",
      dimensions_checked: ["completeness", "uniqueness", "validity"],
      dimensions_skipped: ["timeliness"],
      issues: ["1 duplicate entry found"]
    },
    "reporter_name": {
      overall_column_score: 92,
      priority: "high",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["3 missing values"]
    },
    "manager_name": {
      overall_column_score: 87,
      priority: "high",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["8 missing values"]
    },
    "branch": {
      overall_column_score: 94,
      priority: "medium",
      dimensions_checked: ["completeness", "consistency"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["2 inconsistent branch names"]
    },
    "reported_date": {
      overall_column_score: 96,
      priority: "critical",
      dimensions_checked: ["completeness", "validity", "timeliness"],
      dimensions_skipped: ["uniqueness"],
      issues: ["1 future date detected"]
    },
    "reporter_id": {
      overall_column_score: 89,
      priority: "high",
      dimensions_checked: ["completeness", "uniqueness", "validity"],
      dimensions_skipped: ["timeliness"],
      issues: ["5 missing values"]
    },

    // Column 7-12: Event timing and details
    "date_of_unsafe_event": {
      overall_column_score: 91,
      priority: "critical",
      dimensions_checked: ["completeness", "validity", "timeliness"],
      dimensions_skipped: ["uniqueness"],
      issues: ["3 future dates detected"]
    },
    "time": {
      overall_column_score: 78,
      priority: "medium",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["15 invalid time formats"]
    },
    "time_of_unsafe_event": {
      overall_column_score: 82,
      priority: "medium",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["12 missing values"]
    },
    "unsafe_event_type": {
      overall_column_score: 85,
      priority: "high",
      dimensions_checked: ["completeness", "consistency"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["7 inconsistent categorizations"]
    },
    "business_details": {
      overall_column_score: 73,
      priority: "medium",
      dimensions_checked: ["completeness"],
      dimensions_skipped: ["uniqueness", "validity", "timeliness"],
      issues: ["18 missing values"]
    },
    "site_reference": {
      overall_column_score: 88,
      priority: "medium",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["6 invalid references"]
    },

    // Column 13-20: Location and product
    "unsafe_event_location": {
      overall_column_score: 90,
      priority: "high",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["4 missing values"]
    },
    "product_type": {
      overall_column_score: 84,
      priority: "medium",
      dimensions_checked: ["completeness", "consistency"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["9 inconsistent product types"]
    },
    "employee_id": {
      overall_column_score: 93,
      priority: "critical",
      dimensions_checked: ["completeness", "uniqueness", "validity"],
      dimensions_skipped: ["timeliness"],
      issues: ["2 duplicate entries"]
    },
    "employee_name": {
      overall_column_score: 91,
      priority: "high",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["3 missing values"]
    },
    "subcontractor_company_name": {
      overall_column_score: 76,
      priority: "medium",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["14 missing values"]
    },
    "subcontractor_id": {
      overall_column_score: 79,
      priority: "medium",
      dimensions_checked: ["completeness", "uniqueness"],
      dimensions_skipped: ["validity", "timeliness"],
      issues: ["11 missing values"]
    },
    "subcontractor_city": {
      overall_column_score: 81,
      priority: "medium",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["10 missing values"]
    },
    "subcontractor_name": {
      overall_column_score: 77,
      priority: "medium",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["13 missing values"]
    },

    // Column 21-28: Location hierarchy
    "kg_name": {
      overall_column_score: 95,
      priority: "high",
      dimensions_checked: ["completeness", "consistency"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["2 missing values"]
    },
    "country_name": {
      overall_column_score: 97,
      priority: "high",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["1 missing value"]
    },
    "division": {
      overall_column_score: 93,
      priority: "high",
      dimensions_checked: ["completeness", "consistency"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["3 missing values"]
    },
    "department": {
      overall_column_score: 89,
      priority: "medium",
      dimensions_checked: ["completeness", "consistency"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["6 missing values"]
    },
    "city": {
      overall_column_score: 91,
      priority: "medium",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["4 missing values"]
    },
    "sub_area": {
      overall_column_score: 86,
      priority: "medium",
      dimensions_checked: ["completeness", "consistency"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["7 missing values"]
    },
    "district": {
      overall_column_score: 88,
      priority: "medium",
      dimensions_checked: ["completeness", "consistency"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["5 missing values"]
    },
    "zone": {
      overall_column_score: 92,
      priority: "high",
      dimensions_checked: ["completeness", "consistency"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["3 missing values"]
    },

    // Column 29-33: Event classification
    "serious_near_miss": {
      overall_column_score: 94,
      priority: "critical",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["2 missing values"]
    },
    "unsafe_act": {
      overall_column_score: 87,
      priority: "high",
      dimensions_checked: ["completeness", "consistency"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["8 inconsistent categorizations"]
    },
    "unsafe_act_other": {
      overall_column_score: 71,
      priority: "low",
      dimensions_checked: ["completeness"],
      dimensions_skipped: ["uniqueness", "validity", "timeliness"],
      issues: ["20 missing values"]
    },
    "unsafe_condition": {
      overall_column_score: 83,
      priority: "high",
      dimensions_checked: ["completeness", "consistency"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["10 inconsistent categorizations"]
    },
    "unsafe_condition_other": {
      overall_column_score: 69,
      priority: "low",
      dimensions_checked: ["completeness"],
      dimensions_skipped: ["uniqueness", "validity", "timeliness"],
      issues: ["22 missing values"]
    },

    // Column 34-37: Work stoppage
    "work_stopped": {
      overall_column_score: 96,
      priority: "high",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["1 missing value"]
    },
    "stop_work_nogo_violation": {
      overall_column_score: 85,
      priority: "medium",
      dimensions_checked: ["completeness", "consistency"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["9 missing values"]
    },
    "nogo_violation_detail": {
      overall_column_score: 74,
      priority: "low",
      dimensions_checked: ["completeness"],
      dimensions_skipped: ["uniqueness", "validity", "timeliness"],
      issues: ["17 missing values"]
    },
    "stop_work_duration": {
      overall_column_score: 79,
      priority: "medium",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["12 missing values"]
    },

    // Column 38-40: Additional details
    "other_safety_issues": {
      overall_column_score: 68,
      priority: "low",
      dimensions_checked: ["completeness"],
      dimensions_skipped: ["uniqueness", "validity", "timeliness"],
      issues: ["23 missing values"]
    },
    "comments_remarks": {
      overall_column_score: 72,
      priority: "low",
      dimensions_checked: ["completeness"],
      dimensions_skipped: ["uniqueness", "validity", "timeliness"],
      issues: ["19 missing values"]
    },
    "event_requires_sanction": {
      overall_column_score: 93,
      priority: "high",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["3 missing values"]
    },

    // Column 41-45: Actions taken
    "action_description_1": {
      overall_column_score: 81,
      priority: "medium",
      dimensions_checked: ["completeness"],
      dimensions_skipped: ["uniqueness", "validity", "timeliness"],
      issues: ["11 missing values"]
    },
    "action_description_2": {
      overall_column_score: 67,
      priority: "low",
      dimensions_checked: ["completeness"],
      dimensions_skipped: ["uniqueness", "validity", "timeliness"],
      issues: ["24 missing values"]
    },
    "action_description_3": {
      overall_column_score: 58,
      priority: "low",
      dimensions_checked: ["completeness"],
      dimensions_skipped: ["uniqueness", "validity", "timeliness"],
      issues: ["31 missing values"]
    },
    "action_description_4": {
      overall_column_score: 52,
      priority: "low",
      dimensions_checked: ["completeness"],
      dimensions_skipped: ["uniqueness", "validity", "timeliness"],
      issues: ["35 missing values"]
    },
    "action_description_5": {
      overall_column_score: 48,
      priority: "low",
      dimensions_checked: ["completeness"],
      dimensions_skipped: ["uniqueness", "validity", "timeliness"],
      issues: ["38 missing values"]
    },

    // Column 46-48: Final details
    "image": {
      overall_column_score: 89,
      priority: "medium",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["6 missing values"]
    },
    "status": {
      overall_column_score: 95,
      priority: "high",
      dimensions_checked: ["completeness", "validity"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["2 missing values"]
    },
    "region": {
      overall_column_score: 94,
      priority: "high",
      dimensions_checked: ["completeness", "consistency"],
      dimensions_skipped: ["uniqueness", "timeliness"],
      issues: ["3 missing values"]
    }
  },

};

const DataHealthPage = () => {
  const navigate = useNavigate();

  const getHealthGradeColor = (grade) => {
    switch (grade.toLowerCase()) {
      case "excellent": return "success";
      case "good": return "primary";
      case "poor": return "warning";
      case "bad": return "error";
      default: return "default";
    }
  };

  const getHealthIcon = (grade) => {
    switch (grade.toLowerCase()) {
      case "excellent": return <CheckCircleIcon color="success" />;
      case "good": return <CheckCircleIcon color="primary" />;
      case "poor": return <WarningIcon color="warning" />;
      case "bad": return <ErrorIcon color="error" />;
      default: return <CheckCircleIcon />;
    }
  };

  const getDimensionIcon = (dimension) => {
    switch (dimension) {
      case "completeness": return <StorageIcon />;
      case "uniqueness": return <VerifiedIcon />;
      case "consistency": return <SecurityIcon />;
      case "validity": return <CheckCircleIcon />;
      case "timeliness": return <ScheduleIcon />;
      default: return <AssessmentIcon />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority.toLowerCase()) {
      case "critical": return "error";
      case "high": return "warning";
      case "medium": return "info";
      case "low": return "default";
      default: return "default";
    }
  };

  const dimensionColors = {
    completeness: "#1976d2",
    uniqueness: "#2e7d32",
    consistency: "#ed6c02",
    validity: "#9c27b0",
    timeliness: "#d32f2f"
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', p: 3 }}>
      <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton
              onClick={() => navigate('/dashboard')}
              sx={{ color: 'primary.main' }}
            >
              <ArrowBackIcon />
            </IconButton>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <img 
                src="/database_health.png" 
                alt="Database Health" 
                style={{ 
                  width: 48, 
                  height: 48, 
                  borderRadius: '8px',
                  objectFit: 'cover'
                }} 
              />
              <Box>
                <Typography variant="h4" component="h1" fontWeight="bold" color="primary">
                  Data Health Assessment
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Monitor and maintain data quality across your safety systems
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>

        {/* Overall Health Score */}
        <Card sx={{ mb: 4 }}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
              <Box>
                <Typography variant="h5" component="h2" fontWeight="semibold">
                  Overall Data Health Score
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Assessment Date: {new Date(HEALTH_DATA.overall_health.timestamp).toLocaleDateString()}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                {getHealthIcon(HEALTH_DATA.overall_health.grade)}
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="h3" component="div" fontWeight="bold">
                    {HEALTH_DATA.overall_health.score}%
                  </Typography>
                  <Chip 
                    label={HEALTH_DATA.overall_health.grade}
                    color={getHealthGradeColor(HEALTH_DATA.overall_health.grade)}
                    size="small"
                  />
                </Box>
              </Box>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={HEALTH_DATA.overall_health.score} 
              sx={{ height: 8, borderRadius: 4 }}
            />
          </CardContent>
        </Card>

        {/* Dimension Scores */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {Object.entries(HEALTH_DATA.dimensions).map(([dimension, data]) => (
            <Grid item xs={12} sm={6} md={2.4} key={dimension}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Card sx={{ height: '100%' }}>
                  <CardContent sx={{ p: 3, textAlign: 'center' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
                      <Box sx={{ 
                        color: dimensionColors[dimension],
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1
                      }}>
                        {getDimensionIcon(dimension)}
                        <Typography variant="h6" component="h3" sx={{ textTransform: 'capitalize' }}>
                          {dimension}
                        </Typography>
                      </Box>
                    </Box>
                    <Typography variant="h4" component="div" fontWeight="bold" sx={{ mb: 2 }}>
                      {data.score}%
                    </Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={data.score} 
                      sx={{ 
                        height: 6, 
                        borderRadius: 3,
                        bgcolor: 'grey.200',
                        '& .MuiLinearProgress-bar': {
                          bgcolor: dimensionColors[dimension]
                        }
                      }}
                    />
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                      {data.columns_assessed} columns assessed
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        {/* Column Analysis */}
        <Card>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h5" component="h2" fontWeight="semibold" sx={{ mb: 3 }}>
              Column Analysis ({Object.keys(HEALTH_DATA.column_analysis).length} columns)
            </Typography>
            
            <Box sx={{ 
              maxHeight: '600px', 
              overflowY: 'auto',
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                background: '#f1f1f1',
                borderRadius: '4px',
              },
              '&::-webkit-scrollbar-thumb': {
                background: '#c1c1c1',
                borderRadius: '4px',
                '&:hover': {
                  background: '#a8a8a8',
                },
              },
            }}>
              <Grid container spacing={3}>
                {Object.entries(HEALTH_DATA.column_analysis).map(([columnName, analysis]) => (
                  <Grid item xs={12} md={6} lg={4} key={columnName}>
                    <Paper sx={{ 
                      p: 3, 
                      border: '1px solid', 
                      borderColor: 'divider',
                      height: '100%',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                        transform: 'translateY(-2px)',
                      }
                    }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                        <Typography variant="h6" component="h3" fontWeight="medium" sx={{ 
                          fontSize: '0.9rem',
                          wordBreak: 'break-word'
                        }}>
                          {columnName.replace(/_/g, ' ')}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Chip 
                            label={analysis.priority}
                            color={getPriorityColor(analysis.priority)}
                            size="small"
                            sx={{ fontSize: '0.7rem' }}
                          />
                          <Typography variant="body2" fontWeight="medium">
                            {analysis.overall_column_score}%
                          </Typography>
                        </Box>
                      </Box>
                      
                      <LinearProgress 
                        variant="determinate" 
                        value={analysis.overall_column_score} 
                        sx={{ height: 6, borderRadius: 3, mb: 2 }}
                      />
                      
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                        <Typography variant="caption" color="text.secondary">
                          Checked:
                        </Typography>
                        {analysis.dimensions_checked.map((dim) => (
                          <Chip 
                            key={dim} 
                            label={dim} 
                            size="small" 
                            variant="outline"
                            sx={{ fontSize: '0.6rem' }}
                          />
                        ))}
                      </Box>
                      
                      {analysis.dimensions_skipped.length > 0 && (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                          <Typography variant="caption" color="text.secondary">
                            Skipped:
                          </Typography>
                          {analysis.dimensions_skipped.map((dim) => (
                            <Chip 
                              key={dim} 
                              label={dim} 
                              size="small" 
                              variant="outline"
                              sx={{ fontSize: '0.6rem', bgcolor: 'grey.100' }}
                            />
                          ))}
                        </Box>
                      )}
                      
                      {analysis.issues.length > 0 && (
                        <Alert severity="warning" sx={{ mt: 2 }}>
                          <Typography variant="caption">
                            {analysis.issues.join(', ')}
                          </Typography>
                        </Alert>
                      )}
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Box>
          </CardContent>
        </Card>

        {/* AI Recommendations */}
        <Card sx={{ mt: 4 }}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <LightbulbIcon sx={{ color: 'primary.main', fontSize: 28 }} />
              <Typography variant="h5" component="h2" fontWeight="semibold">
                AI Recommendations
              </Typography>
            </Box>
            
            <List>
              <ListItem sx={{ px: 0, py: 1 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <CheckCircleIcon sx={{ color: 'success.main' }} />
                </ListItemIcon>
                <ListItemText 
                  primary="Implement data validation for employee_id and event_id fields"
                  secondary="Critical fields showing 2-3% duplicate entries need immediate attention to maintain data integrity."
                />
              </ListItem>
              
              <ListItem sx={{ px: 0, py: 1 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <CheckCircleIcon sx={{ color: 'success.main' }} />
                </ListItemIcon>
                <ListItemText 
                  primary="Standardize time format validation across time and time_of_unsafe_event columns"
                  secondary="15 invalid time formats detected suggest inconsistent data entry patterns."
                />
              </ListItem>
              
              <ListItem sx={{ px: 0, py: 1 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <CheckCircleIcon sx={{ color: 'success.main' }} />
                </ListItemIcon>
                <ListItemText 
                  primary="Create mandatory field requirements for unsafe_event_type and unsafe_event_location"
                  secondary="High-priority fields with 7-10% missing values impact incident analysis accuracy."
                />
              </ListItem>
              
              <ListItem sx={{ px: 0, py: 1 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <CheckCircleIcon sx={{ color: 'success.main' }} />
                </ListItemIcon>
                <ListItemText 
                  primary="Establish data quality monitoring for subcontractor information fields"
                  secondary="Subcontractor fields show 10-14% missing values, affecting compliance tracking."
                />
              </ListItem>
              
              <ListItem sx={{ px: 0, py: 1 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <CheckCircleIcon sx={{ color: 'success.main' }} />
                </ListItemIcon>
                <ListItemText 
                  primary="Optimize action description fields with progressive disclosure approach"
                  secondary="Action description fields 3-5 show 31-38% missing values, suggesting optional nature."
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>

      </Box>
    </Box>
  );
};

export default DataHealthPage; 