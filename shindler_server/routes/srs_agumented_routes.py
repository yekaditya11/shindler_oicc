"""
SRS Agumented KPI API Routes
FastAPI routes for SRS (Safety Reporting System) Agumented KPIs with date filtering support
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import date, datetime
import logging

from kpis.srs_agumented_kpis import SRSAGUMENTEDKPIQUERIES
from ai_insights.insights_generator import AIInsightsGenerator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/srs_agumented", tags=["SRS Agumented KPIs"])

@router.get("")
async def get_srs_agumented_kpis(
    start_date: Optional[str] = Query(
        None, 
        description="Start date for filtering (YYYY-MM-DD format). Defaults to 1 year ago if not provided."
    ),
    end_date: Optional[str] = Query(
        None, 
        description="End date for filtering (YYYY-MM-DD format). Defaults to today if not provided."
    )
) -> Dict[str, Any]:
    """
    Get all SRS (Safety Reporting System) Agumented KPIs with optional date filtering
    """
    try:
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid start_date format. Use YYYY-MM-DD format."
                )
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid end_date format. Use YYYY-MM-DD format."
                )
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                raise HTTPException(
                    status_code=400,
                    detail="start_date cannot be later than end_date"
                )
        logger.info(f"Processing SRS Agumented KPI request with date range: {start_date} to {end_date}")
        kpi_queries = SRSAGUMENTEDKPIQUERIES()
        results = kpi_queries.get_all_kpis()
        logger.info("SRS Agumented KPI request completed successfully")
        return {
            "status": "success",
            "message": "SRS Agumented KPIs retrieved successfully",
            "data": results,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing SRS Agumented KPI request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/insights/generate-more")
async def generate_more_srs_agumented_insights(
    request_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate additional AI insights for SRS Agumented data that haven't been generated before
    """
    try:
        logger.info("Processing SRS Agumented generate more insights request")
        existing_insights = request_data.get('existing_insights', [])
        positive_examples = request_data.get('positive_examples', [])
        count = request_data.get('count', 5)
        start_date = request_data.get('start_date')
        end_date = request_data.get('end_date')
        kpi_queries = SRSAGUMENTEDKPIQUERIES()
        session = kpi_queries.get_session()
        try:
            kpi_data = kpi_queries.get_all_kpis(session)
            insights_generator = AIInsightsGenerator()
            additional_insights = insights_generator.generate_additional_insights(
                kpi_data=kpi_data,
                existing_insights=existing_insights,
                positive_examples=positive_examples,
                count=count,
                focus_areas=['compliance_analysis', 'behavioral_patterns', 'systemic_issues']
            )
        finally:
            session.close()
        logger.info(f"Generated {len(additional_insights)} additional SRS Agumented insights")
        return {
            "status": "success",
            "message": f"Generated {len(additional_insights)} additional insights",
            "additional_insights": additional_insights,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "insights_count": len(additional_insights),
                "excluded_existing": len(existing_insights),
                "positive_examples_used": len(positive_examples)
            }
        }
    except Exception as e:
        logger.error(f"Error generating additional SRS Agumented insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/insights")
async def get_srs_agumented_insights(
    start_date: Optional[str] = Query(
        None, 
        description="Start date for filtering (YYYY-MM-DD format). Defaults to 1 year ago if not provided."
    ),
    end_date: Optional[str] = Query(
        None, 
        description="End date for filtering (YYYY-MM-DD format). Defaults to today if not provided."
    )
) -> Dict[str, Any]:
    """
    Generate AI-powered insights from SRS Agumented safety KPIs
    """
    try:
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid start_date format. Use YYYY-MM-DD format."
                )
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid end_date format. Use YYYY-MM-DD format."
                )
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                raise HTTPException(
                    status_code=400,
                    detail="start_date cannot be later than end_date"
                )
        logger.info(f"Processing SRS Agumented AI insights request with date range: {start_date} to {end_date}")
        kpi_queries = SRSAGUMENTEDKPIQUERIES()
        session = kpi_queries.get_session()
        try:
            kpi_data = kpi_queries.get_all_kpis(session)
            insights_generator = AIInsightsGenerator()
            insights_result = insights_generator.generate_insights(kpi_data)
        finally:
            session.close()
        logger.info("SRS Agumented AI insights request completed successfully")
        return {
            "status": "success",
            "message": "AI insights generated successfully",
            "insights": insights_result["insights"],
            "metadata": insights_result["metadata"],
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing SRS Agumented AI insights request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while generating insights: {str(e)}"
        )
