"""
Chart Storage Service
Handles persistent file-based storage of charts and dashboards
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ChartStorageService:
    def __init__(self, base_path: str = "saved_charts"):
        self.base_path = Path(base_path)
        self.charts_path = self.base_path / "charts"
        self.dashboards_path = self.base_path / "dashboards"
        self.users_path = self.base_path / "users"
        
        # Create directories if they don't exist
        self.charts_path.mkdir(parents=True, exist_ok=True)
        self.dashboards_path.mkdir(parents=True, exist_ok=True)
        self.users_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Chart storage initialized at {self.base_path}")
    
    def save_chart(self, chart_data: Dict[str, Any]) -> str:
        """Save a chart to file storage"""
        try:
            chart_id = chart_data.get("id") or f"chart_{datetime.now().timestamp()}"
            user_id = chart_data.get("user_id", "anonymous")
            
            # Create user directory if it doesn't exist
            user_charts_path = self.charts_path / user_id
            user_charts_path.mkdir(parents=True, exist_ok=True)
            
            # Save chart file
            chart_file = user_charts_path / f"{chart_id}.json"
            with open(chart_file, 'w', encoding='utf-8') as f:
                json.dump(chart_data, f, indent=2, ensure_ascii=False)
            
            # Update user's chart index
            self._update_user_chart_index(user_id, chart_id, chart_data)
            
            logger.info(f"Saved chart {chart_id} for user {user_id}")
            return chart_id
            
        except Exception as e:
            logger.error(f"Error saving chart: {e}")
            raise
    
    def load_chart(self, chart_id: str, user_id: str = "anonymous") -> Optional[Dict[str, Any]]:
        """Load a chart from file storage"""
        try:
            chart_file = self.charts_path / user_id / f"{chart_id}.json"
            if not chart_file.exists():
                return None
            
            with open(chart_file, 'r', encoding='utf-8') as f:
                chart_data = json.load(f)
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error loading chart {chart_id}: {e}")
            return None
    
    def get_user_charts(self, user_id: str = "anonymous") -> List[Dict[str, Any]]:
        """Get all charts for a user"""
        try:
            user_charts_path = self.charts_path / user_id
            if not user_charts_path.exists():
                return []
            
            charts = []
            for chart_file in user_charts_path.glob("*.json"):
                try:
                    with open(chart_file, 'r', encoding='utf-8') as f:
                        chart_data = json.load(f)
                    charts.append(chart_data)
                except Exception as e:
                    logger.error(f"Error loading chart file {chart_file}: {e}")
                    continue
            
            # Sort by creation date (newest first)
            charts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return charts
            
        except Exception as e:
            logger.error(f"Error getting charts for user {user_id}: {e}")
            return []
    
    def delete_chart(self, chart_id: str, user_id: str = "anonymous") -> bool:
        """Delete a chart from file storage"""
        try:
            chart_file = self.charts_path / user_id / f"{chart_id}.json"
            if not chart_file.exists():
                return False
            
            # Remove chart file
            chart_file.unlink()
            
            # Update user's chart index
            self._remove_from_user_chart_index(user_id, chart_id)
            
            logger.info(f"Deleted chart {chart_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting chart {chart_id}: {e}")
            return False
    
    def save_dashboard(self, dashboard_data: Dict[str, Any]) -> str:
        """Save a dashboard to file storage"""
        try:
            dashboard_id = dashboard_data.get("id") or f"dashboard_{datetime.now().timestamp()}"
            user_id = dashboard_data.get("user_id", "anonymous")
            
            # Create user directory if it doesn't exist
            user_dashboards_path = self.dashboards_path / user_id
            user_dashboards_path.mkdir(parents=True, exist_ok=True)
            
            # Save dashboard file
            dashboard_file = user_dashboards_path / f"{dashboard_id}.json"
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
            
            # Update user's dashboard index
            self._update_user_dashboard_index(user_id, dashboard_id, dashboard_data)
            
            logger.info(f"Saved dashboard {dashboard_id} for user {user_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Error saving dashboard: {e}")
            raise
    
    def load_dashboard(self, dashboard_id: str, user_id: str = "anonymous") -> Optional[Dict[str, Any]]:
        """Load a dashboard from file storage"""
        try:
            dashboard_file = self.dashboards_path / user_id / f"{dashboard_id}.json"
            if not dashboard_file.exists():
                return None
            
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                dashboard_data = json.load(f)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error loading dashboard {dashboard_id}: {e}")
            return None
    
    def get_user_dashboards(self, user_id: str = "anonymous") -> List[Dict[str, Any]]:
        """Get all dashboards for a user"""
        try:
            user_dashboards_path = self.dashboards_path / user_id
            if not user_dashboards_path.exists():
                return []
            
            dashboards = []
            for dashboard_file in user_dashboards_path.glob("*.json"):
                try:
                    with open(dashboard_file, 'r', encoding='utf-8') as f:
                        dashboard_data = json.load(f)
                    dashboards.append(dashboard_data)
                except Exception as e:
                    logger.error(f"Error loading dashboard file {dashboard_file}: {e}")
                    continue
            
            # Sort by creation date (newest first)
            dashboards.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return dashboards
            
        except Exception as e:
            logger.error(f"Error getting dashboards for user {user_id}: {e}")
            return []
    
    def delete_dashboard(self, dashboard_id: str, user_id: str = "anonymous") -> bool:
        """Delete a dashboard from file storage"""
        try:
            dashboard_file = self.dashboards_path / user_id / f"{dashboard_id}.json"
            if not dashboard_file.exists():
                return False
            
            # Remove dashboard file
            dashboard_file.unlink()
            
            # Update user's dashboard index
            self._remove_from_user_dashboard_index(user_id, dashboard_id)
            
            logger.info(f"Deleted dashboard {dashboard_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting dashboard {dashboard_id}: {e}")
            return False
    
    def _update_user_chart_index(self, user_id: str, chart_id: str, chart_data: Dict[str, Any]):
        """Update user's chart index file"""
        try:
            index_file = self.users_path / f"{user_id}_charts.json"
            
            # Load existing index
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            else:
                index = {"charts": [], "last_updated": ""}
            
            # Update or add chart entry
            chart_entry = {
                "id": chart_id,
                "title": chart_data.get("title", ""),
                "created_at": chart_data.get("created_at", ""),
                "source": chart_data.get("source", "chat")
            }
            
            # Remove existing entry if it exists
            index["charts"] = [c for c in index["charts"] if c["id"] != chart_id]
            
            # Add new entry
            index["charts"].append(chart_entry)
            index["last_updated"] = datetime.now().isoformat()
            
            # Save updated index
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error updating user chart index for {user_id}: {e}")
    
    def _remove_from_user_chart_index(self, user_id: str, chart_id: str):
        """Remove chart from user's chart index file"""
        try:
            index_file = self.users_path / f"{user_id}_charts.json"
            
            if not index_file.exists():
                return
            
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
            
            # Remove chart entry
            index["charts"] = [c for c in index["charts"] if c["id"] != chart_id]
            index["last_updated"] = datetime.now().isoformat()
            
            # Save updated index
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error removing from user chart index for {user_id}: {e}")
    
    def _update_user_dashboard_index(self, user_id: str, dashboard_id: str, dashboard_data: Dict[str, Any]):
        """Update user's dashboard index file"""
        try:
            index_file = self.users_path / f"{user_id}_dashboards.json"
            
            # Load existing index
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            else:
                index = {"dashboards": [], "last_updated": ""}
            
            # Update or add dashboard entry
            dashboard_entry = {
                "id": dashboard_id,
                "name": dashboard_data.get("name", ""),
                "created_at": dashboard_data.get("created_at", ""),
                "chart_count": len(dashboard_data.get("charts", []))
            }
            
            # Remove existing entry if it exists
            index["dashboards"] = [d for d in index["dashboards"] if d["id"] != dashboard_id]
            
            # Add new entry
            index["dashboards"].append(dashboard_entry)
            index["last_updated"] = datetime.now().isoformat()
            
            # Save updated index
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error updating user dashboard index for {user_id}: {e}")
    
    def _remove_from_user_dashboard_index(self, user_id: str, dashboard_id: str):
        """Remove dashboard from user's dashboard index file"""
        try:
            index_file = self.users_path / f"{user_id}_dashboards.json"
            
            if not index_file.exists():
                return
            
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
            
            # Remove dashboard entry
            index["dashboards"] = [d for d in index["dashboards"] if d["id"] != dashboard_id]
            index["last_updated"] = datetime.now().isoformat()
            
            # Save updated index
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error removing from user dashboard index for {user_id}: {e}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            stats = {
                "total_charts": 0,
                "total_dashboards": 0,
                "total_users": 0,
                "charts_by_source": {},
                "storage_size": 0
            }
            
            # Count charts
            for user_dir in self.charts_path.iterdir():
                if user_dir.is_dir():
                    stats["total_users"] += 1
                    for chart_file in user_dir.glob("*.json"):
                        stats["total_charts"] += 1
                        stats["storage_size"] += chart_file.stat().st_size
                        
                        # Count by source
                        try:
                            with open(chart_file, 'r', encoding='utf-8') as f:
                                chart_data = json.load(f)
                                source = chart_data.get("source", "unknown")
                                stats["charts_by_source"][source] = stats["charts_by_source"].get(source, 0) + 1
                        except:
                            pass
            
            # Count dashboards
            for user_dir in self.dashboards_path.iterdir():
                if user_dir.is_dir():
                    for dashboard_file in user_dir.glob("*.json"):
                        stats["total_dashboards"] += 1
                        stats["storage_size"] += dashboard_file.stat().st_size
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}

# Global instance
chart_storage = ChartStorageService() 