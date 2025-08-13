"""
SRS Agumented Dashboard Service for providing standardized dashboard data
Self-contained service with all SQL queries included for augmented KPIs
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from kpis.srs_agumented_kpis import SRSAGUMENTEDKPIQUERIES

logger = logging.getLogger(__name__)

class SRSAugmentedDashboardService:
    """
    Clean and optimized SRS Agumented dashboard service for all augmented KPIs
    """
    def __init__(self):
        self.kpi_queries = SRSAGUMENTEDKPIQUERIES()
        # Mirror SRS dashboard schema config but point to augmented table
        self.schema_config = {
            "table_name": "unsafe_events_srs_agumented",
            "primary_key": "event_id",
            "event_date_field": "date_of_unsafe_event",
            "reported_date_field": "reported_date",
            "serious_field": "serious_near_miss",
            "work_stopped_field": "work_stopped",
            "event_type_field": "unsafe_event_type",
            "location_field": "unsafe_event_location",
            "branch_field": "branch",
            "region_field": "region",
        }
        self.valid_regions = ["NR 1", "NR 2", "SR 1", "SR 2", "WR 1", "WR 2", "INFRA/TRD"]
        logger.info("SRS Agumented Dashboard Service initialized successfully")

    def get_session(self) -> Session:
        return self.kpi_queries.get_session()

    def _get_all_kpis(self, session: Session) -> Dict[str, Any]:
        """Get all KPIs from the augmented KPI queries"""
        return self.kpi_queries.get_all_kpis(session)

    # ==================== SRS Standard KPI Helpers (using augmented table) ====================
    def _execute_query(self, query: str, params: Dict = None, session: Session = None) -> List[Dict]:
        """Execute SQL and return list of dicts (mirrors SRS service helper)."""
        result = session.execute(text(query), params or {})
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]

    def _srs_total_events_count(self, config: Dict, start_date: str, end_date: str, region: str, session: Session) -> Dict[str, Any]:
        region_filter = f"AND {config['region_field']} = :region" if region else ""
        query = f"""
        SELECT
            COUNT(*) as total_events,
            COUNT(DISTINCT {config['primary_key']}) as unique_events
        FROM {config['table_name']}
        WHERE {config['primary_key']} IS NOT NULL
          AND {config['event_date_field']} BETWEEN :start_date AND :end_date
          {region_filter}
        """
        params = {"start_date": start_date, "end_date": end_date, **({"region": region} if region else {})}
        result = self._execute_query(query, params, session)
        data = result[0] if result else {"total_events": 0, "unique_events": 0}
        return {
            "data": {
                "count": {
                    "total_events": data.get("total_events", 0),
                    "unique_events": data.get("unique_events", 0),
                }
            },
            "description": "Total unsafe events recorded",
            "chart_type": "card"
        }

    def _srs_serious_near_miss_rate(self, config: Dict, start_date: str, end_date: str, region: str, session: Session) -> Dict[str, Any]:
        region_filter = f"AND {config['region_field']} = :region" if region else ""
        query = f"""
        SELECT
            COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as serious_percentage
        FROM {config['table_name']}
        WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
          {region_filter}
        """
        params = {"start_date": start_date, "end_date": end_date, **({"region": region} if region else {})}
        result = self._execute_query(query, params, session)
        data = result[0] if result else {"serious_count": 0, "total_events": 0, "serious_percentage": 0.0}
        perc = float(data.get("serious_percentage") or 0.0)
        return {
            "data": {
                "rate": perc,
                "count": {
                    "serious_near_miss_count": data.get("serious_count", 0),
                    "non_serious_count": data.get("total_events", 0) - data.get("serious_count", 0),
                    "total_events": data.get("total_events", 0),
                    "serious_near_miss_percentage": f"{perc}",
                }
            },
            "description": "Percentage of events classified as serious near misses",
            "chart_type": "card"
        }

    def _srs_work_stoppage_rate(self, config: Dict, start_date: str, end_date: str, region: str, session: Session) -> Dict[str, Any]:
        region_filter = f"AND {config['region_field']} = :region" if region else ""
        query = f"""
        SELECT
            COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_count,
            COUNT(*) as total_events,
            ROUND(COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as work_stoppage_percentage
        FROM {config['table_name']}
        WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
          {region_filter}
        """
        params = {"start_date": start_date, "end_date": end_date, **({"region": region} if region else {})}
        result = self._execute_query(query, params, session)
        data = result[0] if result else {"work_stopped_count": 0, "total_events": 0, "work_stoppage_percentage": 0.0}
        perc = float(data.get("work_stoppage_percentage") or 0.0)
        return {
            "data": {
                "rate": perc,
                "count": data.get("work_stopped_count", 0),
                "total": {"total_events": data.get("total_events", 0), "unique_events": data.get("total_events", 0)}
            },
            "description": "Percentage of events that resulted in work stoppage",
            "chart_type": "card"
        }

    def _srs_monthly_trends(self, config: Dict, start_date: str, end_date: str, region: str, session: Session) -> Dict[str, Any]:
        region_filter = f"AND {config['region_field']} = :region" if region else ""
        query = f"""
        SELECT
            TO_CHAR({config['event_date_field']}, 'YYYY-MM') as month,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_count,
            COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_count
        FROM {config['table_name']}
        WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
          {region_filter}
        GROUP BY TO_CHAR({config['event_date_field']}, 'YYYY-MM')
        ORDER BY month
        """
        params = {"start_date": start_date, "end_date": end_date, **({"region": region} if region else {})}
        data = self._execute_query(query, params, session)
        return {
            "data": data,
            "description": "Monthly trends of unsafe events",
            "chart_type": "line"
        }

    def _srs_branch_performance(self, config: Dict, start_date: str, end_date: str, region: str, session: Session) -> Dict[str, Any]:
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
          AND {config['event_date_field']} BETWEEN :start_date AND :end_date
          {region_filter}
        GROUP BY {config['branch_field']}, {config['region_field']}
        ORDER BY performance_score DESC, total_incidents DESC
        LIMIT 15
        """
        params = {"start_date": start_date, "end_date": end_date, **({"region": region} if region else {})}
        data = self._execute_query(query, params, session)
        return {
            "data": data,
            "description": "Branch performance analysis",
            "chart_type": "bar"
        }

    def _srs_event_type_distribution(self, config: Dict, start_date: str, end_date: str, region: str, session: Session) -> Dict[str, Any]:
        region_filter = f"AND {config['region_field']} = :region" if region else ""
        query = f"""
        SELECT
            {config['event_type_field']} as event_type,
            COUNT(*) as event_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM {config['table_name']}
        WHERE {config['event_type_field']} IS NOT NULL
          AND {config['event_date_field']} BETWEEN :start_date AND :end_date
          {region_filter}
        GROUP BY {config['event_type_field']}
        ORDER BY event_count DESC
        LIMIT 10
        """
        params = {"start_date": start_date, "end_date": end_date, **({"region": region} if region else {})}
        data = self._execute_query(query, params, session)
        return {
            "data": data,
            "description": "Distribution of unsafe event types",
            "chart_type": "pie"
        }

    def _srs_repeat_locations(self, config: Dict, start_date: str, end_date: str, region: str, session: Session) -> Dict[str, Any]:
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
          AND {config['event_date_field']} BETWEEN :start_date AND :end_date
          {region_filter}
        GROUP BY {config['location_field']}, {config['region_field']}
        HAVING COUNT(*) > 1
        ORDER BY incident_count DESC
        LIMIT 10
        """
        params = {"start_date": start_date, "end_date": end_date, **({"region": region} if region else {})}
        data = self._execute_query(query, params, session)
        return {
            "data": data,
            "description": "Repeat incident locations",
            "chart_type": "bar"
        }

    def _srs_response_time_analysis(self, config: Dict, start_date: str, end_date: str, region: str, session: Session) -> Dict[str, Any]:
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
        WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
          {region_filter}
        """
        params = {"start_date": start_date, "end_date": end_date, **({"region": region} if region else {})}
        result = self._execute_query(query, params, session)
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
        return {
            "data": {
                "average_response_time": "N/A",
                "median_response_time": "N/A",
                "events_analyzed": 0
            },
            "description": "Response time analysis not available - insufficient timing data",
            "chart_type": "card"
        }

    def _srs_safety_performance_trends(self, config: Dict, start_date: str, end_date: str, region: str, session: Session) -> Dict[str, Any]:
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
                  NULLIF(COUNT(*), 0), 2) as work_stoppage_rate
        FROM {config['table_name']}
        WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
          {region_filter}
        GROUP BY EXTRACT(YEAR FROM {config['event_date_field']}), EXTRACT(QUARTER FROM {config['event_date_field']})
        ORDER BY year DESC, quarter DESC
        LIMIT 8
        """
        params = {"start_date": start_date, "end_date": end_date, **({"region": region} if region else {})}
        data = self._execute_query(query, params, session)
        return {
            "data": data,
            "description": "Safety performance trends by quarter",
            "chart_type": "line"
        }

    def _srs_incident_severity_distribution(self, config: Dict, start_date: str, end_date: str, region: str, session: Session) -> Dict[str, Any]:
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
            WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
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
        params = {"start_date": start_date, "end_date": end_date, **({"region": region} if region else {})}
        result = self._execute_query(query, params, session)
        if not result:
            count_query = f"""
            SELECT COUNT(*) as total_count
            FROM {config['table_name']}
            WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
              {region_filter}
            """
            count_result = self._execute_query(count_query, params, session)
            total_count = count_result[0].get('total_count', 0) if count_result else 0
            if total_count > 0:
                data = [{
                    'severity_level': 'Low',
                    'incident_count': total_count,
                    'percentage': 100.0,
                    'sort_order': 4,
                }]
            else:
                data = []
        else:
            data = result
        return {
            "data": data,
            "description": "Distribution of incidents by severity level",
            "chart_type": "pie"
        }

    def _srs_operational_impact(self, config: Dict, start_date: str, end_date: str, region: str, session: Session) -> Dict[str, Any]:
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
        WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
          {region_filter}
        """
        params = {"start_date": start_date, "end_date": end_date, **({"region": region} if region else {})}
        result = self._execute_query(query, params, session)
        data = result[0] if result else {}
        return {
            "data": {
                "summary": {
                    "total_incidents": data.get("total_incidents", 0),
                    "branches_impacted": data.get("branches_impacted", 0),
                    "locations_impacted": data.get("locations_impacted", 0),
                    "incident_types": data.get("incident_types", 0),
                },
                "impact_metrics": {
                    "operational_disruption_rate": float(data.get("operational_disruption_rate") or 0.0),
                    "safety_risk_rate": float(data.get("safety_risk_rate") or 0.0),
                    "overall_impact_score": float(data.get("overall_impact_score") or 0.0),
                },
                "incident_breakdown": {
                    "work_stopped_incidents": data.get("work_stopped_incidents", 0),
                    "serious_incidents": data.get("serious_incidents", 0),
                }
            },
            "description": "Comprehensive analysis of operational and business impact",
            "chart_type": "card"
        }

    def _srs_time_based_analysis(self, config: Dict, start_date: str, end_date: str, region: str, session: Session) -> Dict[str, Any]:
        region_filter = f"AND {config['region_field']} = :region" if region else ""
        time_of_day_query = f"""
        SELECT
            'All Day' as time_period,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_incidents,
            COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_incidents,
            100.0 as percentage
        FROM {config['table_name']}
        WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
          {region_filter}
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
        WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
          {region_filter}
        GROUP BY TO_CHAR({config['event_date_field']}, 'Day'), EXTRACT(DOW FROM {config['event_date_field']})
        ORDER BY day_number
        """
        params = {"start_date": start_date, "end_date": end_date, **({"region": region} if region else {})}
        time_of_day_results = self._execute_query(time_of_day_query, params, session)
        day_of_week_results = self._execute_query(day_of_week_query, params, session)
        peak_time_period = time_of_day_results[0]['time_period'] if time_of_day_results else "N/A"
        peak_day = max(day_of_week_results, key=lambda x: x['incident_count'])['day_of_week'].strip() if day_of_week_results else "N/A"
        return {
            "chart_type": "bar",
            "description": "Time-based incident pattern analysis (date-only data)",
            "data": day_of_week_results
        }

    def _get_srs_standard_kpis(self, start_date: str, end_date: str, region: Optional[str], session: Session) -> Dict[str, Any]:
        """Compute the same 12 SRS dashboard KPIs but using the augmented table."""
        config = self.schema_config
        return {
            "total_events": self._srs_total_events_count(config, start_date, end_date, region, session),
            "serious_near_miss_rate": self._srs_serious_near_miss_rate(config, start_date, end_date, region, session),
            "work_stoppage_rate": self._srs_work_stoppage_rate(config, start_date, end_date, region, session),
            "monthly_trends": self._srs_monthly_trends(config, start_date, end_date, region, session),
            "branch_performance_analysis": self._srs_branch_performance(config, start_date, end_date, region, session),
            "event_type_distribution": self._srs_event_type_distribution(config, start_date, end_date, region, session),
            "repeat_locations": self._srs_repeat_locations(config, start_date, end_date, region, session),
            "response_time_analysis": self._srs_response_time_analysis(config, start_date, end_date, region, session),
            "safety_performance_trends": self._srs_safety_performance_trends(config, start_date, end_date, region, session),
            "incident_severity_distribution": self._srs_incident_severity_distribution(config, start_date, end_date, region, session),
            "operational_impact_analysis": self._srs_operational_impact(config, start_date, end_date, region, session),
            "time_based_analysis": self._srs_time_based_analysis(config, start_date, end_date, region, session),
        }

    def _get_augmented_kpis(self, session: Session) -> Dict[str, Any]:
        """Get 10 important augmented KPIs from the augmented KPI queries."""
        try:
            # Get all augmented KPIs
            all_augmented_kpis = self.kpi_queries.get_all_kpis(session)
            
            # Select 10 most important augmented KPIs for dashboard with chart types
            selected_augmented_kpis = {
                "unsafe_events_per_employee": {
                    "data": all_augmented_kpis.get("unsafe_events_per_employee", []),
                    "description": "Unsafe events per employee analysis",
                    "chart_type": "bar"
                },
                "training_compliance_rate": {
                    "data": all_augmented_kpis.get("training_compliance_rate", {}),
                    "description": "Training compliance rate across organization",
                    "chart_type": "card"
                },
                "repeat_offenders": {
                    "data": all_augmented_kpis.get("repeat_offenders", []),
                    "description": "Employees with multiple incidents",
                    "chart_type": "bar"
                },
                "incidents_by_hour_of_day": {
                    "data": all_augmented_kpis.get("incidents_by_hour_of_day", []),
                    "description": "Incident distribution by hour of day",
                    "chart_type": "line"
                },
                "top_equipment_involved_in_unsafe_events": {
                    "data": all_augmented_kpis.get("top_equipment_involved_in_unsafe_events", []),
                    "description": "Equipment most involved in unsafe events",
                    "chart_type": "bar"
                },
                "percent_of_incidents_with_corrective_actions": {
                    "data": all_augmented_kpis.get("percent_of_incidents_with_corrective_actions", {}),
                    "description": "Percentage of incidents with corrective actions implemented",
                    "chart_type": "card"
                },
                "top_5_recurrent_root_causes": {
                    "data": all_augmented_kpis.get("top_5_recurrent_root_causes", []),
                    "description": "Top 5 most recurrent root causes",
                    "chart_type": "pie"
                },
                "average_time_to_close_investigation": {
                    "data": all_augmented_kpis.get("average_time_to_close_investigation", {}),
                    "description": "Average time to close investigations",
                    "chart_type": "card"
                },
                "incident_rate_by_weather_condition": {
                    "data": all_augmented_kpis.get("incident_rate_by_weather_condition", []),
                    "description": "Incident rates by weather conditions",
                    "chart_type": "bar"
                },
                "percent_of_incidents_during_extreme_weather_days": {
                    "data": all_augmented_kpis.get("percent_of_incidents_during_extreme_weather_days", {}),
                    "description": "Percentage of incidents during extreme weather",
                    "chart_type": "card"
                }
            }
            
            return selected_augmented_kpis
        except Exception as e:
            logger.error(f"Error getting augmented KPIs: {e}")
            return {}

    def _categorize_kpis_for_dashboard(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Organize KPIs into dashboard-friendly categories"""
        return {
            "employee_analytics": {
                "unsafe_events_per_employee": kpi_data.get("unsafe_events_per_employee", []),
                "average_experience_of_involved_employees": kpi_data.get("average_experience_of_involved_employees", {}),
                "job_designations_involved_in_incidents": kpi_data.get("job_designations_involved_in_incidents", []),
                "incident_rate_by_experience_bracket": kpi_data.get("incident_rate_by_experience_bracket", []),
                "observations_reported_by_age_group": kpi_data.get("observations_reported_by_age_group", []),
                "training_compliance_rate": kpi_data.get("training_compliance_rate", {}),
                "repeat_offenders": kpi_data.get("repeat_offenders", [])
            },
            "work_pattern_analytics": {
                "incidents_after_extended_shifts": kpi_data.get("incidents_after_extended_shifts", []),
                "incident_rate_vs_weekly_hours_worked": kpi_data.get("incident_rate_vs_weekly_hours_worked", []),
                "overtime_linked_unsafe_events": kpi_data.get("overtime_linked_unsafe_events", []),
                "incidents_during_night_shifts": kpi_data.get("incidents_during_night_shifts", []),
                "incidents_by_hour_of_day": kpi_data.get("incidents_by_hour_of_day", []),
                "events_after_consecutive_working_days": kpi_data.get("events_after_consecutive_working_days", [])
            },
            "equipment_analytics": {
                "top_equipment_involved_in_unsafe_events": kpi_data.get("top_equipment_involved_in_unsafe_events", []),
                "incidents_per_equipment_type": kpi_data.get("incidents_per_equipment_type", []),
                "average_time_since_last_maintenance": kpi_data.get("average_time_since_last_maintenance", {}),
                "percentage_of_events_after_unscheduled_maintenance": kpi_data.get("percentage_of_events_after_unscheduled_maintenance", []),
                "time_between_incidents_for_equipment_type": kpi_data.get("time_between_incidents_for_equipment_type", []),
                "repeat_failures_on_same_equipment": kpi_data.get("repeat_failures_on_same_equipment", [])
            },
            "investigation_analytics": {
                "percent_of_incidents_with_corrective_actions": kpi_data.get("percent_of_incidents_with_corrective_actions", {}),
                "recurring_events_with_same_root_cause": kpi_data.get("recurring_events_with_same_root_cause", []),
                "percent_of_incidents_investigated": kpi_data.get("percent_of_incidents_investigated", {}),
                "incidents_by_root_cause_category": kpi_data.get("incidents_by_root_cause_category", []),
                "top_5_recurrent_root_causes": kpi_data.get("top_5_recurrent_root_causes", []),
                "average_time_to_close_investigation": kpi_data.get("average_time_to_close_investigation", {}),
                "repeat_events_despite_capa": kpi_data.get("repeat_events_despite_capa", []),
                "events_by_root_cause_category_and_site": kpi_data.get("events_by_root_cause_category_and_site", [])
            },
            "audit_analytics": {
                "audit_frequency_vs_incidents_of_branch": kpi_data.get("audit_frequency_vs_incidents_of_branch", []),
                "audit_recency_vs_incidents_of_branch": kpi_data.get("audit_recency_vs_incidents_of_branch", []),
                "percent_of_incidents_30_days_since_last_audit": kpi_data.get("percent_of_incidents_30_days_since_last_audit", {}),
                "percent_of_branches_with_overdue_audits_and_high_incident_rates": kpi_data.get("percent_of_branches_with_overdue_audits_and_high_incident_rates", []),
                "trend_days_since_audit_vs_incident_volume": kpi_data.get("trend_days_since_audit_vs_incident_volume", [])
            },
            "environmental_analytics": {
                "incident_rate_by_weather_condition": kpi_data.get("incident_rate_by_weather_condition", []),
                "percent_of_incidents_during_extreme_weather_days": kpi_data.get("percent_of_incidents_during_extreme_weather_days", {}),
                "unsafe_event_type_vs_weather_condition_correlation": kpi_data.get("unsafe_event_type_vs_weather_condition_correlation", [])
            },
            "core_metrics": {
                "number_of_unsafe_events": kpi_data.get("number_of_unsafe_events", {}),
                "monthly_unsafe_events_trend": kpi_data.get("monthly_unsafe_events_trend", []),
                "near_misses": kpi_data.get("near_misses", {}),
                "unsafe_events_by_branch": kpi_data.get("unsafe_events_by_branch", []),
                "unsafe_events_by_region": kpi_data.get("unsafe_events_by_region", []),
                "at_risk_regions": kpi_data.get("at_risk_regions", []),
                "branch_risk_index": kpi_data.get("branch_risk_index", [])
            }
        }

    def _generate_summary_metrics(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary metrics for dashboard overview"""
        summary = {
            "total_events": kpi_data.get("number_of_unsafe_events", {}).get("total_events", 0),
            "total_employees_analyzed": len(kpi_data.get("unsafe_events_per_employee", [])),
            "total_equipment_analyzed": len(kpi_data.get("top_equipment_involved_in_unsafe_events", [])),
            "investigation_rate": kpi_data.get("percent_of_incidents_investigated", {}).get("percent_investigated", 0),
            "corrective_action_rate": kpi_data.get("percent_of_incidents_with_corrective_actions", {}).get("percent_with_corrective_actions", 0),
            "training_compliance": kpi_data.get("training_compliance_rate", {}).get("compliance_rate", 0),
            "repeat_offenders_count": len(kpi_data.get("repeat_offenders", [])),
            "high_risk_equipment_count": len([item for item in kpi_data.get("repeat_failures_on_same_equipment", []) if item.get("failure_count", 0) > 2]),
            "overdue_audits_count": len([item for item in kpi_data.get("percent_of_branches_with_overdue_audits_and_high_incident_rates", []) if item.get("days_since_last_audit", 0) > 365])
        }
        return summary

    def get_dashboard_data(self, start_date: Optional[str] = None,
                          end_date: Optional[str] = None, user_role: str = None,
                          region: str = None) -> Dict[str, Any]:
        try:
            # Set default date range (last 1 year)
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

            logger.info(f"Generating SRS Agumented dashboard data from {start_date} to {end_date}")

            session = self.get_session()
            try:
                # Compute the 12 standard SRS dashboard KPIs using augmented table
                srs_standard_kpis = self._get_srs_standard_kpis(start_date, end_date, region, session)
                
                # Get 10 important augmented KPIs
                augmented_kpis = self._get_augmented_kpis(session)

                dashboard_data = {
                    "schema_type": "srs_agumented",
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
                    "dashboard_data": {
                        **srs_standard_kpis,
                        **augmented_kpis
                    }
                }
                return dashboard_data
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error generating SRS Agumented dashboard data: {e}")
            raise

    def get_dashboard_summary(self, start_date: Optional[str] = None,
                             end_date: Optional[str] = None, user_role: str = None,
                             region: str = None) -> Dict[str, Any]:
        """Get a concise summary of key metrics for dashboard overview"""
        try:
            # Set default date range (last 1 year)
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

            logger.info(f"Generating SRS Agumented dashboard summary from {start_date} to {end_date}")

            session = self.get_session()
            try:
                # Compute the 12 standard SRS dashboard KPIs using augmented table
                srs_standard_kpis = self._get_srs_standard_kpis(start_date, end_date, region, session)
                
                # Get augmented KPIs for summary
                augmented_kpis = self._get_augmented_kpis(session)

                # Derive a concise summary from the standard KPIs
                total_events = srs_standard_kpis.get("total_events", {}).get("count", {}).get("total_events", 0)
                serious_rate = srs_standard_kpis.get("serious_near_miss_rate", {}).get("rate", 0.0)
                work_stop_rate = srs_standard_kpis.get("work_stoppage_rate", {}).get("rate", 0.0)
                avg_resp = srs_standard_kpis.get("response_time_analysis", {}).get("average_response_time", "N/A")
                
                # Get augmented KPI summary metrics
                training_compliance = augmented_kpis.get("training_compliance_rate", {}).get("data", {}).get("compliance_rate", 0.0)
                corrective_actions = augmented_kpis.get("percent_of_incidents_with_corrective_actions", {}).get("data", {}).get("corrective_actions_percentage", 0.0)
                repeat_offenders_count = len(augmented_kpis.get("repeat_offenders", {}).get("data", []))
                top_equipment_count = len(augmented_kpis.get("top_equipment_involved_in_unsafe_events", {}).get("data", []))

                summary_data = {
                    "schema_type": "srs_agumented_summary",
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
                    "summary_metrics": {
                        "total_events": total_events,
                        "serious_near_miss_rate": serious_rate,
                        "work_stoppage_rate": work_stop_rate,
                        "average_response_time": avg_resp,
                        "training_compliance_rate": training_compliance,
                        "corrective_actions_rate": corrective_actions,
                        "repeat_offenders_count": repeat_offenders_count,
                        "equipment_incidents_count": top_equipment_count
                    }
                }
                return summary_data
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error generating SRS Agumented dashboard summary: {e}")
            raise
