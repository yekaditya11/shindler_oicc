# SRS Augmented KPIs Testing Flow

## Overview
This document provides a comprehensive testing flow for the newly integrated SRS Augmented KPIs system, including all endpoints, dashboard functionality, and data validation.

## Prerequisites
- Server is running on `http://localhost:8000`
- Database is populated with test data
- All dependencies are installed

---

## 1. Basic Health Check

### Test Server Status
```bash
curl -X GET "http://localhost:8000/health"
```
**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-14T10:00:00Z"
}
```

---

## 2. Core SRS Augmented KPI Endpoints

### 2.1 Get All Augmented KPIs
```bash
curl -X GET "http://localhost:8000/api/v1/srs_agumented"
```

**Expected Response Structure:**
```json
{
  "number_of_unsafe_events": {
    "total_events": 150,
    "unique_events": 150
  },
  "unsafe_events_per_employee": [...],
  "average_experience_of_involved_employees": {...},
  "job_designations_involved_in_incidents": [...],
  "incident_rate_by_experience_bracket": [...],
  "observations_reported_by_age_group": [...],
  "training_compliance_rate": {...},
  "repeat_offenders": [...],
  "incidents_after_extended_shifts": [...],
  "incident_rate_vs_weekly_hours_worked": [...],
  "overtime_linked_unsafe_events": [...],
  "incidents_during_night_shifts": [...],
  "incidents_by_hour_of_day": [...],
  "events_after_consecutive_working_days": [...],
  "top_equipment_involved_in_unsafe_events": [...],
  "incidents_per_equipment_type": [...],
  "average_time_since_last_maintenance": {...},
  "percentage_of_events_after_unscheduled_maintenance": [...],
  "time_between_incidents_for_equipment_type": [...],
  "repeat_failures_on_same_equipment": [...],
  "percent_of_incidents_with_corrective_actions": {...},
  "recurring_events_with_same_root_cause": [...],
  "percent_of_incidents_investigated": {...},
  "incidents_by_root_cause_category": [...],
  "top_5_recurrent_root_causes": [...],
  "average_time_to_close_investigation": {...},
  "repeat_events_despite_capa": [...],
  "events_by_root_cause_category_and_site": [...],
  "audit_frequency_vs_incidents_of_branch": [...],
  "audit_recency_vs_incidents_of_branch": [...],
  "percent_of_incidents_30_days_since_last_audit": {...},
  "percent_of_branches_with_overdue_audits_and_high_incident_rates": [...],
  "trend_days_since_audit_vs_incident_volume": [...],
  "incident_rate_by_weather_condition": [...],
  "percent_of_incidents_during_extreme_weather_days": {...},
  "unsafe_event_type_vs_weather_condition_correlation": [...]
}
```

### 2.2 Test with Date Filtering
```bash
curl -X GET "http://localhost:8000/api/v1/srs_agumented?start_date=2024-01-01&end_date=2024-12-31"
```

### 2.3 Test with User Role
```bash
curl -X GET "http://localhost:8000/api/v1/srs_agumented?user_role=safety_manager&region=NR%201"
```

---

## 3. AI Insights Endpoints

### 3.1 Get AI Insights
```bash
curl -X GET "http://localhost:8000/api/v1/srs_agumented/insights"
```

**Expected Response:**
```json
{
  "insights": [
    {
      "type": "trend_analysis",
      "title": "Employee Experience Impact",
      "description": "Employees with less than 2 years experience show 40% higher incident rates",
      "severity": "medium",
      "recommendation": "Implement additional training for new employees"
    },
    {
      "type": "pattern_detection",
      "title": "Equipment Maintenance Alert",
      "description": "Equipment ID EQP-001 has 3 repeat failures in the last 30 days",
      "severity": "high",
      "recommendation": "Schedule immediate maintenance review"
    }
  ],
  "generated_at": "2025-01-14T10:00:00Z"
}
```

### 3.2 Generate More Insights
```bash
curl -X POST "http://localhost:8000/api/v1/srs_agumented/insights/generate-more" \
  -H "Content-Type: application/json" \
  -d '{
    "focus_area": "equipment_maintenance",
    "time_period": "last_30_days"
  }'
