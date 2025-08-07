#!/usr/bin/env python3
"""
Simple database initialization script for file processing models
"""

import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import models directly
from models.file_processing_models import Base

def create_database_engine():
    """Create database engine from environment variables"""
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "defaultdb")
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "")
    
    # Construct database URL
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    print(f"Connecting to database: {db_host}:{db_port}/{db_name}")
    
    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=True  # Enable SQL logging for debugging
    )

def initialize_database():
    """Initialize database tables for file processing"""
    try:
        print("Starting database initialization...")
        
        # Create engine
        engine = create_database_engine()
        
        # Test connection
        with engine.connect() as conn:
            print("✅ Database connection successful!")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # List created tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Available tables: {tables}")
        
        # Check if our specific tables exist
        required_tables = [
            'file_upload_sessions',
            'file_processing_logs', 
            'schema_templates',
            'tagged_files'
        ]
        
        for table in required_tables:
            if table in tables:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' missing")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise

def main():
    """Main function to run database initialization"""
    try:
        initialize_database()
        print("\n🎉 Database initialization completed successfully!")
    except Exception as e:
        print(f"\n💥 Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 