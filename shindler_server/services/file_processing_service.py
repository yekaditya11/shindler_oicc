"""
File Processing Service for Tag-based Schema Detection
"""

import pandas as pd
import hashlib
import json
import logging
import uuid
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import io

from services.s3_service import S3Service
from models.file_processing_models import (
    FileProcessingLog, SchemaTemplate, TaggedFile, FileUploadSession,
    SchemaMatchResult, FileProcessingResponse, TagValidationResponse,
    PresignedUrlResponse, UploadSessionInfo
)
from config.database import get_db

logger = logging.getLogger(__name__)

class FileProcessingService:
    """Service for processing files with tag-based schema detection"""
    
    def __init__(self):
        """Initialize the file processing service"""
        self.s3_service = S3Service()
        self.schema_templates = {
            'ei_tech': {
                'required_columns': ['event_type', 'event_date', 'location', 'description'],
                'optional_columns': ['severity', 'equipment', 'operator', 'shift'],
                'indicators': ['ei tech', 'eitech', 'unsafe event', 'electrical incident']
            },
            'srs': {
                'required_columns': ['incident_type', 'report_date', 'location', 'description'],
                'optional_columns': ['severity', 'reporter', 'department', 'status'],
                'indicators': ['srs', 'safety reporting system', 'safety report', 'incident report']
            },
            'ni_tct': {
                'required_columns': ['test_type', 'test_date', 'location', 'result'],
                'optional_columns': ['inspector', 'equipment', 'compliance_status', 'notes'],
                'indicators': ['ni tct', 'nitct', 'non-intrusive', 'testing', 'inspection']
            }
        }
    
    def generate_file_id(self) -> str:
        """Generate a unique file ID"""
        return f"file_{uuid.uuid4().hex[:12]}"
    
    def generate_s3_key(self, file_id: str, filename: str) -> str:
        """Generate S3 key based on file ID and filename"""
        # Clean filename and create safe S3 key
        safe_filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.')).rstrip()
        return f"uploads/{file_id}/{safe_filename}"
    
    async def generate_presigned_url(self, filename: str, content_type: Optional[str] = None, bucket_name: Optional[str] = None) -> PresignedUrlResponse:
        """
        Generate presigned URL for file upload
        
        Args:
            filename: Original filename
            content_type: File content type (optional)
            bucket_name: S3 bucket name (optional)
            
        Returns:
            PresignedUrlResponse with upload details
        """
        try:
            # Generate unique file ID
            file_id = self.generate_file_id()
            
            # Generate S3 key
            s3_key = self.generate_s3_key(file_id, filename)
            
            # Set default content type if not provided
            if not content_type:
                if filename.lower().endswith('.xlsx'):
                    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                elif filename.lower().endswith('.xls'):
                    content_type = 'application/vnd.ms-excel'
                else:
                    content_type = 'application/octet-stream'
            
            # Generate presigned URL
            presigned_url = self.s3_service.generate_presigned_url(
                s3_key=s3_key,
                method='PUT',
                content_type=content_type,
                bucket_name=bucket_name,
                expiration=3600  # 1 hour
            )
            
            # Calculate expiration time
            expires_at = datetime.now() + timedelta(hours=1)
            
            # Create upload session record
            await self._create_upload_session(
                file_id=file_id,
                filename=filename,
                s3_key=s3_key,
                presigned_url=presigned_url,
                content_type=content_type,
                expires_at=expires_at
            )
            
            logger.info(f"Generated presigned URL for file: {file_id} -> {s3_key}")
            
            return PresignedUrlResponse(
                file_id=file_id,
                filename=filename,
                s3_key=s3_key,
                presigned_url=presigned_url,
                expires_at=expires_at,
                upload_method="PUT"
            )
            
        except Exception as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise
    
    async def _create_upload_session(self, file_id: str, filename: str, s3_key: str, presigned_url: str, content_type: str, expires_at: datetime):
        """Create upload session record"""
        try:
            db = next(get_db())
            
            upload_session = FileUploadSession(
                file_id=file_id,
                filename=filename,
                s3_key=s3_key,
                presigned_url=presigned_url,
                upload_status='pending',
                content_type=content_type,
                expires_at=expires_at
            )
            
            db.add(upload_session)
            db.commit()
            
            logger.info(f"Created upload session: {file_id}")
            
        except Exception as e:
            logger.error(f"Error creating upload session: {str(e)}")
            raise
    
    async def update_upload_status(self, file_id: str, upload_status: str, file_size: Optional[int] = None):
        """Update upload session status after file upload"""
        try:
            db = next(get_db())
            from sqlalchemy import text
            
            update_query = """
                UPDATE file_upload_sessions 
                SET upload_status = :upload_status, 
                    file_size = :file_size,
                    updated_at = NOW()
                WHERE file_id = :file_id
            """
            
            db.execute(
                text(update_query),
                {
                    "file_id": file_id,
                    "upload_status": upload_status,
                    "file_size": file_size
                }
            )
            db.commit()
            
            logger.info(f"Updated upload status for {file_id}: {upload_status}")
            
        except Exception as e:
            logger.error(f"Error updating upload status: {str(e)}")
            raise
    
    async def get_upload_session(self, file_id: str) -> Optional[UploadSessionInfo]:
        """Get upload session information by file ID"""
        try:
            db = next(get_db())
            from sqlalchemy import text
            
            result = db.execute(
                text("""
                    SELECT file_id, filename, s3_key, upload_status, file_size,
                           content_type, expires_at, created_at, updated_at
                    FROM file_upload_sessions 
                    WHERE file_id = :file_id
                """),
                {"file_id": file_id}
            )
            
            row = result.fetchone()
            if row:
                return UploadSessionInfo(
                    file_id=row.file_id,
                    filename=row.filename,
                    s3_key=row.s3_key,
                    upload_status=row.upload_status,
                    file_size=row.file_size,
                    content_type=row.content_type,
                    expires_at=row.expires_at,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting upload session for {file_id}: {str(e)}")
            return None
    
    def get_file_by_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file information by ID"""
        try:
            db = next(get_db())
            from sqlalchemy import text

            # First try to get from file_upload_sessions (for new uploads)
            result = db.execute(
                text("""
                    SELECT file_id, s3_key, filename, upload_status, user_tags,
                           created_at, updated_at
                    FROM file_upload_sessions
                    WHERE file_id = :file_id
                """),
                {"file_id": file_id}
            )

            row = result.fetchone()
            if row:
                return {
                    "file_id": row.file_id,
                    "s3_key": row.s3_key,
                    "filename": row.filename,
                    "file_type": "unknown",  # Will be determined during processing
                    "user_tags": row.user_tags,
                    "upload_status": row.upload_status,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at
                }

            # Try to get from tagged_files
            result = db.execute(
                text("""
                    SELECT file_id, s3_key, filename, file_type, user_tags,
                           schema_hash, schema_structure, created_at, updated_at
                    FROM tagged_files
                    WHERE file_id = :file_id
                """),
                {"file_id": file_id}
            )

            row = result.fetchone()
            if row:
                return {
                    "file_id": row.file_id,
                    "s3_key": row.s3_key,
                    "filename": row.filename,
                    "file_type": row.file_type,
                    "user_tags": row.user_tags,
                    "schema_hash": row.schema_hash,
                    "schema_structure": row.schema_structure,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at
                }
            
            # If not found in tagged_files, check processing_logs
            result = db.execute(
                text("""
                    SELECT file_id, s3_key, filename, file_type, assigned_tags,
                           detected_schema, confidence_score, processing_status,
                           created_at, updated_at
                    FROM file_processing_logs 
                    WHERE file_id = :file_id
                """),
                {"file_id": file_id}
            )
            
            row = result.fetchone()
            if row:
                return {
                    "file_id": row.file_id,
                    "s3_key": row.s3_key,
                    "filename": row.filename,
                    "file_type": row.file_type,
                    "user_tags": row.assigned_tags,
                    "schema_hash": row.detected_schema.get('schema_hash') if row.detected_schema else None,
                    "schema_structure": row.detected_schema,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting file by ID {file_id}: {str(e)}")
            return None
    
    def analyze_file_schema(self, df: pd.DataFrame, filename: str = "") -> Dict[str, Any]:
        """
        Analyze file schema and detect file type
        
        Args:
            df: Pandas DataFrame
            filename: Original filename
            
        Returns:
            Dict containing schema analysis results
        """
        try:
            # Get column information
            columns = list(df.columns)
            column_types = {col: str(df[col].dtype) for col in columns}
            
            # Create schema hash for quick matching
            schema_hash = self._generate_schema_hash(columns, column_types)
            
            # Detect file type based on content and filename
            file_type, confidence_score = self._detect_file_type(df, filename)
            
            # Get sample data for validation
            sample_data = self._get_sample_data(df)
            
            schema_analysis = {
                'columns': columns,
                'column_types': column_types,
                'total_rows': len(df),
                'total_columns': len(columns),
                'schema_hash': schema_hash,
                'detected_type': file_type,
                'confidence_score': confidence_score,
                'sample_data': sample_data,
                'filename_indicators': self._extract_filename_indicators(filename)
            }
            
            logger.info(f"Schema analysis completed for {filename}: {file_type} (confidence: {confidence_score}%)")
            return schema_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing file schema: {str(e)}")
            raise
    
    def _generate_schema_hash(self, columns: List[str], column_types: Dict[str, str]) -> str:
        """Generate hash for schema structure"""
        schema_data = {
            'columns': sorted(columns),
            'types': {col: column_types[col] for col in sorted(columns)}
        }
        schema_json = json.dumps(schema_data, sort_keys=True)
        return hashlib.sha256(schema_json.encode()).hexdigest()
    
    def _detect_file_type(self, df: pd.DataFrame, filename: str) -> Tuple[str, int]:
        """
        Detect file type based on content and filename
        
        Returns:
            Tuple of (file_type, confidence_score)
        """
        filename_lower = filename.lower()
        columns_lower = [col.lower() for col in df.columns]
        
        scores = {'ei_tech': 0, 'srs': 0, 'ni_tct': 0}
        
        # Check filename indicators
        for file_type, template in self.schema_templates.items():
            for indicator in template['indicators']:
                if indicator in filename_lower:
                    scores[file_type] += 2  # Higher weight for filename matches
        
        # Check column name indicators
        for file_type, template in self.schema_templates.items():
            for indicator in template['indicators']:
                for col in columns_lower:
                    if indicator in col:
                        scores[file_type] += 1
        
        # Check content indicators (first few rows)
        if len(df) > 0:
            sample_content = ""
            for col in df.columns:
                if df[col].dtype == 'object':
                    sample_values = df[col].head(3).astype(str).str.lower()
                    sample_content += " " + " ".join(sample_values.tolist())
            
            for file_type, template in self.schema_templates.items():
                for indicator in template['indicators']:
                    if indicator in sample_content:
                        scores[file_type] += 1  # Use integer instead of float
        
        # Determine best match
        max_score = max(scores.values())
        if max_score == 0:
            return 'unknown', 0
        
        # Calculate confidence score (0-100)
        total_possible_score = 6  # 2 for filename + 1 for each column + 1 for content
        confidence_score = min(100, int((max_score / total_possible_score) * 100))
        
        # Find the file type with highest score
        for file_type, score in scores.items():
            if score == max_score:
                return file_type, confidence_score
        
        return 'unknown', 0
    
    def _extract_filename_indicators(self, filename: str) -> List[str]:
        """Extract indicators from filename"""
        if not filename:
            return []
        
        filename_lower = filename.lower()
        indicators = []
        
        for file_type, template in self.schema_templates.items():
            for indicator in template['indicators']:
                if indicator in filename_lower:
                    indicators.append(indicator)
        
        return indicators
    
    def _get_sample_data(self, df: pd.DataFrame, max_rows: int = 3) -> Dict[str, List]:
        """Get sample data from DataFrame"""
        sample_data = {}
        for col in df.columns:
            if len(df) > 0:
                sample_values = df[col].head(max_rows).astype(str).tolist()
                sample_data[col] = sample_values
            else:
                sample_data[col] = []
        return sample_data
    
    async def process_file_by_id(self, file_id: str) -> FileProcessingResponse:
        """
        Process file by ID and detect schema
        
        Args:
            file_id: Unique file ID
            
        Returns:
            FileProcessingResponse with analysis results
        """
        try:
            # Get file information by ID
            file_info = self.get_file_by_id(file_id)
            if not file_info:
                raise Exception(f"File with ID {file_id} not found")
            
            # Get file from S3
            success, file_data = self.s3_service.download_file(file_info['s3_key'])
            if not success:
                raise Exception(f"Failed to download file from S3: {file_data.get('error', 'Unknown error')}")
            
            # Read file content
            df = pd.read_excel(io.BytesIO(file_data['content']))
            
            # Analyze schema
            schema_analysis = self.analyze_file_schema(df, file_info['filename'])
            
            # Find existing matches
            existing_matches = await self._find_schema_matches(schema_analysis['schema_hash'], file_id)
            
            # Generate suggested tags
            suggested_tags = self._generate_suggested_tags(schema_analysis, existing_matches)
            
            # Log processing
            await self._log_processing(file_id, file_info['filename'], schema_analysis, file_data['size'])
            
            return FileProcessingResponse(
                success=True,
                file_id=file_id,
                file_type=schema_analysis['detected_type'],
                detected_schema=schema_analysis,
                confidence_score=schema_analysis['confidence_score'],
                suggested_tags=suggested_tags,
                existing_matches=existing_matches,
                message=f"File processed successfully. Detected as {schema_analysis['detected_type']} type."
            )
            
        except Exception as e:
            logger.error(f"Error processing file {file_id}: {str(e)}")
            await self._log_processing_error(file_id, "unknown", str(e))
            raise
    
    async def validate_tags_by_id(self, file_id: str, proposed_tags: List[str]) -> TagValidationResponse:
        """
        Validate proposed tags against existing tagged files
        
        Args:
            file_id: Unique file ID
            proposed_tags: Tags to validate
            
        Returns:
            TagValidationResponse with validation results
        """
        try:
            # Get file information by ID
            file_info = self.get_file_by_id(file_id)
            if not file_info:
                raise Exception(f"File with ID {file_id} not found")
            
            # Get file from S3
            success, file_data = self.s3_service.download_file(file_info['s3_key'])
            if not success:
                raise Exception(f"Failed to download file from S3: {file_data.get('error', 'Unknown error')}")
            
            df = pd.read_excel(io.BytesIO(file_data['content']))
            schema_analysis = self.analyze_file_schema(df)
            
            # Find conflicting files
            conflicting_files = await self._find_conflicting_files(schema_analysis['schema_hash'], proposed_tags, file_id)
            
            # Determine if tags are valid
            is_valid = len(conflicting_files) == 0
            
            # Generate suggested corrections
            suggested_corrections = self._generate_tag_suggestions(schema_analysis, conflicting_files)
            
            return TagValidationResponse(
                success=True,
                is_valid=is_valid,
                conflicting_files=conflicting_files,
                suggested_corrections=suggested_corrections,
                message="Tag validation completed successfully."
            )
            
        except Exception as e:
            logger.error(f"Error validating tags for {file_id}: {str(e)}")
            raise
    
    async def _find_schema_matches(self, schema_hash: str, exclude_file_id: Optional[str] = None) -> List[SchemaMatchResult]:
        """Find existing files with similar schema"""
        try:
            db = next(get_db())
            from sqlalchemy import text
            
            # Find files with same schema hash, excluding the current file
            query = """
                SELECT file_id, filename, user_tags, file_type 
                FROM tagged_files 
                WHERE schema_hash = :schema_hash
            """
            params = {"schema_hash": schema_hash}
            
            if exclude_file_id:
                query += " AND file_id != :exclude_file_id"
                params["exclude_file_id"] = exclude_file_id
            
            result = db.execute(text(query), params)
            
            matches = []
            for row in result:
                matches.append(SchemaMatchResult(
                    matched_file_id=row.file_id,
                    matched_filename=row.filename,
                    matched_tags=row.user_tags,
                    confidence_score=95,  # High confidence for exact schema match
                    schema_similarity=100.0,
                    conflicting_tags=[],
                    suggested_tags=row.user_tags
                ))
            
            return matches
            
        except Exception as e:
            logger.error(f"Error finding schema matches: {str(e)}")
            return []
    
    async def _find_conflicting_files(self, schema_hash: str, proposed_tags: List[str], exclude_file_id: Optional[str] = None) -> List[SchemaMatchResult]:
        """Find files with conflicting tags"""
        try:
            db = next(get_db())
            from sqlalchemy import text
            
            # Find files with same schema but different tags
            query = """
                SELECT file_id, filename, user_tags, file_type 
                FROM tagged_files 
                WHERE schema_hash = :schema_hash AND NOT (user_tags @> :proposed_tags)
            """
            params = {
                "schema_hash": schema_hash, 
                "proposed_tags": json.dumps(proposed_tags)
            }
            
            if exclude_file_id:
                query += " AND file_id != :exclude_file_id"
                params["exclude_file_id"] = exclude_file_id
            
            result = db.execute(text(query), params)
            
            conflicts = []
            for row in result:
                conflicting_tags = [tag for tag in proposed_tags if tag not in row.user_tags]
                conflicts.append(SchemaMatchResult(
                    matched_file_id=row.file_id,
                    matched_filename=row.filename,
                    matched_tags=row.user_tags,
                    confidence_score=90,
                    schema_similarity=100.0,
                    conflicting_tags=conflicting_tags,
                    suggested_tags=row.user_tags
                ))
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error finding conflicting files: {str(e)}")
            return []
    
    def _generate_suggested_tags(self, schema_analysis: Dict[str, Any], existing_matches: List[SchemaMatchResult]) -> List[str]:
        """Generate suggested tags based on schema and existing matches"""
        suggested_tags = []
        
        # Add tags based on detected file type
        if schema_analysis['detected_type'] != 'unknown':
            suggested_tags.append(schema_analysis['detected_type'])
        
        # Add tags from existing matches
        for match in existing_matches:
            suggested_tags.extend(match.matched_tags)
        
        # Add tags based on filename indicators
        suggested_tags.extend(schema_analysis['filename_indicators'])
        
        # Remove duplicates and return
        return list(set(suggested_tags))
    
    def _generate_tag_suggestions(self, schema_analysis: Dict[str, Any], conflicting_files: List[SchemaMatchResult]) -> List[str]:
        """Generate tag suggestions based on conflicts"""
        suggestions = []
        
        # If there are conflicts, suggest the most common tags from conflicting files
        if conflicting_files:
            tag_counts = {}
            for conflict in conflicting_files:
                for tag in conflict.matched_tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Get most common tags
            common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            suggestions = [tag for tag, count in common_tags[:3]]
        
        return suggestions
    
    async def _log_processing(self, file_id: str, filename: str, schema_analysis: Dict[str, Any], file_size: int):
        """Log file processing"""
        try:
            db = next(get_db())
            log_entry = FileProcessingLog(
                file_id=file_id,
                filename=filename,
                s3_key="",  # Will be updated when file is saved
                file_size=file_size,
                file_type=schema_analysis['detected_type'],
                detected_schema=schema_analysis,
                confidence_score=schema_analysis['confidence_score'],
                processing_status='completed'
            )
            db.add(log_entry)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error logging file processing: {str(e)}")
    
    async def _log_processing_error(self, file_id: str, filename: str, error_message: str):
        """Log processing error"""
        try:
            db = next(get_db())
            log_entry = FileProcessingLog(
                file_id=file_id,
                filename=filename,
                s3_key="",  # Will be updated when file is saved
                file_size=0,
                file_type='unknown',
                processing_status='failed',
                error_message=error_message
            )
            db.add(log_entry)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error logging processing error: {str(e)}")
    
    async def save_tagged_file_by_id(self, file_id: str, user_tags: List[str]):
        """Save tagged file to database by ID"""
        try:
            # Get file information by ID
            file_info = self.get_file_by_id(file_id)
            if not file_info:
                raise Exception(f"File with ID {file_id} not found")
            
            # Process file to get schema analysis
            processing_result = await self.process_file_by_id(file_id)
            
            db = next(get_db())
            
            # Check if file already exists in tagged_files
            from sqlalchemy import text
            existing = db.execute(
                text("SELECT id FROM tagged_files WHERE file_id = :file_id"),
                {"file_id": file_id}
            ).fetchone()
            
            if existing:
                # Update existing record
                db.execute(
                    text("""
                        UPDATE tagged_files 
                        SET user_tags = :user_tags, file_type = :file_type,
                            schema_hash = :schema_hash, schema_structure = :schema_structure,
                            sample_data = :sample_data, updated_at = NOW()
                        WHERE file_id = :file_id
                    """),
                    {
                        "file_id": file_id,
                        "user_tags": user_tags,
                        "file_type": processing_result.file_type,
                        "schema_hash": processing_result.detected_schema['schema_hash'],
                        "schema_structure": processing_result.detected_schema,
                        "sample_data": processing_result.detected_schema['sample_data']
                    }
                )
            else:
                # Create new record
                tagged_file = TaggedFile(
                    file_id=file_id,
                    s3_key=file_info['s3_key'],
                    filename=file_info['filename'],
                    file_type=processing_result.file_type,
                    user_tags=user_tags,
                    schema_hash=processing_result.detected_schema['schema_hash'],
                    schema_structure=processing_result.detected_schema,
                    sample_data=processing_result.detected_schema['sample_data']
                )
                db.add(tagged_file)
            
            db.commit()
            
            logger.info(f"Saved tagged file: {file_id} with tags: {user_tags}")
            
        except Exception as e:
            logger.error(f"Error saving tagged file: {str(e)}")
            raise
    
    async def create_file_record(self, s3_key: str, filename: str, bucket_name: Optional[str] = None) -> str:
        """Create a new file record and return the file ID"""
        try:
            # Generate unique file ID
            file_id = self.generate_file_id()
            
            # Get file info from S3
            success, file_data = self.s3_service.download_file(s3_key, bucket_name)
            if not success:
                raise Exception(f"Failed to download file from S3: {file_data.get('error', 'Unknown error')}")
            
            # Create initial record in processing logs
            db = next(get_db())
            log_entry = FileProcessingLog(
                file_id=file_id,
                filename=filename,
                s3_key=s3_key,
                file_size=file_data['size'],
                file_type='unknown',
                processing_status='pending'
            )
            db.add(log_entry)
            db.commit()
            
            logger.info(f"Created file record: {file_id} for {filename}")
            return file_id
            
        except Exception as e:
            logger.error(f"Error creating file record: {str(e)}")
            raise

    async def update_upload_session_tags(self, file_id: str, user_tags: List[str]) -> None:
        """Update upload session with user-provided tags"""
        try:
            db = next(get_db())

            # Find the upload session
            upload_session = db.query(FileUploadSession).filter(
                FileUploadSession.file_id == file_id
            ).first()

            if not upload_session:
                raise ValueError(f"Upload session not found for file ID: {file_id}")

            # Store user tags in the JSON field
            upload_session.user_tags = user_tags

            db.commit()
            logger.info(f"Updated upload session {file_id} with tags: {user_tags}")

        except Exception as e:
            logger.error(f"Error updating upload session tags: {str(e)}")
            raise

    async def get_upload_session_tags(self, file_id: str) -> List[str]:
        """Get user tags from upload session"""
        try:
            db = next(get_db())

            upload_session = db.query(FileUploadSession).filter(
                FileUploadSession.file_id == file_id
            ).first()

            if not upload_session:
                return []

            # Return user tags from JSON field
            return upload_session.user_tags or []

        except Exception as e:
            logger.error(f"Error getting upload session tags: {str(e)}")
            return []