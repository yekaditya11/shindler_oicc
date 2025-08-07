#!/usr/bin/env python3
"""
Migration script to add user_tags column to file_upload_sessions table
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
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    database = os.getenv('DB_NAME', 'shindler_db')
    username = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'password')

    return f"postgresql://{username}:{password}@{host}:{port}/{database}"

def migrate_add_user_tags():
    """Add user_tags column to file_upload_sessions table"""
    try:
        logger.info("Starting migration to add user_tags column...")

        db_url = get_database_url()
        engine = create_engine(db_url)

        with engine.connect() as connection:
            # Check if column already exists
            result = connection.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'file_upload_sessions'
                AND column_name = 'user_tags'
            """))

            if result.fetchone():
                logger.info("user_tags column already exists, skipping migration")
                return

            # Add the user_tags column
            connection.execute(text("""
                ALTER TABLE file_upload_sessions
                ADD COLUMN user_tags JSON
            """))

            connection.commit()
            logger.info("Successfully added user_tags column to file_upload_sessions table")

    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise

def main():
    """Main function to run migration"""
    try:
        migrate_add_user_tags()
        print("✅ Migration completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("Note: Make sure your database is running and connection details are correct")
        print("You can set DATABASE_URL environment variable or update the default connection in the script")
        exit(1)

if __name__ == "__main__":
    main()
