# SafetyConnect API Documentation

## Overview

SafetyConnect is a comprehensive safety management platform that allows users to upload Excel files (SRS, SRS Enriched, SRS Augmented), analyze data health, view KPIs in dashboards, generate AI insights, and interact with data through conversational BI.

## Application Flow

1. **Create New Tab** → User creates a new workspace tab
2. **Upload File** → User uploads an Excel file (SRS, SRS Enriched, or SRS Augmented)
3. **Data Health Check** → System analyzes file health and data quality
4. **Dashboard View** → User views KPIs and analytics in interactive dashboards
5. **AI Insights** → Generate AI-powered insights from the data
6. **Conversational BI** → Chat with the data using natural language queries

---

## File Management Endpoints

### 1. Create New Tab
**Endpoint:** `POST /files/add-tab`

**Description:** Creates a new workspace tab for file management.

**Request Body:**
```json
{
  "tab_name": "string",
  "description": "string (optional)"
}
```

**Response:**
```json
{
  "tab_id": "string",
  "tab_name": "string",
  "status": "created",
  "message": "Tab created successfully"
}
```

### 2. Upload and Analyze File
**Endpoint:** `POST /files/upload-analyze`

**Description:** Uploads an Excel file and performs initial analysis to determine file type and structure.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file`: Excel file (.xlsx, .xls)
  - `tab_id`: Tab ID where file should be uploaded
  - `file_name`: Optional custom file name

**Response:**
```json
{
  "file_id": "string",
  "file_name": "string",
  "file_type": "srs|srs_enriched|srs_agumented",
  "upload_status": "success",
  "analysis_results": {
    "total_rows": 1000,
    "columns_detected": ["event_id", "date_of_unsafe_event", "region"],
    "data_quality_score": 85.5,
    "missing_values": 45,
    "duplicate_records": 12
  },
  "message": "File uploaded and analyzed successfully"
}
```

### 3. Get All Files
**Endpoint:** `GET /files/get-all-files`

**Description:** Retrieves all uploaded files with their metadata and analysis results.

**Query Parameters:**
- `tab_id` (optional): Filter files by tab ID
- `file_type` (optional): Filter by file type (srs, srs_enriched, srs_agumented)

**Response:**
```json
{
  "files": [
    {
      "file_id": "string",
      "file_name": "string",
      "file_type": "srs",
      "tab_id": "string",
      "upload_date": "2025-01-14T10:30:00Z",
      "file_size": 1024000,
      "total_rows": 1000,
      "data_health_score": 85.5,
      "status": "processed"
    }
  ],
  "total_files": 5,
  "summary": {
    "srs_files": 2,
    "srs_enriched_files": 2,
    "srs_agumented_files": 1
  }
}
```

### 4. File Health Analysis
**Endpoint:** `GET /api/v1/file-health`

**Description:** Performs comprehensive data health analysis on uploaded files.

**Query Parameters:**
- `file_id`: ID of the file to analyze
- `include_details` (optional): Include detailed analysis (default: false)

**Response:**
```json
{
  "file_id": "string",
  "file_name": "string",
  "health_score": 85.5,
  "analysis_date": "2025-01-14T10:30:00Z",
  "overall_status": "good",
  "issues": [
    {
      "severity": "warning",
      "category": "data_quality",
      "description": "45 missing values in 'region' column",
      "impact": "medium"
    }
  ],
  "data_quality_metrics": {
    "completeness": 92.5,
    "accuracy": 88.0,
    "consistency": 91.0,
    "timeliness": 95.0
  },
  "column_analysis": [
    {
      "column_name": "event_id",
      "data_type": "string",
      "unique_values": 1000,
      "missing_values": 0,
      "quality_score": 100.0
    }
  ],
  "recommendations": [
    "Consider filling missing region values for better analysis",
    "Verify date format consistency in date_of_unsafe_event column"
  ]
}
```

---

## Dashboard Endpoints

### 5. SRS Dashboard
**Endpoint:** `GET /dashboard/srs`

**Description:** Retrieves comprehensive KPI dashboard data for SRS files.

**Query Parameters:**
- `file_id`: ID of the SRS file
- `start_date` (optional): Filter start date (YYYY-MM-DD)
- `end_date` (optional): Filter end date (YYYY-MM-DD)
- `region` (optional): Filter by region
- `branch` (optional): Filter by branch

**Response:**
```json
{
  "file_id": "string",
  "dashboard_type": "srs",
  "generated_at": "2025-01-14T10:30:00Z",
  "filters_applied": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  },
  "kpis": {
    "total_events_count": {
      "total_events": 1000,
      "unique_events": 995
    },
    "events_by_unsafe_event_type": [
      {
        "unsafe_event_type": "Near Miss",
        "event_count": 450,
        "percentage": 45.0
      }
    ],
    "serious_near_miss_count": {
      "serious_near_miss_count": 150,
      "total_events": 1000,
      "serious_near_miss_rate": 15.0
    },
    "events_by_region_country_division": [
      {
        "region": "North America",
        "country_name": "USA",
        "division": "Manufacturing",
        "event_count": 300,
        "serious_near_miss_count": 45,
        "work_stopped_count": 30
      }
    ]
  },
  "charts": {
    "events_trend": [...],
    "regional_distribution": [...],
    "severity_breakdown": [...]
  }
}
```

### 6. SRS Enriched Dashboard
**Endpoint:** `GET /dashboard/srs-enriched`

**Description:** Retrieves enhanced KPI dashboard data for SRS Enriched files with additional enriched data fields.

**Query Parameters:**
- `file_id`: ID of the SRS Enriched file
- `start_date` (optional): Filter start date (YYYY-MM-DD)
- `end_date` (optional): Filter end date (YYYY-MM-DD)
- `region` (optional): Filter by region
- `branch` (optional): Filter by branch

**Response:**
```json
{
  "file_id": "string",
  "dashboard_type": "srs_enriched",
  "generated_at": "2025-01-14T10:30:00Z",
  "filters_applied": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  },
  "kpis": {
    "total_events_count": {
      "total_events": 1000,
      "unique_events": 995
    },
    "events_by_unsafe_event_type": [...],
    "serious_near_miss_count": {...},
    "events_by_region_country_division": [...],
    "common_unsafe_behaviors": [
      {
        "unsafe_act": "Working without proper PPE",
        "behavior_count": 120,
        "serious_incidents": 25,
        "percentage": 12.0
      }
    ],
    "common_unsafe_conditions": [...],
    "time_taken_to_report_incidents": [
      {
        "reporting_time_category": "Within 1 hour",
        "incident_count": 450,
        "percentage": 45.0
      }
    ]
  },
  "enriched_features": {
    "unsafe_act_analysis": [...],
    "unsafe_condition_analysis": [...],
    "action_tracking": [...],
    "comments_analysis": [...]
  }
}
```

### 7. SRS Augmented Dashboard
**Endpoint:** `GET /dashboard/srs_agumented`

**Description:** Retrieves augmented KPI dashboard data for SRS Augmented files with employee details and enhanced analytics.

**Query Parameters:**
- `file_id`: ID of the SRS Augmented file
- `start_date` (optional): Filter start date (YYYY-MM-DD)
- `end_date` (optional): Filter end date (YYYY-MM-DD)
- `region` (optional): Filter by region
- `branch` (optional): Filter by branch
- `employee_id` (optional): Filter by employee ID

**Response:**
```json
{
  "file_id": "string",
  "dashboard_type": "srs_agumented",
  "generated_at": "2025-01-14T10:30:00Z",
  "filters_applied": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  },
  "kpis": {
    "total_events_count": {
      "total_events": 1000,
      "unique_events": 995
    },
    "events_by_unsafe_event_type": [...],
    "serious_near_miss_count": {...},
    "events_by_region_country_division": [...],
    "employee_safety_analysis": [
      {
        "employee_id": "EMP001",
        "employee_name": "John Doe",
        "department": "Manufacturing",
        "total_incidents": 5,
        "serious_incidents": 1,
        "safety_score": 85.0
      }
    ],
    "department_safety_trends": [...],
    "training_impact_analysis": [...]
  },
  "augmented_features": {
    "employee_details": [...],
    "department_analytics": [...],
    "training_correlation": [...],
    "performance_metrics": [...]
  }
}
```

---

## AI Insights Endpoints

### 8. SRS Insights
**Endpoint:** `GET /api/v1/srs/insights`

**Description:** Generates AI-powered insights from SRS data.

**Query Parameters:**
- `file_id`: ID of the SRS file
- `start_date` (optional): Filter start date (YYYY-MM-DD)
- `end_date` (optional): Filter end date (YYYY-MM-DD)
- `insight_type` (optional): Type of insights to generate (trends, patterns, recommendations)

**Response:**
```json
{
  "file_id": "string",
  "insights_type": "srs",
  "generated_at": "2025-01-14T10:30:00Z",
  "insights": [
    {
      "insight_id": "string",
      "category": "trend_analysis",
      "title": "Increasing Near Miss Incidents in Q4",
      "description": "Analysis shows a 25% increase in near miss incidents during Q4 2024 compared to Q3.",
      "confidence_score": 0.92,
      "impact_level": "high",
      "supporting_data": {
        "q3_count": 120,
        "q4_count": 150,
        "percentage_increase": 25.0
      },
      "recommendations": [
        "Review Q4 safety protocols",
        "Conduct additional safety training",
        "Increase safety inspections"
      ]
    },
    {
      "insight_id": "string",
      "category": "pattern_detection",
      "title": "Regional Safety Performance Variation",
      "description": "North America region shows 40% higher serious incident rate compared to other regions.",
      "confidence_score": 0.88,
      "impact_level": "medium",
      "supporting_data": {
        "north_america_rate": 18.5,
        "other_regions_avg": 11.2,
        "difference": 7.3
      },
      "recommendations": [
        "Investigate North America safety protocols",
        "Share best practices from other regions",
        "Implement region-specific safety measures"
      ]
    }
  ],
  "summary": {
    "total_insights": 5,
    "high_impact_insights": 2,
    "medium_impact_insights": 2,
    "low_impact_insights": 1
  }
}
```

### 9. Generate More SRS Insights
**Endpoint:** `GET /api/v1/srs/insights/generate-more`

**Description:** Generates additional AI insights focusing on different aspects of the SRS data.

**Query Parameters:**
- `file_id`: ID of the SRS file
- `focus_area` (optional): Specific area to focus on (behavioral, operational, risk)
- `start_date` (optional): Filter start date (YYYY-MM-DD)
- `end_date` (optional): Filter end date (YYYY-MM-DD)

**Response:**
```json
{
  "file_id": "string",
  "insights_type": "srs_additional",
  "focus_area": "behavioral",
  "generated_at": "2025-01-14T10:30:00Z",
  "additional_insights": [
    {
      "insight_id": "string",
      "category": "behavioral_analysis",
      "title": "Time-of-Day Safety Patterns",
      "description": "Incidents peak between 2-4 PM, suggesting fatigue or attention lapses during afternoon hours.",
      "confidence_score": 0.85,
      "impact_level": "medium",
      "supporting_data": {
        "peak_hours": "14:00-16:00",
        "incident_count": 180,
        "percentage_of_total": 18.0
      },
      "recommendations": [
        "Implement afternoon safety breaks",
        "Schedule critical tasks in morning hours",
        "Increase supervision during peak hours"
      ]
    }
  ]
}
```

### 10. SRS Augmented Insights
**Endpoint:** `GET /api/v1/srs_agumented/insights`

**Description:** Generates AI insights from SRS Augmented data including employee details and enhanced analytics.

**Query Parameters:**
- `file_id`: ID of the SRS Augmented file
- `start_date` (optional): Filter start date (YYYY-MM-DD)
- `end_date` (optional): Filter end date (YYYY-MM-DD)
- `insight_type` (optional): Type of insights to generate

**Response:**
```json
{
  "file_id": "string",
  "insights_type": "srs_agumented",
  "generated_at": "2025-01-14T10:30:00Z",
  "insights": [
    {
      "insight_id": "string",
      "category": "employee_safety",
      "title": "Department Safety Performance Correlation",
      "description": "Manufacturing department employees with recent safety training show 35% fewer incidents.",
      "confidence_score": 0.91,
      "impact_level": "high",
      "supporting_data": {
        "trained_employees_incidents": 45,
        "untrained_employees_incidents": 69,
        "reduction_percentage": 35.0
      },
      "recommendations": [
        "Expand safety training program",
        "Prioritize training for high-risk departments",
        "Track training effectiveness metrics"
      ]
    },
    {
      "insight_id": "string",
      "category": "operational_optimization",
      "title": "Shift Pattern Safety Impact",
      "description": "Night shift workers experience 50% more serious incidents compared to day shift.",
      "confidence_score": 0.87,
      "impact_level": "high",
      "supporting_data": {
        "night_shift_incidents": 75,
        "day_shift_incidents": 50,
        "increase_percentage": 50.0
      },
      "recommendations": [
        "Review night shift safety protocols",
        "Increase night shift supervision",
        "Consider shift rotation policies"
      ]
    }
  ]
}
```

### 11. Generate More SRS Augmented Insights
**Endpoint:** `GET /api/v1/srs_agumented/insights/generate-more`

**Description:** Generates additional AI insights for SRS Augmented data focusing on employee and operational aspects.

**Query Parameters:**
- `file_id`: ID of the SRS Augmented file
- `focus_area` (optional): Specific area to focus on (employee, operational, training)
- `start_date` (optional): Filter start date (YYYY-MM-DD)
- `end_date` (optional): Filter end date (YYYY-MM-DD)

**Response:**
```json
{
  "file_id": "string",
  "insights_type": "srs_agumented_additional",
  "focus_area": "employee",
  "generated_at": "2025-01-14T10:30:00Z",
  "additional_insights": [
    {
      "insight_id": "string",
      "category": "employee_development",
      "title": "Experience Level Safety Correlation",
      "description": "Employees with 1-2 years of experience have 40% higher incident rates than veterans.",
      "confidence_score": 0.89,
      "impact_level": "medium",
      "supporting_data": {
        "new_employee_incidents": 120,
        "veteran_incidents": 85,
        "increase_percentage": 40.0
      },
      "recommendations": [
        "Implement mentorship programs",
        "Increase supervision for new employees",
        "Develop targeted training for experience levels"
      ]
    }
  ]
}
```

### 12. SRS Enriched Insights
**Endpoint:** `GET /api/v1/srs-enriched/insights`

**Description:** Generates AI insights from SRS Enriched data with additional enriched fields and behavioral analysis.

**Query Parameters:**
- `file_id`: ID of the SRS Enriched file
- `start_date` (optional): Filter start date (YYYY-MM-DD)
- `end_date` (optional): Filter end date (YYYY-MM-DD)
- `insight_type` (optional): Type of insights to generate

**Response:**
```json
{
  "file_id": "string",
  "insights_type": "srs_enriched",
  "generated_at": "2025-01-14T10:30:00Z",
  "insights": [
    {
      "insight_id": "string",
      "category": "behavioral_analysis",
      "title": "Unsafe Act Pattern Recognition",
      "description": "Working without proper PPE is the most common unsafe act, accounting for 25% of all incidents.",
      "confidence_score": 0.94,
      "impact_level": "high",
      "supporting_data": {
        "unsafe_act": "Working without proper PPE",
        "incident_count": 250,
        "percentage_of_total": 25.0,
        "serious_incidents": 45
      },
      "recommendations": [
        "Strengthen PPE enforcement policies",
        "Conduct PPE training sessions",
        "Implement PPE compliance monitoring"
      ]
    },
    {
      "insight_id": "string",
      "category": "operational_efficiency",
      "title": "Reporting Time Optimization",
      "description": "60% of incidents are reported within 24 hours, but 15% take more than 72 hours.",
      "confidence_score": 0.86,
      "impact_level": "medium",
      "supporting_data": {
        "within_24h": 600,
        "within_72h": 250,
        "over_72h": 150,
        "delayed_reporting_percentage": 15.0
      },
      "recommendations": [
        "Simplify reporting procedures",
        "Implement reporting incentives",
        "Provide reporting training"
      ]
    }
  ]
}
```

### 13. Generate More SRS Enriched Insights
**Endpoint:** `GET /api/v1/srs-enriched/insights/generate-more`

**Description:** Generates additional AI insights for SRS Enriched data focusing on behavioral and operational patterns.

**Query Parameters:**
- `file_id`: ID of the SRS Enriched file
- `focus_area` (optional): Specific area to focus on (behavioral, operational, time_analysis)
- `start_date` (optional): Filter start date (YYYY-MM-DD)
- `end_date` (optional): Filter end date (YYYY-MM-DD)

**Response:**
```json
{
  "file_id": "string",
  "insights_type": "srs_enriched_additional",
  "focus_area": "behavioral",
  "generated_at": "2025-01-14T10:30:00Z",
  "additional_insights": [
    {
      "insight_id": "string",
      "category": "behavioral_trends",
      "title": "Unsafe Condition Frequency Analysis",
      "description": "Poor housekeeping conditions contribute to 20% of all incidents, with peak occurrences on Mondays.",
      "confidence_score": 0.88,
      "impact_level": "medium",
      "supporting_data": {
        "unsafe_condition": "Poor housekeeping",
        "incident_count": 200,
        "percentage_of_total": 20.0,
        "monday_incidents": 45,
        "other_days_avg": 31
      },
      "recommendations": [
        "Implement Monday morning safety inspections",
        "Establish housekeeping standards",
        "Create cleanup schedules"
      ]
    }
  ]
}
```

---

## Conversational BI Endpoints

### 14. Stream Chat
**Endpoint:** `POST /conversation/stream/chat`

**Description:** Enables real-time conversational BI with streaming responses for natural language queries about uploaded data.

**Request Body:**
```json
{
  "message": "string",
  "file_id": "string",
  "conversation_id": "string (optional)",
  "context": {
    "dashboard_type": "srs|srs_enriched|srs_agumented",
    "filters": {
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "region": "North America"
    }
  }
}
```

**Response (Streaming):**
```json
{
  "conversation_id": "string",
  "message_id": "string",
  "response": "Based on the SRS data, I can see that...",
  "type": "text|chart|table",
  "data": {
    "chart_type": "bar|line|pie",
    "chart_data": [...],
    "table_data": [...]
  },
  "suggestions": [
    "Show me the trend over time",
    "Compare by region",
    "What are the most common incidents?"
  ],
  "confidence_score": 0.92,
  "timestamp": "2025-01-14T10:30:00Z"
}
```

**Example Queries:**
- "What are the top 5 regions with the most incidents?"
- "Show me the trend of serious near misses over the last 6 months"
- "Which departments have the highest safety scores?"
- "Compare incident rates between day and night shifts"
- "What are the most common unsafe acts in the manufacturing department?"

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": "Additional error details",
    "timestamp": "2025-01-14T10:30:00Z"
  }
}
```

