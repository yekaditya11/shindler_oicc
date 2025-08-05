"""
Excel file processing service for S3-based data ingestion
"""

import pandas as pd
from typing import Tuple, Optional, Dict, Any
import logging

from utils.file_validator import FileValidator
from utils.data_cleaner import DataCleaner
from utils.s3_client_utils import read_excel_file_from_s3_to_dataframe
from services.s3_service import S3Service

logger = logging.getLogger(__name__)

class ExcelProcessor:
    """Excel file processing and parsing for S3-based data ingestion"""

    def __init__(self):
        self.s3_service = S3Service()

    def process_excel_from_s3_path(self,request) -> Tuple[bool, Dict[str, Any]]:
        """
        Process Excel file from S3-downloaded local path
        Returns: (success, result_data)
        """
        try:
            logger.info(f"Processing Excel file from S3: {request.filename}")

            # Process the file using the common processing method
            return self._process_excel_from_path(request)

        except Exception as e:
            logger.error(f"Error processing Excel file from S3 {request.filename}: {e}")
            return False, {"error": f"Processing failed: {str(e)}"}



    def _process_excel_from_path(self,request) -> Tuple[bool, Dict[str, Any]]:
        """
        Common method to process Excel file from local path
        Returns: (success, result_data)
        """
        try:
            # Validate file extension first
            is_valid_ext = FileValidator.validate_file_extension(request.filename)
            if not is_valid_ext:
                return False, {"error": f"Invalid file extension. Only Excel files (.xlsx, .xls) are supported."}

            # Validate filename pattern
            is_valid_pattern, pattern_message = FileValidator.validate_filename_pattern(request.filename)
            if not is_valid_pattern:
                return False, {"error": pattern_message}

            # Read Excel file
            df = self._read_excel_file(request)
            if df is None:
                return False, {"error": "Failed to read Excel file"}

            # Detect schema type
            schema_type = FileValidator.detect_schema_type(df)
            if not schema_type:
                return False, {"error": "Could not detect file schema type"}

            # Validate schema
            is_valid_schema, schema_message = FileValidator.validate_required_columns(df, schema_type)
            if not is_valid_schema:
                return False, {"error": schema_message}

            # Clean data
            cleaned_df = DataCleaner.clean_dataframe(df, schema_type)

            # Normalize column names for database
            normalized_df = DataCleaner.normalize_column_names(cleaned_df, schema_type)

            # Get file size from S3
            file_size = 0
            try:
                success, file_info = self.s3_service.get_file_info(request.s3_key, request.bucket_name)
                if success:
                    file_size = file_info.get('size', 0)
                    logger.info(f"Retrieved file size: {file_size} bytes")
                else:
                    logger.warning(f"Could not retrieve file size: {file_info}")
            except Exception as e:
                logger.warning(f"Error getting file size: {e}")

            result = {
                "filename": request.filename,
                "file_path": request.s3_key,
                "schema_type": schema_type,
                "total_rows": len(df),
                "cleaned_rows": len(cleaned_df),
                "columns": list(normalized_df.columns),
                "dataframe": normalized_df,
                "file_size": file_size
            }

            logger.info(f"Successfully processed {request.filename}: {len(cleaned_df)} rows, schema: {schema_type}")
            return True, result

        except Exception as e:
            logger.error(f"Error processing Excel file {request.filename}: {e}")
            return False, {"error": f"Processing failed: {str(e)}"}
    

    
    def _read_excel_file(self, request) -> Optional[pd.DataFrame]:
        """Read Excel file into DataFrame"""
        try:
            logger.info(f"Attempting to read Excel file from S3: {request.s3_key}")
            # Use the new Excel-specific function with filename validation
            df = read_excel_file_from_s3_to_dataframe(request.s3_key, request.filename)
            logger.info(f"Successfully read Excel file. DataFrame shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error reading Excel file {request.s3_key}: {e}")
            return None
