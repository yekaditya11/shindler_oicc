"""
S3 service for AWS S3 operations
"""

import boto3
from typing import Tuple, Optional
from botocore.exceptions import ClientError, NoCredentialsError
import logging

from config.settings import settings

logger = logging.getLogger(__name__)

class S3Service:
    """AWS S3 service for file operations"""

    def __init__(self):
        """Initialize S3 client with credentials from settings"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
            self.default_bucket = settings.s3_bucket_name

            logger.info("S3 service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize S3 service: {e}")
            raise

    def validate_s3_access(self, bucket_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Validate S3 access and bucket permissions
        
        Args:
            bucket_name: S3 bucket name (uses default if not provided)
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            bucket = bucket_name or self.default_bucket
            
            # Try to list objects in bucket (limited to 1 to minimize cost)
            self.s3_client.list_objects_v2(Bucket=bucket, MaxKeys=1)
            
            logger.info(f"S3 access validated successfully for bucket: {bucket}")
            return True, f"S3 access validated for bucket: {bucket}"
            
        except NoCredentialsError:
            error_msg = "AWS credentials not found or invalid"
            logger.error(error_msg)
            return False, error_msg
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                error_msg = f"S3 bucket does not exist: {bucket}"
            elif error_code == 'AccessDenied':
                error_msg = f"Access denied to S3 bucket: {bucket}"
            else:
                error_msg = f"S3 access validation failed ({error_code}): {e.response['Error']['Message']}"
            
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error validating S3 access: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_file_info(self, s3_key: str, bucket_name: Optional[str] = None) -> Tuple[bool, dict]:
        """
        Get file information from S3 without downloading
        
        Args:
            s3_key: S3 object key
            bucket_name: S3 bucket name (uses default if not provided)
        
        Returns:
            Tuple[bool, dict]: (success, file_info_or_error)
        """
        try:
            bucket = bucket_name or self.default_bucket
            
            response = self.s3_client.head_object(Bucket=bucket, Key=s3_key)
            
            file_info = {
                'size': response.get('ContentLength', 0),
                'last_modified': response.get('LastModified'),
                'content_type': response.get('ContentType'),
                'etag': response.get('ETag', '').strip('"')
            }
            
            logger.info(f"Retrieved file info for S3 key: {s3_key}")
            return True, file_info
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                error_msg = f"File not found in S3: bucket={bucket}, key={s3_key}"
            else:
                error_msg = f"Error getting file info ({error_code}): {e.response['Error']['Message']}"
            
            logger.error(error_msg)
            return False, {'error': error_msg}
            
        except Exception as e:
            error_msg = f"Unexpected error getting file info: {str(e)}"
            logger.error(error_msg)
            return False, {'error': error_msg}
