#!/usr/bin/env python3
"""
Script to create only the unsafe_events_srs_agumented table
"""

import os
import sys
import sqlalchemy as sa
from sqlalchemy import text
import logging
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import database configuration
from config.database_config import db_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_table():
    """Create the unsafe_events_srs_agumented table"""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS unsafe_events_srs_agumented (
        event_id VARCHAR(50) PRIMARY KEY,
        reporter_name VARCHAR(255),
        reported_date DATE,
        reporter_id INTEGER,
        date_of_unsafe_event DATE,
        time_of_unsafe_event TIME,
        unsafe_event_type VARCHAR(255),
        business_details VARCHAR(255),
        site_reference VARCHAR(500),
        unsafe_event_location VARCHAR(255),
        product_type VARCHAR(255),
        employee_id INTEGER,
        employee_name VARCHAR(255),
        employee_age INTEGER,
        job_role VARCHAR(255),
        subcontractor_company_name VARCHAR(255),
        subcontractorid INTEGER,
        subcontractor_city VARCHAR(255),
        subcontractor_name VARCHAR(255),
        kg_name VARCHAR(10),
        country_name VARCHAR(100),
        division VARCHAR(255),
        department VARCHAR(255),
        city VARCHAR(255),
        sub_area NUMERIC,
        district VARCHAR(255),
        zone VARCHAR(255),
        serious_near_miss VARCHAR(10),
        unsafe_act TEXT,
        unsafe_act_other TEXT,
        unsafe_condition TEXT,
        unsafe_condition_other TEXT,
        work_stopped VARCHAR(10),
        stop_work_nogo_violation VARCHAR(10),
        nogo_violation_detail TEXT,
        stop_work_duration VARCHAR(255),
        other_safety_issues TEXT,
        comments_remarks TEXT,
        event_requires_sanction VARCHAR(10),
        action_description_1 TEXT,
        branch VARCHAR(255),
        region VARCHAR(255),
        gender VARCHAR(10),
        joining_date DATE,
        last_training_attended VARCHAR(255),
        training_expiry_date DATE,
        training_scores INTEGER,
        shift_timings VARCHAR(50),
        total_hours_worked_in_previous_week INTEGER,
        overtime_hours INTEGER,
        years_of_experience INTEGER,
        last_maintenance_date VARCHAR(50),
        investigation_closure_date DATE,
        audit_date DATE,
        audit_frequency INTEGER,
        weather_condition VARCHAR(50)
    );
    """
    
    try:
        engine = db_manager.postgres_engine
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
            logger.info("Table unsafe_events_srs_agumented created successfully")
            return True
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        return False

def verify_table_exists():
    """Verify that the table was created successfully"""
    
    try:
        engine = db_manager.postgres_engine
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'unsafe_events_srs_agumented'
                );
            """))
            table_exists = result.fetchone()[0]
            
            if table_exists:
                logger.info("Table unsafe_events_srs_agumented exists successfully")
                
                # Get column information
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'unsafe_events_srs_agumented'
                    ORDER BY ordinal_position;
                """))
                columns = result.fetchall()
                
                logger.info("Table columns:")
                for col in columns:
                    logger.info(f"  {col[0]}: {col[1]}")
                
                return True
            else:
                logger.error("Table was not created successfully")
                return False
                
    except Exception as e:
        logger.error(f"Error verifying table: {e}")
        return False

def main():
    """Main function to create table"""
    
    # Test database connection
    logger.info("Testing database connection...")
    if not db_manager.test_connection():
        logger.error("Database connection failed")
        return False
    
    # Create table
    logger.info("Creating table...")
    if not create_table():
        logger.error("Failed to create table")
        return False
    
    # Verify table
    logger.info("Verifying table creation...")
    if not verify_table_exists():
        logger.error("Table verification failed")
        return False
    
    logger.info("Table creation completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
