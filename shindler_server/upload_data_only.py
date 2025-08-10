#!/usr/bin/env python3
"""
Script to upload data from Excel file to existing unsafe_events_srs_agumented table
"""

import os
import sys
import pandas as pd
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
        
        logger.info(f"Excel file contains {len(df)} rows and {len(df.columns)} columns")
        logger.info(f"Columns: {list(df.columns)}")
        
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
            
            # Check column count
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'unsafe_events_srs_agumented'
            """))
            column_count = result.fetchone()[0]
            logger.info(f"Total columns in table: {column_count}")
            
            return True
            
    except Exception as e:
        logger.error(f"Error verifying data: {e}")
        return False

def main():
    """Main function to upload data"""
    
    # Excel file path - update this to your actual file path
    excel_file_path = "srs_agumented.xlsx"
    
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
    
    # Check if table exists
    try:
        engine = db_manager.postgres_engine
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'unsafe_events_srs_agumented'
                );
            """))
            table_exists = result.fetchone()[0]
            
            if not table_exists:
                logger.error("Table unsafe_events_srs_agumented does not exist")
                logger.info("Please run create_table_only.py first to create the table")
                return False
    except Exception as e:
        logger.error(f"Error checking table existence: {e}")
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
    
    logger.info("Data upload completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
