"""
SRS Dashboard API Routes
FastAPI routes for SRS dashboard KPIs with date filtering and regional support
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import date, datetime
import logging

from dashboard.srs_dashboard_service import SRSDashboardService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/dashboard", tags=["SRS Dashboard"])


@router.get("/srs")
async def get_srs_dashboard(
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
    Get SRS dashboard data with comprehensive KPIs
    
    This endpoint returns standardized dashboard data from the SRS (Safety Reporting System) including:
    - Total Events Count
    - Serious Near Miss Rate
    - Work Stoppage Rate
    - Monthly Trends
    - Branch Performance Analysis
    - Event Type Distribution
    - Repeat Locations
    - Response Time Analysis
    - Safety Performance Trends
    - Incident Severity Distribution
    - Operational Impact Analysis
    - Time-based Analysis
    
    Parameters:
    - start_date: Optional start date for filtering (YYYY-MM-DD). Defaults to 1 year ago.
    - end_date: Optional end date for filtering (YYYY-MM-DD). Defaults to today.
    - user_role: Optional user role for access control and data scoping.
    - region: Optional region filter (required for safety_manager role).
    
    **Default Behavior**: If no date parameters are provided, returns data for the last 1 year.
    
    Returns:
    - JSON object containing dashboard data with 12 KPIs and metadata
    """
    try:
        logger.info(f"SRS Dashboard request - Start: {start_date}, End: {end_date}, Role: {user_role}, Region: {region}")
        
        # Initialize dashboard service
        dashboard_service = SRSDashboardService()
        
        # Get dashboard data
        dashboard_data = dashboard_service.get_dashboard_data(
            start_date=start_date,
            end_date=end_date,
            user_role=user_role,
            region=region
        )
        
        logger.info(f"Successfully generated SRS dashboard data for {dashboard_data['date_range']}")
        return dashboard_data
        
    except ValueError as ve:
        logger.error(f"Validation error in SRS dashboard: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in SRS dashboard endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve SRS dashboard data: {str(e)}"
        )


@router.get("/srs/summary")
async def get_srs_dashboard_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_role: Optional[str] = Query(None, description="User role"),
    region: Optional[str] = Query(None, description="Region filter")
) -> Dict[str, Any]:
    """
    Get SRS dashboard summary with key metrics only
    
    Returns a condensed version of the dashboard with essential KPIs:
    - Total Events
    - Serious Near Miss Rate
    - Work Stoppage Rate
    - Key trends
    """
    try:
        dashboard_service = SRSDashboardService()
        full_data = dashboard_service.get_dashboard_data(
            start_date=start_date,
            end_date=end_date,
            user_role=user_role,
            region=region
        )
        
        # Extract summary metrics
        dashboard_data = full_data["dashboard_data"]
        summary = {
            "schema_type": "srs",
            "date_range": full_data["date_range"],
            "generated_at": full_data["generated_at"],
            "summary_metrics": {
                "total_events": dashboard_data["total_events"],
                "serious_near_miss_rate": dashboard_data["serious_near_miss_rate"],
                "work_stoppage_rate": dashboard_data["work_stoppage_rate"],
                "operational_impact_summary": dashboard_data["operational_impact_analysis"]["summary"],
                "recent_trends": dashboard_data["monthly_trends"][-3:] if dashboard_data["monthly_trends"] else []
            }
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error in SRS dashboard summary endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve SRS dashboard summary: {str(e)}"
        ) 