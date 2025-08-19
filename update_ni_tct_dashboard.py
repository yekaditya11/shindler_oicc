#!/usr/bin/env python3
"""
Script to update NI TCT dashboard service to include chart_type in all responses
"""

import re

def update_ni_tct_dashboard():
    """Update NI TCT dashboard service to include chart_type in all KPI responses"""
    
    with open('shindler_server/dashboard/ni_tct_dashboard_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update monthly trends
    content = re.sub(
        r'return self\.execute_query\(query, params, session\)\n\n        except Exception as e:\n            logger\.error\(f"Error getting monthly trends: {e}"\)\n            return \[\]',
        r'data = self.execute_query(query, params, session)\n            return {\n                "data": data,\n                "description": "Monthly trends of unsafe events",\n                "chart_type": "line"\n            }\n\n        except Exception as e:\n            logger.error(f"Error getting monthly trends: {e}")\n            return {"data": [], "description": "Error retrieving data", "chart_type": "line"}',
        content
    )
    
    # Update branch performance analysis
    content = re.sub(
        r'return self\.execute_query\(query, params, session\)\n\n        except Exception as e:\n            logger\.error\(f"Error getting branch performance analysis: {e}"\)\n            return \[\]',
        r'data = self.execute_query(query, params, session)\n            return {\n                "data": data,\n                "description": "Branch performance analysis",\n                "chart_type": "bar"\n            }\n\n        except Exception as e:\n            logger.error(f"Error getting branch performance analysis: {e}")\n            return {"data": [], "description": "Error retrieving data", "chart_type": "bar"}',
        content
    )
    
    # Update event type distribution
    content = re.sub(
        r'return self\.execute_query\(query, params, session\)\n        except Exception as e:\n            logger\.error\(f"Error getting event type distribution: {e}"\)\n            return \[\]',
        r'data = self.execute_query(query, params, session)\n            return {\n                "data": data,\n                "description": "Distribution of unsafe event types",\n                "chart_type": "pie"\n            }\n        except Exception as e:\n            logger.error(f"Error getting event type distribution: {e}")\n            return {"data": [], "description": "Error retrieving data", "chart_type": "pie"}',
        content
    )
    
    # Update repeat locations
    content = re.sub(
        r'return self\.execute_query\(query, params, session\)\n        except Exception as e:\n            logger\.error\(f"Error getting repeat locations: {e}"\)\n            return \[\]',
        r'data = self.execute_query(query, params, session)\n            return {\n                "data": data,\n                "description": "Repeat incident locations",\n                "chart_type": "bar"\n            }\n        except Exception as e:\n            logger.error(f"Error getting repeat locations: {e}")\n            return {"data": [], "description": "Error retrieving data", "chart_type": "bar"}',
        content
    )
    
    # Update response time analysis
    content = re.sub(
        r'("description": "[^"]*")\s*}',
        r'\1,\n                "chart_type": "card"\n            }',
        content
    )
    
    # Update safety performance trends
    content = re.sub(
        r'return self\.execute_query\(query, params, session\)\n        except Exception as e:\n            logger\.error\(f"Error getting safety performance trends: {e}"\)\n            return \[\]',
        r'data = self.execute_query(query, params, session)\n            return {\n                "data": data,\n                "description": "Safety performance trends by quarter",\n                "chart_type": "line"\n            }\n        except Exception as e:\n            logger.error(f"Error getting safety performance trends: {e}")\n            return {"data": [], "description": "Error retrieving data", "chart_type": "line"}',
        content
    )
    
    # Update incident severity distribution
    content = re.sub(
        r'if total_count > 0:\n                    return \[{.*?}\]\n                else:\n                    return \[\]\n\n            return result\n        except Exception as e:\n            logger\.error\(f"Error getting incident severity distribution: {e}"\)\n            return \[\]',
        r'if total_count > 0:\n                    data = [{\'severity_level\': \'Low\', \'incident_count\': total_count, \'percentage\': 100.0, \'sort_order\': 4}]\n                else:\n                    data = []\n            else:\n                data = result\n            return {\n                "data": data,\n                "description": "Distribution of incidents by severity level",\n                "chart_type": "pie"\n            }\n        except Exception as e:\n            logger.error(f"Error getting incident severity distribution: {e}")\n            return {"data": [], "description": "Error retrieving data", "chart_type": "pie"}',
        content,
        flags=re.DOTALL
    )
    
    # Update operational impact analysis
    content = re.sub(
        r'("description": "[^"]*")\s*}',
        r'\1,\n                "chart_type": "card"\n            }',
        content
    )
    
    # Update time-based analysis
    content = re.sub(
        r'("has_hourly_data": False)\s*}',
        r'\1\n                },\n                "chart_type": "bar"\n            }',
        content
    )
    
    # Update empty dashboard data
    content = re.sub(
        r'("description": "No data available")\s*}',
        r'\1,\n                "chart_type": "card"\n            }',
        content
    )
    
    # Update empty data arrays
    content = re.sub(
        r'"monthly_trends": \[\],',
        r'"monthly_trends": {"data": [], "description": "No data available", "chart_type": "line"},',
        content
    )
    content = re.sub(
        r'"branch_performance_analysis": \[\],',
        r'"branch_performance_analysis": {"data": [], "description": "No data available", "chart_type": "bar"},',
        content
    )
    content = re.sub(
        r'"event_type_distribution": \[\],',
        r'"event_type_distribution": {"data": [], "description": "No data available", "chart_type": "pie"},',
        content
    )
    content = re.sub(
        r'"repeat_locations": \[\],',
        r'"repeat_locations": {"data": [], "description": "No data available", "chart_type": "bar"},',
        content
    )
    content = re.sub(
        r'"safety_performance_trends": \[\],',
        r'"safety_performance_trends": {"data": [], "description": "No data available", "chart_type": "line"},',
        content
    )
    content = re.sub(
        r'"incident_severity_distribution": \[\],',
        r'"incident_severity_distribution": {"data": [], "description": "No data available", "chart_type": "pie"},',
        content
    )
    
    with open('shindler_server/dashboard/ni_tct_dashboard_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Updated NI TCT dashboard service")

if __name__ == "__main__":
    update_ni_tct_dashboard()

