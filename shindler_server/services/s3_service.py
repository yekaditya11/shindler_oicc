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

    def download_file(self, s3_key: str, bucket_name: Optional[str] = None) -> Tuple[bool, dict]:
        """
        Download file from S3
        
        Args:
            s3_key: S3 object key
            bucket_name: S3 bucket name (uses default if not provided)
        
        Returns:
            Tuple[bool, dict]: (success, file_data_or_error)
        """
        try:
            bucket = bucket_name or self.default_bucket
            
            response = self.s3_client.get_object(Bucket=bucket, Key=s3_key)
            
            file_data = {
                'content': response['Body'].read(),
                'size': response.get('ContentLength', 0),
                'content_type': response.get('ContentType'),
                'last_modified': response.get('LastModified')
            }
            
            logger.info(f"Downloaded file from S3: bucket={bucket}, key={s3_key}")
            return True, file_data
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                error_msg = f"File not found in S3: bucket={bucket}, key={s3_key}"
            else:
                error_msg = f"Error downloading file ({error_code}): {e.response['Error']['Message']}"
            
            logger.error(error_msg)
            return False, {'error': error_msg}
            
        except Exception as e:
            error_msg = f"Unexpected error downloading file: {str(e)}"
            logger.error(error_msg)
            return False, {'error': error_msg}

    def upload_file(self, file_content: bytes, s3_key: str, bucket_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Upload file to S3
        
        Args:
            file_content: File content as bytes
            s3_key: S3 object key
            bucket_name: S3 bucket name (uses default if not provided)
        
        Returns:
            Tuple[bool, str]: (success, message_or_error)
        """
        try:
            bucket = bucket_name or self.default_bucket
            
            self.s3_client.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=file_content
            )
            
            logger.info(f"Uploaded file to S3: bucket={bucket}, key={s3_key}")
            return True, f"File uploaded successfully to s3://{bucket}/{s3_key}"
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = f"Error uploading file ({error_code}): {e.response['Error']['Message']}"
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error uploading file: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def delete_file(self, s3_key: str, bucket_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Delete file from S3
        
        Args:
            s3_key: S3 object key
            bucket_name: S3 bucket name (uses default if not provided)
        
        Returns:
            Tuple[bool, str]: (success, message_or_error)
        """
        try:
            bucket = bucket_name or self.default_bucket
            
            self.s3_client.delete_object(Bucket=bucket, Key=s3_key)
            
            logger.info(f"Deleted file from S3: bucket={bucket}, key={s3_key}")
            return True, f"File deleted successfully from s3://{bucket}/{s3_key}"
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = f"Error deleting file ({error_code}): {e.response['Error']['Message']}"
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error deleting file: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def generate_presigned_url(self, s3_key: str, method: str = 'PUT', content_type: Optional[str] = None, bucket_name: Optional[str] = None, expiration: int = 3600) -> str:
        """
        Generate presigned URL for S3 operations
        
        Args:
            s3_key: S3 object key
            method: HTTP method (GET, PUT, POST, DELETE)
            content_type: Content type for PUT operations
            bucket_name: S3 bucket name (uses default if not provided)
            expiration: URL expiration time in seconds (default: 1 hour)
        
        Returns:
            str: Presigned URL
        """
        try:
            bucket = bucket_name or self.default_bucket
            
            # Prepare parameters for presigned URL
            params = {
                'Bucket': bucket,
                'Key': s3_key,
                'Expires': expiration
            }
            
            # Add content type for PUT operations
            if method.upper() == 'PUT' and content_type:
                params['ContentType'] = content_type
            
            # Generate presigned URL
            presigned_url = self.s3_client.generate_presigned_url(
                ClientMethod=f'{method.lower()}_object',
                Params=params
            )
            
            logger.info(f"Generated presigned URL: {method} {s3_key} (expires in {expiration}s)")
            return presigned_url
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = f"Error generating presigned URL ({error_code}): {e.response['Error']['Message']}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error generating presigned URL: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
