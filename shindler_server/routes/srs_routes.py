"""
SRS KPI API Routes
FastAPI routes for SRS (Safety Reporting System) KPIs with date filtering support
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import date, datetime
import logging

from kpis.srs_kpis import SRSKPIQueries
from ai_insights.insights_generator import AIInsightsGenerator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["SRS KPIs"])


@router.get("/srs")
async def get_srs_kpis(
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
    Get all SRS (Safety Reporting System) KPIs with optional date filtering
    
    This endpoint returns comprehensive safety KPIs from the SRS App data including:
    - Core safety metrics (total events, near misses, trends)
    - Geographic & risk analysis (branch/region breakdown, risk indices)
    - Behavioral analysis (unsafe acts/conditions, time trends)
    - Operational impact (NOGO violations, work hours lost, reporting delays)
    - Action & compliance metrics (action completion rates, effectiveness)
    - Time-based patterns and regional performance
    - Violation patterns and staff impact analysis
    
    Parameters:
    - start_date: Optional start date for filtering (YYYY-MM-DD). Defaults to 1 year ago.
    - end_date: Optional end date for filtering (YYYY-MM-DD). Defaults to today.
    
    **Default Behavior**: If no date parameters are provided, returns data for the last 1 year.
    
    Returns:
    - JSON object containing all KPI categories with metadata
    """
    try:
        # Validate date formats if provided
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
        
        # Validate date range
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                raise HTTPException(
                    status_code=400,
                    detail="start_date cannot be later than end_date"
                )
        
        logger.info(f"Processing SRS KPI request with date range: {start_date} to {end_date}")
        
        # Initialize KPI queries (SRS doesn't use date filtering in constructor)
        kpi_queries = SRSKPIQueries()
        
        # Execute all KPIs
        results = kpi_queries.get_all_kpis()
        
        logger.info("SRS KPI request completed successfully")
        
        return {
            "status": "success",
            "message": "SRS KPIs retrieved successfully",
            "data": results,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error processing SRS KPI request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/srs/insights/generate-more")
async def generate_more_srs_insights(
    request_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate additional AI insights for SRS data that haven't been generated before
    
    This endpoint generates new insights based on:
    - Existing insights (to avoid duplicates)
    - Positive feedback examples (to improve quality)
    - Different analysis angles (compliance, behavioral, systemic)
    
    Request body should contain:
    - existing_insights: List of already generated insights
    - positive_examples: List of insights that received positive feedback
    - count: Number of new insights to generate (default: 5)
    - start_date: Optional start date for data filtering
    - end_date: Optional end date for data filtering
    
    Returns:
    - JSON object with "additional_insights" key containing new insights
    """
    try:
        logger.info("Processing SRS generate more insights request")
        
        # Extract request parameters
        existing_insights = request_data.get('existing_insights', [])
        positive_examples = request_data.get('positive_examples', [])
        count = request_data.get('count', 5)
        start_date = request_data.get('start_date')
        end_date = request_data.get('end_date')
        
        # Get fresh KPI data with optimized single session - PERFORMANCE OPTIMIZATION
        kpi_queries = SRSKPIQueries()
        session = kpi_queries.get_session()
        try:
            kpi_data = kpi_queries.get_all_kpis(session)

            # Generate additional insights with different prompts/angles
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
        
        logger.info(f"Generated {len(additional_insights)} additional SRS insights")
        
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
        logger.error(f"Error generating additional SRS insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/srs/insights")
async def get_srs_insights(
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
    Generate AI-powered insights from SRS safety KPIs
    
    This endpoint analyzes SRS safety KPI data using Azure OpenAI to generate:
    - 10 comprehensive safety insights combining multiple aspects (bullet points)
    - Deep analysis covering safety performance, risk analysis, operational impact, trends, and recommendations
    - Strategic insights for leadership decision-making
    - Focus on unsafe events, NOGO violations, and reporting patterns
    
    The AI analyzes patterns, trends, and correlations in the data to provide
    actionable insights for safety management and strategic planning.
    
    Parameters:
    - start_date: Optional start date for filtering (YYYY-MM-DD). Defaults to 1 year ago.
    - end_date: Optional end date for filtering (YYYY-MM-DD). Defaults to today.
    
    Returns:
    - JSON object with "insights" key containing 10 comprehensive bullet points
    """
    try:
        # Validate date formats (same validation as main KPI endpoint)
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
        
        # Validate date range
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                raise HTTPException(
                    status_code=400,
                    detail="start_date cannot be later than end_date"
                )
        
        logger.info(f"Processing SRS AI insights request with date range: {start_date} to {end_date}")

        # Get KPI data with optimized single session - PERFORMANCE OPTIMIZATION
        kpi_queries = SRSKPIQueries()
        session = kpi_queries.get_session()
        try:
            kpi_data = kpi_queries.get_all_kpis(session)

            # Generate AI insights
            insights_generator = AIInsightsGenerator()
            insights_result = insights_generator.generate_insights(kpi_data)
        finally:
            session.close()
        
        logger.info("SRS AI insights request completed successfully")
        
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
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error processing SRS AI insights request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while generating insights: {str(e)}"
        )


 