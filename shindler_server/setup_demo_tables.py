#!/usr/bin/env python3
"""
Setup demo tables using the same database connection as the running application
"""

import sys
import os
import logging

# Add the current directory to Python path so we can import from the app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_demo_tables():
    """Setup demo tables using the application's database connection"""
    try:
        logger.info("Setting up demo tables...")
        
        # Import after adding to path
        from config.database import get_engine
        from sqlalchemy import text
        
        engine = get_engine()
        
        with engine.connect() as connection:
            logger.info("Connected to database successfully")

            # Define table creation statements
            table_statements = [
                """
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
                """,
                """
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
                """,
                """
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
                """,
                """
                CREATE TABLE IF NOT EXISTS schema_patterns (
                    id SERIAL PRIMARY KEY,
                    schema_name VARCHAR(100) NOT NULL UNIQUE,
                    columns JSON NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
                """
            ]

            # Execute each table creation statement separately
            for i, statement in enumerate(table_statements):
                try:
                    logger.info(f"Creating table {i+1}/{len(table_statements)}")
                    connection.execute(text(statement))
                    connection.commit()
                    logger.info(f"✅ Table {i+1} created successfully")
                except Exception as e:
                    logger.error(f"❌ Failed to create table {i+1}: {e}")
                    connection.rollback()

            logger.info("Finished creating all demo tables!")
            
            # Verify tables exist
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('file_upload_sessions', 'file_processing_logs', 'tagged_files', 'schema_templates')
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            logger.info(f"Verified tables exist: {tables}")
            
            if len(tables) == 4:
                logger.info("✅ All demo tables created successfully!")
                return True
            else:
                logger.error(f"❌ Expected 4 tables, found {len(tables)}")
                return False
            
    except Exception as e:
        logger.error(f"Error setting up demo tables: {e}")
        return False

def main():
    """Main function"""
    try:
        success = setup_demo_tables()
        if success:
            print("✅ Demo tables setup completed successfully!")
            print("You can now use the file processing APIs.")
        else:
            print("❌ Demo tables setup failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
