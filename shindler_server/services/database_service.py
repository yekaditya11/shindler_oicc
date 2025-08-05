"""
Database service for data ingestion and management
"""

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Tuple, Dict, Any
import logging
from datetime import datetime
from sqlalchemy import extract


from config.database import get_db
from models.unsafe_event_models import UnsafeEventEITech, UnsafeEventSRS, UnsafeEventNITCT, UnsafeEventNITCTAugmented
from models.upload_data_versioning import VersionByMonth
from models.base_models import UploadLog

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database operations for unsafe event data"""
    
    # Model mapping
    MODEL_MAPPING = {
        "ei_tech": UnsafeEventEITech,
        "srs": UnsafeEventSRS,
        "ni_tct": UnsafeEventNITCT,
        "ni_tct_augmented": UnsafeEventNITCTAugmented
    }
    
    def __init__(self):
        self._session = None

    def get_session(self):
        """
        Get a database session

        Returns:
            SQLAlchemy Session object
        """
        return next(get_db())

    def query(self, *entities, **kwargs):
        """
        Create a query using a new session

        Args:
            *entities: Model classes or columns to query
            **kwargs: Additional query parameters

        Returns:
            SQLAlchemy Query object
        """
        session = self.get_session()
        return session.query(*entities, **kwargs)

    
    def insert_data(self, df: pd.DataFrame, schema_type: str, filename: str, s3_key: str = None, file_size: int = 0) -> Tuple[bool, Dict[str, Any]]:
        """
        Replace all data in the appropriate table with new DataFrame data

        Args:
            df: DataFrame containing the data to insert
            schema_type: Type of schema (ei_tech, srs, ni_tct)
            filename: Original filename for logging
            s3_key: S3 object key/path (optional)
            file_size: Size of the original file in bytes (optional)

        Returns: (success, result_data)
        """
        db = next(get_db())
        try:
            logger.info(f"Replacing all data for schema: {schema_type} with {len(df)} new rows")
            # Create upload log entry
            upload_log = UploadLog(
                filename=filename,
                file_type=schema_type,
                file_size=file_size,
                total_rows=len(df),
                processed_rows=0,
                failed_rows=0,
                status="processing",
                s3_key=s3_key
            )
            db.add(upload_log)
            db.commit()
            db.refresh(upload_log)
            # Get appropriate model
            model_class = self.MODEL_MAPPING.get(schema_type)
            if not model_class:
                raise ValueError(f"Unknown schema type: {schema_type}")
            # Clear current month data from the table
            #1. Get current month and year
            current_month = datetime.now().month
            current_year = datetime.now().year

            #2. Delete only records from current month/year
            existing_count = db.query(model_class).filter(
                extract('month', model_class.db_uploaded_date) == current_month,
                extract('year', model_class.db_uploaded_date) == current_year
            ).count()
            logger.info(f"Clearing {existing_count} rows from {model_class.__tablename__} for {current_month}/{current_year}")

            db.query(model_class).filter(
                extract('month', model_class.db_uploaded_date) == current_month,
                extract('year', model_class.db_uploaded_date) == current_year
            ).delete()

            db.commit()
            logger.info(f"Successfully cleared current month data from {model_class.__tablename__}")

            # Insert new data in batches
            batch_size = 2000
            processed_rows = 0
            failed_rows = 0
            for i in range(0, len(df), batch_size):
                batch_df = df.iloc[i:i + batch_size]
                batch_processed, batch_failed = self._insert_batch(
                    db, batch_df, model_class
                )
                processed_rows += batch_processed
                failed_rows += batch_failed
                logger.info(f"Processed batch {i//batch_size + 1}: {batch_processed} success, {batch_failed} failed")

            # Update upload log
            upload_log.processed_rows = processed_rows
            upload_log.failed_rows = failed_rows
            upload_log.status = "completed" if failed_rows == 0 else "partial"
            db.commit()
            result = {
                "upload_id": upload_log.id,
                "total_rows": len(df),
                "processed_rows": processed_rows,
                "failed_rows": failed_rows,
                "status": upload_log.status,
                "operation": "replace",
                "previous_rows_cleared": existing_count
            }
            self._file_version(db, s3_key=s3_key,schema_type=schema_type,file_name=filename)
            logger.info(f"Data replacement completed: {existing_count} rows cleared, {processed_rows} new rows inserted, {failed_rows} failed")
            return True, result
        except Exception as e:
            db.rollback()
            logger.error(f"Error replacing data: {e}")
            # Update upload log with error
            if 'upload_log' in locals():
                upload_log.status = "failed"
                db.commit()
            return False, {"error": str(e)}
        finally:
            db.close()
    
    def _insert_batch(self, db: Session, batch_df: pd.DataFrame, model_class) -> Tuple[int, int]:
        """Insert a batch of records"""
        
        processed = 0
        failed = 0
        
        for _, row in batch_df.iterrows():
            try:
                # Convert row to dict and clean None values
                row_dict = row.to_dict()
                cleaned_dict = self._clean_row_data(row_dict)
                
                # Create model instance
                instance = model_class(**cleaned_dict)
                db.add(instance)
                processed += 1
                
            except Exception as e:
                logger.warning(f"Failed to insert row: {e}")
                failed += 1
                continue
        
        try:
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Batch commit failed: {e}")
            # All rows in batch failed
            failed = len(batch_df)
            processed = 0
        
        return processed, failed
    
    def _clean_row_data(self, row_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Clean row data for database insertion"""
        
        cleaned = {}
        
        for key, value in row_dict.items():
            # Skip if value is NaN or None
            if pd.isna(value) or value is None:
                continue
            
            # Convert numpy types to Python types
            if hasattr(value, 'item'):
                value = value.item()
            
            # Handle datetime objects
            if isinstance(value, pd.Timestamp):
                value = value.to_pydatetime()
            
            cleaned[key] = value
        
        return cleaned



    def _file_version(self, db, s3_key: str, schema_type: str,file_name:str) -> int:
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Get the latest existing version (if any)
        existing_record = db.query(VersionByMonth).filter(
            VersionByMonth.schema_type == schema_type,
            extract('month', VersionByMonth.db_uploaded_date) == current_month,
            extract('year', VersionByMonth.db_uploaded_date) == current_year
        ).order_by(VersionByMonth.version.desc()).first()  
        
        if existing_record:
            new_version = existing_record.version + 1
            new_record = VersionByMonth(
                s3_key=s3_key,
                file_name=file_name,
                schema_type=schema_type,
                version=new_version
            )
            db.add(new_record)
            db.commit()
            return new_version
        else:
            new_record = VersionByMonth(
                s3_key=s3_key,
                file_name=file_name,
                schema_type=schema_type,
                version=1
            )
            db.add(new_record)
            db.commit()
            return 1
