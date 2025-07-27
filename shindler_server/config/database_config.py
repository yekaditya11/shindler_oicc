"""
Database Configuration for Shindler Server
Handles connection to PostgreSQL database for EI Tech KPIs
"""

import os
from dataclasses import dataclass
from typing import Optional, Generator
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str
    driver: str = "postgresql+psycopg2"

    @property
    def connection_string(self) -> str:
        from urllib.parse import quote_plus
        # URL encode the password to handle special characters
        encoded_password = quote_plus(self.password)
        return f"{self.driver}://{self.username}:{encoded_password}@{self.host}:{self.port}/{self.database}"

class DatabaseManager:
    """Manages database connection for PostgreSQL"""

    def __init__(self):
        self.postgres_config = DatabaseConfig(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "defaultdb"),
            username=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "")
        )

        self._postgres_engine = None

        logger.info(f"Database config initialized for PostgreSQL: {self.postgres_config.host}:{self.postgres_config.port}/{self.postgres_config.database}")

    @property
    def postgres_engine(self):
        if self._postgres_engine is None:
            try:
                self._postgres_engine = sa.create_engine(
                    self.postgres_config.connection_string,
                    pool_pre_ping=True,
                    pool_recycle=300,
                    pool_size=10,
                    max_overflow=20,
                    pool_timeout=30,
                    echo=False,
                    isolation_level="AUTOCOMMIT",
                    connect_args={
                        "connect_timeout": 10,
                        "application_name": "Shindler_EI_Tech_API",
                        "sslmode": "require"  # Required for Aiven cloud databases
                    }
                )
                logger.info("PostgreSQL database engine created successfully")
            except Exception as e:
                logger.error(f"Failed to create PostgreSQL database engine: {str(e)}")
                raise
        return self._postgres_engine

    def get_session(self) -> Session:
        """Get database session"""
        try:
            SessionLocal = sessionmaker(bind=self.postgres_engine, autoflush=False, autocommit=False)
            session = SessionLocal()
            
            # Test the connection
            result = session.execute(sa.text("SELECT 1"))
            result.fetchone()
            
            logger.info("Database session created successfully")
            return session
        except Exception as e:
            logger.error(f"Failed to create database session: {str(e)}")
            raise

    def test_connection(self):
        """Test the database connection"""
        try:
            session = self.get_session()
            result = session.execute(sa.text("SELECT 1"))
            result.fetchone()
            session.close()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False

# Global database manager instance
db_manager = DatabaseManager()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session for FastAPI
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()

def get_session() -> Session:
    """
    Get database session directly
    """
    return db_manager.get_session() 