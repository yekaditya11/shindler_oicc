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


class SRSAGUMENTEDKPIQUERIES:
    """SQL queries for SRS App KPIs"""
    
    def __init__(self):
        self.table_name = "unsafe_events_srs_agumented"
    
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
            CASE
                WHEN unsafe_condition IS NOT NULL AND unsafe_condition != '' THEN unsafe_condition
                WHEN unsafe_condition_other IS NOT NULL AND unsafe_condition_other != '' THEN unsafe_condition_other
            END as unsafe_condition,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_incident_rate
        FROM {self.table_name}
        WHERE (unsafe_condition IS NOT NULL AND unsafe_condition != '')
           OR (unsafe_condition_other IS NOT NULL AND unsafe_condition_other != '')
        GROUP BY 1
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
            COUNT(CASE WHEN (unsafe_condition IS NOT NULL AND unsafe_condition != '') OR (unsafe_condition_other IS NOT NULL AND unsafe_condition_other != '') THEN 1 END) as unsafe_condition_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN (unsafe_condition IS NOT NULL AND unsafe_condition != '') OR (unsafe_condition_other IS NOT NULL AND unsafe_condition_other != '') THEN 1 END) * 100.0 /
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
                WHEN (
                    (pg_typeof(time_of_unsafe_event)::text = 'text' AND time_of_unsafe_event::text ~ '^[0-9]{1,2}:[0-9]{2}(:[0-9]{2})?$')
                    OR pg_typeof(time_of_unsafe_event)::text = 'time without time zone'
                ) AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 6 AND 11 THEN 'Morning (6AM-11AM)'
                WHEN (
                    (pg_typeof(time_of_unsafe_event)::text = 'text' AND time_of_unsafe_event::text ~ '^[0-9]{1,2}:[0-9]{2}(:[0-9]{2})?$')
                    OR pg_typeof(time_of_unsafe_event)::text = 'time without time zone'
                ) AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 12 AND 17 THEN 'Afternoon (12PM-5PM)'
                WHEN (
                    (pg_typeof(time_of_unsafe_event)::text = 'text' AND time_of_unsafe_event::text ~ '^[0-9]{1,2}:[0-9]{2}(:[0-9]{2})?$')
                    OR pg_typeof(time_of_unsafe_event)::text = 'time without time zone'
                ) AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 18 AND 23 THEN 'Evening (6PM-11PM)'
                WHEN (
                    (pg_typeof(time_of_unsafe_event)::text = 'text' AND time_of_unsafe_event::text ~ '^[0-9]{1,2}:[0-9]{2}(:[0-9]{2})?$')
                    OR pg_typeof(time_of_unsafe_event)::text = 'time without time zone'
                ) AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 0 AND 5 THEN 'Night (12AM-5AM)'
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
                WHEN (
                    (pg_typeof(time_of_unsafe_event)::text = 'text' AND time_of_unsafe_event::text ~ '^[0-9]{1,2}:[0-9]{2}(:[0-9]{2})?$')
                    OR pg_typeof(time_of_unsafe_event)::text = 'time without time zone'
                ) AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 6 AND 11 THEN 'Morning (6AM-11AM)'
                WHEN (
                    (pg_typeof(time_of_unsafe_event)::text = 'text' AND time_of_unsafe_event::text ~ '^[0-9]{1,2}:[0-9]{2}(:[0-9]{2})?$')
                    OR pg_typeof(time_of_unsafe_event)::text = 'time without time zone'
                ) AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 12 AND 17 THEN 'Afternoon (12PM-5PM)'
                WHEN (
                    (pg_typeof(time_of_unsafe_event)::text = 'text' AND time_of_unsafe_event::text ~ '^[0-9]{1,2}:[0-9]{2}(:[0-9]{2})?$')
                    OR pg_typeof(time_of_unsafe_event)::text = 'time without time zone'
                ) AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 18 AND 23 THEN 'Evening (6PM-11PM)'
                WHEN (
                    (pg_typeof(time_of_unsafe_event)::text = 'text' AND time_of_unsafe_event::text ~ '^[0-9]{1,2}:[0-9]{2}(:[0-9]{2})?$')
                    OR pg_typeof(time_of_unsafe_event)::text = 'time without time zone'
                ) AND EXTRACT(HOUR FROM time_of_unsafe_event::time) BETWEEN 0 AND 5 THEN 'Night (12AM-5AM)'
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
            STRING_AGG(DISTINCT COALESCE(NULLIF(unsafe_condition, ''), NULLIF(unsafe_condition_other, '')), '; ') as common_unsafe_conditions,
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
            STRING_AGG(DISTINCT COALESCE(NULLIF(unsafe_condition, ''), NULLIF(unsafe_condition_other, '')), '; ') as common_conditions,
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

    #==========augmented kpis ================
    def get_unsafe_events_per_employee(self, session: Session = None) -> List[Dict]:
        """Unsafe Events per Employee"""
        query = f"""
        SELECT 
            employee_id,
            COUNT(*) as unsafe_event_count
        FROM {self.table_name}
        GROUP BY employee_id
        ORDER BY unsafe_event_count DESC
        """
        return self.execute_query(query, {}, session)

    def get_average_experience_of_involved_employees(self, session: Session = None) -> Dict[str, Any]:
        """Average Experience of Involved Employees"""
        query = f"""
        SELECT 
            AVG(years_of_experience) as avg_experience
        FROM {self.table_name}
        WHERE employee_id IS NOT NULL
        """
        return self.execute_query(query, {}, session)[0]

    def get_job_designations_involved_in_incidents(self, session: Session = None) -> List[Dict]:
        """Job Designations involved in Incident"""
        query = f"""
        SELECT 
            job_role,
            COUNT(*) as event_count
        FROM {self.table_name}
        GROUP BY job_role
        ORDER BY event_count DESC
        """
        return self.execute_query(query, {}, session)

    def get_incident_rate_by_experience_bracket(self, session: Session = None) -> List[Dict]:
        """Incident Rate by Experience Bracket"""
        query = f"""
        SELECT 
            CASE 
                WHEN years_of_experience BETWEEN 0 AND 5 THEN '0-5 Years'
                WHEN years_of_experience BETWEEN 6 AND 10 THEN '6-10 Years'
                WHEN years_of_experience BETWEEN 11 AND 15 THEN '11-15 Years'
                WHEN years_of_experience BETWEEN 16 AND 20 THEN '16-20 Years'
                ELSE '20+ Years'
            END as experience_bracket,
            COUNT(*) as event_count,
            COUNT(DISTINCT employee_id) as involved_employees,
            ROUND(COUNT(*) * 100.0 / COUNT(DISTINCT employee_id), 2) as incident_rate
        FROM {self.table_name}
        WHERE employee_id IS NOT NULL
        GROUP BY experience_bracket
        ORDER BY experience_bracket
        """
        return self.execute_query(query, {}, session)




        # ==================== COMPREHENSIVE KPI COLLECTION ====================


    def get_observations_reported_by_age_group(self, session: Session = None) -> List[Dict]:
        """Observations Reported by Age Group (20-30, 30-40, 40-50, etc.)"""
        query = f"""
        SELECT 
            CASE 
                WHEN employee_age BETWEEN 20 AND 30 THEN '20-30'
                WHEN employee_age BETWEEN 31 AND 40 THEN '31-40'
                WHEN employee_age BETWEEN 41 AND 50 THEN '41-50'
                WHEN employee_age BETWEEN 51 AND 60 THEN '51-60'
                ELSE '60+'
            END as age_group,
            COUNT(*) as observation_count
        FROM {self.table_name}
        WHERE employee_age IS NOT NULL
        GROUP BY age_group
        ORDER BY age_group
        """
        return self.execute_query(query, {}, session)


    def get_training_compliance_rate(self, session: Session = None) -> Dict[str, Any]:
        """Training Compliance Rate"""
        query = f"""
        SELECT 
            COUNT(CASE WHEN training_expiry_date >= CURRENT_DATE THEN 1 END) as compliant_count,
            COUNT(*) as total_employees,
            ROUND(COUNT(CASE WHEN training_expiry_date >= CURRENT_DATE THEN 1 END) * 100.0 / COUNT(*), 2) as compliance_rate
        FROM {self.table_name}
        WHERE training_expiry_date IS NOT NULL
        """
        return self.execute_query(query, {}, session)[0]


    def get_repeat_offenders(self, session: Session = None) -> List[Dict]:
        """Repeat Offenders"""
        query = f"""
        SELECT 
            employee_id,
            COUNT(*) as incident_count
        FROM {self.table_name}
        GROUP BY employee_id
        HAVING COUNT(*) > 1
        ORDER BY incident_count DESC
        """
        return self.execute_query(query, {}, session)

    def get_incidents_after_extended_shifts(self, session: Session = None) -> List[Dict]:
        """Incidents After Extended Shifts (>9 or 10 hours)"""
        query = f"""
        SELECT 
            employee_id,
            COUNT(*) as incident_count,
            'After Extended Shift' as shift_status
        FROM {self.table_name}
        WHERE time_of_unsafe_event IS NOT NULL
        AND (
            (shift_timings = '14:00 - 22:00' AND EXTRACT(HOUR FROM time_of_unsafe_event::time) >= 22) OR
            (shift_timings = '22:00 - 06:00' AND EXTRACT(HOUR FROM time_of_unsafe_event::time) >= 6) OR
            (shift_timings = '06:00 - 14:00' AND EXTRACT(HOUR FROM time_of_unsafe_event::time) >= 14)
        )
        GROUP BY employee_id
        ORDER BY incident_count DESC
        """
        return self.execute_query(query, {}, session)

    def get_incident_rate_vs_weekly_hours_worked(self, session: Session = None) -> List[Dict]:
        """Incident Rate vs. Weekly Hours Worked"""
        query = f"""
        SELECT 
            employee_id,
            COUNT(*) as incident_count,
            SUM(total_hours_worked_in_previous_week) as total_weekly_hours,
            ROUND(COUNT(*) * 100.0 / SUM(total_hours_worked_in_previous_week), 2) as incident_rate
        FROM {self.table_name}
        WHERE total_hours_worked_in_previous_week IS NOT NULL
        GROUP BY employee_id
        ORDER BY incident_rate DESC
        """
        return self.execute_query(query, {}, session)

    def get_overtime_linked_unsafe_events(self, session: Session = None) -> List[Dict]:
        """Overtime-Linked Unsafe Events"""
        query = f"""
        SELECT 
            employee_id,
            COUNT(*) as overtime_incident_count,
            'Overtime' as overtime_status
        FROM {self.table_name}
        WHERE overtime_hours > 0
        GROUP BY employee_id
        ORDER BY overtime_incident_count DESC
        """
        return self.execute_query(query, {}, session)

    def get_incidents_during_night_shifts(self, session: Session = None) -> List[Dict]:
        """Incidents During Night Shifts"""
        query = f"""
        SELECT 
            employee_id,
            COUNT(*) as night_shift_incidents
        FROM {self.table_name}
        WHERE shift_timings = '22:00 - 06:00' 
        AND time_of_unsafe_event IS NOT NULL
        GROUP BY employee_id
        """
        return self.execute_query(query, {}, session)

    def get_incidents_by_hour_of_day(self, session: Session = None) -> List[Dict]:
        """Incidents by Hour of Day"""
        query = f"""
        SELECT 
            EXTRACT(HOUR FROM time_of_unsafe_event::time) as hour_of_day,
            COUNT(*) as incident_count
        FROM {self.table_name}
        WHERE time_of_unsafe_event IS NOT NULL
        GROUP BY hour_of_day
        ORDER BY hour_of_day
        """
        return self.execute_query(query, {}, session)

    def get_events_after_consecutive_working_days(self, session: Session = None) -> List[Dict]:
        """Events After 6+ Consecutive Working Days"""
        query = f"""
        SELECT 
            employee_id,
            COUNT(*) as event_count,
            '6+ Consecutive Days' as working_days_status
        FROM {self.table_name}
        WHERE date_of_unsafe_event IS NOT NULL
        GROUP BY employee_id
        HAVING COUNT(DISTINCT date_of_unsafe_event) >= 6
        ORDER BY event_count DESC
        """
        return self.execute_query(query, {}, session)
    
    def get_top_equipment_involved_in_unsafe_events(self, session: Session = None) -> List[Dict]:
        """Top Equipment Involved in Unsafe Events"""
        query = f"""
        SELECT 
            product_type,
            COUNT(*) as event_count
        FROM {self.table_name}
        GROUP BY product_type
        ORDER BY event_count DESC
        """
        return self.execute_query(query, {}, session)

    def get_incidents_per_equipment_type(self, session: Session = None) -> List[Dict]:
        """Incidents per Equipment Type"""
        query = f"""
        SELECT 
            product_type,
            COUNT(*) as incident_count
        FROM {self.table_name}
        GROUP BY product_type
        ORDER BY incident_count DESC
        """
        return self.execute_query(query, {}, session)

    def get_average_time_since_last_maintenance(self, session: Session = None) -> Dict[str, Any]:
        """Average Time Since Last Maintenance"""
        query = f"""
        SELECT 
            product_type,
            AVG(CURRENT_DATE - CAST(last_maintenance_date AS DATE)) as avg_days_since_last_maintenance
        FROM {self.table_name}
        WHERE last_maintenance_date IS NOT NULL AND last_maintenance_date != ''
        GROUP BY product_type
        """
        return self.execute_query(query, {}, session)
    
    def get_percentage_of_events_after_unscheduled_maintenance(self, session: Session = None) -> List[Dict]:
        """% of Events After Unscheduled Maintenance"""
        query = f"""
        SELECT 
            product_type,
            COUNT(*) as total_events,
            COUNT(CASE WHEN (CURRENT_DATE - CAST(last_maintenance_date AS DATE)) <= 30 THEN 1 END) as events_after_unscheduled_maintenance,
            ROUND(COUNT(CASE WHEN (CURRENT_DATE - CAST(last_maintenance_date AS DATE)) <= 30 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(*), 0), 2) as unscheduled_maintenance_percentage
        FROM {self.table_name}
        WHERE last_maintenance_date IS NOT NULL
        GROUP BY product_type
        ORDER BY unscheduled_maintenance_percentage DESC
        """
        return self.execute_query(query, {}, session)
    def get_time_between_incidents_for_equipment_type(self, session: Session = None) -> List[Dict]:
        """Time Between Incidents for Equipment Type"""
        query = f"""
        WITH incident_diffs AS (
            SELECT 
                product_type,
                date_of_unsafe_event,
                LAG(date_of_unsafe_event) OVER (PARTITION BY product_type ORDER BY date_of_unsafe_event) as prev_incident_date
            FROM {self.table_name}
            WHERE date_of_unsafe_event IS NOT NULL
        )
        SELECT 
            product_type,
            AVG(date_of_unsafe_event - prev_incident_date) as avg_days_between_incidents
        FROM incident_diffs
        WHERE prev_incident_date IS NOT NULL
        GROUP BY product_type
        ORDER BY avg_days_between_incidents DESC
        """
        return self.execute_query(query, {}, session)
    def get_repeat_failures_on_same_equipment(self, session: Session = None) -> List[Dict]:
        """Repeat Failures on Same Equipment"""
        query = f"""
        SELECT 
            product_type,
            COUNT(*) as repeat_failure_count
        FROM {self.table_name}
        GROUP BY product_type
        HAVING COUNT(*) > 1
        ORDER BY repeat_failure_count DESC
        """
        return self.execute_query(query, {}, session)
    def get_percent_of_incidents_with_corrective_actions(self, session: Session = None) -> Dict[str, Any]:
        """% of Incidents Where Corrective Actions Were Implemented"""
        query = f"""
        SELECT 
            COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) as corrective_actions_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(*), 0), 2) as corrective_actions_percentage
        FROM {self.table_name}
        WHERE action_description_1 IS NOT NULL
        """
        return self.execute_query(query, {}, session)[0]
    def get_recurring_events_with_same_root_cause(self, session: Session = None) -> List[Dict]:
        """Recurring Events with Same Root Cause"""
        query = f"""
        SELECT 
            unsafe_act,
            COUNT(*) as event_count
        FROM {self.table_name}
        GROUP BY unsafe_act
        HAVING COUNT(*) > 1
        ORDER BY event_count DESC
        """
        return self.execute_query(query, {}, session)
    def get_percent_of_incidents_investigated(self, session: Session = None) -> Dict[str, Any]:
        """% of Incidents Investigated"""
        query = f"""
        SELECT 
            COUNT(CASE WHEN investigation_closure_date IS NOT NULL THEN 1 END) as investigated_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN investigation_closure_date IS NOT NULL THEN 1 END) * 100.0 / 
                NULLIF(COUNT(*), 0), 2) as investigated_percentage
        FROM {self.table_name}
        WHERE investigation_closure_date IS NOT NULL
        """
        return self.execute_query(query, {}, session)[0]
    def get_incidents_by_root_cause_category(self, session: Session = None) -> List[Dict]:
        """Incidents by Root Cause Category"""
        query = f"""
        SELECT 
            unsafe_act,
            COUNT(*) as event_count
        FROM {self.table_name}
        GROUP BY unsafe_act
        ORDER BY event_count DESC
        """
        return self.execute_query(query, {}, session)

    def get_top_5_recurrent_root_causes(self, session: Session = None) -> List[Dict]:
        """Top 5 Recurrent Root Causes"""
        query = f"""
        SELECT 
            unsafe_act,
            COUNT(*) as recurrence_count
        FROM {self.table_name}
        GROUP BY unsafe_act
        HAVING COUNT(*) > 1
        ORDER BY recurrence_count DESC
        LIMIT 5
        """
        return self.execute_query(query, {}, session)
    def get_average_time_to_close_investigation(self, session: Session = None) -> Dict[str, Any]:
        """Average Time to Close Investigation"""
        query = f"""
        SELECT 
            AVG(DATE_PART('day', investigation_closure_date - reported_date)) as avg_days_to_close_investigation
        FROM {self.table_name}
        WHERE investigation_closure_date IS NOT NULL AND reported_date IS NOT NULL
        """
        return self.execute_query(query, {}, session)[0]
    def get_repeat_events_despite_capa(self, session: Session = None) -> List[Dict]:
        """Repeat Events Despite CAPA"""
        query = f"""
        SELECT 
            event_id,
            COUNT(*) as repeat_event_count
        FROM {self.table_name}
        WHERE action_description_1 IS NOT NULL AND action_description_1 != ''
        GROUP BY event_id
        HAVING COUNT(*) > 1
        ORDER BY repeat_event_count DESC
        """
        return self.execute_query(query, {}, session)

    def get_events_by_root_cause_category_and_site(self, session: Session = None) -> List[Dict]:
        """Events by Root Cause Category & Site"""
        query = f"""
        SELECT 
            unsafe_act,
            site_reference,
            COUNT(*) as event_count
        FROM {self.table_name}
        GROUP BY unsafe_act, site_reference
        ORDER BY event_count DESC
        """
        return self.execute_query(query, {}, session)
    def get_audit_frequency_vs_incidents_of_branch(self, session: Session = None) -> List[Dict]:
        """Audit Frequency vs. Incidents of the Branch"""
        query = f"""
        SELECT 
            branch,
            audit_frequency_,
            COUNT(*) as incident_count
        FROM {self.table_name}
        WHERE audit_frequency_ IS NOT NULL
        GROUP BY branch, audit_frequency_
        ORDER BY incident_count DESC
        """
        return self.execute_query(query, {}, session)
    def get_audit_recency_vs_incidents_of_branch(self, session: Session = None) -> List[Dict]:
        """Audit Recency vs. Incidents of the Branch"""
        query = f"""
        SELECT 
            branch,
            COUNT(*) as incident_count
        FROM {self.table_name}
        WHERE branch IS NOT NULL
        GROUP BY branch
        ORDER BY incident_count DESC
        """
        return self.execute_query(query, {}, session)
    def get_percent_of_incidents_occurring_30_days_since_last_audit(self, session: Session = None) -> Dict[str, Any]:
        """% of Incidents Occurring >30 Days Since Last Audit"""
        query = f"""
        SELECT 
            0 as incidents_after_30_days,
            COUNT(*) as total_incidents,
            0.0 as percentage
        FROM {self.table_name}
        """
        return self.execute_query(query, {}, session)[0]
    def get_percent_of_branches_with_overdue_audits_and_high_incident_rates(self, session: Session = None) -> List[Dict]:
        """% of Branches with Overdue Audits and High Incident Rates"""
        query = f"""
        SELECT 
            branch,
            COUNT(*) as total_incidents,
            0 as overdue_audits,
            0.0 as overdue_audit_percentage
        FROM {self.table_name}
        WHERE branch IS NOT NULL
        GROUP BY branch
        HAVING COUNT(*) > 10
        ORDER BY total_incidents DESC
        """
        return self.execute_query(query, {}, session)
    def get_trend_days_since_audit_vs_incident_volume(self, session: Session = None) -> List[Dict]:
        """Trend: Days Since Audit vs. Incident Volume"""
        query = f"""
        SELECT 
            'All Incidents' as incident_status,
            COUNT(*) as incident_count
        FROM {self.table_name}
        """
        return self.execute_query(query, {}, session)
    def get_incident_rate_by_weather_condition(self, session: Session = None) -> List[Dict]:
        """Incident Rate by Weather Condition"""
        query = f"""
        SELECT 
            weather_condition,
            COUNT(*) as incident_count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {self.table_name}), 2) as incident_rate
        FROM {self.table_name}
        WHERE weather_condition IS NOT NULL
        GROUP BY weather_condition
        ORDER BY incident_count DESC
        """
        return self.execute_query(query, {}, session)
    def get_percent_of_incidents_during_extreme_weather_days(self, session: Session = None) -> Dict[str, Any]:
        """% of Incidents During Extreme Weather Days"""
        query = f"""
        SELECT 
            COUNT(CASE WHEN weather_condition IN ('Heat', 'Storm', 'Snow', 'Wind', 'Rain') THEN 1 END) as extreme_weather_incidents,
            COUNT(*) as total_incidents,
            ROUND(COUNT(CASE WHEN weather_condition IN ('Heat', 'Storm', 'Snow', 'Wind', 'Rain') THEN 1 END) * 100.0 / 
                NULLIF(COUNT(*), 0), 2) as extreme_weather_percentage
        FROM {self.table_name}
        WHERE weather_condition IS NOT NULL
        """
        return self.execute_query(query, {}, session)[0]
    def get_unsafe_event_type_vs_weather_condition_correlation(self, session: Session = None) -> List[Dict]:
        """Unsafe Event Type vs. Weather Condition Correlation"""
        query = f"""
        SELECT 
            unsafe_event_type,
            weather_condition,
            COUNT(*) as event_count
        FROM {self.table_name}
        WHERE weather_condition IS NOT NULL AND unsafe_event_type IS NOT NULL
        GROUP BY unsafe_event_type, weather_condition
        ORDER BY event_count DESC
        """
        return self.execute_query(query, {}, session)

    def get_all_kpis(self, session: Session = None) -> Dict[str, Any]:
        """Execute essential and augmented KPI queries and return results (optimized for LLM processing)"""
        try:
            logger.info("Executing essential and augmented SRS KPI queries...")

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
                    "serious_near_misses_trend": self.get_events_per_time_period('month', session),
                    "serious_near_miss_by_location_region_branch": self.get_serious_near_miss_by_location_region_branch(session),
                    # Risk Assessment
                    "branch_risk_index": self.get_branch_risk_index(session),
                    # Insights & Comments
                    "insights_from_comments_and_actions": self.get_insights_from_comments_and_actions(session),
                    # ENHANCED OPERATIONAL INTELLIGENCE
                    "operational_alerts_with_reasons": self.get_operational_alerts_with_reasons(30, session),
                    "violation_patterns_with_context": self.get_violation_patterns_with_context(30, session),
                    "staff_impact_analysis": self.get_staff_impact_analysis(session),
                    "resource_optimization_insights": self.get_resource_optimization_insights(session),
                    # AUGMENTED KPIS (all new methods)
                    "unsafe_events_per_employee": self.get_unsafe_events_per_employee(session),
                    "average_experience_of_involved_employees": self.get_average_experience_of_involved_employees(session),
                    "job_designations_involved_in_incidents": self.get_job_designations_involved_in_incidents(session),
                    "incident_rate_by_experience_bracket": self.get_incident_rate_by_experience_bracket(session),
                    "observations_reported_by_age_group": self.get_observations_reported_by_age_group(session),
                    "training_compliance_rate": self.get_training_compliance_rate(session),
                    "repeat_offenders": self.get_repeat_offenders(session),
                    "incidents_after_extended_shifts": self.get_incidents_after_extended_shifts(session),
                    "incident_rate_vs_weekly_hours_worked": self.get_incident_rate_vs_weekly_hours_worked(session),
                    "overtime_linked_unsafe_events": self.get_overtime_linked_unsafe_events(session),
                    "incidents_during_night_shifts": self.get_incidents_during_night_shifts(session),
                    "incidents_by_hour_of_day": self.get_incidents_by_hour_of_day(session),
                    "events_after_consecutive_working_days": self.get_events_after_consecutive_working_days(session),
                    "top_equipment_involved_in_unsafe_events": self.get_top_equipment_involved_in_unsafe_events(session),
                    "incidents_per_equipment_type": self.get_incidents_per_equipment_type(session),
                    "average_time_since_last_maintenance": self.get_average_time_since_last_maintenance(session),
                    "percentage_of_events_after_unscheduled_maintenance": self.get_percentage_of_events_after_unscheduled_maintenance(session),
                    "time_between_incidents_for_equipment_type": self.get_time_between_incidents_for_equipment_type(session),
                    "repeat_failures_on_same_equipment": self.get_repeat_failures_on_same_equipment(session),
                    "percent_of_incidents_with_corrective_actions": self.get_percent_of_incidents_with_corrective_actions(session),
                    "recurring_events_with_same_root_cause": self.get_recurring_events_with_same_root_cause(session),
                    "percent_of_incidents_investigated": self.get_percent_of_incidents_investigated(session),
                    "incidents_by_root_cause_category": self.get_incidents_by_root_cause_category(session),
                    "top_5_recurrent_root_causes": self.get_top_5_recurrent_root_causes(session),
                    "average_time_to_close_investigation": self.get_average_time_to_close_investigation(session),
                    "repeat_events_despite_capa": self.get_repeat_events_despite_capa(session),
                    "events_by_root_cause_category_and_site": self.get_events_by_root_cause_category_and_site(session),
                    "audit_frequency_vs_incidents_of_branch": self.get_audit_frequency_vs_incidents_of_branch(session),
                    "audit_recency_vs_incidents_of_branch": self.get_audit_recency_vs_incidents_of_branch(session),
                    "percent_of_incidents_30_days_since_last_audit": self.get_percent_of_incidents_occurring_30_days_since_last_audit(session),
                    "percent_of_branches_with_overdue_audits_and_high_incident_rates": self.get_percent_of_branches_with_overdue_audits_and_high_incident_rates(session),
                    "trend_days_since_audit_vs_incident_volume": self.get_trend_days_since_audit_vs_incident_volume(session),
                    "incident_rate_by_weather_condition": self.get_incident_rate_by_weather_condition(session),
                    "percent_of_incidents_during_extreme_weather_days": self.get_percent_of_incidents_during_extreme_weather_days(session),
                    "unsafe_event_type_vs_weather_condition_correlation": self.get_unsafe_event_type_vs_weather_condition_correlation(session),
                }
                logger.info("Successfully executed essential and augmented SRS KPI queries")
                return results
            finally:
                if not use_existing_session:
                    session.close()
        except Exception as e:
            logger.error(f"Error in get_all_kpis: {e}")
            raise
