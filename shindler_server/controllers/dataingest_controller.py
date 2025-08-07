"""
Data ingestion controller for handling S3 file processing requests
"""

from fastapi import HTTPException
from typing import Dict, Any
import logging

from services.excel_processor import ExcelProcessor
from services.database_service import DatabaseService
from services.s3_service import S3Service
from models.base_models import S3FileIngestRequest
from utils.response_formatter import ResponseFormatter
from config.file_name_pattrens_configs import file_name_patterns

logger = logging.getLogger(__name__)

class DataIngestController:
    """Controller for S3-based data ingestion operations"""

    def __init__(self):
        self.excel_processor = ExcelProcessor()
        self.database_service = DatabaseService()
        self.s3_service = S3Service()

    async def ingest_excel_from_s3(self, request: S3FileIngestRequest) -> Dict[str, Any]:
        """
        Handle Excel file ingestion from S3
        """
        try:
            logger.info(f"Received S3 file ingestion request: s3_key={request.s3_key}, filename={request.filename}")
            # Check if filename matches any known patterns
            matched_pattern = None
            for pattern in file_name_patterns:
                if pattern.lower() in request.filename.lower():
                    matched_pattern = pattern
                    break

            if matched_pattern:
                logger.info(f"Filename matches pattern: {matched_pattern}")
                # Process Excel file with known pattern
                success, process_result = self.excel_processor.process_excel_from_s3_path(request)
            else:
                logger.info(f"Filename doesn't match known patterns. Attempting schema detection and processing...")
                # Process Excel file with automatic schema detection
                success, process_result = self.excel_processor.process_excel_from_s3_path(request)

                if not success:
                    # If processing fails, return error with available patterns
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "message": f"Could not detect file schema and filename doesn't match known patterns. Allowed patterns: {', '.join(file_name_patterns)}. Error: {process_result.get('error')}",
                            "body": {}
                        }
                    )

            if not success:
                logger.error(f"Excel processing failed: {process_result.get('error')}")
                error_response = ResponseFormatter.error_response(
                    message=f"Excel processing failed: {process_result.get('error')}",
                    status_code=400
                )
                raise HTTPException(status_code=400, detail=error_response)

            # Extract processed data
            df = process_result['dataframe']
            schema_type = process_result['schema_type']
            filename = process_result['filename']
            file_size = process_result.get('file_size', 0)

            # Insert data into database
            success, db_result = self.database_service.insert_data(
                df, schema_type, filename,
                s3_key=request.s3_key,
                file_size=file_size
            )

            if not success:
                logger.error(f"Database insertion failed: {db_result.get('error')}")
                error_response = ResponseFormatter.error_response(
                    message=f"Database error: {db_result.get('error')}",
                    status_code=500
                )
                raise HTTPException(status_code=500, detail=error_response)

            # Format file size in human-readable format
            if file_size == 0:
                formatted_size = "N/A"
            elif file_size < 1024:
                formatted_size = f"{file_size} B"
            elif file_size < 1024 * 1024:
                formatted_size = f"{file_size / 1024:.1f} KB"
            elif file_size < 1024 * 1024 * 1024:
                formatted_size = f"{file_size / (1024 * 1024):.1f} MB"
            else:
                formatted_size = f"{file_size / (1024 * 1024 * 1024):.1f} GB"

            # Prepare response following consistent API structure
            response = ResponseFormatter.success_response(
                message="S3 file ingested and data replaced successfully",
                body={
                    "dataingest_id": db_result['upload_id'],
                    "s3_key": request.s3_key,
                    "filename": filename,
                    "file_size": formatted_size,
                    "schema_type": schema_type,
                    "operation": "replace",
                    "previous_rows_cleared": db_result.get('previous_rows_cleared', 0),
                    "total_rows": process_result['total_rows'],
                    "processed_rows": db_result['processed_rows'],
                    "failed_rows": db_result['failed_rows'],
                    "status": db_result['status']
                }
            )

            logger.info(f"S3 file processing completed successfully: {filename}")
            return response


        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in S3 file processing: {e}")
            error_response = ResponseFormatter.error_response(
                message=f"Internal server error: {str(e)}",
                status_code=500
            )
            raise HTTPException(status_code=500, detail=error_response)


