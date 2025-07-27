"""
NI TCT Dashboard API Routes
FastAPI routes for NI TCT dashboard KPIs with date filtering and regional support
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import date, datetime
import logging

from dashboard.ni_tct_dashboard_service import NITCTDashboardService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/dashboard", tags=["NI TCT Dashboard"])


@router.get("/ni_tct")
async def get_ni_tct_dashboard(
    start_date: Optional[str] = Query(
        None, 
        description="Start date for filtering (YYYY-MM-DD format). Defaults to 1 year ago if not provided."
    ),
    end_date: Optional[str] = Query(
        None, 
        description="End date for filtering (YYYY-MM-DD format). Defaults to today if not provided."
    ),
    user_role: Optional[str] = Query(
        None,
        description="User role: safety_head, cxo, safety_manager. Affects data scope and permissions."
    ),
    region: Optional[str] = Query(
        None,
        description="Region filter for safety_manager role. Valid regions: NR 1, NR 2, SR 1, SR 2, WR 1, WR 2, INFRA/TRD"
    )
) -> Dict[str, Any]:
    """
    Get NI TCT dashboard data with comprehensive KPIs
    
    This endpoint returns standardized dashboard data from the NI TCT (Non-Intrusive Testing) system including:
    - Total Events Count
    - Serious Near Miss Rate (High-Risk Situations)
    - Work Stoppage Rate
    - Monthly Trends
    - Branch Performance Analysis
    - Event Type Distribution
    - Repeat Locations
    - Response Time Analysis
    - Safety Performance Trends
    - Incident Severity Distribution
    - Operational Impact Analysis
    - Time-based Analysis (with hourly data)
    
    Parameters:
    - start_date: Optional start date for filtering (YYYY-MM-DD). Defaults to 1 year ago.
    - end_date: Optional end date for filtering (YYYY-MM-DD). Defaults to today.
    - user_role: Optional user role for access control and data scoping.
    - region: Optional region filter (required for safety_manager role).
    
    **Default Behavior**: If no date parameters are provided, returns data for the last 1 year.
    
    **Note**: NI TCT data includes time-of-day analysis as it has datetime fields.
    
    Returns:
    - JSON object containing dashboard data with 12 KPIs and metadata
    """
    try:
        logger.info(f"NI TCT Dashboard request - Start: {start_date}, End: {end_date}, Role: {user_role}, Region: {region}")
        
        # Initialize dashboard service
        dashboard_service = NITCTDashboardService()
        
        # Get dashboard data
        dashboard_data = dashboard_service.get_dashboard_data(
            start_date=start_date,
            end_date=end_date,
            user_role=user_role,
            region=region
        )
        
        logger.info(f"Successfully generated NI TCT dashboard data for {dashboard_data['date_range']}")
        return dashboard_data
        
    except ValueError as ve:
        logger.error(f"Validation error in NI TCT dashboard: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in NI TCT dashboard endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve NI TCT dashboard data: {str(e)}"
        )


@router.get("/ni_tct/summary")
async def get_ni_tct_dashboard_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_role: Optional[str] = Query(None, description="User role"),
    region: Optional[str] = Query(None, description="Region filter")
) -> Dict[str, Any]:
    """
    Get NI TCT dashboard summary with key metrics only
    
    Returns a condensed version of the dashboard with essential KPIs:
    - Total Events
    - High-Risk Situation Rate (equivalent to serious near miss)
    - Work Stoppage Rate
    - Key trends
    - Peak time patterns (unique to NI TCT due to hourly data)
    """
    try:
        dashboard_service = NITCTDashboardService()
        full_data = dashboard_service.get_dashboard_data(
            start_date=start_date,
            end_date=end_date,
            user_role=user_role,
            region=region
        )
        
        # Extract summary metrics
        dashboard_data = full_data["dashboard_data"]
        summary = {
            "schema_type": "ni_tct",
            "date_range": full_data["date_range"],
            "generated_at": full_data["generated_at"],
            "summary_metrics": {
                "total_events": dashboard_data["total_events"],
                "serious_near_miss_rate": dashboard_data["serious_near_miss_rate"],
                "work_stoppage_rate": dashboard_data["work_stoppage_rate"],
                "operational_impact_summary": dashboard_data["operational_impact_analysis"]["summary"],
                "recent_trends": dashboard_data["monthly_trends"][-3:] if dashboard_data["monthly_trends"] else [],
                "peak_patterns": dashboard_data["time_based_analysis"]["peak_patterns"]
            }
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error in NI TCT dashboard summary endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve NI TCT dashboard summary: {str(e)}"
        )


@router.get("/ni_tct/time_patterns")
async def get_ni_tct_time_patterns(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    region: Optional[str] = Query(None, description="Region filter")
) -> Dict[str, Any]:
    """
    Get detailed time-based patterns for NI TCT data
    
    This endpoint is specific to NI TCT as it has datetime fields allowing for hourly analysis.
    Returns detailed time-of-day and day-of-week patterns.
    """
    try:
        dashboard_service = NITCTDashboardService()
        full_data = dashboard_service.get_dashboard_data(
            start_date=start_date,
            end_date=end_date,
            region=region
        )
        
        time_analysis = full_data["dashboard_data"]["time_based_analysis"]
        
        return {
            "schema_type": "ni_tct",
            "date_range": full_data["date_range"],
            "time_patterns": time_analysis,
            "description": "Detailed time-based incident patterns for NI TCT data with hourly granularity"
        }
        
    except Exception as e:
        logger.error(f"Error in NI TCT time patterns endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve NI TCT time patterns: {str(e)}"
        ) 