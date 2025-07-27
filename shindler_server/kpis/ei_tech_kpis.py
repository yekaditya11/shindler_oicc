"""
EI Tech App Sheet KPI SQL Queries
Comprehensive SQL queries for all safety KPIs from EI Tech App data with date filtering support
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, date, timedelta

from config.database_config import get_session

logger = logging.getLogger(__name__)

class EITechKPIQueries:
    """SQL queries for EI Tech App KPIs with date filtering support"""
    
    def __init__(self, start_date: Optional[str] = None, end_date: Optional[str] = None):
        self.table_name = "unsafe_events_ei_tech"
        
        # Set default date range to 1 year from today if no dates provided
        if start_date is None and end_date is None:
            # Default to 1 year of data from today
            today = date.today()
            one_year_ago = today - timedelta(days=365)
            self.start_date = one_year_ago.strftime('%Y-%m-%d')
            self.end_date = today.strftime('%Y-%m-%d')
            logger.info(f"No date range provided, defaulting to 1 year: {self.start_date} to {self.end_date}")
        else:
            self.start_date = start_date
            self.end_date = end_date
            
        self.date_filter = self._build_date_filter()
    
    def _build_date_filter(self) -> str:
        """Build date filter clause for SQL queries"""
        conditions = []
        
        if self.start_date:
            conditions.append(f"date_of_unsafe_event >= '{self.start_date}'")
        
        if self.end_date:
            conditions.append(f"date_of_unsafe_event <= '{self.end_date}'")
        
        if conditions:
            return "AND " + " AND ".join(conditions)
        return ""
    
    def get_session(self) -> Session:
        """Get database session"""
        return get_session()
    
    def execute_query(self, query: str, params: Dict = None) -> List[Dict]:
        """Execute SQL query and return results"""
        session = self.get_session()
        try:
            result = session.execute(text(query), params or {})
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
        finally:
            session.close()
    
    # ==================== EVENT VOLUME & FREQUENCY ====================
    
    def get_total_events_count(self) -> Dict[str, Any]:
        """Total events count with date filtering"""
        query = f"""
        SELECT 
            COUNT(*) as total_events,
            COUNT(DISTINCT event_id) as unique_events
        FROM {self.table_name}
        WHERE event_id IS NOT NULL {self.date_filter}
        """
        return self.execute_query(query)[0]
    
    def get_events_per_time_period(self, period: str = 'month') -> List[Dict]:
        """Events per time period using date_of_unsafe_event and reported_date with date filtering"""
        if period == 'month':
            date_part = "TO_CHAR(date_of_unsafe_event, 'YYYY-MM')"
        elif period == 'week':
            date_part = "TO_CHAR(date_of_unsafe_event, 'YYYY-WW')"
        elif period == 'day':
            date_part = "date_of_unsafe_event::date"
        else:
            date_part = "EXTRACT(YEAR FROM date_of_unsafe_event)"

        query = f"""
        SELECT
            {date_part} as event_period,
            COUNT(*) as events_by_event_date,
            COUNT(CASE WHEN reported_date IS NOT NULL THEN 1 END) as events_with_reported_date,
            AVG(CASE
                WHEN date_of_unsafe_event IS NOT NULL AND reported_date IS NOT NULL
                THEN reported_date - date_of_unsafe_event
            END) as avg_reporting_delay_days
        FROM {self.table_name}
        WHERE date_of_unsafe_event IS NOT NULL {self.date_filter}
        GROUP BY {date_part}
        ORDER BY event_period
        """
        return self.execute_query(query)
    
    # ==================== SAFETY SEVERITY ====================
    
    def get_serious_near_miss_count(self) -> Dict[str, Any]:
        """Serious near miss count with date filtering"""
        query = f"""
        SELECT 
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'NO' THEN 1 END) as non_serious_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as serious_near_miss_percentage
        FROM {self.table_name}
        WHERE 1=1 {self.date_filter}
        """
        return self.execute_query(query)[0]
    

    
    def get_nogo_violations_count(self) -> List[Dict]:
        """NOGO violations count with date filtering"""
        query = f"""
        SELECT 
            stop_work_nogo_violation,
            COUNT(*) as violation_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {self.table_name}
        WHERE stop_work_nogo_violation IS NOT NULL 
        AND stop_work_nogo_violation != '' {self.date_filter}
        GROUP BY stop_work_nogo_violation
        ORDER BY violation_count DESC
        """
        return self.execute_query(query)
    
    # ==================== GEOGRAPHIC DISTRIBUTION ====================

    def get_events_by_region_country_division(self) -> List[Dict]:
        """Events by region, country_name, division, department with date filtering"""
        query = f"""
        SELECT
            region,
            country_name,
            division,
            department,
            COUNT(*) as event_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {self.table_name}
        WHERE (region IS NOT NULL OR country_name IS NOT NULL
        OR division IS NOT NULL OR department IS NOT NULL) {self.date_filter}
        GROUP BY region, country_name, division, department
        ORDER BY event_count DESC
        """
        return self.execute_query(query)
    
    def get_events_by_branch(self) -> List[Dict]:
        """Events by branch with date filtering"""
        query = f"""
        SELECT 
            branch,
            COUNT(*) as event_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {self.table_name}
        WHERE branch IS NOT NULL {self.date_filter}
        GROUP BY branch
        ORDER BY event_count DESC
        """
        return self.execute_query(query)
    
    # ==================== OPERATIONAL METRICS ====================

    def get_events_by_business_details(self) -> List[Dict]:
        """Events by business_details with date filtering"""
        query = f"""
        SELECT
            business_details,
            COUNT(*) as event_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {self.table_name}
        WHERE business_details IS NOT NULL {self.date_filter}
        GROUP BY business_details
        ORDER BY event_count DESC
        """
        return self.execute_query(query)

    def get_events_by_unsafe_event_location(self) -> List[Dict]:
        """Events by unsafe_event_location with date filtering"""
        query = f"""
        SELECT
            unsafe_event_location,
            COUNT(*) as event_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {self.table_name}
        WHERE unsafe_event_location IS NOT NULL {self.date_filter}
        GROUP BY unsafe_event_location
        ORDER BY event_count DESC
        """
        return self.execute_query(query)

    def get_stop_work_duration_analysis(self) -> List[Dict]:
        """Stop work duration analysis with date filtering"""
        query = f"""
        SELECT
            stop_work_duration,
            COUNT(*) as event_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {self.table_name}
        WHERE stop_work_duration IS NOT NULL
        AND UPPER(work_stopped) = 'YES' {self.date_filter}
        GROUP BY stop_work_duration
        ORDER BY event_count DESC
        """
        return self.execute_query(query)

    # ==================== RESPONSE & ACTIONS ====================

    def get_action_completion_rate(self) -> Dict[str, Any]:
        """Action completion rate with date filtering"""
        query = f"""
        SELECT
            COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) as action_1_filled,
            COUNT(CASE WHEN action_description_2 IS NOT NULL AND action_description_2 != '' THEN 1 END) as action_2_filled,
            COUNT(CASE WHEN action_description_3 IS NOT NULL AND action_description_3 != '' THEN 1 END) as action_3_filled,
            COUNT(CASE WHEN action_description_4 IS NOT NULL AND action_description_4 != '' THEN 1 END) as action_4_filled,
            COUNT(CASE WHEN action_description_5 IS NOT NULL AND action_description_5 != '' THEN 1 END) as action_5_filled,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as action_1_completion_rate,
            ROUND(COUNT(CASE WHEN action_description_2 IS NOT NULL AND action_description_2 != '' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as action_2_completion_rate,
            ROUND(COUNT(CASE WHEN action_description_3 IS NOT NULL AND action_description_3 != '' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as action_3_completion_rate,
            ROUND(COUNT(CASE WHEN action_description_4 IS NOT NULL AND action_description_4 != '' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as action_4_completion_rate,
            ROUND(COUNT(CASE WHEN action_description_5 IS NOT NULL AND action_description_5 != '' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as action_5_completion_rate
        FROM {self.table_name}
        WHERE 1=1 {self.date_filter}
        """
        return self.execute_query(query)[0]

    # ==================== ADDITIONAL ANALYSIS METHODS ====================

    def get_unsafe_acts_and_conditions_analysis(self) -> List[Dict]:
        """Analysis of unsafe acts and conditions with date filtering"""
        query = f"""
        SELECT
            'Unsafe Acts' as category,
            unsafe_act as description,
            COUNT(*) as count
        FROM {self.table_name}
        WHERE unsafe_act IS NOT NULL AND unsafe_act != '' {self.date_filter}
        GROUP BY unsafe_act

        UNION ALL

        SELECT
            'Unsafe Conditions' as category,
            unsafe_condition as description,
            COUNT(*) as count
        FROM {self.table_name}
        WHERE unsafe_condition IS NOT NULL AND unsafe_condition != '' {self.date_filter}
        GROUP BY unsafe_condition

        ORDER BY count DESC
        """
        return self.execute_query(query)

    def get_branch_risk_index(self) -> List[Dict]:
        """Branch Risk Index calculation with date filtering"""
        query = f"""
        SELECT
            branch,
            COUNT(*) as total_incidents,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
            COUNT(CASE WHEN UPPER(event_requires_sanction) = 'YES' THEN 1 END) as sanctions_required,
            ROUND(
                (COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 3 +
                 COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 2 +
                 COUNT(CASE WHEN UPPER(event_requires_sanction) = 'YES' THEN 1 END) * 1 +
                 COUNT(*) * 0.5) * 100.0 / NULLIF(COUNT(*), 0), 2
            ) as branch_risk_index,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate
        FROM {self.table_name}
        WHERE branch IS NOT NULL {self.date_filter}
        GROUP BY branch
        ORDER BY branch_risk_index DESC, total_incidents DESC
        """
        return self.execute_query(query)

    def get_time_based_trends(self) -> List[Dict]:
        """Time-based trend analysis with date filtering"""
        query = f"""
        SELECT
            EXTRACT(YEAR FROM date_of_unsafe_event) as year,
            EXTRACT(MONTH FROM date_of_unsafe_event) as month,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_count,
            COUNT(CASE WHEN UPPER(event_requires_sanction) = 'YES' THEN 1 END) as sanction_required_count
        FROM {self.table_name}
        WHERE date_of_unsafe_event IS NOT NULL {self.date_filter}
        GROUP BY EXTRACT(YEAR FROM date_of_unsafe_event), EXTRACT(MONTH FROM date_of_unsafe_event)
        ORDER BY year, month
        """
        return self.execute_query(query)

    # ==================== ENHANCED KPIs FOR BETTER INSIGHTS ====================

    def get_reporting_delay_analysis(self) -> Dict[str, Any]:
        """Analyze reporting delays and patterns with date filtering"""
        query = f"""
        SELECT
            COUNT(*) as total_events_with_dates,
            COUNT(CASE WHEN reported_date - date_of_unsafe_event = 0 THEN 1 END) as same_day_reports,
            COUNT(CASE WHEN reported_date - date_of_unsafe_event BETWEEN 1 AND 3 THEN 1 END) as reports_1_3_days,
            COUNT(CASE WHEN reported_date - date_of_unsafe_event BETWEEN 4 AND 7 THEN 1 END) as reports_4_7_days,
            COUNT(CASE WHEN reported_date - date_of_unsafe_event > 7 THEN 1 END) as reports_over_7_days,
            CAST((AVG(reported_date - date_of_unsafe_event)) AS DECIMAL(10,2)) as avg_delay_days,
            MAX(reported_date - date_of_unsafe_event) as max_delay_days,
            ROUND(COUNT(CASE WHEN reported_date - date_of_unsafe_event = 0 THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as same_day_reporting_rate
        FROM {self.table_name}
        WHERE date_of_unsafe_event IS NOT NULL
        AND reported_date IS NOT NULL {self.date_filter}
        """
        return self.execute_query(query)[0]



    def get_action_effectiveness_analysis(self) -> Dict[str, Any]:
        """Analyze action plan effectiveness and completeness with date filtering"""
        query = f"""
        SELECT
            COUNT(*) as total_events,
            COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) as events_with_action_1,
            COUNT(CASE WHEN action_description_2 IS NOT NULL AND action_description_2 != '' THEN 1 END) as events_with_action_2,
            COUNT(CASE WHEN action_description_3 IS NOT NULL AND action_description_3 != '' THEN 1 END) as events_with_action_3,
            COUNT(CASE WHEN action_description_4 IS NOT NULL AND action_description_4 != '' THEN 1 END) as events_with_action_4,
            COUNT(CASE WHEN action_description_5 IS NOT NULL AND action_description_5 != '' THEN 1 END) as events_with_action_5,
            COUNT(CASE WHEN (action_description_1 IS NOT NULL AND action_description_1 != '')
                           AND (action_description_2 IS NOT NULL AND action_description_2 != '') THEN 1 END) as events_with_multiple_actions,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES'
                           AND (action_description_1 IS NULL OR action_description_1 = '') THEN 1 END) as serious_incidents_no_action,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES'
                               AND (action_description_1 IS NOT NULL AND action_description_1 != '') THEN 1 END) * 100.0 /
                  NULLIF(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END), 0), 2) as serious_incidents_action_rate
        FROM {self.table_name}
        WHERE 1=1 {self.date_filter}
        """
        return self.execute_query(query)[0]



    def get_high_risk_location_analysis(self) -> List[Dict]:
        """Identify high-risk locations and unsafe event hotspots with date filtering"""
        query = f"""
        SELECT
            unsafe_event_location,
            COUNT(*) as total_incidents,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
            COUNT(DISTINCT COALESCE(employee_name, subcontractor_name)) as unique_people_involved,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total
        FROM {self.table_name}
        WHERE unsafe_event_location IS NOT NULL {self.date_filter}
        GROUP BY unsafe_event_location
        HAVING COUNT(*) >= 2
        ORDER BY total_incidents DESC, serious_incident_rate DESC
        LIMIT 30
        """
        return self.execute_query(query)



    def get_time_of_day_incident_patterns(self) -> List[Dict]:
        """Time of day incident patterns with date filtering"""
        query = f"""
        SELECT
            CASE
                WHEN time_of_unsafe_event IS NULL OR time_of_unsafe_event = '' THEN 'Unknown'
                WHEN time_of_unsafe_event ~ '^([0-9]|1[0-9]|2[0-3]):[0-5][0-9]' THEN
                    CASE
                        WHEN CAST(SPLIT_PART(time_of_unsafe_event, ':', 1) AS INTEGER) BETWEEN 6 AND 11 THEN 'Morning (6-11 AM)'
                        WHEN CAST(SPLIT_PART(time_of_unsafe_event, ':', 1) AS INTEGER) BETWEEN 12 AND 17 THEN 'Afternoon (12-5 PM)'
                        WHEN CAST(SPLIT_PART(time_of_unsafe_event, ':', 1) AS INTEGER) BETWEEN 18 AND 23 THEN 'Evening (6-11 PM)'
                        WHEN CAST(SPLIT_PART(time_of_unsafe_event, ':', 1) AS INTEGER) BETWEEN 0 AND 5 THEN 'Night (12-5 AM)'
                        ELSE 'Unknown'
                    END
                ELSE 'Invalid Format'
            END as time_period,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate,
            STRING_AGG(DISTINCT unsafe_act, '; ') as common_unsafe_acts
        FROM {self.table_name}
        WHERE time_of_unsafe_event IS NOT NULL AND time_of_unsafe_event != '' {self.date_filter}
        GROUP BY
            CASE
                WHEN time_of_unsafe_event IS NULL OR time_of_unsafe_event = '' THEN 'Unknown'
                WHEN time_of_unsafe_event ~ '^([0-9]|1[0-9]|2[0-3]):[0-5][0-9]' THEN
                    CASE
                        WHEN CAST(SPLIT_PART(time_of_unsafe_event, ':', 1) AS INTEGER) BETWEEN 6 AND 11 THEN 'Morning (6-11 AM)'
                        WHEN CAST(SPLIT_PART(time_of_unsafe_event, ':', 1) AS INTEGER) BETWEEN 12 AND 17 THEN 'Afternoon (12-5 PM)'
                        WHEN CAST(SPLIT_PART(time_of_unsafe_event, ':', 1) AS INTEGER) BETWEEN 18 AND 23 THEN 'Evening (6-11 PM)'
                        WHEN CAST(SPLIT_PART(time_of_unsafe_event, ':', 1) AS INTEGER) BETWEEN 0 AND 5 THEN 'Night (12-5 AM)'
                        ELSE 'Unknown'
                    END
                ELSE 'Invalid Format'
            END
        ORDER BY incident_count DESC
        """
        return self.execute_query(query)



    def get_regional_safety_performance(self) -> List[Dict]:
        """Comprehensive regional safety performance analysis with date filtering"""
        query = f"""
        SELECT
            region,
            country_name,
            COUNT(*) as total_incidents,
            COUNT(DISTINCT branch) as branches_involved,
            COUNT(DISTINCT manager_name) as managers_involved,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
            COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) as incidents_with_actions,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate,
            ROUND(COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as action_completion_rate,
            AVG(CASE
                WHEN date_of_unsafe_event IS NOT NULL AND reported_date IS NOT NULL
                THEN reported_date - date_of_unsafe_event
            END) as avg_reporting_delay_days
        FROM {self.table_name}
        WHERE (region IS NOT NULL OR country_name IS NOT NULL) {self.date_filter}
        GROUP BY region, country_name
        ORDER BY total_incidents DESC, serious_incident_rate DESC
        """
        return self.execute_query(query)

    # ==================== OPERATIONAL ALERTS & INSIGHTS ====================

    def get_regional_operational_alerts(self, days_back: int = 30) -> List[Dict]:
        """Generate operational alerts comparing recent performance to historical averages"""
        query = f"""
        WITH recent_data AS (
            SELECT
                region,
                COUNT(*) as recent_incidents,
                COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as recent_work_stoppages,
                COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as recent_serious_incidents
            FROM {self.table_name}
            WHERE date_of_unsafe_event >= CURRENT_DATE - INTERVAL '{days_back} days'
            AND region IS NOT NULL
            GROUP BY region
        ),
        historical_avg AS (
            SELECT
                region,
                AVG(monthly_incidents) as avg_monthly_incidents,
                AVG(monthly_work_stoppages) as avg_monthly_work_stoppages,
                AVG(monthly_serious_incidents) as avg_monthly_serious_incidents
            FROM (
                SELECT
                    region,
                    EXTRACT(YEAR FROM date_of_unsafe_event) as year,
                    EXTRACT(MONTH FROM date_of_unsafe_event) as month,
                    COUNT(*) as monthly_incidents,
                    COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as monthly_work_stoppages,
                    COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as monthly_serious_incidents
                FROM {self.table_name}
                WHERE date_of_unsafe_event < CURRENT_DATE - INTERVAL '{days_back} days'
                AND date_of_unsafe_event >= CURRENT_DATE - INTERVAL '12 months'
                AND region IS NOT NULL
                GROUP BY region, EXTRACT(YEAR FROM date_of_unsafe_event), EXTRACT(MONTH FROM date_of_unsafe_event)
            ) monthly_stats
            GROUP BY region
        )
        SELECT
            r.region,
            r.recent_incidents,
            r.recent_work_stoppages,
            r.recent_serious_incidents,
            h.avg_monthly_incidents,
            h.avg_monthly_work_stoppages,
            h.avg_monthly_serious_incidents,
            ROUND(((r.recent_incidents - h.avg_monthly_incidents) / NULLIF(h.avg_monthly_incidents, 0)) * 100, 1) as incident_variance_percent,
            ROUND(((r.recent_work_stoppages - h.avg_monthly_work_stoppages) / NULLIF(h.avg_monthly_work_stoppages, 0)) * 100, 1) as work_stoppage_variance_percent,
            CASE
                WHEN ((r.recent_incidents - h.avg_monthly_incidents) / NULLIF(h.avg_monthly_incidents, 0)) * 100 > 25 THEN 'HIGH_ALERT'
                WHEN ((r.recent_incidents - h.avg_monthly_incidents) / NULLIF(h.avg_monthly_incidents, 0)) * 100 > 15 THEN 'MEDIUM_ALERT'
                ELSE 'NORMAL'
            END as alert_level
        FROM recent_data r
        JOIN historical_avg h ON r.region = h.region
        WHERE h.avg_monthly_incidents > 0
        ORDER BY incident_variance_percent DESC
        """
        return self.execute_query(query)

    def get_branch_workload_alerts(self, days_back: int = 7) -> List[Dict]:
        """Identify branches with unusual workload patterns"""
        query = f"""
        WITH recent_branch_data AS (
            SELECT
                branch,
                COUNT(*) as recent_incidents,
                COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
                AVG(CASE
                    WHEN reported_date IS NOT NULL AND date_of_unsafe_event IS NOT NULL
                    THEN reported_date - date_of_unsafe_event
                END) as avg_reporting_delay,
                COUNT(CASE WHEN stop_work_duration IS NOT NULL AND stop_work_duration != '' THEN 1 END) as incidents_with_duration
            FROM {self.table_name}
            WHERE date_of_unsafe_event >= CURRENT_DATE - INTERVAL '{days_back} days'
            AND branch IS NOT NULL
            GROUP BY branch
        ),
        branch_avg AS (
            SELECT
                branch,
                AVG(weekly_incidents) as avg_weekly_incidents
            FROM (
                SELECT
                    branch,
                    EXTRACT(YEAR FROM date_of_unsafe_event) as year,
                    EXTRACT(WEEK FROM date_of_unsafe_event) as week,
                    COUNT(*) as weekly_incidents
                FROM {self.table_name}
                WHERE date_of_unsafe_event < CURRENT_DATE - INTERVAL '{days_back} days'
                AND date_of_unsafe_event >= CURRENT_DATE - INTERVAL '12 weeks'
                AND branch IS NOT NULL
                GROUP BY branch, EXTRACT(YEAR FROM date_of_unsafe_event), EXTRACT(WEEK FROM date_of_unsafe_event)
            ) weekly_stats
            GROUP BY branch
        )
        SELECT
            r.branch,
            r.recent_incidents,
            r.work_stoppages,
            r.avg_reporting_delay,
            b.avg_weekly_incidents,
            ROUND(((r.recent_incidents - b.avg_weekly_incidents) / NULLIF(b.avg_weekly_incidents, 0)) * 100, 1) as workload_variance_percent,
            CASE
                WHEN ((r.recent_incidents - b.avg_weekly_incidents) / NULLIF(b.avg_weekly_incidents, 0)) * 100 > 30 THEN 'OVERLOADED'
                WHEN r.avg_reporting_delay > 3 THEN 'DELAYED_REPORTING'
                WHEN r.work_stoppages > r.recent_incidents * 0.5 THEN 'HIGH_DISRUPTION'
                ELSE 'NORMAL'
            END as workload_status
        FROM recent_branch_data r
        JOIN branch_avg b ON r.branch = b.branch
        WHERE b.avg_weekly_incidents > 0
        ORDER BY workload_variance_percent DESC
        """
        return self.execute_query(query)

    # ==================== VIOLATION CLUSTERS & PATTERNS ====================

    def get_violation_clusters_with_reasons(self, days_back: int = 30) -> List[Dict]:
        """Identify violation clusters with detailed reasons from comments"""
        query = f"""
        SELECT
            stop_work_nogo_violation,
            branch,
            region,
            COUNT(*) as violation_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total,
            STRING_AGG(DISTINCT
                CASE
                    WHEN comments_remarks IS NOT NULL AND LENGTH(TRIM(comments_remarks)) > 10
                    THEN SUBSTRING(comments_remarks, 1, 100)
                END, ' | ') as common_reasons,
            STRING_AGG(DISTINCT
                CASE
                    WHEN nogo_violation_detail IS NOT NULL AND LENGTH(TRIM(nogo_violation_detail)) > 5
                    THEN SUBSTRING(nogo_violation_detail, 1, 100)
                END, ' | ') as violation_details,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            MAX(date_of_unsafe_event) as latest_incident_date,
            COUNT(DISTINCT employee_name) as unique_people_involved
        FROM {self.table_name}
        WHERE date_of_unsafe_event >= CURRENT_DATE - INTERVAL '{days_back} days'
        AND stop_work_nogo_violation IS NOT NULL
        AND stop_work_nogo_violation != ''
        GROUP BY stop_work_nogo_violation, branch, region
        HAVING COUNT(*) >= 2
        ORDER BY violation_count DESC, branch
        LIMIT 20
        """
        return self.execute_query(query)

    def get_location_incident_clusters(self, min_incidents: int = 3) -> List[Dict]:
        """Identify high-risk locations with incident clustering and reasons"""
        query = f"""
        SELECT
            unsafe_event_location,
            branch,
            region,
            COUNT(*) as total_incidents,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate,
            STRING_AGG(DISTINCT unsafe_act, '; ') as common_unsafe_acts,
            STRING_AGG(DISTINCT unsafe_condition, '; ') as common_unsafe_conditions,
            STRING_AGG(DISTINCT
                CASE
                    WHEN comments_remarks IS NOT NULL AND LENGTH(TRIM(comments_remarks)) > 10
                    THEN SUBSTRING(comments_remarks, 1, 150)
                END, ' | ') as incident_reasons,
            COUNT(DISTINCT COALESCE(employee_name, subcontractor_name)) as unique_people_involved,
            MAX(date_of_unsafe_event) as latest_incident,
            MIN(date_of_unsafe_event) as first_incident
        FROM {self.table_name}
        WHERE unsafe_event_location IS NOT NULL
        GROUP BY unsafe_event_location, branch, region
        HAVING COUNT(*) >= {min_incidents}
        ORDER BY total_incidents DESC, serious_incident_rate DESC
        LIMIT 25
        """
        return self.execute_query(query)

    # ==================== STAFF IMPACT & PERFORMANCE ANALYSIS ====================

    def get_staff_performance_analysis(self) -> List[Dict]:
        """Analyze staff performance with work stoppage and incident rates"""
        query = f"""
        SELECT
            COALESCE(employee_name, subcontractor_name, 'Unknown') as staff_name,
            COALESCE(subcontractor_company_name, 'Internal') as company,
            branch,
            COUNT(*) as total_incidents,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            SUM(CASE
                WHEN stop_work_duration LIKE '%hour%' THEN
                    CAST(REGEXP_REPLACE(stop_work_duration, '[^0-9.]', '', 'g') AS FLOAT)
                WHEN stop_work_duration LIKE '%day%' THEN
                    CAST(REGEXP_REPLACE(stop_work_duration, '[^0-9.]', '', 'g') AS FLOAT) * 8
                ELSE 0
            END) as total_work_hours_lost,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'NO' OR work_stopped IS NULL THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as work_continuation_rate,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'NO' OR serious_near_miss IS NULL THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as safety_performance_rate,
            COUNT(DISTINCT site_reference) as sites_worked,
            MAX(date_of_unsafe_event) as last_incident_date,
            STRING_AGG(DISTINCT
                CASE
                    WHEN comments_remarks IS NOT NULL AND LENGTH(TRIM(comments_remarks)) > 10
                    THEN SUBSTRING(comments_remarks, 1, 100)
                END, ' | ') as performance_notes
        FROM {self.table_name}
        WHERE (employee_name IS NOT NULL OR subcontractor_name IS NOT NULL)
        GROUP BY COALESCE(employee_name, subcontractor_name),
                 COALESCE(subcontractor_company_name, 'Internal'), branch
        HAVING COUNT(*) >= 2
        ORDER BY work_continuation_rate DESC, safety_performance_rate DESC, total_incidents DESC
        LIMIT 30
        """
        return self.execute_query(query)

    def get_high_performing_staff(self) -> List[Dict]:
        """Identify high-performing staff with minimal disruptions"""
        query = f"""
        SELECT
            COALESCE(employee_name, subcontractor_name) as staff_name,
            COALESCE(subcontractor_company_name, 'Internal') as company,
            branch,
            region,
            COUNT(*) as total_jobs_involved,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'NO' OR work_stopped IS NULL THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as job_completion_rate,
            ROUND(COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as proactive_action_rate,
            COUNT(DISTINCT unsafe_event_location) as locations_worked,
            AVG(CASE
                WHEN reported_date IS NOT NULL AND date_of_unsafe_event IS NOT NULL
                THEN reported_date - date_of_unsafe_event
            END) as avg_reporting_speed_days
        FROM {self.table_name}
        WHERE (employee_name IS NOT NULL OR subcontractor_name IS NOT NULL)
        AND date_of_unsafe_event >= CURRENT_DATE - INTERVAL '6 months'
        GROUP BY COALESCE(employee_name, subcontractor_name),
                 COALESCE(subcontractor_company_name, 'Internal'), branch, region
        HAVING COUNT(*) >= 3
        AND COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) = 0  -- Zero work stoppages
        ORDER BY job_completion_rate DESC, proactive_action_rate DESC
        LIMIT 20
        """
        return self.execute_query(query)

    # ==================== RESOURCE OPTIMIZATION INSIGHTS ====================

    def get_resource_optimization_patterns(self) -> List[Dict]:
        """Identify patterns for resource optimization based on incident analysis"""
        query = f"""
        SELECT
            branch,
            unsafe_event_location,
            business_details,
            COUNT(*) as incident_frequency,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_disruptions,
            STRING_AGG(DISTINCT unsafe_condition, '; ') as common_conditions,
            STRING_AGG(DISTINCT
                CASE
                    WHEN comments_remarks IS NOT NULL AND LENGTH(TRIM(comments_remarks)) > 10
                    THEN SUBSTRING(comments_remarks, 1, 100)
                END, ' | ') as root_causes,
            STRING_AGG(DISTINCT
                CASE
                    WHEN action_description_1 IS NOT NULL AND LENGTH(TRIM(action_description_1)) > 10
                    THEN SUBSTRING(action_description_1, 1, 100)
                END, ' | ') as recommended_actions,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as disruption_rate,
            EXTRACT(MONTH FROM MAX(date_of_unsafe_event)) as peak_month,
            COUNT(DISTINCT COALESCE(employee_name, subcontractor_name)) as people_affected
        FROM {self.table_name}
        WHERE unsafe_event_location IS NOT NULL
        AND business_details IS NOT NULL
        GROUP BY branch, unsafe_event_location, business_details
        HAVING COUNT(*) >= 3
        ORDER BY incident_frequency DESC, disruption_rate DESC
        LIMIT 25
        """
        return self.execute_query(query)

    def get_seasonal_resource_recommendations(self) -> List[Dict]:
        """Generate seasonal resource recommendations based on incident patterns"""
        query = f"""
        WITH seasonal_patterns AS (
            SELECT
                branch,
                business_details,
                EXTRACT(MONTH FROM date_of_unsafe_event) as incident_month,
                CASE
                    WHEN EXTRACT(MONTH FROM date_of_unsafe_event) IN (6,7,8,9) THEN 'Monsoon'
                    WHEN EXTRACT(MONTH FROM date_of_unsafe_event) IN (12,1,2) THEN 'Winter'
                    WHEN EXTRACT(MONTH FROM date_of_unsafe_event) IN (3,4,5) THEN 'Summer'
                    ELSE 'Post-Monsoon'
                END as season,
                COUNT(*) as incidents,
                COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
                STRING_AGG(DISTINCT unsafe_condition, '; ') as seasonal_conditions,
                STRING_AGG(DISTINCT
                    CASE
                        WHEN comments_remarks IS NOT NULL AND LENGTH(TRIM(comments_remarks)) > 10
                        THEN SUBSTRING(comments_remarks, 1, 100)
                    END, ' | ') as seasonal_issues
            FROM {self.table_name}
            WHERE date_of_unsafe_event IS NOT NULL
            GROUP BY branch, business_details,
                     EXTRACT(MONTH FROM date_of_unsafe_event),
                     CASE
                         WHEN EXTRACT(MONTH FROM date_of_unsafe_event) IN (6,7,8,9) THEN 'Monsoon'
                         WHEN EXTRACT(MONTH FROM date_of_unsafe_event) IN (12,1,2) THEN 'Winter'
                         WHEN EXTRACT(MONTH FROM date_of_unsafe_event) IN (3,4,5) THEN 'Summer'
                         ELSE 'Post-Monsoon'
                     END
        )
        SELECT
            branch,
            business_details,
            season,
            SUM(incidents) as total_seasonal_incidents,
            SUM(work_stoppages) as total_seasonal_stoppages,
            ROUND(SUM(work_stoppages) * 100.0 / NULLIF(SUM(incidents), 0), 2) as seasonal_disruption_rate,
            STRING_AGG(DISTINCT seasonal_conditions, '; ') as common_seasonal_conditions,
            STRING_AGG(DISTINCT seasonal_issues, ' | ') as seasonal_root_causes
        FROM seasonal_patterns
        GROUP BY branch, business_details, season
        HAVING SUM(incidents) >= 3
        ORDER BY total_seasonal_incidents DESC, seasonal_disruption_rate DESC
        LIMIT 30
        """
        return self.execute_query(query)

    # ==================== ENHANCED KPIs FOR LLM INSIGHTS ====================

    def get_site_risk_profiles(self) -> List[Dict]:
        """Comprehensive site-level risk analysis for LLM insights"""
        query = f"""
        SELECT
            site_reference,
            product_type,
            branch,
            COUNT(*) as total_incidents,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
            COUNT(DISTINCT COALESCE(employee_name, subcontractor_name)) as unique_people_involved,
            COUNT(DISTINCT unsafe_event_location) as incident_locations,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate,
            CAST((AVG(CASE WHEN reported_date IS NOT NULL AND date_of_unsafe_event IS NOT NULL
                          THEN reported_date - date_of_unsafe_event END)) AS DECIMAL(10,2)) as avg_reporting_delay,
            MAX(date_of_unsafe_event) as last_incident_date,
            MIN(date_of_unsafe_event) as first_incident_date,
            STRING_AGG(DISTINCT unsafe_act, '; ') as common_unsafe_acts,
            STRING_AGG(DISTINCT unsafe_condition, '; ') as common_unsafe_conditions
        FROM {self.table_name}
        WHERE site_reference IS NOT NULL
        GROUP BY site_reference, product_type, branch
        HAVING COUNT(*) >= 2
        ORDER BY serious_incident_rate DESC, total_incidents DESC
        """
        return self.execute_query(query)

    def get_workforce_risk_profiles(self) -> List[Dict]:
        """Analyze risk patterns by workforce type for people-focused insights"""
        query = f"""
        SELECT
            CASE
                WHEN employee_name IS NOT NULL THEN 'Employee'
                WHEN subcontractor_name IS NOT NULL THEN 'Subcontractor'
                ELSE 'Unknown'
            END as workforce_type,
            COALESCE(subcontractor_company_name, 'Internal') as company,
            COUNT(*) as total_incidents,
            COUNT(DISTINCT COALESCE(employee_name, subcontractor_name)) as unique_individuals,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate,
            ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT COALESCE(employee_name, subcontractor_name)), 0), 2) as incidents_per_person,
            COUNT(DISTINCT site_reference) as sites_involved,
            COUNT(DISTINCT branch) as branches_involved,
            STRING_AGG(DISTINCT unsafe_act, '; ') as common_unsafe_acts
        FROM {self.table_name}
        GROUP BY
            CASE
                WHEN employee_name IS NOT NULL THEN 'Employee'
                WHEN subcontractor_name IS NOT NULL THEN 'Subcontractor'
                ELSE 'Unknown'
            END,
            COALESCE(subcontractor_company_name, 'Internal')
        ORDER BY serious_incident_rate DESC, total_incidents DESC
        """
        return self.execute_query(query)

    def get_day_of_week_patterns(self) -> List[Dict]:
        """Analyze incidents by day of week for temporal insights"""
        query = f"""
        SELECT
            TO_CHAR(date_of_unsafe_event, 'Day') as day_of_week,
            EXTRACT(DOW FROM date_of_unsafe_event) as day_number,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate,
            CAST((AVG(CASE WHEN reported_date IS NOT NULL AND date_of_unsafe_event IS NOT NULL
                          THEN reported_date - date_of_unsafe_event END)) AS DECIMAL(10,2)) as avg_reporting_delay,
            STRING_AGG(DISTINCT unsafe_act, '; ') as common_unsafe_acts
        FROM {self.table_name}
        WHERE date_of_unsafe_event IS NOT NULL
        GROUP BY TO_CHAR(date_of_unsafe_event, 'Day'), EXTRACT(DOW FROM date_of_unsafe_event)
        ORDER BY day_number
        """
        return self.execute_query(query)

    # ==================== ESSENTIAL KPI EXECUTION ====================

    def get_all_kpis(self) -> Dict[str, Any]:
        """Execute essential KPI queries optimized for analysis with date filtering"""
        try:
            logger.info(f"Executing essential EI Tech KPI queries with date filter: {self.date_filter}")

            results = {
                # ==================== CORE SAFETY METRICS ====================
                "number_of_unsafe_events": self.get_total_events_count(),
                "monthly_unsafe_events_trend": self.get_events_per_time_period('month'),
                "near_misses": self.get_serious_near_miss_count(),
                "serious_near_misses_trend": self.get_events_per_time_period('month'),

                # ==================== GEOGRAPHIC & RISK ANALYSIS ====================
                "unsafe_events_by_branch": self.get_events_by_branch(),
                "unsafe_events_by_region": self.get_events_by_region_country_division(),
                "at_risk_regions": self.get_high_risk_location_analysis(),
                "branch_risk_index": self.get_branch_risk_index(),
                "frequent_unsafe_event_locations": self.get_events_by_unsafe_event_location(),

                # ==================== BEHAVIORAL ANALYSIS ====================
                "common_unsafe_behaviors": self.get_unsafe_acts_and_conditions_analysis(),
                "common_unsafe_conditions": self.get_unsafe_acts_and_conditions_analysis(),
                "monthly_weekly_trends_unsafe_behaviors": self.get_time_based_trends(),
                "monthly_weekly_trends_unsafe_conditions": self.get_time_based_trends(),

                # ==================== OPERATIONAL IMPACT ====================
                "number_of_nogo_violations": self.get_nogo_violations_count(),
                "work_hours_lost": self.get_stop_work_duration_analysis(),
                "time_taken_to_report_incidents": self.get_reporting_delay_analysis(),

                # ==================== ACTION & COMPLIANCE ====================
                "action_creation_and_compliance": self.get_action_effectiveness_analysis(),
                "action_closure_rate": self.get_action_completion_rate(),

                # ==================== SECONDARY ANALYSIS ====================
                "unsafe_events_by_time_of_day": self.get_time_of_day_incident_patterns(),
                "unsafe_event_distribution_by_business_type": self.get_events_by_business_details(),
                "nogo_violation_trends_by_regions_branches": self.get_regional_safety_performance(),
            }

            # Add filter information to the results
            results["query_metadata"] = {
                "start_date": self.start_date,
                "end_date": self.end_date,
                "date_filter_applied": bool(self.start_date or self.end_date),
                "executed_at": datetime.now().isoformat()
            }

            logger.info("Essential KPI queries executed successfully")
            return results

        except Exception as e:
            logger.error(f"Error executing essential KPI queries: {e}")
            raise



