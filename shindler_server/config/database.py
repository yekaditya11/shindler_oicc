"""
Database configuration and connection management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging

logger = logging.getLogger(__name__)

# Base class for models
Base = declarative_base()

# Global variables for engine and session
_engine = None
_SessionLocal = None

def get_engine():
    """Get or create database engine"""
    global _engine
    if _engine is None:
        from src.config.settings import settings
        logger.info(f"Creating database engine for: {settings.db_host}:{settings.db_port}/{settings.db_name}")
        _engine = create_engine(
            settings.database_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
            echo=settings.debug
        )
    return _engine

def get_session_local():
    """Get or create session factory"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

# For backward compatibility - these will be accessed directly
# but will create the engine/session dynamically when first accessed
class LazyEngine:
    def __getattr__(self, name):
        engine = get_engine()
        return getattr(engine, name)

    def __call__(self, *args, **kwargs):
        engine = get_engine()
        return engine(*args, **kwargs)

class LazySessionLocal:
    def __getattr__(self, name):
        session_local = get_session_local()
        return getattr(session_local, name)

    def __call__(self, *args, **kwargs):
        session_local = get_session_local()
        return session_local(*args, **kwargs)

engine = LazyEngine()
SessionLocal = LazySessionLocal()

def reset_database_connection():
    """Reset database connection - useful when settings change"""
    global _engine, _SessionLocal
    if _engine:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
    logger.info("Database connection reset")

async def init_db():
    """Initialize database tables"""
    try:
        # Import all models to register them
        from src.models import unsafe_event_models, base_models, upload_data_versioning

        # Use the models to ensure they're registered (suppress unused warnings)
        _ = unsafe_event_models, base_models, upload_data_versioning

        # Create all tables using the dynamic engine
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def get_db():
    """Get database session"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


