# Regional Work Stoppages KPI Implementation

## Overview

The **Regional Work Stoppages Analysis** KPI has been successfully implemented across all SRS dashboard variants (Standard, Enriched, and Augmented). This KPI provides comprehensive analysis of work stoppages by region, identifying the most common causes and their impact on operational efficiency.

## Business Context

**KPI Name**: Regional Work Stoppages Analysis  
**Business Purpose**: Analyze work stoppages by region to identify patterns, most common causes, and operational impact  
**Target Audience**: Safety managers, regional supervisors, operational leaders  
**Business Value**: Enables targeted interventions to reduce work stoppages and improve operational efficiency

## Technical Implementation

### Files Modified

#### KPI Query Files
1. **`shindler_server/kpis/srs_kpis.py`**
   - Added `get_regional_work_stoppages_analysis()` method
   - Updated `get_all_kpis()` to include the new KPI

2. **`shindler_server/kpis/srs_enriched_kpis.py`**
   - Added `get_regional_work_stoppages_analysis()` method
   - Updated `get_all_kpis()` to include the new KPI

3. **`shindler_server/kpis/srs_agumented_kpis.py`**
   - Added `get_regional_work_stoppages_analysis()` method
   - Updated `get_all_kpis()` to include the new KPI

#### Dashboard Service Files
1. **`shindler_server/dashboard/srs_dashboard_service.py`**
   - Added `_get_regional_work_stoppages_analysis()` method
   - Updated `_get_all_kpis()` to include the new KPI
   - Updated `_get_empty_dashboard_data()` to include empty structure
   - Updated KPI count from 14 to 15

2. **`shindler_server/dashboard/srs_enriched_dashboard_service.py`**
   - Added `_get_regional_work_stoppages_analysis()` method
   - Updated `_get_all_kpis()` to include the new KPI
   - Updated `_get_empty_dashboard_data()` to include empty structure
   - Updated KPI count from 14 to 15

3. **`shindler_server/dashboard/srs_agumented_dashboard_service.py`**
   - Added `_srs_regional_work_stoppages_analysis()` method
   - Updated `_get_srs_standard_kpis()` to include the new KPI
   - Updated KPI count from 13 to 15

### SQL Logic

The KPI uses a sophisticated SQL query with multiple CTEs (Common Table Expressions) to:

1. **Filter Work Stoppages**: Identifies records where work was actually stopped using multiple criteria (`YES`, `Y`, `1`, `TRUE`)
2. **Categorize Causes**: Determines the primary cause of each work stoppage by analyzing:
   - `unsafe_event_type` field to identify act vs condition types
   - `unsafe_act` and `unsafe_act_other` fields for unsafe acts
   - `unsafe_condition` and `unsafe_condition_other` fields for unsafe conditions
   - Cross-references between fields when primary fields are empty
3. **Aggregate by Region**: Groups stoppages by region and calculates totals
4. **Identify Most Common Causes**: Uses `ROW_NUMBER()` to find the most frequent cause per region
5. **Calculate Percentages**: Shows what percentage of regional stoppages each cause represents

### Key Features

- **Comprehensive Cause Analysis**: Handles multiple field combinations and cross-references
- **Regional Focus**: Provides region-specific insights for targeted interventions
- **Most Common Cause Identification**: Highlights the primary cause in each region
- **Percentage Calculations**: Shows relative impact of each cause
- **Date and Region Filtering**: Supports dashboard filtering capabilities
- **Error Handling**: Graceful degradation when data is unavailable

## Data Structure

### Output Format
```json
{
  "chart_type": "table",
  "description": "Regional analysis of work stoppages with most common causes per region",
  "data": [
    {
      "region": "Region Name",
      "total_work_stoppages": 25,
      "most_common_stoppage_cause": "Unsafe Act: Improper lifting technique",
      "most_common_cause_count": 8,
      "percentage_of_region_stoppages": 32.0
    }
  ]
}
```

### Fields Explained
- **region**: Geographic region where stoppages occurred
- **total_work_stoppages**: Total number of work stoppages in the region
- **most_common_stoppage_cause**: The most frequently occurring cause of work stoppage
- **most_common_cause_count**: Number of times the most common cause occurred
- **percentage_of_region_stoppages**: Percentage of regional stoppages attributed to the most common cause

## Usage in Dashboards

### Dashboard Integration
The KPI is available in all SRS dashboard variants:
- **SRS Standard Dashboard**: Shows work stoppages analysis for standard SRS data
- **SRS Enriched Dashboard**: Enhanced analysis with enriched data fields
- **SRS Augmented Dashboard**: Comprehensive analysis including augmented employee and equipment data

### Chart Type
- **Display Format**: Table chart for detailed regional comparison
- **Sorting**: Ordered by total work stoppages (descending)
- **Filtering**: Supports date range and region-specific filtering

## Business Value

### Operational Insights
1. **Regional Hotspots**: Identifies regions with highest work stoppage rates
2. **Cause Patterns**: Reveals most common causes by region for targeted training
3. **Resource Allocation**: Helps prioritize safety interventions and training programs
4. **Performance Monitoring**: Tracks improvement in work stoppage reduction

### Strategic Benefits
1. **Risk Mitigation**: Proactive identification of high-risk regions and causes
2. **Cost Reduction**: Reduces operational costs associated with work stoppages
3. **Compliance**: Supports safety compliance and regulatory reporting
4. **Continuous Improvement**: Enables data-driven safety program enhancements

## Technical Specifications

### Performance Considerations
- **Query Optimization**: Uses CTEs for efficient data processing
- **Indexing**: Leverages existing indexes on region and date fields
- **Filtering**: Efficient date and region filtering for dashboard performance
- **Session Management**: Optimized database session handling

### Data Quality
- **Null Handling**: Comprehensive handling of null and empty values
- **Data Validation**: Validates work stoppage indicators across multiple formats
- **Cross-Reference Logic**: Robust logic for determining causes when primary fields are empty
- **Error Recovery**: Graceful handling of data inconsistencies

### Scalability
- **Large Dataset Support**: Efficient processing of large datasets
- **Regional Distribution**: Scales across multiple regions and locations
- **Time Series Analysis**: Supports historical trend analysis
- **Real-time Updates**: Compatible with real-time dashboard updates

## Future Enhancements

### Potential Improvements
1. **Trend Analysis**: Add time-based trend analysis for work stoppages
2. **Predictive Modeling**: Implement predictive analytics for stoppage prevention
3. **Cost Impact**: Include financial impact calculations for work stoppages
4. **Employee Correlation**: Link stoppages to specific employee factors (training, experience)
5. **Equipment Analysis**: Analyze equipment-related work stoppages
6. **Weather Correlation**: Include weather conditions in stoppage analysis

### Integration Opportunities
1. **Training Management**: Link to training completion and effectiveness data
2. **Equipment Maintenance**: Integrate with equipment maintenance schedules
3. **Weather Data**: Include weather condition correlations
4. **Employee Analytics**: Connect with employee performance and training data

## Conclusion

The Regional Work Stoppages Analysis KPI provides valuable insights into operational safety and efficiency across all regions. By identifying patterns and most common causes, it enables targeted interventions to reduce work stoppages and improve overall operational performance. The implementation follows established patterns and integrates seamlessly with existing dashboard infrastructure.

