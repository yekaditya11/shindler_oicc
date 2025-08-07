"""
File Processing API Routes
FastAPI routes for file processing with tag-based schema detection
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
import logging
import json

from models.file_processing_models import (
    PresignedUrlRequest, PresignedUrlResponse, FileListResponse, FileInfo
)
from services.file_processing_service import FileProcessingService
from utils.response_formatter import ResponseFormatter

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/file-processing", tags=["File Processing"])

# Initialize service
file_processing_service = FileProcessingService()

@router.post("/presigned-url", response_model=PresignedUrlResponse)
async def generate_presigned_url(request: PresignedUrlRequest):
    """
    Generate presigned URL for file upload
    
    This endpoint:
    1. Generates a unique file ID
    2. Creates an S3 key based on file ID and filename
    3. Generates a presigned URL for PUT upload
    4. Creates an upload session record
    5. Returns upload details with file ID
    
    The client can then use the presigned URL to upload the file directly to S3.
    """
    try:
        logger.info(f"Generating presigned URL for: {request.filename}")
        
        result = await file_processing_service.generate_presigned_url(
            filename=request.filename,
            content_type=request.content_type,
            bucket_name=request.bucket_name
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate presigned URL: {str(e)}"
        )

@router.post("/upload-complete/{file_id}")
async def mark_upload_complete(file_id: str):
    """
    Mark file upload as complete

    This endpoint should be called after the client successfully uploads the file
    using the presigned URL. It updates the upload status and prepares the file
    for processing.
    """
    try:
        logger.info(f"Marking upload complete for file ID: {file_id}")

        # Update upload status to completed
        await file_processing_service.update_upload_status(
            file_id=file_id,
            upload_status='uploaded'
        )

        return ResponseFormatter.success_response(
            message="Upload marked as complete",
            body={
                "file_id": file_id,
                "status": "uploaded",
                "message": "File is ready for processing"
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"Error marking upload complete for {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark upload complete: {str(e)}"
        )



@router.post("/upload-and-check-schema")
async def upload_and_check_schema(request: dict):
    """
    Simple file upload with immediate schema pattern check

    Request body:
    {
        "filename": "example.xlsx",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }

    Returns:
    - Upload URL for S3
    - Schema pattern recommendations if match found
    - Option to add new schema pattern if no match
    """
    try:
        filename = request.get("filename")
        content_type = request.get("content_type")

        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="filename is required"
            )

        logger.info(f"Upload and schema check for: {filename}")

        # Generate presigned URL and file ID
        presigned_result = await file_processing_service.generate_presigned_url(
            filename=filename,
            content_type=content_type
        )

        return ResponseFormatter.success_response(
            message="Upload URL generated - upload file then call /check-schema",
            body={
                "file_id": presigned_result.file_id,
                "upload_url": presigned_result.presigned_url,
                "s3_key": presigned_result.s3_key,
                "expires_at": presigned_result.expires_at.isoformat(),
                "next_step": f"After uploading, call POST /file-processing/check-schema/{presigned_result.file_id}"
            },
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        logger.error(f"Error in upload and schema check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process upload: {str(e)}"
        )

@router.post("/check-schema/{file_id}")
async def check_schema_pattern(file_id: str):
    """
    Simple schema pattern check after file upload

    1. Downloads file from S3 and reads columns
    2. Matches against existing SCHEMA_PATTERNS
    3. If match found: shows recommendation
    4. If no match: asks if user wants to add new schema pattern
    """
    try:
        logger.info(f"Checking schema pattern for file: {file_id}")

        # Get file info
        file_info = file_processing_service.get_file_by_id(file_id)
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_id} not found"
            )

        # Download and read file to get columns
        success, file_data = file_processing_service.s3_service.download_file(file_info['s3_key'])

        if not success:
            # Demo mode: simulate columns based on filename
            filename = file_info['filename'].lower()
            if 'safety' in filename or 'incident' in filename:
                file_columns = ['Event ID', 'Reporter Name', 'Reported Date', 'Unsafe Event Type', 'Status']
            elif 'srs' in filename:
                file_columns = ['Event Id', 'Reporter Name', 'Reported Date', 'Division', 'Branch']
            elif 'tct' in filename:
                file_columns = ['Reporting ID', 'Status', 'Location', 'Branch Name', 'Region']
            elif 'maintenance' in filename:
                file_columns = ['Date', 'Equipment', 'Maintenance Type', 'Technician', 'Status']
            else:
                file_columns = ['Date', 'Description', 'Status', 'Type']

            logger.info(f"Demo mode: simulated columns for {filename}: {file_columns}")
        else:
            # Real mode: read Excel file to get actual columns
            import pandas as pd
            import io
            try:
                df = pd.read_excel(io.BytesIO(file_data['content']))
                file_columns = list(df.columns)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Could not read Excel file: {str(e)}"
                )

        # Check against existing schema patterns from database
        from services.schema_pattern_service import schema_pattern_service

        # Get all patterns from database
        schema_patterns = await schema_pattern_service.get_all_patterns()

        # Calculate confidence for all schemas and get top 5
        schema_matches = {}
        for schema_name, expected_columns in schema_patterns.items():
            confidence = _calculate_column_match(file_columns, expected_columns)
            schema_matches[schema_name] = confidence

        # Sort by confidence and get top 5 nearby schemas
        sorted_matches = sorted(schema_matches.items(), key=lambda x: x[1], reverse=True)
        top_5_schemas = sorted_matches[:5]

        # Best match is the top one
        best_match = top_5_schemas[0][0] if top_5_schemas else None
        best_confidence = top_5_schemas[0][1] if top_5_schemas else 0

        # Determine response based on match quality
        if best_confidence > 50:  # Good match found
            return ResponseFormatter.success_response(
                message="Schema pattern match found",
                body={
                    "file_id": file_id,
                    "filename": file_info['filename'],
                    "file_columns": file_columns,
                    "best_match": best_match,
                    "confidence": best_confidence,
                    "top_5_schemas": [{"schema_name": name, "confidence": conf} for name, conf in top_5_schemas],
                    "recommendation": f"Best match: '{best_match}' ({best_confidence}% confidence). You can pick from top 5 or add new schema.",
                    "action": "confirm_schema",
                    "next_step": f"Call POST /file-processing/confirm-schema/{file_id} with chosen schema_name"
                }
            )
        else:  # No good match - ask to add new schema
            return ResponseFormatter.success_response(
                message="No good schema pattern match found",
                body={
                    "file_id": file_id,
                    "filename": file_info['filename'],
                    "file_columns": file_columns,
                    "best_match": best_match,
                    "confidence": best_confidence,
                    "top_5_schemas": [{"schema_name": name, "confidence": conf} for name, conf in top_5_schemas],
                    "message": "No existing schema pattern matches well. You can pick from nearby matches or add new schema.",
                    "action": "choose_or_add_schema",
                    "next_step": "Pick from top_5_schemas or call POST /file-processing/add-schema-pattern"
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking schema pattern {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check schema pattern: {str(e)}"
        )

@router.post("/confirm-schema/{file_id}")
async def confirm_schema_pattern(file_id: str, request: dict):
    """
    Confirm the chosen schema pattern for a file

    The schema name becomes the primary tag, and any additional tags are optional.

    Request body:
    {
        "schema_name": "ei_tech",
        "additional_tags": ["monthly", "production"]  # Optional
    }
    """
    try:
        schema_name = request.get("schema_name")
        additional_tags = request.get("additional_tags", [])

        if not schema_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="schema_name is required"
            )

        # Schema name becomes the primary tag
        all_tags = [schema_name]
        if additional_tags:
            all_tags.extend(additional_tags)

        logger.info(f"Confirming schema {schema_name} for file {file_id}. All tags: {all_tags}")

        # Get file info
        file_info = file_processing_service.get_file_by_id(file_id)
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_id} not found"
            )

        # Save file with confirmed schema and tags
        from config.database import get_db
        from models.file_processing_models import TaggedFile
        from sqlalchemy import text

        db = next(get_db())

        # Remove any existing record
        db.execute(
            text("DELETE FROM tagged_files WHERE file_id = :file_id"),
            {"file_id": file_id}
        )

        # Create new tagged file record - schema name is both file_type and primary tag
        tagged_file = TaggedFile(
            file_id=file_id,
            s3_key=file_info['s3_key'],
            filename=file_info['filename'],
            file_type=schema_name,  # Schema name as file type
            user_tags=all_tags,     # Schema name + additional tags
            schema_hash=f"{schema_name}_confirmed"
        )

        db.add(tagged_file)
        db.commit()

        return ResponseFormatter.success_response(
            message="Schema pattern confirmed and file saved",
            body={
                "file_id": file_id,
                "schema_name": schema_name,
                "all_tags": all_tags,
                "primary_tag": schema_name,
                "additional_tags": additional_tags,
                "status": "confirmed_and_saved"
            }
        )

    except Exception as e:
        logger.error(f"Error confirming schema for {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm schema: {str(e)}"
        )

@router.post("/add-schema-pattern")
async def add_new_schema_pattern(request: dict):
    """
    Add a new schema pattern to the system

    Request body:
    {
        "schema_name": "new_safety_report",
        "columns": ["Date", "Event", "Severity", "Location"],
        "description": "New safety report format"
    }
    """
    try:
        schema_name = request.get("schema_name")
        columns = request.get("columns", [])
        description = request.get("description", "")

        if not schema_name or not columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="schema_name and columns are required"
            )

        logger.info(f"Adding new schema pattern: {schema_name} with columns: {columns}")

        # Store in database using schema pattern service
        from services.schema_pattern_service import schema_pattern_service

        success = await schema_pattern_service.add_pattern(schema_name, columns, description)

        if success:
            return ResponseFormatter.success_response(
                message="New schema pattern added successfully",
                body={
                    "schema_name": schema_name,
                    "columns": columns,
                    "description": description,
                    "status": "added",
                    "note": "Schema pattern stored in database. Files can now be matched against this pattern."
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Schema pattern '{schema_name}' already exists or could not be added"
            )

    except Exception as e:
        logger.error(f"Error adding schema pattern: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add schema pattern: {str(e)}"
        )

@router.get("/schema-patterns")
async def get_all_schema_patterns():
    """Get all active schema patterns"""
    try:
        from services.schema_pattern_service import schema_pattern_service

        patterns = await schema_pattern_service.get_all_patterns()

        return ResponseFormatter.success_response(
            message=f"Retrieved {len(patterns)} schema patterns",
            body={
                "patterns": patterns,
                "count": len(patterns)
            }
        )

    except Exception as e:
        logger.error(f"Error getting schema patterns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get schema patterns: {str(e)}"
        )

@router.post("/initialize-default-patterns")
async def initialize_default_patterns():
    """Initialize database with default schema patterns from config"""
    try:
        from services.schema_pattern_service import schema_pattern_service

        await schema_pattern_service.initialize_default_patterns()

        return ResponseFormatter.success_response(
            message="Default schema patterns initialized successfully",
            body={
                "status": "initialized",
                "note": "Default patterns from config file have been stored in database"
            }
        )

    except Exception as e:
        logger.error(f"Error initializing default patterns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize default patterns: {str(e)}"
        )

@router.get("/user-tags")
async def get_all_user_tags():
    """Get all user tags that have been used in the system"""
    try:
        from config.database import get_db
        from sqlalchemy import text

        db = next(get_db())

        # Get all user tags from tagged files
        result = db.execute(
            text("SELECT user_tags FROM tagged_files WHERE user_tags IS NOT NULL")
        )

        # Collect all unique tags
        all_tags = set()
        for row in result:
            if row.user_tags:
                try:
                    # Handle different tag storage formats
                    if isinstance(row.user_tags, list):
                        tags = row.user_tags
                    elif isinstance(row.user_tags, str):
                        import json
                        tags = json.loads(row.user_tags) if row.user_tags != 'null' else []
                    else:
                        continue

                    all_tags.update(tags)
                except Exception as e:
                    logger.warning(f"Error parsing tags: {e}")
                    continue

        # Convert to sorted list
        unique_tags = sorted(list(all_tags))

        return ResponseFormatter.success_response(
            message=f"Retrieved {len(unique_tags)} unique user tags",
            body={
                "tags": unique_tags,
                "count": len(unique_tags)
            }
        )

    except Exception as e:
        logger.error(f"Error getting user tags: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user tags: {str(e)}"
        )

@router.get("/files/list")
async def get_all_file_ids(
    limit: int = 100,
    offset: int = 0,
    include_details: bool = False
):
    """
    Get list of all file IDs with basic information (Demo API)

    Query parameters:
    - limit: Maximum number of results (default: 100)
    - offset: Number of results to skip (default: 0)
    - include_details: Include file details like tags and schema info (default: false)

    Returns a simple list of file IDs for demo purposes.
    """
    try:
        from config.database import get_db
        from sqlalchemy import text

        db = next(get_db())

        # Get files from upload sessions (simpler approach)
        if include_details:
            query = """
                SELECT
                    file_id,
                    filename,
                    user_tags::text as user_tags_text,
                    upload_status,
                    created_at
                FROM file_upload_sessions
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """
        else:
            query = """
                SELECT
                    file_id,
                    filename,
                    created_at
                FROM file_upload_sessions
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """

        result = db.execute(text(query), {"limit": limit, "offset": offset})

        files = []
        for row in result:
            if include_details:
                # Parse user_tags from JSON string
                user_tags = []
                if row.user_tags_text:
                    try:
                        import json
                        user_tags = json.loads(row.user_tags_text) if row.user_tags_text != 'null' else []
                    except:
                        user_tags = []

                files.append({
                    "file_id": row.file_id,
                    "filename": row.filename,
                    "user_tags": user_tags,
                    "file_type": "unknown",  # Will be determined during processing
                    "upload_status": row.upload_status or "unknown",
                    "created_at": row.created_at.isoformat() if row.created_at else None
                })
            else:
                files.append({
                    "file_id": row.file_id,
                    "filename": row.filename,
                    "created_at": row.created_at.isoformat() if row.created_at else None
                })

        return ResponseFormatter.success_response(
            message=f"Retrieved {len(files)} file(s)",
            body={
                "files": files,
                "total_count": len(files),
                "limit": limit,
                "offset": offset,
                "include_details": include_details
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"Error getting file list: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file list: {str(e)}"
        )

@router.get("/files", response_model=FileListResponse)
async def get_tagged_files(
    file_type: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Get list of tagged files with optional filtering

    Query parameters:
    - file_type: Filter by file type (ei_tech, srs, ni_tct)
    - tag: Filter by specific tag
    - limit: Maximum number of results (default: 50)
    - offset: Number of results to skip (default: 0)
    """
    try:
        from config.database import get_db
        from sqlalchemy import text

        db = next(get_db())

        # Build query
        query = "SELECT file_id, s3_key, filename, file_type, user_tags, created_at, updated_at FROM tagged_files WHERE 1=1"
        params = {}

        if file_type:
            query += " AND file_type = :file_type"
            params["file_type"] = file_type

        if tag:
            query += " AND :tag = ANY(user_tags)"
            params["tag"] = tag

        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        result = db.execute(text(query), params)

        files = []
        for row in result:
            files.append(FileInfo(
                file_id=row.file_id,
                filename=row.filename,
                s3_key=row.s3_key,
                file_type=row.file_type,
                user_tags=row.user_tags or [],
                file_size=0,  # Will be updated when needed
                created_at=row.created_at,
                updated_at=row.updated_at
            ))

        return FileListResponse(
            files=files,
            total_count=len(files),
            limit=limit,
            offset=offset
        )

    except Exception as e:
        logger.error(f"Error getting tagged files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tagged files: {str(e)}"
        )

