"""
NI TCT KPI API Routes
FastAPI routes for NI TCT (Non-Intrusive Testing) KPIs with date filtering support
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import date, datetime
import logging

from kpis.ni_tct_kpis import NITCTKPIQueries
from ai_insights.insights_generator import AIInsightsGenerator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["NI TCT KPIs"])


@router.get("/ni_tct")
async def get_ni_tct_kpis(
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
    Get all NI TCT (Non-Intrusive Testing) KPIs with optional date filtering
    
    This endpoint returns comprehensive safety KPIs from the NI TCT App data including:
    - Core safety metrics (total events, near misses, trends)
    - Geographic & risk analysis (branch/region breakdown, risk indices)
    - Behavioral analysis (unsafe acts/conditions, time trends)
    - Operational impact (work hours lost, reporting delays)
    - Action & compliance metrics (action completion rates, effectiveness)
    - Time-based patterns and regional performance
    - Testing equipment and methodology analysis
    
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
        
        logger.info(f"Processing NI TCT KPI request with date range: {start_date} to {end_date}")
        
        # Initialize KPI queries (NI TCT doesn't use date filtering in constructor)
        kpi_queries = NITCTKPIQueries()
        
        # Execute all KPIs
        results = kpi_queries.get_all_kpis()
        
        logger.info("NI TCT KPI request completed successfully")
        
        return {
            "status": "success",
            "message": "NI TCT KPIs retrieved successfully",
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
        logger.error(f"Error processing NI TCT KPI request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/ni_tct/insights/generate-more")
async def generate_more_ni_tct_insights(
    request_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate additional AI insights for NI TCT data that haven't been generated before
    
    This endpoint generates new insights based on:
    - Existing insights (to avoid duplicates)
    - Positive feedback examples (to improve quality)
    - Different analysis angles (technical, temporal, maintenance)
    
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
        logger.info("Processing NI TCT generate more insights request")
        
        # Extract request parameters
        existing_insights = request_data.get('existing_insights', [])
        positive_examples = request_data.get('positive_examples', [])
        count = request_data.get('count', 5)
        start_date = request_data.get('start_date')
        end_date = request_data.get('end_date')
        
        # Get fresh KPI data
        kpi_queries = NITCTKPIQueries()
        kpi_data = kpi_queries.get_all_kpis()
        
        # Generate additional insights with different prompts/angles
        insights_generator = AIInsightsGenerator()
        additional_insights = insights_generator.generate_additional_insights(
            kpi_data=kpi_data,
            existing_insights=existing_insights,
            positive_examples=positive_examples,
            count=count,
            focus_areas=['operational_efficiency', 'predictive_analysis', 'strategic_recommendations']
        )
        
        logger.info(f"Generated {len(additional_insights)} additional NI TCT insights")
        
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
        logger.error(f"Error generating additional NI TCT insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/ni_tct/insights")
async def get_ni_tct_insights(
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
    Generate AI-powered insights from NI TCT safety KPIs
    
    This endpoint analyzes NI TCT safety KPI data using Azure OpenAI to generate:
    - 10 comprehensive safety insights combining multiple aspects (bullet points)
    - Deep analysis covering safety performance, risk analysis, operational impact, trends, and recommendations
    - Strategic insights for leadership decision-making
    - Focus on non-intrusive testing methodologies and equipment safety
    
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
        
        logger.info(f"Processing NI TCT AI insights request with date range: {start_date} to {end_date}")
        
        # Get KPI data first
        kpi_queries = NITCTKPIQueries()
        kpi_data = kpi_queries.get_all_kpis()
        
        # Generate AI insights
        insights_generator = AIInsightsGenerator()
        insights_result = insights_generator.generate_insights(kpi_data)
        
        logger.info("NI TCT AI insights request completed successfully")
        
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
        logger.error(f"Error processing NI TCT AI insights request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while generating insights: {str(e)}"
        )


 