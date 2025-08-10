
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Import database configuration
from config.database_config import db_manager

def insert_file_data(uploaded_file_name, file_id):
    """Insert a single record into file_ids_table"""
    
    insert_sql = """
    INSERT INTO file_ids_table (uploaded_file_name, file_id)
    VALUES (:uploaded_file_name, :file_id)
    ON CONFLICT (uploaded_file_name) 
    DO UPDATE SET file_id = EXCLUDED.file_id;
    """
    
    try:
        engine = db_manager.postgres_engine
        with engine.connect() as conn:
            conn.execute(text(insert_sql), {
                'uploaded_file_name': uploaded_file_name,
                'file_id': file_id
            })
            conn.commit()
            logger.info(f"Successfully inserted/updated record: {uploaded_file_name} -> {file_id}")
            return True
    except Exception as e:
        logger.error(f"Error inserting data: {e}")
        return False
    

def get_all_files():
    """Retrieve all records from file_ids_table"""
    
    select_sql = "SELECT uploaded_file_name, file_id FROM file_ids_table ORDER BY uploaded_file_name;"
    
    try:
        engine = db_manager.postgres_engine
        with engine.connect() as conn:
            result = conn.execute(text(select_sql))
            rows = result.fetchall()
            print(rows)
            return [{'uploaded_file_name': row[0], 'file_id': row[1]} for row in rows]
        
    except Exception as e:
        logger.error(f"Error retrieving all files: {e}")
        return []