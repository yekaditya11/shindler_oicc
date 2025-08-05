import boto3
import pandas as pd
from io import BytesIO
import os
import logging
from urllib.parse import unquote
from botocore.exceptions import ClientError, NoCredentialsError

from config.settings import settings

logger = logging.getLogger(__name__)

def read_excel_file_from_s3_to_dataframe(s3_key, filename):
    """
    Read an Excel file from S3 into a pandas DataFrame using centralized settings

    Parameters:
    - s3_key: S3 key or full S3 URL to the file
    - filename: Original filename for extension validation

    Returns:
    - pandas DataFrame

    Uses centralized settings from src.config.settings
    """
    try:
        # Get credentials and S3 details from centralized settings
        aws_access_key_id = settings.aws_access_key_id
        aws_secret_access_key = settings.aws_secret_access_key
        aws_region = settings.aws_region
        bucket_name = settings.s3_bucket_name
        allowed_extensions = settings.allowed_extensions

        # Validate settings
        if not all([aws_access_key_id, aws_secret_access_key, bucket_name]):
            raise ValueError("Missing required AWS settings: aws_access_key_id, aws_secret_access_key, or s3_bucket_name")

        if not s3_key:
            raise ValueError("S3 key cannot be empty")

        if not filename:
            raise ValueError("Filename cannot be empty")

        # Validate file extension
        _validate_excel_file_extension(filename, allowed_extensions)

        # Validate filename pattern
        _validate_filename_pattern(filename)

        # Extract S3 key from URL if needed and decode URL encoding
        processed_key = _extract_and_decode_s3_key(s3_key)
        logger.info(f"Processing S3 key: {processed_key}")

        # Create S3 client with region
        s3 = boto3.client('s3',
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         region_name=aws_region)

        # Check if object exists
        try:
            s3.head_object(Bucket=bucket_name, Key=processed_key)
            logger.info(f"S3 object found: s3://{bucket_name}/{processed_key}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                raise FileNotFoundError(f"S3 object not found: s3://{bucket_name}/{processed_key}")
            else:
                raise Exception(f"Error accessing S3 object: {e}")

        # Get the object from S3
        response = s3.get_object(Bucket=bucket_name, Key=processed_key)
        file_content = response['Body'].read()

        logger.info(f"Successfully downloaded Excel file from S3. Size: {len(file_content)} bytes")

        # Read Excel file only
        try:
            df = pd.read_excel(BytesIO(file_content), engine='openpyxl')
            logger.info(f"Successfully parsed Excel file. Shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error parsing Excel file: {e}")
            raise ValueError(f"Failed to parse Excel file: {str(e)}. Please ensure the file is a valid Excel format.")

    except NoCredentialsError:
        raise Exception("AWS credentials not found. Please check your environment variables.")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        raise Exception(f"AWS S3 error ({error_code}): {error_message}")
    except Exception as e:
        logger.error(f"Error reading file from S3: {str(e)}")
        raise Exception(f"Failed to read file from S3: {str(e)}")

def _extract_and_decode_s3_key(s3_path: str) -> str:
    """
    Extract S3 key from full URL or return as-is if already a key, and decode URL encoding

    Parameters:
    - s3_path: S3 URL or key

    Returns:
    - Decoded S3 key
    """
    try:
        if s3_path.startswith('https://'):
            # Extract key from URL like: https://bucket.s3.region.amazonaws.com/key/path
            parts = s3_path.split('/')
            if len(parts) > 3:
                key = '/'.join(parts[3:])  # Everything after the domain
            else:
                raise ValueError(f"Invalid S3 URL format: {s3_path}")
        else:
            key = s3_path  # Already a key

        # Decode URL encoding (e.g., %20 -> space, + -> space)
        decoded_key = unquote(key).replace('+', ' ')
        logger.info(f"Extracted and decoded S3 key: '{decoded_key}' from input: '{s3_path}'")
        return decoded_key

    except Exception as e:
        logger.error(f"Error extracting S3 key from: {s3_path}. Error: {e}")
        raise ValueError(f"Invalid S3 path format: {s3_path}")

def _validate_excel_file_extension(filename: str, allowed_extensions: str) -> None:
    """
    Validate that the file has an allowed Excel extension

    Parameters:
    - filename: Name of the file to validate
    - allowed_extensions: Comma-separated string of allowed extensions

    Raises:
    - ValueError: If file extension is not allowed
    """
    if not filename:
        raise ValueError("Filename cannot be empty")

    # Get file extension
    _, ext = os.path.splitext(filename.lower())

    # Parse allowed extensions
    allowed_ext_list = [ext.strip().lower() for ext in allowed_extensions.split(',')]

    if ext not in allowed_ext_list:
        raise ValueError(
            f"Invalid file extension '{ext}'. Only Excel files are supported. "
            f"Allowed extensions: {', '.join(allowed_ext_list)}"
        )

    logger.info(f"File extension validation passed for: {filename} (extension: {ext})")

def _validate_filename_pattern(filename: str) -> None:
    """
    Validate that filename contains one of the allowed patterns

    Parameters:
    - filename: Name of the file to validate

    Raises:
    - ValueError: If filename doesn't contain any allowed patterns
    """
    # Import here to avoid circular imports
    from src.config.file_name_pattrens_configs import file_name_patterns

    if not filename:
        raise ValueError("Filename cannot be empty")

    # Check if filename contains any of the allowed patterns (case-insensitive)
    filename_lower = filename.lower()
    matched_pattern = None

    for pattern in file_name_patterns:
        if pattern.lower() in filename_lower:
            matched_pattern = pattern
            break

    if matched_pattern:
        logger.info(f"Filename pattern validation passed: '{filename}' matches pattern '{matched_pattern}'")
    else:
        allowed_patterns = ', '.join(file_name_patterns)
        error_msg = f"Filename '{filename}' does not contain any allowed patterns. Allowed patterns: {allowed_patterns}"
        logger.error(error_msg)
        raise ValueError(error_msg)