```

**Expected Response:**
```json
{
  "additional_insights": [
    {
      "type": "equipment_analysis",
      "title": "Maintenance Schedule Optimization",
      "description": "Equipment type 'Forklift' shows 60% of incidents occur within 7 days after scheduled maintenance",
      "severity": "medium",
      "recommendation": "Review maintenance procedures for forklift equipment"
    }
  ],
  "generated_at": "2025-01-14T10:00:00Z"
}
```

---

## 4. Dashboard Endpoints

### 4.1 Full Dashboard Data
```bash
curl -X GET "http://localhost:8000/dashboard/srs_agumented"
```

**Expected Response Structure:**
```json
{
  "schema_type": "srs_agumented",
  "date_range": {
    "start_date": "2024-01-14",
    "end_date": "2025-01-14"
  },
  "generated_at": "2025-01-14T10:00:00Z",
  "user_context": {
    "user_role": "safety_manager",
    "region": "NR 1",
    "data_scope": "regional"
  },
  "summary_metrics": {
    "total_events": 150,
    "total_employees_analyzed": 45,
    "total_equipment_analyzed": 23,
    "investigation_rate": 85.5,
    "corrective_action_rate": 78.2,
    "training_compliance": 92.1,
    "repeat_offenders_count": 8,
    "high_risk_equipment_count": 3,
    "overdue_audits_count": 2
  },
  "dashboard_data": {
    "employee_analytics": {
      "unsafe_events_per_employee": [...],
      "average_experience_of_involved_employees": {...},
      "job_designations_involved_in_incidents": [...],
      "incident_rate_by_experience_bracket": [...],
      "observations_reported_by_age_group": [...],
      "training_compliance_rate": {...},
      "repeat_offenders": [...]
    },
    "work_pattern_analytics": {
      "incidents_after_extended_shifts": [...],
      "incident_rate_vs_weekly_hours_worked": [...],
      "overtime_linked_unsafe_events": [...],
      "incidents_during_night_shifts": [...],
      "incidents_by_hour_of_day": [...],
      "events_after_consecutive_working_days": [...]
    },
    "equipment_analytics": {
      "top_equipment_involved_in_unsafe_events": [...],
      "incidents_per_equipment_type": [...],
      "average_time_since_last_maintenance": {...},
      "percentage_of_events_after_unscheduled_maintenance": [...],
      "time_between_incidents_for_equipment_type": [...],
      "repeat_failures_on_same_equipment": [...]
    },
    "investigation_analytics": {
      "percent_of_incidents_with_corrective_actions": {...},
      "recurring_events_with_same_root_cause": [...],
      "percent_of_incidents_investigated": {...},
      "incidents_by_root_cause_category": [...],
      "top_5_recurrent_root_causes": [...],
      "average_time_to_close_investigation": {...},
      "repeat_events_despite_capa": [...],
      "events_by_root_cause_category_and_site": [...]
    },
    "audit_analytics": {
      "audit_frequency_vs_incidents_of_branch": [...],
      "audit_recency_vs_incidents_of_branch": [...],
      "percent_of_incidents_30_days_since_last_audit": {...},
      "percent_of_branches_with_overdue_audits_and_high_incident_rates": [...],
      "trend_days_since_audit_vs_incident_volume": [...]
    },
    "environmental_analytics": {
      "incident_rate_by_weather_condition": [...],
      "percent_of_incidents_during_extreme_weather_days": {...},
      "unsafe_event_type_vs_weather_condition_correlation": [...]
    },
    "core_metrics": {
      "number_of_unsafe_events": {...},
      "monthly_unsafe_events_trend": [...],
      "near_misses": {...},
      "unsafe_events_by_branch": [...],
      "unsafe_events_by_region": [...],
      "at_risk_regions": [...],
      "branch_risk_index": [...]
    }
  },
  "raw_kpi_data": {...}
}
```

### 4.2 Dashboard Summary
```bash
curl -X GET "http://localhost:8000/dashboard/srs_agumented/summary"
```

**Expected Response Structure:**
```json
{
  "schema_type": "srs_agumented_summary",
  "date_range": {
    "start_date": "2024-01-14",
    "end_date": "2025-01-14"
  },
  "generated_at": "2025-01-14T10:00:00Z",
  "user_context": {
    "user_role": "safety_manager",
    "region": "NR 1",
    "data_scope": "regional"
  },
  "summary_metrics": {
    "total_events": 150,
    "total_employees_analyzed": 45,
    "total_equipment_analyzed": 23,
    "investigation_rate": 85.5,
    "corrective_action_rate": 78.2,
    "training_compliance": 92.1,
    "repeat_offenders_count": 8,
    "high_risk_equipment_count": 3,
    "overdue_audits_count": 2
  },
  "top_insights": {
    "employee_insights": {
      "top_repeat_offenders": [...],
      "experience_brackets": [...],
      "training_gaps": {...}
    },
    "work_pattern_insights": {
      "extended_shift_incidents": [...],
      "night_shift_incidents": [...],
      "overtime_events": [...]
    },
    "equipment_insights": {
      "high_risk_equipment": [...],
      "maintenance_issues": [...],
      "equipment_types": [...]
    },
    "investigation_insights": {
      "root_causes": [...],
      "investigation_time": {...},
      "corrective_actions": {...}
    },
    "audit_insights": {
      "overdue_audits": [...],
      "audit_effectiveness": [...]
    },
    "environmental_insights": {
      "weather_conditions": [...],
      "extreme_weather_impact": {...}
    }
  }
}
```

---

## 5. Error Handling Tests

### 5.1 Invalid Date Format
```bash
curl -X GET "http://localhost:8000/api/v1/srs_agumented?start_date=invalid-date"
```
**Expected Response:**
```json
{
  "detail": "Invalid date format. Use YYYY-MM-DD format."
}
```

### 5.2 Invalid User Role
```bash
curl -X GET "http://localhost:8000/api/v1/srs_agumented?user_role=invalid_role"
```
**Expected Response:**
```json
{
  "detail": "Invalid user role. Valid roles: safety_head, cxo, safety_manager"
}
```

### 5.3 Database Connection Error
```bash
# Simulate database connection issue by stopping the database
curl -X GET "http://localhost:8000/api/v1/srs_agumented"
```
**Expected Response:**
```json
{
  "detail": "Database connection error. Please try again later."
}
```

---

## 6. Performance Tests

### 6.1 Response Time Test
```bash
time curl -X GET "http://localhost:8000/api/v1/srs_agumented"
```
**Expected:** Response time < 5 seconds

### 6.2 Concurrent Requests Test
```bash
# Test with 10 concurrent requests
for i in {1..10}; do
  curl -X GET "http://localhost:8000/api/v1/srs_agumented" &
