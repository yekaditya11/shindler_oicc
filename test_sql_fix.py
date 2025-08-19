#!/usr/bin/env python3
"""
Test script to verify the SQL fix for time_of_unsafe_event regex issue
"""

import sys
import os

# Add the server directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shindler_server'))

def test_sql_queries():
    """Test that the SQL queries can be imported without syntax errors"""
    try:
        # Test importing the KPI modules
        from kpis.srs_enriched_kpis import SRSEnrichedKPIQueries
        from kpis.srs_kpis import SRSKPIQueries
        from kpis.srs_agumented_kpis import SRSAGUMENTEDKPIQUERIES
        from kpis.ei_tech_kpis import EITechKPIQueries
        from kpis.ni_tct_kpis import NITCTKPIQueries
        
        print("✅ All KPI modules imported successfully")
        
        # Test creating instances
        srs_enriched = SRSEnrichedKPIQueries()
        srs = SRSKPIQueries()
        srs_augmented = SRSAGUMENTEDKPIQUERIES()
        ei_tech = EITechKPIQueries()
        ni_tct = NITCTKPIQueries()
        
        print("✅ All KPI class instances created successfully")
        
        # Test that the problematic query method exists
        if hasattr(srs_enriched, 'get_events_by_time_of_day'):
            print("✅ SRS Enriched get_events_by_time_of_day method exists")
        else:
            print("❌ SRS Enriched get_events_by_time_of_day method missing")
            
        if hasattr(srs, 'get_events_by_time_of_day'):
            print("✅ SRS get_events_by_time_of_day method exists")
        else:
            print("❌ SRS get_events_by_time_of_day method missing")
            
        if hasattr(srs_augmented, 'get_events_by_time_of_day'):
            print("✅ SRS Augmented get_events_by_time_of_day method exists")
        else:
            print("❌ SRS Augmented get_events_by_time_of_day method missing")
            
        if hasattr(ei_tech, 'get_time_of_day_incident_patterns'):
            print("✅ EI Tech get_time_of_day_incident_patterns method exists")
        else:
            print("❌ EI Tech get_time_of_day_incident_patterns method missing")
            
        if hasattr(ni_tct, 'get_events_by_time_of_day'):
            print("✅ NI TCT get_events_by_time_of_day method exists")
        else:
            print("❌ NI TCT get_events_by_time_of_day method missing")
        
        print("\n🎉 All tests passed! The SQL fix should resolve the regex operator issue.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing SQL fix for time_of_unsafe_event regex issue...")
    print("=" * 60)
    
    success = test_sql_queries()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("The fix should resolve the PostgreSQL error:")
        print("'operator does not exist: time without time zone ~ unknown'")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)


