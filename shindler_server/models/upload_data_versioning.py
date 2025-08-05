"""
Versioning the uploaded data by month and year.
"""
from models.base_models import BaseModel
from sqlalchemy import Column, Integer, DateTime, Text
from sqlalchemy.sql import func


class VersionByMonth(BaseModel):
    """Track file upload versions by month and year"""
    __tablename__ = "version_by_month"

    s3_key = Column(Text, nullable=False)
    file_name = Column(Text, nullable=False)
    schema_type = Column(Text, nullable=False)
    db_uploaded_date = Column(DateTime, server_default=func.now(), nullable=False)
    version = Column(Integer, nullable=False)