done
wait
```

---

## 7. Data Validation Tests

### 7.1 Verify All KPI Categories Present
```bash
curl -X GET "http://localhost:8000/api/v1/srs_agumented" | jq 'keys'
```
**Expected Categories:**
- `number_of_unsafe_events`
- `unsafe_events_per_employee`
- `average_experience_of_involved_employees`
- `job_designations_involved_in_incidents`
- `incident_rate_by_experience_bracket`
- `observations_reported_by_age_group`
- `training_compliance_rate`
- `repeat_offenders`
- `incidents_after_extended_shifts`
- `incident_rate_vs_weekly_hours_worked`
- `overtime_linked_unsafe_events`
- `incidents_during_night_shifts`
- `incidents_by_hour_of_day`
- `events_after_consecutive_working_days`
- `top_equipment_involved_in_unsafe_events`
- `incidents_per_equipment_type`
- `average_time_since_last_maintenance`
- `percentage_of_events_after_unscheduled_maintenance`
- `time_between_incidents_for_equipment_type`
- `repeat_failures_on_same_equipment`
- `percent_of_incidents_with_corrective_actions`
- `recurring_events_with_same_root_cause`
- `percent_of_incidents_investigated`
- `incidents_by_root_cause_category`
- `top_5_recurrent_root_causes`
- `average_time_to_close_investigation`
- `repeat_events_despite_capa`
- `events_by_root_cause_category_and_site`
- `audit_frequency_vs_incidents_of_branch`
- `audit_recency_vs_incidents_of_branch`
- `percent_of_incidents_30_days_since_last_audit`
- `percent_of_branches_with_overdue_audits_and_high_incident_rates`
- `trend_days_since_audit_vs_incident_volume`
- `incident_rate_by_weather_condition`
- `percent_of_incidents_during_extreme_weather_days`
- `unsafe_event_type_vs_weather_condition_correlation`

### 7.2 Verify Dashboard Categories
```bash
curl -X GET "http://localhost:8000/dashboard/srs_agumented" | jq '.dashboard_data | keys'
```
**Expected Categories:**
- `employee_analytics`
- `work_pattern_analytics`
- `equipment_analytics`
- `investigation_analytics`
- `audit_analytics`
- `environmental_analytics`
- `core_metrics`

---

## 8. Integration Tests

### 8.1 Test Complete Flow
```bash
# 1. Get basic KPIs
curl -X GET "http://localhost:8000/api/v1/srs_agumented"

