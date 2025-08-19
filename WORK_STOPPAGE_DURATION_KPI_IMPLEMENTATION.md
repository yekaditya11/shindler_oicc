# Work Stoppage Duration Analysis KPI Implementation

## Overview

The **Work Stoppage Duration Analysis** KPI has been successfully implemented across all SRS dashboard variants (Standard, Enriched, and Augmented). This KPI provides comprehensive analysis of work stoppages by duration categories, helping organizations understand the operational impact of safety incidents.

## Business Context

**KPI Name**: Work Stoppage Duration Analysis  
**Business Purpose**: Analyze work stoppages by duration to understand operational impact and prioritize interventions  
**Target Audience**: Operations managers, safety supervisors, business leaders  
**Business Value**: Enables better resource planning and operational impact assessment

## Technical Implementation

### Files Modified

#### KPI Query Files
1. **`shindler_server/kpis/srs_kpis.py`**
   - Added `get_work_stoppage_duration_analysis()` method
   - Updated `get_all_kpis()` to include the new KPI

2. **`shindler_server/kpis/srs_enriched_kpis.py`**
   - Added `get_work_stoppage_duration_analysis()` method
   - Updated `get_all_kpis()` to include the new KPI

3. **`shindler_server/kpis/srs_agumented_kpis.py`**
   - Added `get_work_stoppage_duration_analysis()` method
   - Updated `get_all_kpis()` to include the new KPI

#### Dashboard Service Files
1. **`shindler_server/dashboard/srs_dashboard_service.py`**
   - Added `_get_work_stoppage_duration_analysis()` method
   - Updated `_get_all_kpis()` to include the new KPI
   - Updated `_get_empty_dashboard_data()` to include empty structure
   - Updated KPI count from 15 to 16

2. **`shindler_server/dashboard/srs_enriched_dashboard_service.py`**
   - Added `_get_work_stoppage_duration_analysis()` method
   - Updated `_get_all_kpis()` to include the new KPI
   - Updated `_get_empty_dashboard_data()` to include empty structure
   - Updated KPI count from 15 to 16

3. **`shindler_server/dashboard/srs_agumented_dashboard_service.py`**
   - Added `_srs_work_stoppage_duration_analysis()` method
   - Updated `_get_srs_standard_kpis()` to include the new KPI
   - Updated KPI count from 15 to 16

### SQL Logic

The KPI uses a sophisticated SQL query with CTEs (Common Table Expressions) to:

1. **Categorize Events**: Classifies each event into duration categories:
   - **No Work Stoppage**: Events where work was not stopped
   - **One Day or Less**: Work stoppages lasting one day or less
   - **More than One Day**: Work stoppages lasting more than one day
   - **Duration Unknown**: Work stoppages with unknown duration
   - **Other Duration**: Work stoppages with other duration values
   - **Work Stoppage Status Unknown**: Events with unclear stoppage status

2. **Calculate Metrics**: For each category, calculates:
   - **Event Count**: Number of events in each category
   - **Percentage of Stoppages**: Percentage within work stoppage events
   - **Percentage of Total Events**: Percentage of all events

3. **Order Results**: Sorts results in logical order for dashboard display

### Key Features

- **Comprehensive Categorization**: Handles all possible work stoppage scenarios
- **Percentage Calculations**: Provides both relative and absolute impact metrics
- **Date and Region Filtering**: Supports dashboard filtering capabilities
- **Error Handling**: Graceful degradation when data is unavailable
- **Logical Ordering**: Results ordered by business importance

## Data Structure

### Output Format
```json
{
  "chart_type": "pie",
  "description": "Analysis of work stoppages by duration categories",
  "data": [
    {
      "duration_category": "No Work Stoppage",
      "event_count": 150,
      "percentage_of_stoppages": 0.0,
      "percentage_of_total_events": 75.0
    },
    {
      "duration_category": "One Day or Less",
      "event_count": 25,
      "percentage_of_stoppages": 50.0,
      "percentage_of_total_events": 12.5
    },
    {
      "duration_category": "More than One Day",
      "event_count": 20,
      "percentage_of_stoppages": 40.0,
      "percentage_of_total_events": 10.0
    },
    {
      "duration_category": "Duration Unknown",
      "event_count": 5,
      "percentage_of_stoppages": 10.0,
      "percentage_of_total_events": 2.5
    }
  ]
}
```

