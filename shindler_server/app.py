from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Azure OpenAI configuration
from config import azure_config, get_azure_openai_client

# Import Langfuse configuration and initialize
try:
    from config.langfuse_config import langfuse_client, langfuse_config
    logger.info(f"Langfuse configuration loaded. Enabled: {langfuse_config.langfuse_enabled}")
except ImportError as e:
    logger.warning(f"Langfuse configuration not available: {e}")
    langfuse_client = None

# Import route modules
from routes.ei_tech_routes import router as ei_tech_router
from routes.srs_routes import router as srs_router
from routes.ni_tct_routes import router as ni_tct_router
from routes.conversation_routers import  router as conv_bi_router
from routes.srs_agumented_routes import router as srs_agumented_router
from routes.srs_enriched_routes import router as srs_enriched_router
from routes.dashboard_srs_agumented_routes import router as dashboard_srs_agumented_router
# Import dashboard route modules
from routes.dashboard_ei_tech_routes import router as dashboard_ei_tech_router
from routes.dashboard_srs_routes import router as dashboard_srs_router
from routes.dashboard_srs_enriched_routes import router as dashboard_srs_enriched_router
from routes.dashboard_ni_tct_routes import router as dashboard_ni_tct_router
from routes.dashboard_management_routes import router as dashboard_management_router
# Import file upload route module
from routes.file_upload_routes import router as file_upload_router
from routes.file_health_routers import health_router
# Create FastAPI app
app = FastAPI(
    title="Shindler Safety Analytics API Server",
    description="FastAPI server for comprehensive safety KPIs from EI Tech, SRS (Safety Reporting System), and NI TCT (Non-Intrusive Testing) with date filtering capabilities, plus conversational BI for natural language queries",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ei_tech_router)
app.include_router(srs_router)
app.include_router(ni_tct_router)
app.include_router(conv_bi_router)
app.include_router(srs_agumented_router)
app.include_router(srs_enriched_router)
app.include_router(dashboard_srs_agumented_router)
# Include dashboard routers
app.include_router(dashboard_ei_tech_router)
app.include_router(dashboard_srs_router)
app.include_router(dashboard_srs_enriched_router)
app.include_router(dashboard_ni_tct_router)
app.include_router(dashboard_management_router)
# Include file upload router
app.include_router(file_upload_router)

app.include_router(health_router)

# Pydantic models for request/response
class HealthResponse(BaseModel):
    status: str
    message: str
    azure_openai_configured: bool
    database_connected: Optional[bool] = None
    langfuse_configured: Optional[bool] = None

# Health check endpoint
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Shindler Safety Analytics API Server is running"}

@app.get("/health", response_model=HealthResponse)
async def health():
    """Detailed health check"""
    try:
        # Test database connection
        from config.database_config import db_manager
        db_status = db_manager.test_connection()
        
        return HealthResponse(
            status="healthy" if db_status else "partial",
            message="Shindler Safety Analytics API Server health check",
            azure_openai_configured=bool(azure_config.azure_openai_endpoint and azure_config.azure_openai_api_key),
            database_connected=db_status,
            langfuse_configured=langfuse_client is not None
        )
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            message=f"Health check failed: {str(e)}",
            azure_openai_configured=bool(azure_config.azure_openai_endpoint and azure_config.azure_openai_api_key),
            database_connected=False
        )