# 2. Get AI insights
curl -X GET "http://localhost:8000/api/v1/srs_agumented/insights"

# 3. Generate more insights
curl -X POST "http://localhost:8000/api/v1/srs_agumented/insights/generate-more" \
  -H "Content-Type: application/json" \
  -d '{"focus_area": "employee_safety"}'

# 4. Get full dashboard
curl -X GET "http://localhost:8000/dashboard/srs_agumented"

# 5. Get dashboard summary
curl -X GET "http://localhost:8000/dashboard/srs_agumented/summary"
```

### 8.2 Test with Different User Roles
```bash
# Safety Head
curl -X GET "http://localhost:8000/api/v1/srs_agumented?user_role=safety_head"

# CXO
curl -X GET "http://localhost:8000/api/v1/srs_agumented?user_role=cxo"

# Safety Manager with Region
curl -X GET "http://localhost:8000/api/v1/srs_agumented?user_role=safety_manager&region=NR%201"
```

---

## 9. Browser Testing

### 9.1 OpenAPI Documentation
```
http://localhost:8000/docs
```
Navigate to the SRS Augmented endpoints and test them through the interactive interface.

### 9.2 Test All Endpoints in Browser
1. **Basic KPIs**: `http://localhost:8000/api/v1/srs_agumented`
2. **AI Insights**: `http://localhost:8000/api/v1/srs_agumented/insights`
3. **Dashboard**: `http://localhost:8000/dashboard/srs_agumented`
4. **Dashboard Summary**: `http://localhost:8000/dashboard/srs_agumented/summary`

---

## 10. Success Criteria

### ✅ All tests should pass if:
1. **Response Status**: All endpoints return 200 OK
2. **Data Structure**: All expected fields are present
3. **Performance**: Response time < 5 seconds
4. **Error Handling**: Proper error messages for invalid inputs
5. **Categorization**: Dashboard data is properly categorized
6. **Summary Metrics**: Summary endpoint provides key metrics
7. **AI Insights**: Insights endpoints return meaningful analysis
8. **User Roles**: Different roles get appropriate data scope
9. **Date Filtering**: Date parameters work correctly
10. **Regional Filtering**: Region parameters work for safety managers

---

## 11. Troubleshooting

### Common Issues:
1. **Database Connection**: Check if database is running
2. **Missing Dependencies**: Ensure all packages are installed
3. **Port Conflicts**: Verify port 8000 is available
4. **Data Issues**: Check if test data is properly loaded
5. **Import Errors**: Verify all module imports are correct

### Debug Commands:
```bash
# Check server logs
tail -f logs/server.log

# Check database connection
python -c "from config.database_config import db_manager; print(db_manager.test_connection())"

# Test KPI queries directly
python -c "from kpis.srs_agumented_kpis import SRSAGUMENTEDKPIQUERIES; kpi = SRSAGUMENTEDKPIQUERIES(); print(kpi.get_all_kpis())"
```

---

## 12. Post-Testing Checklist

- [ ] All endpoints return 200 OK
- [ ] All expected KPI categories are present
- [ ] Dashboard categorization works correctly
- [ ] Summary metrics are calculated properly
- [ ] AI insights are generated
- [ ] Error handling works for invalid inputs
- [ ] Performance is acceptable (< 5 seconds)
- [ ] User role filtering works
- [ ] Date filtering works
- [ ] Regional filtering works for safety managers
- [ ] All new augmented KPIs are included
- [ ] Dashboard summary provides actionable insights

---

This testing flow ensures comprehensive validation of the SRS Augmented KPIs system integration! 🎯
