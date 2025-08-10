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
    """Create the file_ids_table"""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS file_ids_table (
        uploaded_file_name VARCHAR(225) PRIMARY KEY,
        file_id INTEGER
       
    );
    """
    
    try:
        engine = db_manager.postgres_engine
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
            logger.info("Table file_ids_table created successfully")
            return True
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        return False
    

create_table()