@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    from datetime import date, timedelta
    
    # Calculate current default dates
    today = date.today()
    one_year_ago = today - timedelta(days=365)
    default_start = one_year_ago.strftime('%Y-%m-%d')
    default_end = today.strftime('%Y-%m-%d')
    
    return {
        "name": "Shindler Safety Analytics API",
        "version": "1.0.0",
        "description": "Comprehensive safety KPIs from EI Tech, SRS (Safety Reporting System), and NI TCT (Non-Intrusive Testing) data with conversational BI capabilities and unified dashboard services",
        "main_endpoints": {
            "ei_tech": "/api/v1/ei_tech",
            "srs": "/api/v1/srs",
            "ni_tct": "/api/v1/ni_tct",
            "conversational_bi": "/api/v1/chat"
        },
        "dashboard_endpoints": {
            "ei_tech_dashboard": "/dashboard/ei_tech",
            "srs_dashboard": "/dashboard/srs",
            "ni_tct_dashboard": "/dashboard/ni_tct"
        },
        "documentation": {
            "/docs": "Interactive API documentation (Swagger UI)",
            "/redoc": "Alternative API documentation (ReDoc)"
        },
        "features": [
            "Date range filtering with start_date and end_date parameters",
            "Default 1-year data range when no dates provided",
            "18+ comprehensive safety KPIs in organized categories",
            "Real-time database connectivity", 
            "JSON response format with metadata",
            "AI-powered insights generation for EI Tech, SRS, and NI TCT data",
            "Conversational BI - Natural language to SQL query conversion",
            "Interactive chat interface for safety data analysis",
            "Unified dashboard services with 12 standardized KPIs per schema",
            "Role-based access control with regional filtering",
            "Time-based analysis with hourly data for NI TCT"
        ],
        "current_defaults": {
            "start_date": default_start,
            "end_date": default_end,
            "description": "Current default date range (1 year from today)"
        },
        "usage_examples": {
            "ei_tech": {
                "default_1_year": "/api/v1/ei_tech",
                "date_range": "/api/v1/ei_tech?start_date=2024-01-01&end_date=2024-12-31",
                "from_date": "/api/v1/ei_tech?start_date=2024-06-01",
                "insights": "/api/v1/ei_tech/insights"
            },
            "srs": {
                "default_1_year": "/api/v1/srs",
                "date_range": "/api/v1/srs?start_date=2024-01-01&end_date=2024-12-31",
                "from_date": "/api/v1/srs?start_date=2024-06-01",
                "insights": "/api/v1/srs/insights"
            },
            "ni_tct": {
                "default_1_year": "/api/v1/ni_tct",
                "date_range": "/api/v1/ni_tct?start_date=2024-01-01&end_date=2024-12-31",
                "from_date": "/api/v1/ni_tct?start_date=2024-06-01",
                "insights": "/api/v1/ni_tct/insights"
            },
            "conversational_bi": {
                "endpoint": "POST /api/v1/chat",
                "description": "Send natural language questions about safety data",
                "example_questions": [
                    "Show me the top 5 unsafe events by region",
                    "What are the most common safety violations this month?",
                    "How many incidents occurred in the last quarter?"
                ]
            },
            "dashboard_endpoints": {
                "ei_tech_dashboard": {
                    "full_dashboard": "/dashboard/ei_tech",
                    "summary": "/dashboard/ei_tech/summary",
                    "with_region": "/dashboard/ei_tech?user_role=safety_manager&region=NR 1",
                    "date_range": "/dashboard/ei_tech?start_date=2024-01-01&end_date=2024-12-31"
                },
                "srs_dashboard": {
                    "full_dashboard": "/dashboard/srs",
                    "summary": "/dashboard/srs/summary",
                    "with_region": "/dashboard/srs?user_role=safety_manager&region=SR 1",
                    "date_range": "/dashboard/srs?start_date=2024-01-01&end_date=2024-12-31"
                },
                "ni_tct_dashboard": {
                    "full_dashboard": "/dashboard/ni_tct",
                    "summary": "/dashboard/ni_tct/summary",
                    "time_patterns": "/dashboard/ni_tct/time_patterns",
                    "with_region": "/dashboard/ni_tct?user_role=safety_manager&region=WR 1",
                    "date_range": "/dashboard/ni_tct?start_date=2024-01-01&end_date=2024-12-31"
                }
            }
        },
        "default_behavior": "Returns data for the last 1 year when no date parameters are provided"
    }


if __name__ == "__main__":
    # Start the server on port 8000
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
