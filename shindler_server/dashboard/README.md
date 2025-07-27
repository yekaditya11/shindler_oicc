# Dashboard Services

This directory contains schema-specific dashboard services that provide standardized KPI data across all safety systems.

## Overview

The dashboard services replace the unified dashboard approach with separate, optimized services for each schema type:

- **EI Tech Dashboard Service**: Handles EI Tech unsafe events data
- **SRS Dashboard Service**: Handles SRS (Safety Reporting System) data  
- **NI TCT Dashboard Service**: Handles NI TCT (Non-Intrusive Testing) data

## Key Features

### Standardized KPIs
Each dashboard service provides 12 core KPIs:

1. **Total Events Count** - Basic event statistics
2. **Serious Near Miss Rate** - Percentage of high-risk events
3. **Work Stoppage Rate** - Percentage of events causing work stoppages
4. **Monthly Trends** - Time-series data by month
5. **Branch Performance Analysis** - Performance metrics by branch/region
6. **Event Type Distribution** - Breakdown by incident types
7. **Repeat Locations** - Locations with multiple incidents
8. **Response Time Analysis** - Time between occurrence and reporting
9. **Safety Performance Trends** - Quarterly performance trends
10. **Incident Severity Distribution** - Categorization by severity levels
11. **Operational Impact Analysis** - Business impact assessment
12. **Time-based Analysis** - Patterns by time of day/day of week

### Schema-Specific Optimizations

- **EI Tech & SRS**: Date-only analysis (no hourly data)
- **NI TCT**: Full datetime analysis with hourly patterns
- **Field Mappings**: Each service uses correct field names for its schema

### Role-Based Access Control

- **safety_head**: Global access to all data
- **cxo**: Global access to all data
- **safety_manager**: Regional access only (requires region parameter)

## API Endpoints

### Main Dashboard Endpoints

```
GET /dashboard/ei_tech
GET /dashboard/srs  
GET /dashboard/ni_tct
```

**Parameters:**
- `start_date` (optional): Start date (YYYY-MM-DD), defaults to 1 year ago
- `end_date` (optional): End date (YYYY-MM-DD), defaults to today
- `user_role` (optional): User role for access control
- `region` (optional): Region filter (required for safety_manager role)

### Summary Endpoints

```
GET /dashboard/ei_tech/summary
GET /dashboard/srs/summary
GET /dashboard/ni_tct/summary
```

Returns condensed dashboard data with key metrics only.

### Special NI TCT Endpoint

```
GET /dashboard/ni_tct/time_patterns
```

Returns detailed time-based patterns unique to NI TCT (hourly analysis).

## Example Usage

### Basic Dashboard Request
```http
GET /dashboard/ei_tech
```

### With Date Range
```http
GET /dashboard/ei_tech?start_date=2024-01-01&end_date=2024-12-31
```

### Regional Manager Access
```http
GET /dashboard/ei_tech?user_role=safety_manager&region=NR 1
```

### Summary View
```http
GET /dashboard/ei_tech/summary?start_date=2024-06-01
```

## Response Format

```json
{
  "schema_type": "ei_tech",
  "date_range": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  },
  "generated_at": "2024-01-15T10:30:00",
  "user_context": {
    "user_role": "safety_manager",
    "region": "NR 1",
    "data_scope": "regional"
  },
  "dashboard_data": {
    "total_events": { ... },
    "serious_near_miss_rate": { ... },
    "work_stoppage_rate": { ... },
    "monthly_trends": [ ... ],
    "branch_performance_analysis": [ ... ],
    "event_type_distribution": [ ... ],
    "repeat_locations": [ ... ],
    "response_time_analysis": { ... },
    "safety_performance_trends": [ ... ],
    "incident_severity_distribution": [ ... ],
    "operational_impact_analysis": { ... },
    "time_based_analysis": { ... }
  }
}
```

## Service Architecture

```
dashboard/
├── __init__.py                     # Package exports
├── ei_tech_dashboard_service.py    # EI Tech service
├── srs_dashboard_service.py        # SRS service
├── ni_tct_dashboard_service.py     # NI TCT service
└── README.md                       # This file

routes/
├── dashboard_ei_tech_routes.py     # EI Tech routes
├── dashboard_srs_routes.py         # SRS routes
└── dashboard_ni_tct_routes.py      # NI TCT routes
```

## Error Handling

All endpoints include comprehensive error handling:

- **400 Bad Request**: Invalid parameters (e.g., invalid region)
- **500 Internal Server Error**: Database or processing errors

## Performance Notes

- Each service is optimized for its specific schema
- Queries include appropriate LIMIT clauses to prevent large result sets
- Database connections are properly managed with session cleanup
- Regional filtering reduces query scope for better performance

## Migration from Unified Service

If migrating from a unified dashboard service:

1. Replace unified endpoint calls with schema-specific endpoints
2. Update response parsing to handle new structure
3. Add user role and region parameters as needed
4. Update error handling for new status codes 