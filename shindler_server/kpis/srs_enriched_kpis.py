"""
SRS Enriched KPI Queries Module

This module provides comprehensive KPI queries for SRS Enriched (Safety Reporting System) unsafe events data.
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
    """SQL queries for SRS Enriched App KPIs"""
    
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
    
    # ==================== SEVERITY & IMPACT ANALYSIS ====================
    
    def get_serious_near_miss_count(self, session: Session = None) -> Dict[str, Any]:
        """Serious near miss count and rate"""
        query = f"""
        SELECT 
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 / COUNT(*), 2) as serious_near_miss_rate
        FROM {self.table_name}
        WHERE serious_near_miss IS NOT NULL
        """
        return self.execute_query(query, {}, session)[0]
    
    def get_work_stopped_incidents(self, session: Session = None) -> Dict[str, Any]:
        """Work stopped incidents count and rate"""
        query = f"""
        SELECT 
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 100.0 / COUNT(*), 2) as work_stopped_rate
        FROM {self.table_name}
        WHERE work_stopped IS NOT NULL
        """
        return self.execute_query(query, {}, session)[0]
    
    def get_events_requiring_sanctions(self, session: Session = None) -> Dict[str, Any]:
        """Events requiring sanctions count and rate"""
        query = f"""
        SELECT 
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as sanctions_required_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 100.0 / COUNT(*), 2) as sanctions_rate
        FROM {self.table_name}
        WHERE work_stopped IS NOT NULL
        """
        return self.execute_query(query, {}, session)[0]
    
    def get_nogo_violations_count(self, session: Session = None) -> Dict[str, Any]:
        """NOGO violations count and analysis"""
        query = f"""
        SELECT 
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as nogo_violations,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 100.0 / COUNT(*), 2) as nogo_violation_rate,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' AND UPPER(work_stopped) = 'YES' THEN 1 END) as serious_nogo_violations
        FROM {self.table_name}
        WHERE work_stopped IS NOT NULL
        """
        return self.execute_query(query, {}, session)[0]
    
    # ==================== GEOGRAPHIC & ORGANIZATIONAL ANALYSIS ====================
    
    def get_events_by_region_country_division(self, session: Session = None) -> List[Dict]:
        """Events by region, country, division"""
        query = f"""
        SELECT 
            region,
            country_name,
            division,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_count
        FROM {self.table_name}
        WHERE region IS NOT NULL
        GROUP BY region, country_name, division
        ORDER BY event_count DESC
        """
        return self.execute_query(query, {}, session)
    
    def get_events_by_city_district_zone(self, session: Session = None) -> List[Dict]:
        """Events by city, district, zone"""
        query = f"""
        SELECT 
            city,
            district,
            zone,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_count
        FROM {self.table_name}
        WHERE city IS NOT NULL
        GROUP BY city, district, zone
        ORDER BY event_count DESC
        LIMIT 20
        """
        return self.execute_query(query, {}, session)
    
    def get_events_by_branch(self, session: Session = None) -> List[Dict]:
        """Events by branch with performance metrics"""
        query = f"""
        SELECT 
            branch,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_count,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 / COUNT(*), 2) as serious_near_miss_rate,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 100.0 / COUNT(*), 2) as work_stopped_rate
        FROM {self.table_name}
        WHERE branch IS NOT NULL
        GROUP BY branch
        ORDER BY event_count DESC
        """
        return self.execute_query(query, {}, session)
    
    def get_events_by_business_details(self, session: Session = None) -> List[Dict]:
        """Events by business details"""
        query = f"""
        SELECT 
            business_details,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count
        FROM {self.table_name}
        WHERE business_details IS NOT NULL
        GROUP BY business_details
        ORDER BY event_count DESC
        LIMIT 15
        """
        return self.execute_query(query, {}, session)
    
    def get_events_by_unsafe_event_location(self, session: Session = None) -> List[Dict]:
        """Events by unsafe event location"""
        query = f"""
        SELECT 
            unsafe_event_location,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_count
        FROM {self.table_name}
        WHERE unsafe_event_location IS NOT NULL
        GROUP BY unsafe_event_location
        ORDER BY event_count DESC
        LIMIT 20
        """
        return self.execute_query(query, {}, session)
    
    # ==================== OPERATIONAL IMPACT ====================
    
    def get_work_hours_lost_analysis(self, session: Session = None) -> Dict[str, Any]:
        """Work hours lost analysis"""
        query = f"""
        SELECT 
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_events,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 100.0 / COUNT(*), 2) as work_stopped_percentage
        FROM {self.table_name}
        WHERE work_stopped IS NOT NULL
        """
        return self.execute_query(query, {}, session)[0]
    
    def get_action_creation_and_compliance(self, session: Session = None) -> Dict[str, Any]:
        """Action creation and compliance analysis"""
        query = f"""
        SELECT 
            COUNT(*) as total_events,
            COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) as events_with_actions,
            ROUND(COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) * 100.0 / COUNT(*), 2) as action_compliance_rate
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
            ROUND(COUNT(CASE WHEN "comments/remarks" IS NOT NULL AND "comments/remarks" != '' THEN 1 END) * 100.0 / COUNT(*), 2) as comment_rate,
            ROUND(COUNT(CASE WHEN action_description_1 IS NOT NULL AND action_description_1 != '' THEN 1 END) * 100.0 / COUNT(*), 2) as action_rate
        FROM {self.table_name}
        """
        return self.execute_query(query, {}, session)[0]
    
    # ==================== BEHAVIORAL ANALYSIS ====================
    
    def get_common_unsafe_behaviors(self, session: Session = None) -> List[Dict]:
        """Common unsafe behaviors analysis"""
        query = f"""
        SELECT 
            unsafe_act,
            COUNT(*) as behavior_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {self.table_name}
        WHERE unsafe_act IS NOT NULL AND unsafe_act != ''
        GROUP BY unsafe_act
        ORDER BY behavior_count DESC
        LIMIT 15
        """
        return self.execute_query(query, {}, session)
    
    def get_common_unsafe_conditions(self, session: Session = None) -> List[Dict]:
        """Common unsafe conditions analysis"""
        query = f"""
        SELECT 
            unsafe_condition,
            COUNT(*) as condition_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {self.table_name}
        WHERE unsafe_condition IS NOT NULL AND unsafe_condition != ''
        GROUP BY unsafe_condition
        ORDER BY condition_count DESC
        LIMIT 15
        """
        return self.execute_query(query, {}, session)
    
    def get_monthly_weekly_trends_unsafe_behaviors(self, session: Session = None) -> List[Dict]:
        """Monthly/weekly trends for unsafe behaviors"""
        query = f"""
        SELECT 
            EXTRACT(YEAR FROM date_of_unsafe_event::date) || '-' || LPAD(EXTRACT(MONTH FROM date_of_unsafe_event::date)::text, 2, '0') as month,
            unsafe_act,
            COUNT(*) as behavior_count
        FROM {self.table_name}
        WHERE unsafe_act IS NOT NULL AND unsafe_act != '' AND date_of_unsafe_event IS NOT NULL
        GROUP BY EXTRACT(YEAR FROM date_of_unsafe_event::date), EXTRACT(MONTH FROM date_of_unsafe_event::date), unsafe_act
        ORDER BY month DESC, behavior_count DESC
        LIMIT 30
        """
        return self.execute_query(query, {}, session)
    
    def get_monthly_weekly_trends_unsafe_conditions(self, session: Session = None) -> List[Dict]:
        """Monthly/weekly trends for unsafe conditions"""
        query = f"""
        SELECT 
            EXTRACT(YEAR FROM date_of_unsafe_event::date) || '-' || LPAD(EXTRACT(MONTH FROM date_of_unsafe_event::date)::text, 2, '0') as month,
            unsafe_condition,
            COUNT(*) as condition_count
        FROM {self.table_name}
        WHERE unsafe_condition IS NOT NULL AND unsafe_condition != '' AND date_of_unsafe_event IS NOT NULL
        GROUP BY EXTRACT(YEAR FROM date_of_unsafe_event::date), EXTRACT(MONTH FROM date_of_unsafe_event::date), unsafe_condition
        ORDER BY month DESC, condition_count DESC
        LIMIT 30
        """
        return self.execute_query(query, {}, session)
    
    # ==================== TIME ANALYSIS ====================
    
    def get_time_taken_to_report_incidents(self, session: Session = None) -> List[Dict]:
        """Time taken to report incidents analysis"""
        query = f"""
        SELECT * FROM (
            SELECT 
                CASE 
                    WHEN EXTRACT(EPOCH FROM (reported_date::timestamp - date_of_unsafe_event::timestamp)) / 3600 <= 1 THEN 'Within 1 hour'
                    WHEN EXTRACT(EPOCH FROM (reported_date::timestamp - date_of_unsafe_event::timestamp)) / 3600 <= 24 THEN 'Within 24 hours'
                    WHEN EXTRACT(EPOCH FROM (reported_date::timestamp - date_of_unsafe_event::timestamp)) / 3600 <= 72 THEN 'Within 72 hours'
                    ELSE 'More than 72 hours'
                END as reporting_time_category,
                COUNT(*) as incident_count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
            FROM {self.table_name}
            WHERE date_of_unsafe_event IS NOT NULL AND reported_date IS NOT NULL
            GROUP BY 
                CASE 
                    WHEN EXTRACT(EPOCH FROM (reported_date::timestamp - date_of_unsafe_event::timestamp)) / 3600 <= 1 THEN 'Within 1 hour'
                    WHEN EXTRACT(EPOCH FROM (reported_date::timestamp - date_of_unsafe_event::timestamp)) / 3600 <= 24 THEN 'Within 24 hours'
                    WHEN EXTRACT(EPOCH FROM (reported_date::timestamp - date_of_unsafe_event::timestamp)) / 3600 <= 72 THEN 'Within 72 hours'
                    ELSE 'More than 72 hours'
                END
        ) subquery
        ORDER BY 
            CASE reporting_time_category
                WHEN 'Within 1 hour' THEN 1
                WHEN 'Within 24 hours' THEN 2
                WHEN 'Within 72 hours' THEN 3
                ELSE 4
            END
        """
        return self.execute_query(query, {}, session)
    
    def get_average_time_between_event_and_reporting(self, session: Session = None) -> Dict[str, Any]:
        """Average time between event and reporting"""
        query = f"""
        SELECT 
            ROUND(AVG(EXTRACT(EPOCH FROM (reported_date::timestamp - date_of_unsafe_event::timestamp)) / 3600), 2) as avg_hours_to_report,
            ROUND(AVG(EXTRACT(EPOCH FROM (reported_date::timestamp - date_of_unsafe_event::timestamp)) / 86400), 2) as avg_days_to_report
        FROM {self.table_name}
        WHERE date_of_unsafe_event IS NOT NULL AND reported_date IS NOT NULL
        """
        return self.execute_query(query, {}, session)[0]
    
    def get_events_by_time_of_day(self, session: Session = None) -> List[Dict]:
        """Events by time of day analysis"""
        query = f"""
        SELECT * FROM (
            SELECT 
                CASE 
                    WHEN EXTRACT(HOUR FROM date_of_unsafe_event::timestamp) BETWEEN 6 AND 11 THEN 'Morning (6-11)'
                    WHEN EXTRACT(HOUR FROM date_of_unsafe_event::timestamp) BETWEEN 12 AND 17 THEN 'Afternoon (12-17)'
                    WHEN EXTRACT(HOUR FROM date_of_unsafe_event::timestamp) BETWEEN 18 AND 23 THEN 'Evening (18-23)'
                    ELSE 'Night (0-5)'
                END as time_period,
                COUNT(*) as event_count,
                COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count,
                COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
            FROM {self.table_name}
            WHERE date_of_unsafe_event IS NOT NULL
            GROUP BY 
                CASE 
                    WHEN EXTRACT(HOUR FROM date_of_unsafe_event::timestamp) BETWEEN 6 AND 11 THEN 'Morning (6-11)'
                    WHEN EXTRACT(HOUR FROM date_of_unsafe_event::timestamp) BETWEEN 12 AND 17 THEN 'Afternoon (12-17)'
                    WHEN EXTRACT(HOUR FROM date_of_unsafe_event::timestamp) BETWEEN 18 AND 23 THEN 'Evening (18-23)'
                    ELSE 'Night (0-5)'
                END
        ) subquery
        ORDER BY 
            CASE time_period
                WHEN 'Morning (6-11)' THEN 1
                WHEN 'Afternoon (12-17)' THEN 2
                WHEN 'Evening (18-23)' THEN 3
                ELSE 4
            END
        """
        return self.execute_query(query, {}, session)
    
    # ==================== COMPLIANCE & APPROVAL ====================
    
    def get_events_by_approval_status(self, session: Session = None) -> List[Dict]:
        """Events by approval status - Not available in enriched table"""
        # This field is not available in the unsafe_events_srs_enriched table
        return []
    
    # ==================== RISK ANALYSIS ====================
    
    def get_nogo_violation_trends_by_regions_branches(self, session: Session = None) -> List[Dict]:
        """NOGO violation trends by regions and branches"""
        query = f"""
        SELECT 
            region,
            branch,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as nogo_violations,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 100.0 / COUNT(*), 2) as nogo_violation_rate
        FROM {self.table_name}
        WHERE region IS NOT NULL AND branch IS NOT NULL
        GROUP BY region, branch
        HAVING COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) > 0
        ORDER BY nogo_violation_rate DESC
        """
        return self.execute_query(query, {}, session)
    
    def get_serious_near_miss_by_location_region_branch(self, session: Session = None) -> List[Dict]:
        """Serious near miss analysis by location, region, branch"""
        query = f"""
        SELECT 
            region,
            branch,
            unsafe_event_location,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 / COUNT(*), 2) as serious_near_miss_rate
        FROM {self.table_name}
        WHERE region IS NOT NULL AND branch IS NOT NULL
        GROUP BY region, branch, unsafe_event_location
        HAVING COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) > 0
        ORDER BY serious_near_miss_rate DESC
        LIMIT 20
        """
        return self.execute_query(query, {}, session)
    
    def get_branch_risk_index(self, session: Session = None) -> List[Dict]:
        """Branch risk index calculation"""
        query = f"""
        SELECT 
            branch,
            COUNT(*) as total_events,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_count,
            ROUND(
                (COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 0.6 + 
                 COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 0.4) * 100.0 / COUNT(*), 2
            ) as risk_index
        FROM {self.table_name}
        WHERE branch IS NOT NULL
        GROUP BY branch
        HAVING COUNT(*) >= 5
        ORDER BY risk_index DESC
        """
        return self.execute_query(query, {}, session)
    
    def get_at_risk_regions(self, session: Session = None) -> List[Dict]:
        """At-risk regions analysis"""
        query = f"""
        SELECT 
            region,
            COUNT(*) as total_events,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_near_miss_count,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_count,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 / COUNT(*), 2) as serious_near_miss_rate,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 100.0 / COUNT(*), 2) as work_stopped_rate,
            ROUND(
                (COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 0.6 + 
                 COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 0.4) * 100.0 / COUNT(*), 2
            ) as risk_score
        FROM {self.table_name}
        WHERE region IS NOT NULL
        GROUP BY region
        HAVING COUNT(*) >= 10
        ORDER BY risk_score DESC
        """
        return self.execute_query(query, {}, session)
    
    # ==================== OPERATIONAL ALERTS ====================
    
    def get_operational_alerts_with_reasons(self, days_back: int = 30, session: Session = None) -> List[Dict]:
        """Operational alerts with reasons"""
        query = f"""
        SELECT 
            branch,
            region,
            unsafe_event_location,
            unsafe_event_type,
            COUNT(*) as alert_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_alerts,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_alerts,
            MAX(date_of_unsafe_event) as latest_incident_date
        FROM {self.table_name}
        WHERE date_of_unsafe_event >= CURRENT_DATE - INTERVAL '{days_back} days'
        GROUP BY branch, region, unsafe_event_location, unsafe_event_type
        HAVING COUNT(*) >= 3 OR COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) >= 1
        ORDER BY alert_count DESC, serious_alerts DESC
        LIMIT 20
        """
        return self.execute_query(query, {}, session)
    
    def get_violation_patterns_with_context(self, days_back: int = 30, session: Session = None) -> List[Dict]:
        """Violation patterns with context"""
        query = f"""
        SELECT 
            unsafe_event_type,
            unsafe_act,
            unsafe_condition,
            COUNT(*) as violation_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_violations,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_violations
        FROM {self.table_name}
        WHERE date_of_unsafe_event >= CURRENT_DATE - INTERVAL '{days_back} days'
        AND (unsafe_act IS NOT NULL OR unsafe_condition IS NOT NULL)
        GROUP BY unsafe_event_type, unsafe_act, unsafe_condition
        HAVING COUNT(*) >= 2
        ORDER BY violation_count DESC
        LIMIT 15
        """
        return self.execute_query(query, {}, session)
    
    # ==================== STAFF IMPACT ====================
    
    def get_staff_impact_analysis(self, session: Session = None) -> List[Dict]:
        """Staff impact analysis"""
        query = f"""
        SELECT 
            branch,
            region,
            COUNT(*) as total_events,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            ROUND(COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) * 100.0 / COUNT(*), 2) as serious_incident_rate,
            ROUND(COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) * 100.0 / COUNT(*), 2) as work_stopped_rate
        FROM {self.table_name}
        WHERE branch IS NOT NULL
        GROUP BY branch, region
        ORDER BY serious_incident_rate DESC, work_stopped_rate DESC
        """
        return self.execute_query(query, {}, session)
    
    # ==================== RESOURCE OPTIMIZATION ====================
    
    def get_resource_optimization_insights(self, session: Session = None) -> List[Dict]:
        """Resource optimization insights"""
        query = f"""
        SELECT 
            unsafe_event_location,
            unsafe_event_type,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(serious_near_miss) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER(work_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total
        FROM {self.table_name}
        WHERE unsafe_event_location IS NOT NULL
        GROUP BY unsafe_event_location, unsafe_event_type
        HAVING COUNT(*) >= 3
        ORDER BY event_count DESC
        LIMIT 20
        """
        return self.execute_query(query, {}, session)
    
    # ==================== COMPREHENSIVE KPI COLLECTION ====================
    
    def get_all_kpis(self, session: Session = None) -> Dict[str, Any]:
        """Get all KPIs in a single optimized session"""
        try:
            # Use provided session or create a new one
            use_existing_session = session is not None
            if not session:
                session = self.get_session()
            
            # Execute all KPI queries
            kpis = {
                # Event Volume & Frequency
                "total_events_count": self.get_total_events_count(session),
                "events_by_unsafe_event_type": self.get_events_by_unsafe_event_type(session),
                "events_per_month": self.get_events_per_time_period('month', session),
                "events_per_week": self.get_events_per_time_period('week', session),
                "events_per_quarter": self.get_events_per_time_period('quarter', session),
                
                # Severity & Impact
                "serious_near_miss_count": self.get_serious_near_miss_count(session),
                "work_stopped_incidents": self.get_work_stopped_incidents(session),
                "events_requiring_sanctions": self.get_events_requiring_sanctions(session),
                "nogo_violations_count": self.get_nogo_violations_count(session),
                
                # Geographic & Organizational
                "events_by_region_country_division": self.get_events_by_region_country_division(session),
                "events_by_city_district_zone": self.get_events_by_city_district_zone(session),
                "events_by_branch": self.get_events_by_branch(session),
                "events_by_business_details": self.get_events_by_business_details(session),
                "events_by_unsafe_event_location": self.get_events_by_unsafe_event_location(session),
                
                # Operational Impact
                "work_hours_lost_analysis": self.get_work_hours_lost_analysis(session),
                "action_creation_and_compliance": self.get_action_creation_and_compliance(session),
                "insights_from_comments_and_actions": self.get_insights_from_comments_and_actions(session),
                
                # Behavioral Analysis
                "common_unsafe_behaviors": self.get_common_unsafe_behaviors(session),
                "common_unsafe_conditions": self.get_common_unsafe_conditions(session),
                "monthly_trends_unsafe_behaviors": self.get_monthly_weekly_trends_unsafe_behaviors(session),
                "monthly_trends_unsafe_conditions": self.get_monthly_weekly_trends_unsafe_conditions(session),
                
                # Time Analysis
                "time_taken_to_report_incidents": self.get_time_taken_to_report_incidents(session),
                "average_time_between_event_and_reporting": self.get_average_time_between_event_and_reporting(session),
                "events_by_time_of_day": self.get_events_by_time_of_day(session),
                
                # Compliance & Approval
                "events_by_approval_status": self.get_events_by_approval_status(session),
                
                # Risk Analysis
                "nogo_violation_trends_by_regions_branches": self.get_nogo_violation_trends_by_regions_branches(session),
                "serious_near_miss_by_location_region_branch": self.get_serious_near_miss_by_location_region_branch(session),
                "branch_risk_index": self.get_branch_risk_index(session),
                "at_risk_regions": self.get_at_risk_regions(session),
                
                # Operational Alerts
                "operational_alerts_with_reasons": self.get_operational_alerts_with_reasons(30, session),
                "violation_patterns_with_context": self.get_violation_patterns_with_context(30, session),
                
                # Staff Impact
                "staff_impact_analysis": self.get_staff_impact_analysis(session),
                
                # Resource Optimization
                "resource_optimization_insights": self.get_resource_optimization_insights(session)
            }
            
            return kpis
            
        except Exception as e:
            logger.error(f"Error getting all KPIs: {e}")
            raise
        finally:
            # Only close session if we created it
            if not use_existing_session and session:
                session.close()
