"""
Dashboard Management API Routes
FastAPI routes for managing custom dashboards and charts
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import logging
import json
import os

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/dashboard", tags=["Dashboard Management"])

# Import chart storage service
from services.chart_storage_service import chart_storage

# Pydantic models for request/response validation
class ChartData(BaseModel):
    chart_data: Dict[str, Any]
    title: str
    source: str = "chat"
    user_id: str = "anonymous"

class DashboardSave(BaseModel):
    dashboard_name: str
    charts: List[Dict[str, Any]]
    user_id: str = "anonymous"

class ChartConfig(BaseModel):
    chart_data: Dict[str, Any]  # Frontend sends chart_data (snake_case)
    title: Union[str, Dict]
    source: str = "chat"
    user_id: str = "anonymous"
    timestamp: Optional[str] = None  # Make timestamp optional

@router.post("/save")
async def save_dashboard(dashboard_data: DashboardSave):
    """
    Save a custom dashboard configuration
    """
    try:
        dashboard_config = {
            "name": dashboard_data.dashboard_name,
            "charts": dashboard_data.charts,
            "user_id": dashboard_data.user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        dashboard_id = chart_storage.save_dashboard(dashboard_config)
        
        logger.info(f"Saved dashboard {dashboard_id} for user {dashboard_data.user_id}")
        
        return {
            "status": "success",
            "message": "Dashboard saved successfully",
            "dashboard_id": dashboard_id,
            "dashboard": {**dashboard_config, "id": dashboard_id}
        }
        
    except Exception as e:
        logger.error(f"Error saving dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save dashboard: {str(e)}")

@router.get("/load/{dashboard_id}")
async def load_dashboard(dashboard_id: str, user_id: str = Query("anonymous", description="User ID")):
    """
    Load a specific dashboard configuration
    """
    try:
        dashboard = chart_storage.load_dashboard(dashboard_id, user_id)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        logger.info(f"Loaded dashboard {dashboard_id}")
        
        return {
            "status": "success",
            "message": "Dashboard loaded successfully",
            "dashboard": dashboard
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading dashboard {dashboard_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard: {str(e)}")

@router.get("/list")
async def list_dashboards(user_id: str = Query("anonymous", description="User ID to filter dashboards")):
    """
    List all dashboards for a user
    """
    try:
        user_dashboards = chart_storage.get_user_dashboards(user_id)
        
        logger.info(f"Listed {len(user_dashboards)} dashboards for user {user_id}")
        
        return {
            "status": "success",
            "message": f"Found {len(user_dashboards)} dashboards",
            "dashboards": user_dashboards
        }
        
    except Exception as e:
        logger.error(f"Error listing dashboards for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list dashboards: {str(e)}")

@router.post("/add-chart")
async def add_chart_to_dashboard(chart_config: ChartConfig):
    """
    Add a chart to user's chart collection
    """
    try:
        user_id = chart_config.user_id
        
        # Use provided timestamp or generate new one
        timestamp = chart_config.timestamp or datetime.now().isoformat()
        
        # Ensure title is a string (handle object titles from conversational BI)
        title = chart_config.title
        if isinstance(title, dict):
            title = title.get('text', str(title))
        elif not isinstance(title, str):
            title = str(title)
        
        # Auto-detect and set chart type for better frontend handling
        chart_data_with_type = chart_config.chart_data.copy()
        if 'type' not in chart_data_with_type:
            if 'series' in chart_data_with_type and isinstance(chart_data_with_type['series'], list):
                # ECharts format - has series array
                chart_data_with_type['type'] = 'echarts'
            elif 'data' in chart_data_with_type and 'layout' in chart_data_with_type:
                # Plotly format - has data and layout
                chart_data_with_type['type'] = 'plotly'
            else:
                # Default to echarts for conversational BI charts
                chart_data_with_type['type'] = 'echarts'
        
        chart_data = {
            "title": title,
            "chartData": chart_data_with_type,
            "source": chart_config.source,
            "timestamp": timestamp,
            "user_id": user_id,
            "created_at": datetime.now().isoformat()
        }
        
        # Save chart using storage service
        chart_id = chart_storage.save_chart(chart_data)
        
        logger.info(f"Added chart {chart_id} for user {user_id}")
        logger.info(f"Chart data keys: {list(chart_data_with_type.keys())}")
        logger.info(f"Chart type set to: {chart_data_with_type.get('type', 'NONE')}")
        
        return {
            "status": "success",
            "message": "Chart added to dashboard successfully",
            "chart_id": chart_id,
            "chart": {**chart_data, "id": chart_id}
        }
        
    except Exception as e:
        logger.error(f"Error adding chart to dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add chart: {str(e)}")

@router.get("/charts/{user_id}")
async def get_user_charts(user_id: str):
    """
    Get all charts for a specific user
    """
    try:
        user_charts = chart_storage.get_user_charts(user_id)
        
        logger.info(f"Retrieved {len(user_charts)} charts for user {user_id}")
        
        return {
            "status": "success",
            "message": f"Found {len(user_charts)} charts",
            "charts": user_charts
        }
        
    except Exception as e:
        logger.error(f"Error getting charts for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user charts: {str(e)}")

@router.delete("/charts/{chart_id}")
async def delete_chart(chart_id: str, user_id: str = Query("anonymous", description="User ID")):
    """
    Delete a specific chart
    """
    try:
        success = chart_storage.delete_chart(chart_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chart not found")
        
        logger.info(f"Deleted chart {chart_id} for user {user_id}")
        
        return {
            "status": "success",
            "message": "Chart deleted successfully",
            "chart_id": chart_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chart {chart_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete chart: {str(e)}")

@router.delete("/dashboard/{dashboard_id}")
async def delete_dashboard(dashboard_id: str, user_id: str = Query("anonymous", description="User ID")):
    """
    Delete a specific dashboard
    """
    try:
        success = chart_storage.delete_dashboard(dashboard_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        logger.info(f"Deleted dashboard {dashboard_id} for user {user_id}")
        
        return {
            "status": "success",
            "message": "Dashboard deleted successfully",
            "dashboard_id": dashboard_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dashboard {dashboard_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete dashboard: {str(e)}")

@router.get("/stats")
async def get_dashboard_stats():
    """
    Get dashboard and chart statistics
    """
    try:
        stats = chart_storage.get_storage_stats()
        
        # Add recent activity from charts
        all_charts = []
        for user_id in ["anonymous"]:  # Add more user IDs if needed
            user_charts = chart_storage.get_user_charts(user_id)
            all_charts.extend(user_charts)
        
        # Recent activity (last 10 charts)
        recent_charts = sorted(
            all_charts,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )[:10]
        
        stats["recent_activity"] = [
            {
                "type": "chart_added",
                "title": chart["title"],
                "timestamp": chart["created_at"],
                "user_id": chart["user_id"]
            }
            for chart in recent_charts
        ]
        
        return {
            "status": "success",
            "message": "Dashboard statistics retrieved successfully",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}") 