# Schema pattern matching functions using SCHEMA_PATTERNS config
def _normalize_column_name(col_name: str) -> str:
    """Normalize column name for better matching"""
    return col_name.lower().strip().replace('_', ' ').replace('-', ' ')

def _calculate_column_match(file_columns: List[str], expected_columns: List[str]) -> int:
    """Calculate percentage match between file columns and expected schema columns"""
    if not expected_columns:
        return 0

    # Normalize column names for better matching
    file_cols_normalized = [_normalize_column_name(col) for col in file_columns]
    expected_cols_normalized = [_normalize_column_name(col) for col in expected_columns]

    # Count exact matches (case-insensitive, normalized)
    exact_matches = sum(1 for expected_col in expected_cols_normalized
                       if expected_col in file_cols_normalized)

    # Count partial matches (expected column name contains file column or vice versa)
    partial_matches = 0
    for expected_col in expected_cols_normalized:
        if expected_col not in file_cols_normalized:
            # Check for partial matches
            for file_col in file_cols_normalized:
                if (expected_col in file_col or file_col in expected_col) and len(expected_col) > 2:
                    partial_matches += 1
                    break

    # Calculate weighted score: exact matches = 1.0, partial matches = 0.5
    total_score = exact_matches + (partial_matches * 0.5)
    percentage = int((total_score / len(expected_columns)) * 100)

    return min(percentage, 100)  # Cap at 100%

# Simple helper functions for schema pattern matching

# Simple helper functions - no complex logic needed