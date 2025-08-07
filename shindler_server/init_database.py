#!/usr/bin/env python3
"""
Database initialization script for file processing models
"""

import asyncio
import logging
from sqlalchemy import inspect
from config.database import init_db, get_engine
from models.file_processing_models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def initialize_database():
    """Initialize database tables for file processing"""
    try:
        logger.info("Starting database initialization...")
        
        # Get the engine
        engine = get_engine()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully!")
        
        # List created tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Available tables: {tables}")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def main():
    """Main function to run database initialization"""
    try:
        asyncio.run(initialize_database())
        print("✅ Database initialization completed successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        exit(1)

if __name__ == "__main__":
    main() 