**Common Error Codes:**
- `FILE_NOT_FOUND`: Requested file not found
- `INVALID_FILE_TYPE`: Unsupported file type
- `PROCESSING_ERROR`: Error during file processing
- `INVALID_PARAMETERS`: Invalid request parameters
- `DATABASE_ERROR`: Database connection or query error
- `AI_SERVICE_ERROR`: Error in AI insights generation
- `UNAUTHORIZED`: Authentication required
- `RATE_LIMIT_EXCEEDED`: Too many requests

---

## Rate Limits

- **File Upload:** 10 files per hour per user
- **Dashboard Requests:** 100 requests per hour per user
- **Insights Generation:** 20 requests per hour per user
- **Conversational BI:** 50 requests per hour per user

---

## Authentication

Most endpoints require authentication. Include the following header:
```
Authorization: Bearer <your_access_token>
```

---

## File Type Specifications

### SRS (Safety Reporting System)
- **Purpose:** Basic safety incident reporting
- **Key Fields:** event_id, date_of_unsafe_event, region, branch, unsafe_event_type, serious_near_miss, work_stopped
- **Use Cases:** Standard safety incident tracking and reporting

### SRS Enriched
- **Purpose:** Enhanced safety data with behavioral analysis
- **Additional Fields:** unsafe_act, unsafe_condition, action_description_1, comments/remarks
- **Use Cases:** Detailed behavioral analysis, action tracking, enhanced insights

### SRS Augmented
- **Purpose:** Employee-focused safety analytics
- **Additional Fields:** employee_id, employee_name, department, shift, training_status
- **Use Cases:** Employee safety performance, training impact analysis, department comparisons

---

## Best Practices

1. **File Upload:**
   - Ensure Excel files are properly formatted
   - Include all required columns for the file type
   - Clean data before upload for better analysis

2. **Dashboard Usage:**
   - Use date filters to focus on relevant time periods
   - Combine multiple filters for detailed analysis
   - Export dashboard data for external reporting

3. **AI Insights:**
   - Generate insights after uploading new data
   - Review recommendations and implement actionable items
   - Use generate-more endpoints for deeper analysis

4. **Conversational BI:**
   - Use natural language for queries
   - Provide context about what you're looking for
   - Follow up on suggestions for deeper analysis

---

## Support

For technical support or questions about the API:
- Email: support@safetyconnect.com
- Documentation: https://docs.safetyconnect.com
- API Status: https://status.safetyconnect.com
