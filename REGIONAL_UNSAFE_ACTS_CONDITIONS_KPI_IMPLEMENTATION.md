# Regional Unsafe Acts and Conditions Analysis KPI Implementation

## Overview

This document describes the implementation of a new comprehensive KPI called **"Regional Unsafe Acts and Conditions Analysis"** that has been added to all SRS-related dashboards and KPI systems. This KPI provides detailed insights into unsafe acts and conditions by region, identifying the most common occurrences per region.

## Business Context

The KPI is named **"Regional Safety Behavior and Condition Analysis"** in the business context, as it provides:

1. **Regional Safety Performance Insights**: Analysis of unsafe acts and conditions by geographic region
2. **Most Common Safety Issues**: Identification of the most frequent unsafe acts and conditions per region
3. **Regional Risk Assessment**: Understanding which regions have higher concentrations of specific safety issues
4. **Targeted Intervention Planning**: Data-driven insights for region-specific safety improvement initiatives

## KPI Details

### KPI Name
- **Technical Name**: `regional_unsafe_acts_conditions_analysis`
- **Business Name**: "Regional Safety Behavior and Condition Analysis"
- **Chart Type**: Table
- **Description**: "Regional analysis of unsafe acts and conditions with most common occurrences per region"

### Data Structure
The KPI returns comprehensive data for each region including:

- **Region**: Geographic region identifier
- **Total Unsafe Items**: Total count of unsafe acts and conditions in the region
- **Unsafe Acts Summary**:
  - Total unsafe acts count
  - Most common unsafe act
  - Count of most common unsafe act
  - Percentage of most common act relative to region total
- **Unsafe Conditions Summary**:
  - Total unsafe conditions count
  - Most common unsafe condition
  - Count of most common unsafe condition
  - Percentage of most common condition relative to region total

## Implementation Details

### Files Modified

#### 1. KPI Query Files
- `shindler_server/kpis/srs_kpis.py`
- `shindler_server/kpis/srs_enriched_kpis.py`
- `shindler_server/kpis/srs_agumented_kpis.py`

**Method Added**: `get_regional_unsafe_acts_conditions_analysis()`

#### 2. Dashboard Service Files
- `shindler_server/dashboard/srs_dashboard_service.py`
- `shindler_server/dashboard/srs_enriched_dashboard_service.py`
- `shindler_server/dashboard/srs_agumented_dashboard_service.py`

**Method Added**: `_get_regional_unsafe_acts_conditions_analysis()` or `_srs_regional_unsafe_acts_conditions_analysis()`

### SQL Query Logic

The KPI uses a sophisticated SQL query that:

1. **Processes Event Types**: Determines if each record involves an unsafe act or condition based on `unsafe_event_type`
2. **Extracts Descriptions**: Intelligently extracts descriptions from multiple fields:
   - Primary fields: `unsafe_act`, `unsafe_condition`
   - Secondary fields: `unsafe_act_other`, `unsafe_condition_other`
   - Cross-references between acts and conditions when primary fields are empty
3. **Aggregates by Region**: Groups and counts occurrences by region and category
4. **Identifies Most Common**: Uses window functions to find the most frequent unsafe acts and conditions per region
5. **Calculates Percentages**: Provides percentage breakdowns for better insights

### Key Features

1. **Intelligent Data Extraction**: Handles cases where data might be in different fields
2. **Cross-Reference Logic**: When unsafe act fields are empty, checks unsafe condition fields and vice versa
3. **Regional Focus**: Provides region-specific insights for targeted safety interventions
4. **Comprehensive Metrics**: Includes both counts and percentages for better analysis
5. **Error Handling**: Robust error handling with fallback data structures

## Usage in Dashboards

### Dashboard Integration
The KPI is now available in all SRS dashboards:

1. **SRS Standard Dashboard**: Available as KPI #14
2. **SRS Enriched Dashboard**: Available as KPI #14
3. **SRS Augmented Dashboard**: Available as part of standard KPIs

### Chart Type
- **Type**: Table
- **Purpose**: Display regional breakdown with detailed metrics
- **Format**: Structured table showing region, unsafe acts summary, and unsafe conditions summary

### Data Access
The KPI can be accessed through:
- Dashboard API endpoints
- Direct KPI query methods
- Dashboard data aggregation

## Business Value

### Safety Management
1. **Regional Risk Assessment**: Identify high-risk regions for specific safety issues
2. **Targeted Training**: Focus training programs on most common unsafe acts per region
3. **Resource Allocation**: Allocate safety resources based on regional needs
4. **Performance Tracking**: Monitor regional safety performance improvements

### Operational Insights
1. **Pattern Recognition**: Identify recurring safety issues by region
2. **Intervention Planning**: Design region-specific safety interventions
3. **Benchmarking**: Compare safety performance across regions
4. **Trend Analysis**: Track changes in regional safety patterns over time

## Technical Specifications

### Query Performance
- Uses CTEs (Common Table Expressions) for efficient data processing
- Implements proper indexing considerations for region and date fields
- Optimized for large datasets with proper aggregation

### Data Quality
- Handles NULL values and empty strings appropriately
- Provides fallback data when primary fields are empty
- Maintains data integrity through proper COALESCE usage

### Scalability
- Designed to work with growing datasets
- Efficient memory usage through streaming aggregation
- Supports regional filtering for performance optimization

## Future Enhancements

### Potential Improvements
1. **Time-based Analysis**: Add temporal trends to regional analysis
2. **Severity Weighting**: Include severity factors in regional risk assessment
3. **Comparative Analysis**: Add year-over-year regional comparisons
4. **Predictive Insights**: Implement predictive analytics for regional safety trends

### Integration Opportunities
1. **Alert System**: Trigger alerts for regions with concerning patterns
2. **Reporting Automation**: Generate automated regional safety reports
3. **Mobile Dashboard**: Optimize for mobile safety management access
4. **API Integration**: Provide REST API endpoints for external systems

## Conclusion

The Regional Unsafe Acts and Conditions Analysis KPI provides comprehensive insights into regional safety performance, enabling data-driven safety management decisions. By identifying the most common safety issues per region, organizations can implement targeted interventions and track improvements effectively.

This implementation follows the existing codebase patterns and integrates seamlessly with all SRS dashboard systems, providing consistent and reliable safety analytics across the organization.

