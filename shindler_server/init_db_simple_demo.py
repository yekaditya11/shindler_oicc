#!/usr/bin/env python3
"""
Simple database initialization script for demo file processing models
"""

import logging
import os
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment or use default"""
    # Try to get from environment first
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url
    
    # Default PostgreSQL connection (adjust as needed)
    host = os.getenv('DB_HOST', 'schindler-safetyconnect.ccgjylc7uxqb.us-east-1.rds.amazonaws.com')
    port = os.getenv('DB_PORT', '5432')
    database = os.getenv('DB_NAME', 'postgres')
    username = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'password')
    
    return f"postgresql://{username}:{password}@{host}:{port}/{database}"

def create_demo_tables():
    """Create the required tables for demo file processing"""
    try:
        logger.info("Starting database table creation...")
        
        db_url = get_database_url()
        engine = create_engine(db_url)
        
        with engine.connect() as connection:
            # Create file_upload_sessions table
            logger.info("Creating file_upload_sessions table...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS file_upload_sessions (
                    id SERIAL PRIMARY KEY,
                    file_id VARCHAR(100) NOT NULL UNIQUE,
                    filename VARCHAR(255) NOT NULL,
                    s3_key VARCHAR(500) NOT NULL,
                    presigned_url VARCHAR(1000),
                    upload_status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    file_size INTEGER,
                    content_type VARCHAR(100),
                    user_tags JSON,
                    expires_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            
            # Create file_processing_logs table
            logger.info("Creating file_processing_logs table...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS file_processing_logs (
                    id SERIAL PRIMARY KEY,
                    file_id VARCHAR(100) NOT NULL UNIQUE,
                    filename VARCHAR(255) NOT NULL,
                    s3_key VARCHAR(500),
                    file_size INTEGER NOT NULL,
                    file_type VARCHAR(50) NOT NULL,
                    detected_schema JSON,
                    assigned_tags JSON,
                    confidence_score INTEGER,
                    processing_status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    error_message TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            
            # Create tagged_files table
            logger.info("Creating tagged_files table...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS tagged_files (
                    id SERIAL PRIMARY KEY,
                    file_id VARCHAR(100) NOT NULL UNIQUE,
                    s3_key VARCHAR(500) NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    file_type VARCHAR(50) NOT NULL,
                    user_tags JSON NOT NULL,
                    schema_hash VARCHAR(64),
                    schema_structure JSON,
                    sample_data JSON,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            
            # Create schema_templates table
            logger.info("Creating schema_templates table...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_templates (
                    id SERIAL PRIMARY KEY,
                    template_name VARCHAR(100) NOT NULL,
                    file_type VARCHAR(50) NOT NULL,
                    schema_structure JSON NOT NULL,
                    required_columns JSON,
                    optional_columns JSON,
                    confidence_threshold INTEGER DEFAULT 80,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE,
                    UNIQUE(template_name, file_type)
                )
            """))
            
            connection.commit()
            logger.info("Successfully created all demo tables!")
            
            # List created tables
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('file_upload_sessions', 'file_processing_logs', 'tagged_files', 'schema_templates')
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            logger.info(f"Created tables: {tables}")
            
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

def main():
    """Main function to run database initialization"""
    try:
        create_demo_tables()
        print("✅ Demo database tables created successfully!")
        print("You can now use the file processing APIs.")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("Please check your database connection settings.")
        exit(1)

if __name__ == "__main__":
    main()
