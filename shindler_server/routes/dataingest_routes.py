"""
Data ingestion routes for S3 file processing API endpoints
"""

from fastapi import APIRouter
from typing import Dict, Any
import logging

from controllers.dataingest_controller import DataIngestController
from models.base_models import S3FileIngestRequest

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize controller
dataingest_controller = DataIngestController()

@router.post("/dataingest", response_model=Dict[str, Any])
async def ingest_excel_file_from_s3(
    request: S3FileIngestRequest
) -> Dict[str, Any]:
    """
    Ingest and process Excel file from S3 storage

    This endpoint processes Excel files containing unsafe event data directly from S3 storage.

    **Request Parameters:**
    - **s3_key**: S3 object key (full path to file in S3 bucket)
    - **filename**: Original filename for processing and logging
    - **bucket_name**: S3 bucket name (optional, uses configured default if not provided)

    **Processing Features:**
    - Automatically detects schema type (EI Tech, SRS, or NI TCT) based on column structure
    - Uses filename patterns for quick identification, falls back to intelligent schema detection
    - Validates file format and required columns with 60% minimum match threshold
    - Cleans and standardizes data before database insertion
    - Replaces existing data in the corresponding table (complete data refresh)
    - Provides detailed processing statistics and error reporting

    **Returns:**
    - Processing status and statistics
    - Data ingestion ID for tracking
    - Schema type detected
    - Row counts (total, processed, failed)
    - Operation details
    """
    
    logger.info(f"S3 file ingestion endpoint called for: {request.s3_key}")
    return await dataingest_controller.ingest_excel_from_s3(request)





