#!/usr/bin/env python3
"""
Script to create unsafe_events_srs_agumented table and upload data from Excel file
"""

import os
import sys
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import text
from datetime import datetime
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

def clean_dataframe(df):
    """Clean and prepare the dataframe for database insertion"""
    
    # Convert date columns
    date_columns = [
        'reported_date', 'date_of_unsafe_event', 'joining_date', 
        'training_expiry_date', 'investigation_closure_date', 'audit_date'
    ]
    
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Convert time column
    if 'time_of_unsafe_event' in df.columns:
        df['time_of_unsafe_event'] = pd.to_datetime(df['time_of_unsafe_event'], format='%H:%M:%S', errors='coerce').dt.time
    
    # Convert numeric columns
    numeric_columns = [
        'reporter_id', 'employee_id', 'employee_age', 'subcontractorid',
        'training_scores', 'total_hours_worked_in_previous_week', 
        'overtime_hours', 'years_of_experience', 'audit_frequency'
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Handle NaN values
    df = df.fillna('')
    
    return df

def upload_excel_data(excel_file_path):
    """Upload data from Excel file to the database table"""
    
    try:
        # Read Excel file
        logger.info(f"Reading Excel file: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        
        # Clean the dataframe
        df = clean_dataframe(df)
        
        # Get database engine
        engine = db_manager.postgres_engine
        
        # Upload data to database
        logger.info("Uploading data to database...")
        df.to_sql(
            'unsafe_events_srs_agumented', 
            engine, 
            if_exists='replace',  # Replace existing data
            index=False,
            method='multi',  # Use multi-row insert for better performance
            chunksize=1000  # Process in chunks
        )
        
        logger.info(f"Successfully uploaded {len(df)} rows to unsafe_events_srs_agumented table")
        return True
        
    except Exception as e:
        logger.error(f"Error uploading data: {e}")
        return False

def verify_data():
    """Verify that data was uploaded correctly"""
    
    try:
        engine = db_manager.postgres_engine
        with engine.connect() as conn:
            # Check row count
            result = conn.execute(text("SELECT COUNT(*) FROM unsafe_events_srs_agumented"))
            row_count = result.fetchone()[0]
            logger.info(f"Total rows in table: {row_count}")
            
            # Check sample data
            result = conn.execute(text("SELECT event_id, reporter_name, reported_date FROM unsafe_events_srs_agumented LIMIT 5"))
            sample_data = result.fetchall()
            logger.info("Sample data:")
            for row in sample_data:
                logger.info(f"  {row}")
            
            return True
            
    except Exception as e:
        logger.error(f"Error verifying data: {e}")
        return False

def main():
    """Main function to create table and upload data"""
    
    # Excel file path - update this to your actual file path
    excel_file_path = "sanitize_SRS - Augmented (Employee Details)[39] 1.xlsx"
    
    # Check if Excel file exists
    if not os.path.exists(excel_file_path):
        logger.error(f"Excel file not found: {excel_file_path}")
        logger.info("Please place the srs_agumented.xlsx file in the same directory as this script")
        return False
    
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
    
    # Upload data
    logger.info("Uploading data from Excel file...")
    if not upload_excel_data(excel_file_path):
        logger.error("Failed to upload data")
        return False
    
    # Verify data
    logger.info("Verifying uploaded data...")
    if not verify_data():
        logger.error("Data verification failed")
        return False
    
    logger.info("Table creation and data upload completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
