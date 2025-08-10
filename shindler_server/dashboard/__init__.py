"""
Dashboard services for schema-specific KPI analysis
"""

from .ei_tech_dashboard_service import EITechDashboardService
from .srs_dashboard_service import SRSDashboardService  
from .ni_tct_dashboard_service import NITCTDashboardService
from .srs_agumented_dashboard_service import SRSAugmentedDashboardService

__all__ = [
    "EITechDashboardService",
    "SRSDashboardService", 
    "NITCTDashboardService",
    "SRSAugmentedDashboardService"
] 