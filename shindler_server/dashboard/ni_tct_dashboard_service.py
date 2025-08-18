"""
NI TCT Dashboard Service for providing standardized dashboard data
Self-contained service with all SQL queries included for common KPIs
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session
from config.database_config import DatabaseManager

logger = logging.getLogger(__name__)


class NITCTDashboardService:
    """
    Clean and optimized NI TCT dashboard service for 12 common KPIs:
    1. Total Events Count
    2. Serious Near Miss Rate
    3. Work Stoppage Rate
    4. Monthly Trends
    5. Branch Performance Analysis
    6. Event Type Distribution
    7. Repeat Locations
    8. Response Time Analysis
    9. Safety Performance Trends
    10. Incident Severity Distribution
    11. Operational Impact Analysis
    12. Time-based Analysis
    """

    def __init__(self):
        """Initialize the NI TCT dashboard service with schema configuration"""
        self.schema_config = {
            "table_name": "unsafe_events_ni_tct",
            "primary_key": "reporting_id",
            "event_date_field": "date_and_time_of_unsafe_event",
            "reported_date_field": "created_on",
            "serious_field": "action_related_to_high_risk_situation",
            "work_stopped_field": "work_was_stopped",
            "event_type_field": "type_of_unsafe_event",
            "location_field": "location",
            "branch_field": "branch_name",
            "region_field": "region"
        }

        self.valid_regions = ["NR 1", "NR 2", "SR 1", "SR 2", "WR 1", "WR 2", "INFRA/TRD"]
        self.db_manager = DatabaseManager()
        
        logger.info("NI TCT Dashboard Service initialized successfully")

    def get_session(self) -> Session:
        """Get database session"""
        return self.db_manager.get_session()

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

    def get_dashboard_data(self, start_date: Optional[str] = None,
                          end_date: Optional[str] = None, user_role: str = None,
                          region: str = None) -> Dict[str, Any]:
        """
        Get NI TCT dashboard data with optimized single session

        Args:
            start_date: Start date for filtering (YYYY-MM-DD format)
            end_date: End date for filtering (YYYY-MM-DD format)
            user_role: User role (safety_head, cxo, safety_manager)
            region: Region for safety_manager role

        Returns:
            Dictionary containing NI TCT dashboard data with 12 KPIs
        """
        try:
            # Validate region if provided
            if user_role == "safety_manager" and region and region not in self.valid_regions:
                raise ValueError(f"Invalid region: {region}. Valid regions: {self.valid_regions}")

            # Set default date range (last 1 year)
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

            logger.info(f"Generating NI TCT dashboard data from {start_date} to {end_date}")
            if user_role == "safety_manager" and region:
                logger.info(f"Regional scope: {region}")

            # Create single session for all KPI queries - PERFORMANCE OPTIMIZATION
            session = self.get_session()
            try:
                # Get all KPI data using the same session
                kpi_data = self._get_all_kpis(start_date, end_date, region, session)

                # Build response
                dashboard_data = {
                    "schema_type": "ni_tct",
                    "date_range": {
                        "start_date": start_date,
                        "end_date": end_date
                    },
                    "generated_at": datetime.now().isoformat(),
                    "user_context": {
                        "user_role": user_role or "unknown",
                        "region": region,
                        "data_scope": "regional" if region else "global"
                    },
                    "dashboard_data": kpi_data
                }

                return dashboard_data
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error generating NI TCT dashboard data: {e}")
            raise

    def _get_all_kpis(self, start_date: str, end_date: str, region: str = None, session: Session = None) -> Dict[str, Any]:
        """Get all KPIs for the NI TCT dashboard using a single session"""
        try:
            config = self.schema_config

            # Execute KPI queries using the shared session - PERFORMANCE OPTIMIZATION
            total_events = self._get_total_events_count(config, start_date, end_date, region, session)
            serious_near_miss = self._get_serious_near_miss_rate(config, start_date, end_date, region, session)
            work_stoppage = self._get_work_stoppage_rate(config, start_date, end_date, region, session)
            monthly_trends = self._get_monthly_trends(config, start_date, end_date, region, session)
            branch_performance = self._get_branch_performance_analysis(config, start_date, end_date, region, session)
            event_types = self._get_event_type_distribution(config, start_date, end_date, region, session)
            repeat_locations = self._get_repeat_locations(config, start_date, end_date, region, session)
            response_time = self._get_response_time_analysis(config, start_date, end_date, region, session)
            safety_performance_trends = self._get_safety_performance_trends(config, start_date, end_date, region, session)
            incident_severity = self._get_incident_severity_distribution(config, start_date, end_date, region, session)
            operational_impact = self._get_operational_impact_analysis(config, start_date, end_date, region, session)
            time_based_analysis = self._get_time_based_analysis(config, start_date, end_date, region, session)
            regional_unsafe_acts_conditions = self._get_regional_unsafe_acts_conditions_analysis(config, start_date, end_date, region, session)
            regional_work_stoppages = self._get_regional_work_stoppages_analysis(config, start_date, end_date, region, session)

            return {
                "total_events": total_events,
                "serious_near_miss_rate": serious_near_miss,
                "work_stoppage_rate": work_stoppage,
                "monthly_trends": {
                    "data": monthly_trends,
                    "description": "Monthly incident trends and patterns",
                    "chart_type": "line"
                },
                "branch_performance_analysis": {
                    "data": branch_performance,
                    "description": "Branch-wise performance analysis",
                    "chart_type": "bar"
                },
                "event_type_distribution": {
                    "data": event_types,
                    "description": "Distribution of unsafe event types",
                    "chart_type": "pie"
                },
                "repeat_locations": {
                    "data": repeat_locations,
                    "description": "Locations with repeated incidents",
                    "chart_type": "bar"
                },
                "response_time_analysis": response_time,
                "safety_performance_trends": {
                    "data": safety_performance_trends,
                    "description": "Safety performance trends over time",
                    "chart_type": "line"
                },
                "incident_severity_distribution": {
                    "data": incident_severity,
                    "description": "Distribution of incident severity levels",
                    "chart_type": "pie"
                },
                "operational_impact_analysis": operational_impact,
                "time_based_analysis": time_based_analysis,
                "regional_unsafe_acts_conditions_analysis": regional_unsafe_acts_conditions
                ,"regional_work_stoppages_analysis": regional_work_stoppages
            }

        except Exception as e:
            logger.error(f"Error getting NI TCT KPIs: {e}")
            return self._get_empty_dashboard_data()

    # ==================== KPI QUERY METHODS ====================

    def _get_total_events_count(self, config: Dict, start_date: str, end_date: str, region: str = None, session: Session = None) -> Dict[str, Any]:
        """KPI 1: Total Events Count"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                COUNT(*) as total_events,
                COUNT(DISTINCT {config['primary_key']}) as unique_events
            FROM {config['table_name']}
            WHERE {config['primary_key']} IS NOT NULL
                AND {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                {region_filter}
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            result = self.execute_query(query, params, session)
            data = result[0] if result else {"total_events": 0, "unique_events": 0}

            return {
                "data": {
                    "count": {
                        "total_events": data.get("total_events", 0),
                        "unique_events": data.get("unique_events", 0)
                    }
                },
                "description": f"Total unsafe events recorded in NI TCT system",
                "chart_type": "card"
            }

        except Exception as e:
            logger.error(f"Error getting total events count: {e}")
            return {"data": {"count": {"total_events": 0, "unique_events": 0}}, "description": "Error retrieving data", "chart_type": "card"}

    def _get_serious_near_miss_rate(self, config: Dict, start_date: str, end_date: str, region: str = None, session: Session = None) -> Dict[str, Any]:
        """KPI 2: Serious Near Miss Rate"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_count,
                COUNT(*) as total_events,
                ROUND(COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as serious_percentage
            FROM {config['table_name']}
            WHERE {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                {region_filter}
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            result = self.execute_query(query, params, session)
            data = result[0] if result else {"serious_count": 0, "total_events": 0, "serious_percentage": 0.0}

            # Safe conversion to handle None values
            serious_percentage = data.get("serious_percentage")
            safe_percentage = float(serious_percentage) if serious_percentage is not None else 0.0
            
            return {
                "data": {
                    "rate": safe_percentage,
                    "count": {
                        "serious_near_miss_count": data.get("serious_count", 0),
                        "non_serious_count": data.get("total_events", 0) - data.get("serious_count", 0),
                        "total_events": data.get("total_events", 0),
                        "serious_near_miss_percentage": str(safe_percentage)
                    }
                },
                "description": "Percentage of events classified as high-risk situations",
                "chart_type": "card"
            }

        except Exception as e:
            logger.error(f"Error getting serious near miss rate: {e}")
            return {"data": {"rate": 0.0, "count": {"serious_near_miss_count": 0, "non_serious_count": 0, "total_events": 0, "serious_near_miss_percentage": "0.0"}}, "description": "Error retrieving data", "chart_type": "card"}

    def _get_work_stoppage_rate(self, config: Dict, start_date: str, end_date: str, region: str = None, session: Session = None) -> Dict[str, Any]:
        """KPI 3: Work Stoppage Rate"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_count,
                COUNT(*) as total_events,
                ROUND(COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as work_stoppage_percentage
            FROM {config['table_name']}
            WHERE {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                {region_filter}
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            result = self.execute_query(query, params, session)
            data = result[0] if result else {"work_stopped_count": 0, "total_events": 0, "work_stoppage_percentage": 0.0}

            # Safe conversion to handle None values
            work_stoppage_percentage = data.get("work_stoppage_percentage")
            safe_percentage = float(work_stoppage_percentage) if work_stoppage_percentage is not None else 0.0
            
            return {
                "data": {
                    "rate": safe_percentage,
                    "count": data.get("work_stopped_count", 0),
                    "total": {
                        "total_events": data.get("total_events", 0),
                        "unique_events": data.get("total_events", 0)
                    }
                },
                "description": "Percentage of events that resulted in work stoppage",
                "chart_type": "card"
            }

        except Exception as e:
            logger.error(f"Error getting work stoppage rate: {e}")
            return {"data": {"rate": 0.0, "count": 0, "total": {"total_events": 0, "unique_events": 0}}, "description": "Error retrieving data", "chart_type": "card"}

    def _get_monthly_trends(self, config: Dict, start_date: str, end_date: str, region: str = None, session: Session = None) -> List[Dict]:
        """KPI 4: Monthly Trends"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                TO_CHAR({config['event_date_field']}, 'YYYY-MM') as month,
                COUNT(*) as event_count,
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_count,
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_count
            FROM {config['table_name']}
            WHERE {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                {region_filter}
            GROUP BY TO_CHAR({config['event_date_field']}, 'YYYY-MM')
            ORDER BY month
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            return self.execute_query(query, params, session)

        except Exception as e:
            logger.error(f"Error getting monthly trends: {e}")
            return []

    def _get_branch_performance_analysis(self, config: Dict, start_date: str, end_date: str, region: str = None, session: Session = None) -> List[Dict]:
        """KPI 5: Branch Performance Analysis"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                {config['branch_field']} as branch,
                {config['region_field']} as region,
                COUNT(*) as total_incidents,
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_incidents,
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stoppages,
                COUNT(DISTINCT {config['location_field']}) as unique_locations,
                COUNT(DISTINCT {config['event_type_field']}) as unique_event_types,
                ROUND(COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as serious_incident_rate,
                ROUND(COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as work_stoppage_rate,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total_incidents,
                ROUND(
                    (COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) * 3 +
                     COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 2) * 100.0 /
                    NULLIF(COUNT(*), 0), 2
                ) as performance_score
            FROM {config['table_name']}
            WHERE {config['branch_field']} IS NOT NULL
                AND {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                {region_filter}
            GROUP BY {config['branch_field']}, {config['region_field']}
            ORDER BY performance_score DESC, total_incidents DESC
            LIMIT 15
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            return self.execute_query(query, params, session)

        except Exception as e:
            logger.error(f"Error getting branch performance analysis: {e}")
            return []

    def _get_event_type_distribution(self, config: Dict, start_date: str, end_date: str, region: str = None, session: Session = None) -> List[Dict]:
        """KPI 6: Event Type Distribution"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                {config['event_type_field']} as event_type,
                COUNT(*) as event_count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
            FROM {config['table_name']}
            WHERE {config['event_type_field']} IS NOT NULL
                AND {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                {region_filter}
            GROUP BY {config['event_type_field']}
            ORDER BY event_count DESC
            LIMIT 10
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            return self.execute_query(query, params, session)

        except Exception as e:
            logger.error(f"Error getting event type distribution: {e}")
            return []

    def _get_repeat_locations(self, config: Dict, start_date: str, end_date: str, region: str = None, session: Session = None) -> List[Dict]:
        """KPI 7: Repeat Locations"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                {config['location_field']} as location,
                {config['region_field']} as region,
                COUNT(*) as incident_count,
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_incidents,
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_incidents,
                ROUND(COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as work_stopped_rate,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total
            FROM {config['table_name']}
            WHERE {config['location_field']} IS NOT NULL
                AND {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                {region_filter}
            GROUP BY {config['location_field']}, {config['region_field']}
            HAVING COUNT(*) > 1
            ORDER BY incident_count DESC
            LIMIT 10
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            return self.execute_query(query, params, session)

        except Exception as e:
            logger.error(f"Error getting repeat locations: {e}")
            return []

    def _get_response_time_analysis(self, config: Dict, start_date: str, end_date: str, region: str = None, session: Session = None) -> Dict[str, Any]:
        """KPI 8: Response Time Analysis"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                AVG(CASE
                    WHEN {config['event_date_field']} IS NOT NULL AND {config['reported_date_field']} IS NOT NULL
                    THEN {config['reported_date_field']}::date - {config['event_date_field']}::date
                END) as avg_reporting_delay_days,
                COUNT(CASE
                    WHEN {config['event_date_field']} IS NOT NULL AND {config['reported_date_field']} IS NOT NULL
                    THEN 1
                END) as events_with_timing_data
            FROM {config['table_name']}
            WHERE {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                {region_filter}
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            result = self.execute_query(query, params, session)
            data = result[0] if result else {"avg_reporting_delay_days": None, "events_with_timing_data": 0}

            avg_delay = data.get("avg_reporting_delay_days")
            if avg_delay is not None:
                return {
                    "data": {
                        "average_response_time": f"{float(avg_delay):.2f} days",
                        "median_response_time": "N/A",
                        "events_analyzed": data.get("events_with_timing_data", 0)
                    },
                    "description": "Average time between incident occurrence and reporting",
                    "chart_type": "card"
                }
            else:
                return {
                    "data": {
                        "average_response_time": "N/A",
                        "median_response_time": "N/A",
                        "events_analyzed": 0
                    },
                    "description": "Response time analysis not available - insufficient timing data",
                    "chart_type": "card"
                }

        except Exception as e:
            logger.error(f"Error getting response time analysis: {e}")
            return {
                "data": {
                    "average_response_time": "N/A",
                    "median_response_time": "N/A",
                    "events_analyzed": 0
                },
                "description": "Error retrieving response time data",
                "chart_type": "card"
            }

    def _get_safety_performance_trends(self, config: Dict, start_date: str, end_date: str, region: str = None, session: Session = None) -> List[Dict]:
        """KPI 9: Safety Performance Trends"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                EXTRACT(YEAR FROM {config['event_date_field']}) as year,
                EXTRACT(QUARTER FROM {config['event_date_field']}) as quarter,
                CONCAT(EXTRACT(YEAR FROM {config['event_date_field']}), '-Q', EXTRACT(QUARTER FROM {config['event_date_field']})) as period,
                COUNT(*) as total_incidents,
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_incidents,
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stoppages,
                COUNT(DISTINCT {config['branch_field']}) as branches_affected,
                COUNT(DISTINCT {config['location_field']}) as locations_affected,
                ROUND(COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as serious_incident_rate,
                ROUND(COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as work_stoppage_rate,
                LAG(COUNT(*)) OVER (ORDER BY EXTRACT(YEAR FROM {config['event_date_field']}), EXTRACT(QUARTER FROM {config['event_date_field']})) as previous_quarter_incidents,
                ROUND(
                    (COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY EXTRACT(YEAR FROM {config['event_date_field']}), EXTRACT(QUARTER FROM {config['event_date_field']}))) * 100.0 /
                    NULLIF(LAG(COUNT(*)) OVER (ORDER BY EXTRACT(YEAR FROM {config['event_date_field']}), EXTRACT(QUARTER FROM {config['event_date_field']})), 0), 2
                ) as quarter_over_quarter_change
            FROM {config['table_name']}
            WHERE {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                {region_filter}
            GROUP BY EXTRACT(YEAR FROM {config['event_date_field']}), EXTRACT(QUARTER FROM {config['event_date_field']})
            ORDER BY year DESC, quarter DESC
            LIMIT 8
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            return self.execute_query(query, params, session)

        except Exception as e:
            logger.error(f"Error getting safety performance trends: {e}")
            return []

    def _get_incident_severity_distribution(self, config: Dict, start_date: str, end_date: str, region: str = None, session: Session = None) -> List[Dict]:
        """KPI 10: Incident Severity Distribution"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            WITH severity_data AS (
                SELECT
                    COUNT(*) as total_incidents,
                    COUNT(CASE WHEN UPPER(COALESCE({config['serious_field']}, '')) IN ('YES', 'Y', '1', 'TRUE')
                               AND UPPER(COALESCE({config['work_stopped_field']}, '')) IN ('YES', 'Y', '1', 'TRUE') THEN 1 END) as critical_count,
                    COUNT(CASE WHEN UPPER(COALESCE({config['serious_field']}, '')) IN ('YES', 'Y', '1', 'TRUE')
                               AND UPPER(COALESCE({config['work_stopped_field']}, '')) NOT IN ('YES', 'Y', '1', 'TRUE') THEN 1 END) as high_count,
                    COUNT(CASE WHEN UPPER(COALESCE({config['serious_field']}, '')) NOT IN ('YES', 'Y', '1', 'TRUE')
                               AND UPPER(COALESCE({config['work_stopped_field']}, '')) IN ('YES', 'Y', '1', 'TRUE') THEN 1 END) as medium_work_stopped,
                    COUNT(CASE WHEN UPPER(COALESCE({config['serious_field']}, '')) NOT IN ('YES', 'Y', '1', 'TRUE')
                               AND UPPER(COALESCE({config['work_stopped_field']}, '')) NOT IN ('YES', 'Y', '1', 'TRUE') THEN 1 END) as low_count
                FROM {config['table_name']}
                WHERE {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                    {region_filter}
            )
            SELECT 'Critical' as severity_level, critical_count as incident_count,
                   ROUND(critical_count * 100.0 / NULLIF(total_incidents, 0), 2) as percentage,
                   1 as sort_order
            FROM severity_data WHERE critical_count > 0
            UNION ALL
            SELECT 'High' as severity_level, high_count as incident_count,
                   ROUND(high_count * 100.0 / NULLIF(total_incidents, 0), 2) as percentage,
                   2 as sort_order
            FROM severity_data WHERE high_count > 0
            UNION ALL
            SELECT 'Medium' as severity_level, medium_work_stopped as incident_count,
                   ROUND(medium_work_stopped * 100.0 / NULLIF(total_incidents, 0), 2) as percentage,
                   3 as sort_order
            FROM severity_data WHERE medium_work_stopped > 0
            UNION ALL
            SELECT 'Low' as severity_level, low_count as incident_count,
                   ROUND(low_count * 100.0 / NULLIF(total_incidents, 0), 2) as percentage,
                   4 as sort_order
            FROM severity_data WHERE low_count > 0
            ORDER BY sort_order
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            result = self.execute_query(query, params, session)

            if not result:
                count_query = f"""
                SELECT COUNT(*) as total_count
                FROM {config['table_name']}
                WHERE {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                    {region_filter}
                """
                count_result = self.execute_query(count_query, params)
                total_count = count_result[0].get('total_count', 0) if count_result else 0

                if total_count > 0:
                    return [{
                        'severity_level': 'Low',
                        'incident_count': total_count,
                        'percentage': 100.0,
                        'sort_order': 4
                    }]
                else:
                    return []

            return result

        except Exception as e:
            logger.error(f"Error getting incident severity distribution: {e}")
            return []

    def _get_operational_impact_analysis(self, config: Dict, start_date: str, end_date: str, region: str = None, session: Session = None) -> Dict[str, Any]:
        """KPI 11: Operational Impact Analysis"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                COUNT(*) as total_incidents,
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_incidents,
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_incidents,
                COUNT(DISTINCT {config['branch_field']}) as branches_impacted,
                COUNT(DISTINCT {config['location_field']}) as locations_impacted,
                COUNT(DISTINCT {config['event_type_field']}) as incident_types,
                ROUND(COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as operational_disruption_rate,
                ROUND(COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as safety_risk_rate,
                ROUND(
                    (COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 1.0 +
                     COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) * 2.0) /
                    NULLIF(COUNT(*), 0), 2
                ) as overall_impact_score
            FROM {config['table_name']}
            WHERE {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                {region_filter}
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            result = self.execute_query(query, params, session)
            data = result[0] if result else {}

            return {
                "data": {
                    "summary": {
                        "total_incidents": data.get("total_incidents", 0),
                        "branches_impacted": data.get("branches_impacted", 0),
                        "locations_impacted": data.get("locations_impacted", 0),
                        "incident_types": data.get("incident_types", 0)
                    },
                    "impact_metrics": {
                        "operational_disruption_rate": float(data.get("operational_disruption_rate")) if data.get("operational_disruption_rate") is not None else 0.0,
                        "safety_risk_rate": float(data.get("safety_risk_rate")) if data.get("safety_risk_rate") is not None else 0.0,
                        "overall_impact_score": float(data.get("overall_impact_score")) if data.get("overall_impact_score") is not None else 0.0
                    },
                    "incident_breakdown": {
                        "work_stopped_incidents": data.get("work_stopped_incidents", 0),
                        "serious_incidents": data.get("serious_incidents", 0)
                    }
                },
                "description": "Comprehensive analysis of operational and business impact from safety incidents",
                "chart_type": "card"
            }

        except Exception as e:
            logger.error(f"Error getting operational impact analysis: {e}")
            return {
                "data": {
                    "summary": {"total_incidents": 0, "branches_impacted": 0, "locations_impacted": 0, "incident_types": 0},
                    "impact_metrics": {"operational_disruption_rate": 0.0, "safety_risk_rate": 0.0, "overall_impact_score": 0.0},
                    "incident_breakdown": {"work_stopped_incidents": 0, "serious_incidents": 0}
                },
                "description": "Error retrieving operational impact data",
                "chart_type": "card"
            }

    def _get_time_based_analysis(self, config: Dict, start_date: str, end_date: str, region: str = None, session: Session = None) -> Dict[str, Any]:
        """KPI 12: Time-based Analysis"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            # NI TCT has datetime fields, so we can provide hourly analysis
            time_of_day_query = f"""
            SELECT
                CASE
                    WHEN EXTRACT(HOUR FROM {config['event_date_field']}) BETWEEN 6 AND 11 THEN 'Morning (6AM-12PM)'
                    WHEN EXTRACT(HOUR FROM {config['event_date_field']}) BETWEEN 12 AND 17 THEN 'Afternoon (12PM-6PM)'
                    WHEN EXTRACT(HOUR FROM {config['event_date_field']}) BETWEEN 18 AND 23 THEN 'Evening (6PM-12AM)'
                    ELSE 'Night (12AM-6AM)'
                END as time_period,
                COUNT(*) as incident_count,
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_incidents,
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_incidents,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
            FROM {config['table_name']}
            WHERE {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                AND EXTRACT(HOUR FROM {config['event_date_field']}) IS NOT NULL
                {region_filter}
            GROUP BY
                CASE
                    WHEN EXTRACT(HOUR FROM {config['event_date_field']}) BETWEEN 6 AND 11 THEN 'Morning (6AM-12PM)'
                    WHEN EXTRACT(HOUR FROM {config['event_date_field']}) BETWEEN 12 AND 17 THEN 'Afternoon (12PM-6PM)'
                    WHEN EXTRACT(HOUR FROM {config['event_date_field']}) BETWEEN 18 AND 23 THEN 'Evening (6PM-12AM)'
                    ELSE 'Night (12AM-6AM)'
                END
            ORDER BY incident_count DESC
            """

            day_of_week_query = f"""
            SELECT
                TO_CHAR({config['event_date_field']}, 'Day') as day_of_week,
                EXTRACT(DOW FROM {config['event_date_field']}) as day_number,
                COUNT(*) as incident_count,
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_incidents,
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_incidents,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
            FROM {config['table_name']}
            WHERE {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                {region_filter}
            GROUP BY TO_CHAR({config['event_date_field']}, 'Day'), EXTRACT(DOW FROM {config['event_date_field']})
            ORDER BY day_number
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            time_of_day_results = self.execute_query(time_of_day_query, params)
            day_of_week_results = self.execute_query(day_of_week_query, params)

            peak_time_period = max(time_of_day_results, key=lambda x: x['incident_count'])['time_period'] if time_of_day_results else "N/A"
            peak_day = max(day_of_week_results, key=lambda x: x['incident_count'])['day_of_week'].strip() if day_of_week_results else "N/A"

            return {
                "chart_type": "bar",
                "description": "Time-based incident pattern analysis with hourly data",
                "data": [{
                    "time_of_day_analysis": time_of_day_results,
                    "day_of_week_analysis": day_of_week_results,
                    "peak_patterns": {
                        "peak_time_period": peak_time_period,
                        "peak_day_of_week": peak_day
                    },
                    "summary": {
                        "total_time_periods_analyzed": len(time_of_day_results),
                        "total_days_analyzed": len(day_of_week_results),
                        "has_hourly_data": True
                    }
                }]
            }

        except Exception as e:
            logger.error(f"Error getting time-based analysis: {e}")
            return {
                "chart_type": "bar",
                "description": "Error retrieving time-based analysis data",
                "data": []
            }

    def _get_empty_dashboard_data(self) -> Dict[str, Any]:
        """Return empty dashboard data structure for all 12 KPIs"""
        return {
            "total_events": {
                "data": {"count": {"total_events": 0, "unique_events": 0}},
                "description": "No data available",
                "chart_type": "card"
            },
            "serious_near_miss_rate": {
                "data": {
                    "rate": 0.0,
                    "count": {
                        "serious_near_miss_count": 0,
                        "non_serious_count": 0,
                        "total_events": 0,
                        "serious_near_miss_percentage": "0.0"
                    }
                },
                "description": "No data available",
                "chart_type": "card"
            },
            "work_stoppage_rate": {
                "data": {
                    "rate": 0.0,
                    "count": 0,
                    "total": {"total_events": 0, "unique_events": 0}
                },
                "description": "No data available",
                "chart_type": "card"
            },
            "monthly_trends": {
                "data": [],
                "description": "No data available",
                "chart_type": "line"
            },
            "branch_performance_analysis": {
                "data": [],
                "description": "No data available",
                "chart_type": "bar"
            },
            "event_type_distribution": {
                "data": [],
                "description": "No data available",
                "chart_type": "pie"
            },
            "repeat_locations": {
                "data": [],
                "description": "No data available",
                "chart_type": "bar"
            },
            "response_time_analysis": {
                "data": {
                    "average_response_time": "N/A",
                    "median_response_time": "N/A",
                    "events_analyzed": 0
                },
                "description": "No data available",
                "chart_type": "card"
            },
            "safety_performance_trends": {
                "data": [],
                "description": "No data available",
                "chart_type": "line"
            },
            "incident_severity_distribution": {
                "data": [],
                "description": "No data available",
                "chart_type": "pie"
            },
            "operational_impact_analysis": {
                "data": {
                    "summary": {"total_incidents": 0, "branches_impacted": 0, "locations_impacted": 0, "incident_types": 0},
                    "impact_metrics": {"operational_disruption_rate": 0.0, "safety_risk_rate": 0.0, "overall_impact_score": 0.0},
                    "incident_breakdown": {"work_stopped_incidents": 0, "serious_incidents": 0}
                },
                "description": "No data available",
                "chart_type": "card"
            },
            "time_based_analysis": {
                "chart_type": "bar",
                "description": "No data available",
                "data": []
            },
            "regional_unsafe_acts_conditions_analysis": {
                "chart_type": "table",
                "description": "No data available",
                "data": []
            },
            "regional_work_stoppages_analysis": {
                "chart_type": "table",
                "description": "No data available",
                "data": []
            }
        } 

    def _get_regional_unsafe_acts_conditions_analysis(self, config: Dict, start_date: str, end_date: str, region: str = None, session: Session = None) -> Dict[str, Any]:
        """KPI: Regional Unsafe Acts and Conditions Analysis (NI TCT)"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            WITH unsafe_events_processed AS (
                SELECT 
                    {config['region_field']},
                    {config['event_type_field']} as unsafe_event_type,
                    unsafe_event_details,
                    CASE 
                        WHEN {config['event_type_field']} ILIKE '%unsafe act%' OR {config['event_type_field']} ILIKE '%act%' THEN 1 
                        ELSE 0 
                    END as has_unsafe_act_type,
                    CASE 
                        WHEN {config['event_type_field']} ILIKE '%unsafe condition%' OR {config['event_type_field']} ILIKE '%condition%' THEN 1 
                        ELSE 0 
                    END as has_unsafe_condition_type
                FROM {config['table_name']}
                WHERE {config['region_field']} IS NOT NULL AND {config['region_field']} != ''
                    AND {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                    {region_filter}
            ),
            unsafe_acts_extracted AS (
                SELECT 
                    {config['region_field']},
                    'Unsafe Act' as category,
                    CASE 
                        WHEN has_unsafe_act_type = 1 AND unsafe_event_details IS NOT NULL AND TRIM(unsafe_event_details) != '' 
                            THEN TRIM(unsafe_event_details)
                        WHEN has_unsafe_act_type = 1 AND (unsafe_event_details IS NULL OR TRIM(unsafe_event_details) = '')
                            THEN TRIM(unsafe_event_type)
                        ELSE NULL
                    END AS description
                FROM unsafe_events_processed
                WHERE has_unsafe_act_type = 1
                
                UNION ALL
                
                SELECT 
                    {config['region_field']},
                    'Unsafe Condition' as category,
                    CASE 
                        WHEN has_unsafe_condition_type = 1 AND unsafe_event_details IS NOT NULL AND TRIM(unsafe_event_details) != '' 
                            THEN TRIM(unsafe_event_details)
                        WHEN has_unsafe_condition_type = 1 AND (unsafe_event_details IS NULL OR TRIM(unsafe_event_details) = '')
                            THEN TRIM(unsafe_event_type)
                        ELSE NULL
                    END AS description
                FROM unsafe_events_processed
                WHERE has_unsafe_condition_type = 1
            ),
            all_items_counts AS (
                SELECT 
                    {config['region_field']},
                    category,
                    description,
                    COUNT(*) as item_count
                FROM unsafe_acts_extracted
                WHERE description IS NOT NULL AND description != ''
                GROUP BY {config['region_field']}, category, description
            ),
            region_category_totals AS (
                SELECT 
                    {config['region_field']},
                    category,
                    SUM(item_count) as total_items_in_region_category
                FROM all_items_counts
                GROUP BY {config['region_field']}, category
            ),
            region_totals AS (
                SELECT 
                    {config['region_field']},
                    SUM(item_count) as total_items_in_region
                FROM all_items_counts
                GROUP BY {config['region_field']}
            ),
            most_common_items AS (
                SELECT 
                    {config['region_field']},
                    category,
                    description as most_common_item,
                    item_count as most_common_count,
                    ROW_NUMBER() OVER (PARTITION BY {config['region_field']}, category ORDER BY item_count DESC) as rn
                FROM all_items_counts
            )
            SELECT 
                rt.{config['region_field']},
                rt.total_items_in_region as total_unsafe_items,
                COALESCE(rct_act.total_items_in_region_category, 0) as total_unsafe_acts,
                COALESCE(mci_act.most_common_item, 'None recorded') as most_common_unsafe_act,
                COALESCE(mci_act.most_common_count, 0) as most_common_act_count,
                CASE 
                    WHEN mci_act.most_common_count IS NOT NULL AND rt.total_items_in_region > 0
                    THEN ROUND((mci_act.most_common_count * 100.0 / rt.total_items_in_region), 2) 
                    ELSE 0 
                END as act_percentage_of_region_total,
                COALESCE(rct_cond.total_items_in_region_category, 0) as total_unsafe_conditions,
                COALESCE(mci_cond.most_common_item, 'None recorded') as most_common_unsafe_condition,
                COALESCE(mci_cond.most_common_count, 0) as most_common_condition_count,
                CASE 
                    WHEN mci_cond.most_common_count IS NOT NULL AND rt.total_items_in_region > 0
                    THEN ROUND((mci_cond.most_common_count * 100.0 / rt.total_items_in_region), 2) 
                    ELSE 0 
                END as condition_percentage_of_region_total

            FROM region_totals rt
            LEFT JOIN region_category_totals rct_act ON rt.{config['region_field']} = rct_act.{config['region_field']} AND rct_act.category = 'Unsafe Act'
            LEFT JOIN region_category_totals rct_cond ON rt.{config['region_field']} = rct_cond.{config['region_field']} AND rct_cond.category = 'Unsafe Condition'
            LEFT JOIN most_common_items mci_act ON rt.{config['region_field']} = mci_act.{config['region_field']} AND mci_act.category = 'Unsafe Act' AND mci_act.rn = 1
            LEFT JOIN most_common_items mci_cond ON rt.{config['region_field']} = mci_cond.{config['region_field']} AND mci_cond.category = 'Unsafe Condition' AND mci_cond.rn = 1
            ORDER BY rt.total_items_in_region DESC
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            data = self.execute_query(query, params, session)

            return {
                "chart_type": "table",
                "description": "Regional analysis of unsafe acts and conditions with most common occurrences per region (NI TCT)",
                "data": data
            }
        except Exception as e:
            logger.error(f"Error getting regional unsafe acts and conditions analysis (NI TCT): {e}")
            return {"chart_type": "table", "description": "Error retrieving data", "data": []}

    def _get_regional_work_stoppages_analysis(self, config: Dict, start_date: str, end_date: str, region: str = None, session: Session = None) -> Dict[str, Any]:
        """KPI: Work stoppages by region with most common causes (NI TCT)"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            WITH work_stoppages_data AS (
                SELECT 
                    {config['region_field']},
                    {config['work_stopped_field']} as work_was_stopped,
                    {config['event_type_field']} as type_of_unsafe_event,
                    unsafe_event_details
                FROM {config['table_name']}
                WHERE {config['region_field']} IS NOT NULL AND {config['region_field']} != ''
                    AND {config['work_stopped_field']} IS NOT NULL 
                    AND UPPER(TRIM({config['work_stopped_field']})) IN ('YES', 'Y', '1', 'TRUE')
                    AND {config['event_date_field']}::date BETWEEN :start_date AND :end_date
                    {region_filter}
            ),
            work_stoppage_causes AS (
                SELECT 
                    {config['region_field']},
                    work_was_stopped,
                    CASE 
                        WHEN unsafe_event_details IS NOT NULL AND TRIM(unsafe_event_details) != '' 
                            THEN CONCAT(COALESCE(type_of_unsafe_event, 'Unsafe Event'), ': ', TRIM(unsafe_event_details))
                        WHEN (unsafe_event_details IS NULL OR TRIM(unsafe_event_details) = '')
                             AND type_of_unsafe_event IS NOT NULL AND TRIM(type_of_unsafe_event) != ''
                            THEN TRIM(type_of_unsafe_event)
                        ELSE 'Cause Not Specified'
                    END AS stoppage_cause
                FROM work_stoppages_data
            ),
            cause_counts AS (
                SELECT 
                    {config['region_field']},
                    stoppage_cause,
                    COUNT(*) as cause_count
                FROM work_stoppage_causes
                GROUP BY {config['region_field']}, stoppage_cause
            ),
            region_totals AS (
                SELECT 
                    {config['region_field']},
                    SUM(cause_count) as total_work_stoppages
                FROM cause_counts
                GROUP BY {config['region_field']}
            ),
            most_common_causes AS (
                SELECT 
                    {config['region_field']},
                    stoppage_cause as most_common_cause,
                    cause_count as most_common_count,
                    ROW_NUMBER() OVER (PARTITION BY {config['region_field']} ORDER BY cause_count DESC) as rn
                FROM cause_counts
            )
            SELECT 
                rt.{config['region_field']},
                rt.total_work_stoppages,
                COALESCE(mcc.most_common_cause, 'No causes recorded') as most_common_stoppage_cause,
                COALESCE(mcc.most_common_count, 0) as most_common_cause_count,
                CASE 
                    WHEN mcc.most_common_count IS NOT NULL AND rt.total_work_stoppages > 0
                    THEN ROUND((mcc.most_common_count * 100.0 / rt.total_work_stoppages), 2) 
                    ELSE 0 
                END as percentage_of_region_stoppages
            FROM region_totals rt
            LEFT JOIN most_common_causes mcc ON rt.{config['region_field']} = mcc.{config['region_field']} AND mcc.rn = 1
            ORDER BY rt.total_work_stoppages DESC
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            data = self.execute_query(query, params, session)

            return {
                "chart_type": "table",
                "description": "Work stoppages by region with most common causes (NI TCT)",
                "data": data
            }
        except Exception as e:
            logger.error(f"Error getting regional work stoppages analysis (NI TCT): {e}")
            return {"chart_type": "table", "description": "Error retrieving data", "data": []}