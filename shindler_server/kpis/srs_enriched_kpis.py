"""
SRS KPI Queries Module

This module provides comprehensive KPI queries for SRS (Safety Reporting System) unsafe events data.
It includes all standard KPIs plus advanced analytics for better safety insights.

Author: AI Assistant
Created: 2025-01-14
"""

import logging
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from config.database_config import db_manager

logger = logging.getLogger(__name__)


class SRSEnrichedKPIQueries:
    """SQL queries for SRS App KPIs"""
    
    def __init__(self):
        self.table_name = "unsafe_events_srs_enriched"
    
    def get_session(self) -> Session:
        """Get database session"""
        return db_manager.get_session()
    
    def execute_query(self, query: str, params: Dict = None, session: Session = None) -> List[Dict]:
        """Execute SQL query and return results"""
        # Use provided session or create a new one
        use_existing_session = session is not None
        if not session:
            session = self.get_session()

        try:
            result = session.execute(text(query), params or {})
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
        finally:
            # Only close session if we created it
            if not use_existing_session:
                session.close()
    
    # ==================== EVENT VOLUME & FREQUENCY ====================
    
    def get_total_events_count(self, session: Session = None) -> Dict[str, Any]:
        """Total events count"""
        query = f"""
        SELECT 
            COUNT(*) as total_events,
            COUNT(DISTINCT event_id) as unique_events
        FROM {self.table_name}
        WHERE event_id IS NOT NULL
        """
        return self.execute_query(query, {}, session)[0]
    
    def get_events_by_unsafe_event_type(self, session: Session = None) -> List[Dict]:
        """Events by unsafe_event_type"""
        query = f"""
        SELECT 
            unsafe_event_type,
            COUNT(*) as event_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {self.table_name}
        WHERE unsafe_event_type IS NOT NULL
        GROUP BY unsafe_event_type
        ORDER BY event_count DESC
        """
        return self.execute_query(query, {}, session)
    
    def get_events_per_time_period(self, period: str = 'month', session: Session = None) -> List[Dict]:
        """Events per time period (month/week/quarter)"""
        if period == 'month':
            date_part = "EXTRACT(YEAR FROM date_of_unsafe_event::date), EXTRACT(MONTH FROM date_of_unsafe_event::date)"
            date_format = "EXTRACT(YEAR FROM date_of_unsafe_event::date) || '-' || LPAD(EXTRACT(MONTH FROM date_of_unsafe_event::date)::text, 2, '0')"
        elif period == 'week':
            date_part = "EXTRACT(YEAR FROM date_of_unsafe_event::date), EXTRACT(WEEK FROM date_of_unsafe_event::date)"
            date_format = "EXTRACT(YEAR FROM date_of_unsafe_event::date) || '-W' || LPAD(EXTRACT(WEEK FROM date_of_unsafe_event::date)::text, 2, '0')"
        elif period == 'quarter':
            date_part = "EXTRACT(YEAR FROM date_of_unsafe_event::date), EXTRACT(QUARTER FROM date_of_unsafe_event::date)"
            date_format = "EXTRACT(YEAR FROM date_of_unsafe_event::date) || '-Q' || EXTRACT(QUARTER FROM date_of_unsafe_event::date)"
        else:
            raise ValueError("Period must be 'month', 'week', or 'quarter'")
        
        query = f"""
        SELECT 
            {date_format} as time_period,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_count
        FROM {self.table_name}
        WHERE date_of_unsafe_event IS NOT NULL
        GROUP BY {date_part}
        ORDER BY {date_part}
        """
        return self.execute_query(query, {}, session)
    
    # ==================== SAFETY SEVERITY METRICS ====================
    
    def get_serious_near_miss_count(self, session: Session = None) -> Dict[str, Any]:
        """Serious near miss incidents count and percentage"""
        query = f"""
        SELECT 
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as serious_near_miss_percentage
        FROM {self.table_name}
        """
        return self.execute_query(query, {}, session)[0]
    
    def get_work_stopped_incidents(self, session: Session = None) -> Dict[str, Any]:
        """Work stopped incidents analysis"""
        query = f"""
        SELECT 
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as work_stopped_percentage
        FROM {self.table_name}
        """
        return self.execute_query(query, {}, session)[0]
    
    def get_events_requiring_sanctions(self, session: Session = None) -> Dict[str, Any]:
        """Events requiring sanctions analysis"""
        query = f"""
        SELECT 
            COUNT(CASE WHEN UPPER(event_requires_sanction) = 'YES' THEN 1 END) as sanction_required_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER(event_requires_sanction) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as sanction_required_percentage
        FROM {self.table_name}
        """
        return self.execute_query(query, {}, session)[0]
    
    def get_nogo_violations_count(self, session: Session = None) -> Dict[str, Any]:
        """NOGO violations analysis"""
        query = f"""
        SELECT 
            COUNT(CASE WHEN UPPER(stop_work_nogo_violation) = 'YES' THEN 1 END) as nogo_violation_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER(stop_work_nogo_violation) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as nogo_violation_percentage
        FROM {self.table_name}
        """
        return self.execute_query(query, {}, session)[0]
    
    # ==================== GEOGRAPHIC DISTRIBUTION ====================
    
    def get_events_by_region_country_division(self, session: Session = None) -> List[Dict]:
        """Events by region, country, and division"""
        query = f"""
        SELECT 
            region,
            country_name,
            division,
            COUNT(*) as event_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {self.table_name}
        WHERE region IS NOT NULL OR country_name IS NOT NULL OR division IS NOT NULL
        GROUP BY region, country_name, division
        ORDER BY event_count DESC
        """
        return self.execute_query(query, {}, session)
    
    def get_events_by_city_district_zone(self, session: Session = None) -> List[Dict]:
        """Events by city, district, and zone"""
        query = f"""
        SELECT 
            city,
            district,
            zone,
            sub_area,
            COUNT(*) as event_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {self.table_name}
        WHERE city IS NOT NULL OR district IS NOT NULL OR zone IS NOT NULL
        GROUP BY city, district, zone, sub_area
        ORDER BY event_count DESC
        LIMIT 50
        """
        return self.execute_query(query, {}, session)
    
    def get_events_by_branch(self, session: Session = None) -> List[Dict]:
        """Events by branch"""
        query = f"""
        SELECT 
            branch,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate
        FROM {self.table_name}
        WHERE branch IS NOT NULL
        GROUP BY branch
        ORDER BY event_count DESC
        """
        return self.execute_query(query, {}, session)
    
    # ==================== PERSONNEL METRICS (REMOVED - NOT ESSENTIAL) ====================
    # Removed: get_events_by_reporter, get_employee_vs_subcontractor_incidents, get_events_by_subcontractor_company
    
    # ==================== OPERATIONAL METRICS ====================

    def get_events_by_business_details(self, session: Session = None) -> List[Dict]:
        """Events by business details (business type)"""
        query = f"""
        SELECT
            business_details,
            COUNT(*) as event_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {self.table_name}
        WHERE business_details IS NOT NULL
        GROUP BY business_details
        ORDER BY event_count DESC
        LIMIT 20
        """
        return self.execute_query(query, {}, session)

    def get_events_by_unsafe_event_location(self, session: Session = None) -> List[Dict]:
        """Frequent Unsafe Event Locations"""
        query = f"""
        SELECT
            unsafe_event_location,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate
        FROM {self.table_name}
        WHERE unsafe_event_location IS NOT NULL
        GROUP BY unsafe_event_location
        ORDER BY event_count DESC
        LIMIT 25
        """
        return self.execute_query(query, {}, session)

    def get_work_hours_lost_analysis(self, session: Session = None) -> Dict[str, Any]:
        """Work Hours lost analysis"""
        query = f"""
        SELECT
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_disruption_events,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as work_disruption_percentage
        FROM {self.table_name}
        """
        return self.execute_query(query, {}, session)[0]

    def get_action_creation_and_compliance(self, session: Session = None) -> Dict[str, Any]:
        """Action creation and compliance analysis"""
        query = f"""
        SELECT
            COUNT(*) as total_events,
            COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) as corrective_actions_created,
            ROUND(COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as action_closure_rate
        FROM {self.table_name}
        """
        return self.execute_query(query, {}, session)[0]

    def get_insights_from_comments_and_actions(self, session: Session = None) -> Dict[str, Any]:
        """Insights from comments and actions"""
        query = f"""
        SELECT
            COUNT(*) as total_events,
            COUNT(CASE WHEN "comments/remarks" IS NOT NULL AND "comments/remarks" != '' THEN 1 END) as events_with_comments,
            COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) as events_with_actions,
            ROUND(COUNT(CASE WHEN "comments/remarks" IS NOT NULL AND "comments/remarks" != '' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as comments_completion_rate,
            ROUND(COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as actions_completion_rate
        FROM {self.table_name}
        """
        return self.execute_query(query, {}, session)[0]

    # ==================== UNSAFE ACTS & CONDITIONS ANALYSIS ====================

    def get_common_unsafe_behaviors(self, session: Session = None) -> List[Dict]:
        """Common Unsafe Behaviors breakdown"""
        query = f"""
        SELECT
            unsafe_act,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate
        FROM {self.table_name}
        WHERE unsafe_act IS NOT NULL AND unsafe_act != ''
        GROUP BY unsafe_act
        ORDER BY event_count DESC
        LIMIT 20
        """
        return self.execute_query(query, {}, session)

    def get_common_unsafe_conditions(self, session: Session = None) -> List[Dict]:
        """Common Unsafe Conditions breakdown"""
        query = f"""
        SELECT
            unsafe_condition,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate
        FROM {self.table_name}
        WHERE unsafe_condition IS NOT NULL AND unsafe_condition != ''
        GROUP BY unsafe_condition
        ORDER BY event_count DESC
        LIMIT 20
        """
        return self.execute_query(query, {}, session)

    def get_monthly_weekly_trends_unsafe_behaviors(self, session: Session = None) -> List[Dict]:
        """Monthly/Weekly Trends of Unsafe Behaviours"""
        query = f"""
        SELECT
            EXTRACT(YEAR FROM date_of_unsafe_event::date) || '-' || LPAD(EXTRACT(MONTH FROM date_of_unsafe_event::date)::text, 2, '0') as time_period,
            COUNT(CASE WHEN unsafe_act IS NOT NULL AND unsafe_act != '' THEN 1 END) as unsafe_behavior_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN unsafe_act IS NOT NULL AND unsafe_act != '' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as unsafe_behavior_percentage
        FROM {self.table_name}
        WHERE date_of_unsafe_event IS NOT NULL
        GROUP BY EXTRACT(YEAR FROM date_of_unsafe_event::date), EXTRACT(MONTH FROM date_of_unsafe_event::date)
        ORDER BY EXTRACT(YEAR FROM date_of_unsafe_event::date), EXTRACT(MONTH FROM date_of_unsafe_event::date)
        """
        return self.execute_query(query, {}, session)

    def get_monthly_weekly_trends_unsafe_conditions(self, session: Session = None) -> List[Dict]:
        """Monthly/Weekly Trends of Unsafe Conditions"""
        query = f"""
        SELECT
            EXTRACT(YEAR FROM date_of_unsafe_event::date) || '-' || LPAD(EXTRACT(MONTH FROM date_of_unsafe_event::date)::text, 2, '0') as time_period,
            COUNT(CASE WHEN unsafe_condition IS NOT NULL AND unsafe_condition != '' THEN 1 END) as unsafe_condition_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN unsafe_condition IS NOT NULL AND unsafe_condition != '' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as unsafe_condition_percentage
        FROM {self.table_name}
        WHERE date_of_unsafe_event IS NOT NULL
        GROUP BY EXTRACT(YEAR FROM date_of_unsafe_event::date), EXTRACT(MONTH FROM date_of_unsafe_event::date)
        ORDER BY EXTRACT(YEAR FROM date_of_unsafe_event::date), EXTRACT(MONTH FROM date_of_unsafe_event::date)
        """
        return self.execute_query(query, {}, session)

    # ==================== REPORTING & TIME ANALYSIS ====================

    def get_time_taken_to_report_incidents(self, session: Session = None) -> List[Dict]:
        """Time taken to report incidents"""
        query = f"""
        SELECT
            CASE
                WHEN (reported_date::date - date_of_unsafe_event::date) = 0 THEN 'Same Day'
                WHEN (reported_date::date - date_of_unsafe_event::date) = 1 THEN '1 Day'
                WHEN (reported_date::date - date_of_unsafe_event::date) BETWEEN 2 AND 7 THEN '2-7 Days'
                WHEN (reported_date::date - date_of_unsafe_event::date) BETWEEN 8 AND 30 THEN '1-4 Weeks'
                WHEN (reported_date::date - date_of_unsafe_event::date) > 30 THEN 'Over 1 Month'
                ELSE 'Unknown'
            END as delay_category,
            COUNT(*) as event_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {self.table_name}
        WHERE reported_date IS NOT NULL AND date_of_unsafe_event IS NOT NULL
        GROUP BY
            CASE
                WHEN (reported_date::date - date_of_unsafe_event::date) = 0 THEN 'Same Day'
                WHEN (reported_date::date - date_of_unsafe_event::date) = 1 THEN '1 Day'
                WHEN (reported_date::date - date_of_unsafe_event::date) BETWEEN 2 AND 7 THEN '2-7 Days'
                WHEN (reported_date::date - date_of_unsafe_event::date) BETWEEN 8 AND 30 THEN '1-4 Weeks'
                WHEN (reported_date::date - date_of_unsafe_event::date) > 30 THEN 'Over 1 Month'
                ELSE 'Unknown'
            END
        ORDER BY event_count DESC
        """
        return self.execute_query(query, {}, session)

    def get_average_time_between_event_and_reporting(self, session: Session = None) -> Dict[str, Any]:
        """Average Time Between Event and Reporting"""
        query = f"""
        SELECT
            AVG((reported_date::date - date_of_unsafe_event::date)) as avg_delay_days,
            COUNT(*) as total_events_with_dates,
            MIN((reported_date::date - date_of_unsafe_event::date)) as min_delay_days,
            MAX((reported_date::date - date_of_unsafe_event::date)) as max_delay_days
        FROM {self.table_name}
        WHERE reported_date IS NOT NULL AND date_of_unsafe_event IS NOT NULL
        """
        return self.execute_query(query, {}, session)[0]

    def get_events_by_time_of_day(self, session: Session = None) -> List[Dict]:
        """Unsafe Events by Time of Day"""
        query = f"""
        SELECT
            CASE
                WHEN time_of_unsafe_event IS NULL THEN 'Unknown'
                WHEN (time_of_unsafe_event IS NOT NULL AND time_of_unsafe_event::text ~ '^[0-9]{{1,2}}:[0-9]{{2}}(:[0-9]{{2}})?$') AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 6 AND 11 THEN 'Morning (6AM-11AM)'
                WHEN (time_of_unsafe_event IS NOT NULL AND time_of_unsafe_event::text ~ '^[0-9]{{1,2}}:[0-9]{{2}}(:[0-9]{{2}})?$') AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 12 AND 17 THEN 'Afternoon (12PM-5PM)'
                WHEN (time_of_unsafe_event IS NOT NULL AND time_of_unsafe_event::text ~ '^[0-9]{{1,2}}:[0-9]{{2}}(:[0-9]{{2}})?$') AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 18 AND 23 THEN 'Evening (6PM-11PM)'
                WHEN (time_of_unsafe_event IS NOT NULL AND time_of_unsafe_event::text ~ '^[0-9]{{1,2}}:[0-9]{{2}}(:[0-9]{{2}})?$') AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 0 AND 5 THEN 'Night (12AM-5AM)'
                ELSE 'Unknown'
            END as time_period,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate
        FROM {self.table_name}
        GROUP BY
            CASE
                WHEN time_of_unsafe_event IS NULL THEN 'Unknown'
                WHEN (time_of_unsafe_event IS NOT NULL AND time_of_unsafe_event::text ~ '^[0-9]{{1,2}}:[0-9]{{2}}(:[0-9]{{2}})?$') AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 6 AND 11 THEN 'Morning (6AM-11AM)'
                WHEN (time_of_unsafe_event IS NOT NULL AND time_of_unsafe_event::text ~ '^[0-9]{{1,2}}:[0-9]{{2}}(:[0-9]{{2}})?$') AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 12 AND 17 THEN 'Afternoon (12PM-5PM)'
                WHEN (time_of_unsafe_event IS NOT NULL AND time_of_unsafe_event::text ~ '^[0-9]{{1,2}}:[0-9]{{2}}(:[0-9]{{2}})?$') AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 18 AND 23 THEN 'Evening (6PM-11PM)'
                WHEN (time_of_unsafe_event IS NOT NULL AND time_of_unsafe_event::text ~ '^[0-9]{{1,2}}:[0-9]{{2}}(:[0-9]{{2}})?$') AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 0 AND 5 THEN 'Night (12AM-5AM)'
                ELSE 'Unknown'
            END
        ORDER BY incident_count DESC
        """
        return self.execute_query(query, {}, session)

    def get_events_by_approval_status(self, session: Session = None) -> List[Dict]:
        """Events by approval status"""
        query = f"""
        SELECT
            CASE
                WHEN UPPER(event_requires_sanction) = 'YES' THEN 'Requires Approval/Sanction'
                WHEN UPPER(serious_near_miss) = 'YES' THEN 'Serious - Needs Review'
                WHEN UPPER(work_stopped) = 'YES' THEN 'Work Stopped - Approved'
                ELSE 'Standard Approval'
            END as approval_status,
            COUNT(*) as incident_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {self.table_name}
        GROUP BY
            CASE
                WHEN UPPER(event_requires_sanction) = 'YES' THEN 'Requires Approval/Sanction'
                WHEN UPPER(serious_near_miss) = 'YES' THEN 'Serious - Needs Review'
                WHEN UPPER(work_stopped) = 'YES' THEN 'Work Stopped - Approved'
                ELSE 'Standard Approval'
            END
        ORDER BY incident_count DESC
        """
        return self.execute_query(query, {}, session)

    def get_nogo_violation_trends_by_regions_branches(self, session: Session = None) -> List[Dict]:
        """No Go Violation trends by Regions/Branches"""
        query = f"""
        SELECT
            region,
            branch,
            COUNT(CASE WHEN UPPER(stop_work_nogo_violation) = 'YES' THEN 1 END) as nogo_violation_count,
            COUNT(*) as total_incidents,
            ROUND(COUNT(CASE WHEN UPPER(stop_work_nogo_violation) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as nogo_violation_rate
        FROM {self.table_name}
        WHERE region IS NOT NULL OR branch IS NOT NULL
        GROUP BY region, branch
        HAVING COUNT(CASE WHEN UPPER(stop_work_nogo_violation) = 'YES' THEN 1 END) > 0
        ORDER BY nogo_violation_count DESC
        """
        return self.execute_query(query, {}, session)

    def get_serious_near_miss_by_location_region_branch(self, session: Session = None) -> List[Dict]:
        """Serious Near Miss - by location/region/branch"""
        query = f"""
        SELECT
            region,
            branch,
            unsafe_event_location,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count,
            COUNT(*) as total_incidents,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_near_miss_rate
        FROM {self.table_name}
        WHERE region IS NOT NULL OR branch IS NOT NULL OR unsafe_event_location IS NOT NULL
        GROUP BY region, branch, unsafe_event_location
        HAVING COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) > 0
        ORDER BY serious_near_miss_count DESC
        LIMIT 25
        """
        return self.execute_query(query, {}, session)

    def get_branch_risk_index(self, session: Session = None) -> List[Dict]:
        """Branch Risk Index calculation"""
        query = f"""
        SELECT
            branch,
            COUNT(*) as total_incidents,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
            COUNT(CASE WHEN UPPER(stop_work_nogo_violation) = 'YES' THEN 1 END) as nogo_violations,
            ROUND(
                (COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 3 +
                 COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 2 +
                 COUNT(CASE WHEN UPPER(stop_work_nogo_violation) = 'YES' THEN 1 END) * 4 +
                 COUNT(*) * 1) * 100.0 / NULLIF(COUNT(*), 0), 2
            ) as branch_risk_index,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate
        FROM {self.table_name}
        WHERE branch IS NOT NULL
        GROUP BY branch
        ORDER BY branch_risk_index DESC, total_incidents DESC
        """
        return self.execute_query(query, {}, session)

    def get_at_risk_regions(self, session: Session = None) -> List[Dict]:
        """At risk regions identification"""
        query = f"""
        SELECT
            region,
            COUNT(*) as total_incidents,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
            COUNT(CASE WHEN UPPER(stop_work_nogo_violation) = 'YES' THEN 1 END) as nogo_violations,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate,
            ROUND(
                (COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 3 +
                 COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 2 +
                 COUNT(CASE WHEN UPPER(stop_work_nogo_violation) = 'YES' THEN 1 END) * 4) * 100.0 /
                NULLIF(COUNT(*), 0), 2
            ) as risk_score
        FROM {self.table_name}
        WHERE region IS NOT NULL
        GROUP BY region
        HAVING
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) > 2 OR
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) > 3 OR
            COUNT(CASE WHEN UPPER(stop_work_nogo_violation) = 'YES' THEN 1 END) > 1
        ORDER BY risk_score DESC, serious_incident_rate DESC
        """
        return self.execute_query(query, {}, session)

    # ==================== OPERATIONAL INTELLIGENCE & INSIGHTS ====================

    def get_operational_alerts_with_reasons(self, days_back: int = 30, session: Session = None) -> List[Dict]:
        """Generate operational alerts with detailed reasons from comments"""
        query = f"""
        WITH recent_performance AS (
            SELECT
                region,
                branch,
                COUNT(*) as recent_incidents,
                COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages,
                COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
                STRING_AGG(DISTINCT
                    CASE
                WHEN "comments/remarks" IS NOT NULL AND LENGTH(TRIM("comments/remarks")) > 10
                THEN SUBSTRING("comments/remarks", 1, 100)
                    END, ' | ') as incident_reasons
            FROM {self.table_name}
            WHERE date_of_unsafe_event >= CURRENT_DATE - INTERVAL '{days_back} days'
            AND (region IS NOT NULL OR branch IS NOT NULL)
            GROUP BY region, branch
        ),
        historical_avg AS (
            SELECT
                region,
                branch,
                AVG(monthly_incidents) as avg_monthly_incidents
            FROM (
                SELECT
                    region,
                    branch,
                    EXTRACT(YEAR FROM date_of_unsafe_event::date) as year,
                    EXTRACT(MONTH FROM date_of_unsafe_event::date) as month,
                    COUNT(*) as monthly_incidents
                FROM {self.table_name}
                WHERE date_of_unsafe_event < CURRENT_DATE - INTERVAL '{days_back} days'
                AND date_of_unsafe_event >= CURRENT_DATE - INTERVAL '12 months'
                GROUP BY region, branch, EXTRACT(YEAR FROM date_of_unsafe_event::date), EXTRACT(MONTH FROM date_of_unsafe_event::date)
            ) monthly_stats
            GROUP BY region, branch
        )
        SELECT
            r.region,
            r.branch,
            r.recent_incidents,
            r.work_stoppages,
            r.serious_incidents,
            r.incident_reasons,
            h.avg_monthly_incidents,
            ROUND(((r.recent_incidents - h.avg_monthly_incidents) / NULLIF(h.avg_monthly_incidents, 0)) * 100, 1) as variance_percent,
            CASE
                WHEN ((r.recent_incidents - h.avg_monthly_incidents) / NULLIF(h.avg_monthly_incidents, 0)) * 100 > 30 THEN 'HIGH_ALERT'
                WHEN r.serious_incidents > 2 THEN 'SERIOUS_INCIDENTS_ALERT'
                WHEN r.work_stoppages > r.recent_incidents * 0.4 THEN 'HIGH_DISRUPTION_ALERT'
                ELSE 'NORMAL'
            END as alert_level
        FROM recent_performance r
        LEFT JOIN historical_avg h ON r.region = h.region AND r.branch = h.branch
        WHERE r.recent_incidents >= 2
        ORDER BY variance_percent DESC, serious_incidents DESC
        """
        return self.execute_query(query, {}, session)

    def get_violation_patterns_with_context(self, days_back: int = 30, session: Session = None) -> List[Dict]:
        """Analyze violation patterns with detailed context and reasons"""
        query = f"""
        SELECT
            UPPER(stop_work_nogo_violation) as nogo_violation_status,
            region,
            branch,
            unsafe_event_location,
            COUNT(*) as violation_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_violations,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total,
            STRING_AGG(DISTINCT unsafe_act, '; ') as common_unsafe_acts,
            STRING_AGG(DISTINCT unsafe_condition, '; ') as common_unsafe_conditions,
            STRING_AGG(DISTINCT
                CASE
                    WHEN "comments/remarks" IS NOT NULL AND LENGTH(TRIM("comments/remarks")) > 10
                    THEN SUBSTRING("comments/remarks", 1, 100)
                END, ' | ') as violation_reasons,
            STRING_AGG(DISTINCT
                CASE
                    WHEN nogo_violation_detail IS NOT NULL AND LENGTH(TRIM(nogo_violation_detail)) > 5
                    THEN SUBSTRING(nogo_violation_detail, 1, 100)
                END, ' | ') as violation_details,
            COUNT(DISTINCT COALESCE(employee_name, subcontractor_name)) as people_involved,
            MAX(date_of_unsafe_event) as latest_violation
        FROM {self.table_name}
        WHERE date_of_unsafe_event >= CURRENT_DATE - INTERVAL '{days_back} days'
        AND stop_work_nogo_violation IS NOT NULL
        GROUP BY UPPER(stop_work_nogo_violation), region, branch, unsafe_event_location
        HAVING COUNT(*) >= 2
        ORDER BY violation_count DESC, serious_violations DESC
        LIMIT 25
        """
        return self.execute_query(query, {}, session)

    def get_staff_impact_analysis(self, session: Session = None) -> List[Dict]:
        """Analyze staff impact with performance metrics and context"""
        query = f"""
        SELECT
            COALESCE(employee_name, subcontractor_name, 'Unknown') as staff_name,
            COALESCE(subcontractor_company_name, 'Internal') as company,
            branch,
            region,
            COUNT(*) as total_incidents_involved,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stoppages_caused,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER(event_requires_sanction) = 'YES' THEN 1 END) as sanctions_required,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'NO' OR work_stopped IS NULL THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as work_continuation_rate,
            ROUND(COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as proactive_action_rate,
            COUNT(DISTINCT unsafe_event_location) as locations_worked,
            AVG(CASE
                WHEN reported_date IS NOT NULL AND date_of_unsafe_event IS NOT NULL
                THEN (reported_date::date - date_of_unsafe_event::date)
            END) as avg_reporting_delay_days,
            STRING_AGG(DISTINCT
                CASE
                    WHEN "comments/remarks" IS NOT NULL AND LENGTH(TRIM("comments/remarks")) > 10
                    THEN SUBSTRING("comments/remarks", 1, 100)
                END, ' | ') as performance_context
        FROM {self.table_name}
        WHERE (employee_name IS NOT NULL OR subcontractor_name IS NOT NULL)
        GROUP BY COALESCE(employee_name, subcontractor_name, 'Unknown'),
                 COALESCE(subcontractor_company_name, 'Internal'), branch, region
        HAVING COUNT(*) >= 2
        ORDER BY work_continuation_rate DESC, proactive_action_rate DESC
        LIMIT 30
        """
        return self.execute_query(query, {}, session)

    def get_resource_optimization_insights(self, session: Session = None) -> List[Dict]:
        """Generate resource optimization insights based on incident patterns"""
        query = f"""
        SELECT
            business_details,
            unsafe_event_location,
            branch,
            COUNT(*) as incident_frequency,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_disruptions,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            STRING_AGG(DISTINCT unsafe_condition, '; ') as common_conditions,
            STRING_AGG(DISTINCT
                CASE
                    WHEN "comments/remarks" IS NOT NULL AND LENGTH(TRIM("comments/remarks")) > 10
                    THEN SUBSTRING("comments/remarks", 1, 100)
                END, ' | ') as root_causes,
            STRING_AGG(DISTINCT
                CASE
                    WHEN action_description_1 IS NOT NULL AND LENGTH(TRIM(action_description_1)) > 10
                    THEN SUBSTRING(action_description_1, 1, 100)
                END, ' | ') as recommended_actions,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as disruption_rate,
            COUNT(DISTINCT COALESCE(employee_name, subcontractor_name)) as people_affected,
            CASE
                WHEN COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) > 50
                     THEN 'HIGH_DISRUPTION_AREA'
                WHEN COUNT(*) >= 5 AND COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) > 0
                     THEN 'HIGH_RISK_LOCATION'
                WHEN COUNT(DISTINCT COALESCE(employee_name, subcontractor_name)) > 3
                     THEN 'TRAINING_FOCUS_AREA'
                ELSE 'MONITOR'
            END as optimization_priority
        FROM {self.table_name}
        WHERE business_details IS NOT NULL
        AND unsafe_event_location IS NOT NULL
        GROUP BY business_details, unsafe_event_location, branch
        HAVING COUNT(*) >= 3
        ORDER BY incident_frequency DESC, disruption_rate DESC
        LIMIT 25
        """
        return self.execute_query(query, {}, session)

    # ==================== COMPREHENSIVE KPI COLLECTION ====================

    def get_all_kpis(self, session: Session = None) -> Dict[str, Any]:
        """Execute essential KPI queries and return results (optimized for LLM processing)"""
        try:
            logger.info("Executing essential SRS KPI queries...")

            # Use provided session or create a new one for all KPI queries - PERFORMANCE OPTIMIZATION
            use_existing_session = session is not None
            if not session:
                session = self.get_session()

            try:
                results = {
                    # Core Event Metrics
                    "number_of_unsafe_events": self.get_total_events_count(session),
                    "monthly_unsafe_events_trend": self.get_events_per_time_period('month', session),
                    "monthly_weekly_trends_unsafe_behaviors": self.get_monthly_weekly_trends_unsafe_behaviors(session),
                    "monthly_weekly_trends_unsafe_conditions": self.get_monthly_weekly_trends_unsafe_conditions(session),
                    "near_misses": self.get_serious_near_miss_count(session),

                    # Geographic & Location Analysis
                    "unsafe_events_by_branch": self.get_events_by_branch(session),
                    "unsafe_events_by_region": self.get_events_by_region_country_division(session),
                    "at_risk_regions": self.get_at_risk_regions(session),
                    "frequent_unsafe_event_locations": self.get_events_by_unsafe_event_location(session),

                    # Time & Reporting Analysis
                    "time_taken_to_report_incidents": self.get_time_taken_to_report_incidents(session),
                    "average_time_between_event_and_reporting": self.get_average_time_between_event_and_reporting(session),
                    "unsafe_events_by_time_of_day": self.get_events_by_time_of_day(session),

                    # Actions & Compliance
                    "corrective_actions_created": self.get_action_creation_and_compliance(session),
                    "action_creation_and_compliance": self.get_action_creation_and_compliance(session),
                    "action_closure_rate": self.get_action_creation_and_compliance(session),

                    # Business & Operational
                    "unsafe_event_distribution_by_business_type": self.get_events_by_business_details(session),
                    "events_by_approval_status": self.get_events_by_approval_status(session),

                    # No Go Violations & Work Disruptions
                    "number_of_nogo_violations": self.get_nogo_violations_count(session),
                    "nogo_violation_trends_by_regions_branches": self.get_nogo_violation_trends_by_regions_branches(session),
                    "work_hours_lost": self.get_work_hours_lost_analysis(session),

                    # Safety Behaviors & Conditions
                    "common_unsafe_behaviors": self.get_common_unsafe_behaviors(session),
                    "common_unsafe_conditions": self.get_common_unsafe_conditions(session),

                    # Serious Incidents Analysis
                    "serious_near_misses_trend": self.get_events_per_time_period('month', session),  # Reusing monthly trend
                    "serious_near_miss_by_location_region_branch": self.get_serious_near_miss_by_location_region_branch(session),

                    # Risk Assessment
                    "branch_risk_index": self.get_branch_risk_index(session),

                    # Insights & Comments
                    "insights_from_comments_and_actions": self.get_insights_from_comments_and_actions(session),

                    # ==================== ENHANCED OPERATIONAL INTELLIGENCE ====================
                    "operational_alerts_with_reasons": self.get_operational_alerts_with_reasons(30, session),
                    "violation_patterns_with_context": self.get_violation_patterns_with_context(30, session),
                    "staff_impact_analysis": self.get_staff_impact_analysis(session),
                    "resource_optimization_insights": self.get_resource_optimization_insights(session),
                }

                logger.info("Successfully executed essential SRS KPI queries")
                return results
            finally:
                # Only close session if we created it
                if not use_existing_session:
                    session.close()

        except Exception as e:
            logger.error(f"Error in get_all_kpis: {e}")
            raise



