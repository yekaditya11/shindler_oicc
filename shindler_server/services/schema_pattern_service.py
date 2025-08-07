"""
Schema Pattern Management Service
Handles storing, retrieving, and managing schema patterns in the database
"""

import logging
from typing import List, Dict, Optional, Any
from sqlalchemy import text
from config.database import get_db

logger = logging.getLogger(__name__)

class SchemaPatternService:
    """Service for managing schema patterns"""
    
    def __init__(self):
        self.db = None
    
    def get_db_connection(self):
        """Get database connection"""
        if not self.db:
            self.db = next(get_db())
        return self.db
    
    async def initialize_default_patterns(self):
        """Initialize database with patterns from config file"""
        try:
            from config.schema_patterns_configs import SCHEMA_PATTERNS
            
            db = self.get_db_connection()
            
            for schema_name, columns in SCHEMA_PATTERNS.items():
                # Check if pattern already exists
                result = db.execute(
                    text("SELECT id FROM schema_patterns WHERE schema_name = :schema_name"),
                    {"schema_name": schema_name}
                )
                
                if not result.fetchone():
                    # Insert new pattern using direct model approach
                    from models.file_processing_models import SchemaPattern

                    schema_pattern = SchemaPattern(
                        schema_name=schema_name,
                        columns=columns,  # SQLAlchemy will handle JSON conversion
                        description=f"Default {schema_name} schema pattern",
                        is_active=True
                    )

                    db.add(schema_pattern)
                    logger.info(f"Added default schema pattern: {schema_name}")
            
            db.commit()
            logger.info("Default schema patterns initialized")
            
        except Exception as e:
            logger.error(f"Error initializing default patterns: {e}")
            if self.db:
                self.db.rollback()
            raise
    
    async def get_all_patterns(self) -> Dict[str, List[str]]:
        """Get all active schema patterns"""
        try:
            db = self.get_db_connection()
            
            result = db.execute(
                text("SELECT schema_name, columns FROM schema_patterns WHERE is_active = TRUE")
            )
            
            patterns = {}
            for row in result:
                try:
                    # Parse columns from JSON string
                    import json
                    if isinstance(row.columns, str):
                        columns = json.loads(row.columns.replace("'", '"'))  # Handle single quotes
                    else:
                        columns = row.columns
                    patterns[row.schema_name] = columns
                except Exception as e:
                    logger.warning(f"Error parsing columns for {row.schema_name}: {e}")
                    # Fallback: try to parse as Python list string
                    try:
                        columns = eval(row.columns) if isinstance(row.columns, str) else row.columns
                        patterns[row.schema_name] = columns
                    except:
                        logger.error(f"Could not parse columns for {row.schema_name}")
                        continue
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error getting schema patterns: {e}")
            return {}
    
    async def add_pattern(self, schema_name: str, columns: List[str], description: str = "") -> bool:
        """Add a new schema pattern"""
        try:
            db = self.get_db_connection()
            
            # Check if pattern already exists
            result = db.execute(
                text("SELECT id FROM schema_patterns WHERE schema_name = :schema_name"),
                {"schema_name": schema_name}
            )
            
            if result.fetchone():
                logger.warning(f"Schema pattern {schema_name} already exists")
                return False
            
            # Insert new pattern using model approach
            from models.file_processing_models import SchemaPattern

            schema_pattern = SchemaPattern(
                schema_name=schema_name,
                columns=columns,  # SQLAlchemy will handle JSON conversion
                description=description or f"User-defined {schema_name} schema pattern",
                is_active=True
            )

            db.add(schema_pattern)
            
            db.commit()
            logger.info(f"Added new schema pattern: {schema_name} with {len(columns)} columns")
            return True
            
        except Exception as e:
            logger.error(f"Error adding schema pattern {schema_name}: {e}")
            if self.db:
                self.db.rollback()
            return False
    
    async def update_pattern(self, schema_name: str, columns: List[str], description: str = "") -> bool:
        """Update an existing schema pattern"""
        try:
            db = self.get_db_connection()
            
            import json
            result = db.execute(
                text("""
                    UPDATE schema_patterns
                    SET columns = :columns::json, description = :description, updated_at = NOW()
                    WHERE schema_name = :schema_name
                """),
                {
                    "schema_name": schema_name,
                    "columns": json.dumps(columns),
                    "description": description
                }
            )
            
            if result.rowcount > 0:
                db.commit()
                logger.info(f"Updated schema pattern: {schema_name}")
                return True
            else:
                logger.warning(f"Schema pattern {schema_name} not found for update")
                return False
                
        except Exception as e:
            logger.error(f"Error updating schema pattern {schema_name}: {e}")
            if self.db:
                self.db.rollback()
            return False
    
    async def delete_pattern(self, schema_name: str) -> bool:
        """Deactivate a schema pattern"""
        try:
            db = self.get_db_connection()
            
            result = db.execute(
                text("""
                    UPDATE schema_patterns 
                    SET is_active = FALSE, updated_at = NOW()
                    WHERE schema_name = :schema_name
                """),
                {"schema_name": schema_name}
            )
            
            if result.rowcount > 0:
                db.commit()
                logger.info(f"Deactivated schema pattern: {schema_name}")
                return True
            else:
                logger.warning(f"Schema pattern {schema_name} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting schema pattern {schema_name}: {e}")
            if self.db:
                self.db.rollback()
            return False
    
    async def get_pattern_details(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific schema pattern"""
        try:
            db = self.get_db_connection()
            
            result = db.execute(
                text("""
                    SELECT schema_name, columns, description, created_at, updated_at
                    FROM schema_patterns 
                    WHERE schema_name = :schema_name AND is_active = TRUE
                """),
                {"schema_name": schema_name}
            )
            
            row = result.fetchone()
            if row:
                import json
                try:
                    columns = json.loads(row.columns) if isinstance(row.columns, str) else row.columns
                except:
                    columns = eval(row.columns) if isinstance(row.columns, str) else row.columns
                
                return {
                    "schema_name": row.schema_name,
                    "columns": columns,
                    "description": row.description,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting pattern details for {schema_name}: {e}")
            return None

# Global instance
schema_pattern_service = SchemaPatternService()
