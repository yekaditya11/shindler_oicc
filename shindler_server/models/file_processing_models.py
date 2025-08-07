"""
File Processing Models for Tag-based Schema Detection
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from pydantic import BaseModel as PydanticBaseModel, Field
from typing import Optional, Dict, Any, List
from config.database import Base
from datetime import datetime

# Database Models
class FileProcessingLog(Base):
    """Track file processing and tag assignments"""
    __tablename__ = "file_processing_logs"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(100), nullable=False, unique=True)  # Unique file ID
    filename = Column(String(255), nullable=False)
    s3_key = Column(String(500), nullable=True)  # S3 object key (nullable for processing)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)  # ei_tech, srs, ni_tct, unknown
    detected_schema = Column(JSON, nullable=True)  # Store detected schema structure
    assigned_tags = Column(JSON, nullable=True)  # Store assigned tags
    confidence_score = Column(Integer, nullable=True)  # Schema detection confidence (0-100)
    processing_status = Column(String(20), nullable=False, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SchemaTemplate(Base):
    """Store schema templates for different file types"""
    __tablename__ = "schema_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(100), nullable=False)
    file_type = Column(String(50), nullable=False)  # ei_tech, srs, ni_tct
    schema_structure = Column(JSON, nullable=False)  # Column names and types
    required_columns = Column(JSON, nullable=True)  # Required columns for this schema
    optional_columns = Column(JSON, nullable=True)  # Optional columns
    confidence_threshold = Column(Integer, default=80)  # Minimum confidence for auto-detection
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TaggedFile(Base):
    """Store files with their tags for schema matching"""
    __tablename__ = "tagged_files"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(100), nullable=False, unique=True)  # Unique file ID
    s3_key = Column(String(500), nullable=False)  # S3 object key
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    user_tags = Column(JSON, nullable=False)  # Tags assigned by user
    schema_hash = Column(String(64), nullable=True)  # Hash of schema structure for quick matching
    schema_structure = Column(JSON, nullable=True)  # Full schema structure
    sample_data = Column(JSON, nullable=True)  # Sample data for validation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class FileUploadSession(Base):
    """Track file upload sessions and presigned URLs"""
    __tablename__ = "file_upload_sessions"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(100), nullable=False, unique=True)  # Unique file ID
    filename = Column(String(255), nullable=False)
    s3_key = Column(String(500), nullable=False)  # S3 object key
    presigned_url = Column(String(1000), nullable=True)  # Generated presigned URL
    upload_status = Column(String(20), nullable=False, default="pending")  # pending, uploaded, failed
    file_size = Column(Integer, nullable=True)  # File size after upload
    content_type = Column(String(100), nullable=True)  # File content type
    user_tags = Column(JSON, nullable=True)  # User-provided tags for demo
    expires_at = Column(DateTime(timezone=True), nullable=True)  # URL expiration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SchemaPattern(Base):
    """Schema pattern model for storing column patterns"""
    __tablename__ = "schema_patterns"

    id = Column(Integer, primary_key=True, index=True)
    schema_name = Column(String(100), nullable=False, unique=True)
    columns = Column(JSON, nullable=False)  # List of column names
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Pydantic Models for API Requests/Responses
class PresignedUrlRequest(PydanticBaseModel):
    """Request model for generating presigned URL"""
    filename: str = Field(..., description="Original filename")
    content_type: Optional[str] = Field(None, description="File content type")
    bucket_name: Optional[str] = Field(None, description="S3 bucket name")

class PresignedUrlResponse(PydanticBaseModel):
    """Response model for presigned URL generation"""
    file_id: str = Field(..., description="Unique file ID")
    filename: str = Field(..., description="Original filename")
    s3_key: str = Field(..., description="S3 object key")
    presigned_url: str = Field(..., description="Presigned URL for upload")
    expires_at: datetime = Field(..., description="URL expiration time")
    upload_method: str = Field(default="PUT", description="HTTP method for upload")

class FileUploadRequest(PydanticBaseModel):
    """Request model for file upload with tags"""
    s3_key: str = Field(..., description="S3 object key")
    filename: str = Field(..., description="Original filename")
    user_tags: List[str] = Field(..., description="Tags assigned by user")
    bucket_name: Optional[str] = Field(None, description="S3 bucket name")

class FileProcessRequest(PydanticBaseModel):
    """Request model for processing file by ID"""
    file_id: str = Field(..., description="Unique file ID")

class TagValidationRequest(PydanticBaseModel):
    """Request model for tag validation"""
    file_id: str = Field(..., description="Unique file ID")
    proposed_tags: List[str] = Field(..., description="Proposed tags to validate")

class SaveTaggedFileRequest(PydanticBaseModel):
    """Request model for saving tagged file"""
    file_id: str = Field(..., description="Unique file ID")
    user_tags: List[str] = Field(..., description="Tags assigned by user")

class SchemaMatchResult(PydanticBaseModel):
    """Schema matching result"""
    matched_file_id: Optional[str] = Field(None, description="File ID of matched file")
    matched_filename: Optional[str] = Field(None, description="Filename of matched file")
    matched_tags: List[str] = Field(default_factory=list, description="Tags of matched file")
    confidence_score: int = Field(..., description="Match confidence (0-100)")
    schema_similarity: float = Field(..., description="Schema similarity percentage")
    conflicting_tags: List[str] = Field(default_factory=list, description="Conflicting tags")
    suggested_tags: List[str] = Field(default_factory=list, description="Suggested tags based on schema")

class FileProcessingResponse(PydanticBaseModel):
    """Response model for file processing"""
    success: bool = Field(..., description="Processing success status")
    file_id: str = Field(..., description="Unique file ID")
    file_type: str = Field(..., description="Detected file type")
    detected_schema: Dict[str, Any] = Field(..., description="Detected schema structure")
    confidence_score: int = Field(..., description="Detection confidence (0-100)")
    suggested_tags: List[str] = Field(default_factory=list, description="Suggested tags")
    existing_matches: List[SchemaMatchResult] = Field(default_factory=list, description="Existing schema matches")
    message: str = Field(..., description="Processing message")

class TagValidationResponse(PydanticBaseModel):
    """Response model for tag validation"""
    success: bool = Field(..., description="Validation success status")
    is_valid: bool = Field(..., description="Whether tags are valid")
    conflicting_files: List[SchemaMatchResult] = Field(default_factory=list, description="Files with conflicting tags")
    suggested_corrections: List[str] = Field(default_factory=list, description="Suggested tag corrections")
    message: str = Field(..., description="Validation message")

class SchemaTemplateCreate(PydanticBaseModel):
    """Request model for creating schema template"""
    template_name: str = Field(..., description="Template name")
    file_type: str = Field(..., description="File type (ei_tech, srs, ni_tct)")
    schema_structure: Dict[str, Any] = Field(..., description="Schema structure")
    required_columns: List[str] = Field(default_factory=list, description="Required columns")
    optional_columns: List[str] = Field(default_factory=list, description="Optional columns")
    confidence_threshold: int = Field(default=80, description="Confidence threshold")

class FileProcessingStatus(PydanticBaseModel):
    """File processing status response"""
    file_id: str = Field(..., description="Unique file ID")
    filename: str = Field(..., description="Original filename")
    status: str = Field(..., description="Processing status")
    file_type: Optional[str] = Field(None, description="Detected file type")
    confidence_score: Optional[int] = Field(None, description="Detection confidence")
    assigned_tags: Optional[List[str]] = Field(None, description="Assigned tags")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Processing start time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")

class FileInfo(PydanticBaseModel):
    """File information response"""
    file_id: str = Field(..., description="Unique file ID")
    filename: str = Field(..., description="Original filename")
    s3_key: str = Field(..., description="S3 object key")
    file_type: str = Field(..., description="File type")
    user_tags: List[str] = Field(..., description="User assigned tags")
    file_size: int = Field(..., description="File size in bytes")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")

class FileListResponse(PydanticBaseModel):
    """Response model for file listing"""
    files: List[FileInfo] = Field(..., description="List of files")
    total_count: int = Field(..., description="Total number of files")
    limit: int = Field(..., description="Limit used")
    offset: int = Field(..., description="Offset used")

class UploadSessionInfo(PydanticBaseModel):
    """Upload session information"""
    file_id: str = Field(..., description="Unique file ID")
    filename: str = Field(..., description="Original filename")
    s3_key: str = Field(..., description="S3 object key")
    upload_status: str = Field(..., description="Upload status")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    content_type: Optional[str] = Field(None, description="File content type")
    expires_at: Optional[datetime] = Field(None, description="URL expiration time")
    created_at: datetime = Field(..., description="Session creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time") 