### Fields Explained
- **duration_category**: The category of work stoppage duration
- **event_count**: Number of events in this category
- **percentage_of_stoppages**: Percentage within work stoppage events only
- **percentage_of_total_events**: Percentage of all events (including non-stoppages)

## Usage in Dashboards

### Dashboard Integration
The KPI is available in all SRS dashboard variants:
- **SRS Standard Dashboard**: Shows duration analysis for standard SRS data
- **SRS Enriched Dashboard**: Enhanced analysis with enriched data fields
- **SRS Augmented Dashboard**: Comprehensive analysis including augmented data

### Chart Type
- **Display Format**: Pie chart for clear category distribution visualization
- **Sorting**: Ordered by business importance (No Stoppage → One Day → More than One Day → Unknown)
- **Filtering**: Supports date range and region-specific filtering

## Business Value

### Operational Insights
1. **Impact Assessment**: Understand the operational impact of safety incidents
2. **Resource Planning**: Plan resources based on expected work stoppage durations
3. **Risk Prioritization**: Focus on incidents that cause longer stoppages
4. **Performance Monitoring**: Track improvements in reducing stoppage durations

### Strategic Benefits
1. **Cost Management**: Understand financial impact of work stoppages
2. **Operational Efficiency**: Identify patterns in stoppage durations
3. **Safety Program Effectiveness**: Measure success of safety interventions
4. **Business Continuity**: Plan for operational disruptions

## Technical Specifications

### Performance Considerations
- **Query Optimization**: Uses CTEs for efficient data processing
- **Indexing**: Leverages existing indexes on date and region fields
- **Filtering**: Efficient date and region filtering for dashboard performance
- **Session Management**: Optimized database session handling

### Data Quality
- **Null Handling**: Comprehensive handling of null and empty values
- **Data Validation**: Validates work stoppage indicators and duration values
- **Categorization Logic**: Robust logic for handling various data formats
- **Error Recovery**: Graceful handling of data inconsistencies

### Scalability
- **Large Dataset Support**: Efficient processing of large datasets
- **Regional Distribution**: Scales across multiple regions and locations
- **Time Series Analysis**: Supports historical trend analysis
- **Real-time Updates**: Compatible with real-time dashboard updates

## Duration Categories Explained

### 1. No Work Stoppage
- **Definition**: Events where work was not stopped
- **Business Impact**: Minimal operational disruption
- **Action Required**: Monitor for potential escalation

### 2. One Day or Less
- **Definition**: Work stoppages lasting one day or less
- **Business Impact**: Short-term operational disruption
- **Action Required**: Quick resolution and preventive measures

### 3. More than One Day
- **Definition**: Work stoppages lasting more than one day
- **Business Impact**: Significant operational disruption
- **Action Required**: Immediate attention and root cause analysis

### 4. Duration Unknown
- **Definition**: Work stoppages with unknown duration
- **Business Impact**: Uncertain operational impact
- **Action Required**: Data quality improvement and investigation

### 5. Other Duration
- **Definition**: Work stoppages with other duration values
- **Business Impact**: Variable operational impact
- **Action Required**: Standardization of duration reporting

## Future Enhancements

### Potential Improvements
1. **Time-based Trends**: Add temporal analysis of stoppage durations
2. **Cost Impact**: Include financial calculations for each duration category
3. **Predictive Analytics**: Predict stoppage duration based on incident type
4. **Department Analysis**: Break down durations by department or function
5. **Seasonal Patterns**: Analyze duration patterns by season or time of year
6. **Equipment Correlation**: Link stoppage duration to equipment involved

### Integration Opportunities
1. **Financial Systems**: Integrate with cost tracking systems
2. **Maintenance Systems**: Link to equipment maintenance schedules
3. **HR Systems**: Connect with employee training and experience data
4. **Weather Data**: Include weather condition correlations
5. **Supply Chain**: Integrate with supply chain impact analysis

## Conclusion

The Work Stoppage Duration Analysis KPI provides valuable insights into the operational impact of safety incidents. By categorizing stoppages by duration and calculating relevant percentages, organizations can better understand the business impact of safety events and prioritize interventions accordingly. The implementation follows established patterns and integrates seamlessly with existing dashboard infrastructure.

