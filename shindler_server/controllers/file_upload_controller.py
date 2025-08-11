
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

def update_file_id(uploaded_file_name, new_file_id, file_type):
    """Update file_id and file_type for an existing record based on uploaded_file_name"""
    
    update_sql = """
    UPDATE file_ids_table 
    SET file_id = :new_file_id, file_type = :file_type
    WHERE uploaded_file_name = :uploaded_file_name;
    """
    
    try:
        engine = db_manager.postgres_engine
        with engine.connect() as conn:
            result = conn.execute(text(update_sql), {
                'uploaded_file_name': uploaded_file_name,
                'new_file_id': new_file_id,
                'file_type': file_type
            })
            
            conn.commit()
            
            # Check if any rows were affected
            if result.rowcount > 0:
                logger.info(f"Successfully updated record: {uploaded_file_name} -> file_id: {new_file_id}, file_type: {file_type}")
                return True
            else:
                logger.warning(f"No record found with uploaded_file_name: {uploaded_file_name}")
                return False
                
    except Exception as e:
        logger.error(f"Error updating data: {e}")
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


def add_tab(tab_name: str):
    """Add a new tab to the file_ids_table and return the id and uploaded_file_name"""
    
    insert_sql = """
    INSERT INTO file_ids_table (uploaded_file_name)
    VALUES (:uploaded_file_name)
    RETURNING id, uploaded_file_name;
    """
    try:
        engine = db_manager.postgres_engine
        with engine.connect() as conn:
            result = conn.execute(text(insert_sql), {
                'uploaded_file_name': tab_name
            })
            row = result.fetchone()
            conn.commit()
            
            if row:
                returned_data = {
                    'id': row[0],
                    'uploaded_file_name': row[1]
                }
                logger.info(f"Successfully added tab: {tab_name} with ID: {row[0]}")
                return returned_data
            else:
                logger.error("No row returned after insert")
                return None
                
    except Exception as e:
        logger.error(f"Error adding tab: {e}")
        return None
    

def delete_tab(tab_id: int):
    """Delete a tab from the file_ids_table by id and return the deleted row data"""
    
    delete_sql = """
    DELETE FROM file_ids_table 
    WHERE id = :tab_id
    RETURNING id, uploaded_file_name;
    """
    
    try:
        engine = db_manager.postgres_engine
        with engine.connect() as conn:
            result = conn.execute(text(delete_sql), {
                'tab_id': tab_id
            })
            row = result.fetchone()
            conn.commit()
            
            if row:
                deleted_data = {
                    'id': row[0],
                    'uploaded_file_name': row[1]
                }
                logger.info(f"Successfully deleted tab with ID: {tab_id}, name: {row[1]}")
                return deleted_data
            else:
                logger.warning(f"No tab found with ID: {tab_id}")
                return None
                
    except Exception as e:
        logger.error(f"Error deleting tab with ID {tab_id}: {e}")
        return None



