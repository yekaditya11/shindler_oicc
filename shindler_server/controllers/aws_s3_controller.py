from fastapi import HTTPException
from botocore.exceptions import ClientError
from datetime import datetime

import boto3
import uuid

from config.settings import settings

# Initialize S3 client using centralized settings
s3_client = boto3.client(
    's3',
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key
)

def generate_presigned_url()->dict:
    """Generate a presigned URL for uploading an Excel file to S3"""
    try:

        # Generate a unique key for the file
        object_key = f"uploads/excel/{datetime.now().isoformat()}_{uuid.uuid4()}.xlsx"
        
        # Generate presigned POST data
        presigned_data = s3_client.generate_presigned_post(
            Bucket=settings.s3_bucket_name,
            Key=object_key,
            Fields={"Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
            Conditions=[
                ["starts-with", "$Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
                ["content-length-range", 0, 10485760]  # 10MB max
            ],
            ExpiresIn=3600  # 1 hour
        )
        
        return {
            "url": presigned_data["url"],
            "fields": presigned_data["fields"],
            "s3_key": object_key
        }
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
    


