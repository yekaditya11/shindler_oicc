"""
SRS Agumented Dashboard API Routes
FastAPI routes for SRS Agumented dashboard KPIs with date filtering and regional support
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import date, datetime
import logging

from dashboard.srs_agumented_dashboard_service import SRSAugmentedDashboardService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard/srs_agumented", tags=["SRS Agumented Dashboard"])

@router.get("")
async def get_srs_agumented_dashboard(
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
    Get SRS Agumented dashboard data with comprehensive KPIs
    """
    try:
        logger.info(f"SRS Agumented Dashboard request - Start: {start_date}, End: {end_date}, Role: {user_role}, Region: {region}")
        dashboard_service = SRSAugmentedDashboardService()
        dashboard_data = dashboard_service.get_dashboard_data(
            start_date=start_date,
            end_date=end_date,
            user_role=user_role,
            region=region
        )
        logger.info(f"Successfully generated SRS Agumented dashboard data for {dashboard_data['date_range']}")
        return dashboard_data
    except ValueError as ve:
        logger.error(f"Validation error in SRS Agumented dashboard: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in SRS Agumented dashboard endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve SRS Agumented dashboard data: {str(e)}"
        )

@router.get("/summary")
async def get_srs_agumented_dashboard_summary(
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
    Get SRS Agumented dashboard summary with key metrics and top insights
    """
    try:
        logger.info(f"SRS Agumented Dashboard Summary request - Start: {start_date}, End: {end_date}, Role: {user_role}, Region: {region}")
        dashboard_service = SRSAugmentedDashboardService()
        summary_data = dashboard_service.get_dashboard_summary(
            start_date=start_date,
            end_date=end_date,
            user_role=user_role,
            region=region
        )
        logger.info(f"Successfully generated SRS Agumented dashboard summary for {summary_data['date_range']}")
        return summary_data
    except ValueError as ve:
        logger.error(f"Validation error in SRS Agumented dashboard summary: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in SRS Agumented dashboard summary endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve SRS Agumented dashboard summary: {str(e)}"
        )
