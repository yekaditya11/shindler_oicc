"""
Base models and common fields
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel as PydanticBaseModel, Field
from typing import Optional, Dict, Any
from config.database import Base

class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UploadLog(BaseModel):
    """Track file uploads and processing"""
    __tablename__ = "upload_logs"

    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # ei_tech, srs, ni_tct
    file_size = Column(Integer, nullable=False)
    total_rows = Column(Integer, nullable=False)
    processed_rows = Column(Integer, nullable=False)
    failed_rows = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="processing")  # processing, completed, failed
    s3_key = Column(String(500), nullable=True)  # S3 object key/path


# Pydantic models for API requests
class S3FileIngestRequest(PydanticBaseModel):
    """Request model for S3 file ingestion"""
    s3_key: str = Field(..., description="S3 object key (path to file in S3)")
    filename: str = Field(..., description="Original filename for processing")
    bucket_name: Optional[str] = Field(None, description="S3 bucket name (uses default if not provided)")


class InsightFeedback(BaseModel):
    """Feedback for AI-generated insights (like/dislike)"""
    __tablename__ = "insight_feedback"

    user_id = Column(String(100), nullable=False, index=True)
    schema_type = Column(String(50), nullable=False, index=True)  # srs, ei_tech, ni_tct
    insight_text = Column(String(1000), nullable=False)
    feedback = Column(String(10), nullable=False)  # 'like' or 'dislike'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# API Response Models
class StandardResponse(PydanticBaseModel):
    """Standard API response format"""
    status_code: int
    message: str
    body: Dict[str, Any]


# Feedback Models
class InsightFeedbackCreate(PydanticBaseModel):
    """Pydantic model for creating insight feedback"""
    schema_type: str = Field(..., description="Schema type (srs, ei_tech, ni_tct)")
    insight_text: str = Field(..., description="The AI-generated insight text")
    feedback: str = Field(..., description="User feedback (like or dislike)")
