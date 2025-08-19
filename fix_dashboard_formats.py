#!/usr/bin/env python3
"""
Script to fix all dashboard services to follow consistent response format:
- Chart types (line, bar, pie): {"chart_type": "", "description": "", "data": [...]}
- Card types: {"chart_type": "card", "description": "", "data": {...}}
"""

import re
import os

def fix_dashboard_format(file_path):
    """Fix dashboard service to follow consistent response format"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix card-type KPIs to wrap data in a "data" field
    # Total events count
    content = re.sub(
        r'return \{\s*"count": \{[^}]*\},\s*"description": "[^"]*",\s*"chart_type": "card"\s*\}',
        r'return {\n                "chart_type": "card",\n                "description": "Total unsafe events recorded",\n                "data": {\n                    "count": {\n                        "total_events": data.get("total_events", 0),\n                        "unique_events": data.get("unique_events", 0)\n                    }\n                }\n            }',
        content
    )
    
    # Serious near miss rate
    content = re.sub(
        r'return \{\s*"rate": [^,]*,\s*"count": \{[^}]*\},\s*"description": "[^"]*",\s*"chart_type": "card"\s*\}',
        r'return {\n                "chart_type": "card",\n                "description": "Percentage of events classified as serious near misses",\n                "data": {\n                    "rate": safe_percentage,\n                    "count": {\n                        "serious_near_miss_count": data.get("serious_count", 0),\n                        "non_serious_count": data.get("total_events", 0) - data.get("serious_count", 0),\n                        "total_events": data.get("total_events", 0),\n                        "serious_near_miss_percentage": str(safe_percentage)\n                    }\n                }\n            }',
        content
    )
    
    # Work stoppage rate
    content = re.sub(
        r'return \{\s*"rate": [^,]*,\s*"count": [^,]*,\s*"total": \{[^}]*\},\s*"description": "[^"]*",\s*"chart_type": "card"\s*\}',
        r'return {\n                "chart_type": "card",\n                "description": "Percentage of events that resulted in work stoppage",\n                "data": {\n                    "rate": safe_percentage,\n                    "count": data.get("work_stopped_count", 0),\n                    "total": {\n                        "total_events": data.get("total_events", 0),\n                        "unique_events": data.get("total_events", 0)\n                    }\n                }\n            }',
        content
    )
    
    # Response time analysis
    content = re.sub(
        r'return \{\s*"average_response_time": "[^"]*",\s*"median_response_time": "[^"]*",\s*"events_analyzed": [^,]*,\s*"description": "[^"]*",\s*"chart_type": "card"\s*\}',
        r'return {\n                "chart_type": "card",\n                "description": "Average time between incident occurrence and reporting",\n                "data": {\n                    "average_response_time": f"{float(avg_delay):.2f} days",\n                    "median_response_time": "N/A",\n                    "events_analyzed": data.get("events_with_timing_data", 0)\n                }\n            }',
        content
    )
    
    # Response time analysis (N/A case)
    content = re.sub(
        r'return \{\s*"average_response_time": "N/A",\s*"median_response_time": "N/A",\s*"events_analyzed": 0,\s*"description": "[^"]*",\s*"chart_type": "card"\s*\}',
        r'return {\n                "chart_type": "card",\n                "description": "Response time analysis not available - insufficient timing data",\n                "data": {\n                    "average_response_time": "N/A",\n                    "median_response_time": "N/A",\n                    "events_analyzed": 0\n                }\n            }',
        content
    )
    
    # Response time analysis (error case)
    content = re.sub(
        r'return \{\s*"average_response_time": "N/A",\s*"median_response_time": "N/A",\s*"events_analyzed": 0,\s*"description": "Error retrieving response time data",\s*"chart_type": "card"\s*\}',
        r'return {\n                "chart_type": "card",\n                "description": "Error retrieving response time data",\n                "data": {\n                    "average_response_time": "N/A",\n                    "median_response_time": "N/A",\n                    "events_analyzed": 0\n                }\n            }',
        content
    )
    
    # Operational impact analysis
    content = re.sub(
        r'return \{\s*"summary": \{[^}]*\},\s*"impact_metrics": \{[^}]*\},\s*"incident_breakdown": \{[^}]*\},\s*"description": "[^"]*",\s*"chart_type": "card"\s*\}',
        r'return {\n                "chart_type": "card",\n                "description": "Comprehensive analysis of operational and business impact from safety incidents",\n                "data": {\n                    "summary": {\n                        "total_incidents": data.get("total_incidents", 0),\n                        "branches_impacted": data.get("branches_impacted", 0),\n                        "locations_impacted": data.get("locations_impacted", 0),\n                        "incident_types": data.get("incident_types", 0)\n                    },\n                    "impact_metrics": {\n                        "operational_disruption_rate": safe_operational_rate,\n                        "safety_risk_rate": safe_safety_rate,\n                        "overall_impact_score": safe_impact_score\n                    },\n                    "incident_breakdown": {\n                        "work_stopped_incidents": data.get("work_stopped_incidents", 0),\n                        "serious_incidents": data.get("serious_incidents", 0)\n                    }\n                }\n            }',
        content
    )
    
    # Operational impact analysis (error case)
    content = re.sub(
        r'return \{\s*"summary": \{[^}]*\},\s*"impact_metrics": \{[^}]*\},\s*"incident_breakdown": \{[^}]*\},\s*"description": "Error retrieving operational impact data",\s*"chart_type": "card"\s*\}',
        r'return {\n                "chart_type": "card",\n                "description": "Error retrieving operational impact data",\n                "data": {\n                    "summary": {"total_incidents": 0, "branches_impacted": 0, "locations_impacted": 0, "incident_types": 0},\n                    "impact_metrics": {"operational_disruption_rate": 0.0, "safety_risk_rate": 0.0, "overall_impact_score": 0.0},\n                    "incident_breakdown": {"work_stopped_incidents": 0, "serious_incidents": 0}\n                }\n            }',
        content
    )
    
    # Fix empty dashboard data for card types
    content = re.sub(
        r'"total_events": \{\s*"count": \{[^}]*\},\s*"description": "No data available",\s*"chart_type": "card"\s*\}',
        r'"total_events": {\n                "chart_type": "card",\n                "description": "No data available",\n                "data": {\n                    "count": {"total_events": 0, "unique_events": 0}\n                }\n            }',
        content
    )
    
    content = re.sub(
        r'"serious_near_miss_rate": \{\s*"rate": [^,]*,\s*"count": \{[^}]*\},\s*"description": "No data available",\s*"chart_type": "card"\s*\}',
        r'"serious_near_miss_rate": {\n                "chart_type": "card",\n                "description": "No data available",\n                "data": {\n                    "rate": 0.0,\n                    "count": {"serious_near_miss_count": 0, "non_serious_count": 0, "total_events": 0, "serious_near_miss_percentage": "0.0"}\n                }\n            }',
        content
    )
    
    content = re.sub(
        r'"work_stoppage_rate": \{\s*"rate": [^,]*,\s*"count": [^,]*,\s*"total": \{[^}]*\},\s*"description": "No data available",\s*"chart_type": "card"\s*\}',
        r'"work_stoppage_rate": {\n                "chart_type": "card",\n                "description": "No data available",\n                "data": {\n                    "rate": 0.0,\n                    "count": 0,\n                    "total": {"total_events": 0, "unique_events": 0}\n                }\n            }',
        content
    )
    
    content = re.sub(
        r'"response_time_analysis": \{\s*"average_response_time": "[^"]*",\s*"median_response_time": "[^"]*",\s*"events_analyzed": [^,]*,\s*"description": "No data available",\s*"chart_type": "card"\s*\}',
        r'"response_time_analysis": {\n                "chart_type": "card",\n                "description": "No data available",\n                "data": {\n                    "average_response_time": "N/A",\n                    "median_response_time": "N/A",\n                    "events_analyzed": 0\n                }\n            }',
        content
    )
    
    content = re.sub(
        r'"operational_impact_analysis": \{\s*"summary": \{[^}]*\},\s*"impact_metrics": \{[^}]*\},\s*"incident_breakdown": \{[^}]*\},\s*"description": "No data available",\s*"chart_type": "card"\s*\}',
        r'"operational_impact_analysis": {\n                "chart_type": "card",\n                "description": "No data available",\n                "data": {\n                    "summary": {"total_incidents": 0, "branches_impacted": 0, "locations_impacted": 0, "incident_types": 0},\n                    "impact_metrics": {"operational_disruption_rate": 0.0, "safety_risk_rate": 0.0, "overall_impact_score": 0.0},\n                    "incident_breakdown": {"work_stopped_incidents": 0, "serious_incidents": 0}\n                }\n            }',
        content
    )
    
    # Fix error cases for card types
    content = re.sub(
        r'return \{\s*"count": \{[^}]*\},\s*"description": "Error retrieving data"\s*\}',
        r'return {\n                "chart_type": "card",\n                "description": "Error retrieving data",\n                "data": {\n                    "count": {"total_events": 0, "unique_events": 0}\n                }\n            }',
        content
    )
    
    content = re.sub(
        r'return \{\s*"rate": [^,]*,\s*"count": \{[^}]*\},\s*"description": "Error retrieving data"\s*\}',
        r'return {\n                "chart_type": "card",\n                "description": "Error retrieving data",\n                "data": {\n                    "rate": 0.0,\n                    "count": {"serious_near_miss_count": 0, "non_serious_count": 0, "total_events": 0, "serious_near_miss_percentage": "0.0"}\n                }\n            }',
        content
    )
    
    content = re.sub(
        r'return \{\s*"rate": [^,]*,\s*"count": [^,]*,\s*"total": \{[^}]*\},\s*"description": "Error retrieving data"\s*\}',
        r'return {\n                "chart_type": "card",\n                "description": "Error retrieving data",\n                "data": {\n                    "rate": 0.0,\n                    "count": 0,\n                    "total": {"total_events": 0, "unique_events": 0}\n                }\n            }',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {file_path}")

def main():
    """Update all dashboard services"""
    dashboard_files = [
        'shindler_server/dashboard/srs_dashboard_service.py',
        'shindler_server/dashboard/srs_enriched_dashboard_service.py',
        'shindler_server/dashboard/srs_agumented_dashboard_service.py',
        'shindler_server/dashboard/ei_tech_dashboard_service.py',
        'shindler_server/dashboard/ni_tct_dashboard_service.py'
    ]
    
    for file_path in dashboard_files:
        if os.path.exists(file_path):
            fix_dashboard_format(file_path)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()

