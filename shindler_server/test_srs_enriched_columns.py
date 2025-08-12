#!/usr/bin/env python3
"""
Test script to verify column names in SRS enriched table
"""

import sys
import os
from sqlalchemy import text

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database_config import db_manager

def test_column_names():
    """Test if the column names exist in the table"""
    
    # Test queries for different column names
    test_queries = [
        "SELECT COUNT(*) FROM unsafe_events_srs_enriched LIMIT 1",
        "SELECT COUNT(*) FROM unsafe_events_srs_enriched WHERE \"comments/remarks\" IS NOT NULL LIMIT 1",
        "SELECT COUNT(*) FROM unsafe_events_srs_enriched WHERE comments_remarks IS NOT NULL LIMIT 1",
        "SELECT COUNT(*) FROM unsafe_events_srs_enriched WHERE action_description_1 IS NOT NULL LIMIT 1",
        "SELECT COUNT(*) FROM unsafe_events_srs_enriched WHERE unsafe_act IS NOT NULL LIMIT 1",
        "SELECT COUNT(*) FROM unsafe_events_srs_enriched WHERE unsafe_condition IS NOT NULL LIMIT 1"
    ]
    
    session = db_manager.get_session()
    try:
        for i, query in enumerate(test_queries):
            try:
                result = session.execute(text(query))
                count = result.fetchone()[0]
                print(f"Query {i+1} SUCCESS: {count} rows")
            except Exception as e:
                print(f"Query {i+1} FAILED: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    test_column_names()

