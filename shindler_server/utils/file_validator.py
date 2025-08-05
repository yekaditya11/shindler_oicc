"""
File validation utilities for S3-based file processing
"""

import os
import pandas as pd
from typing import Tuple, Optional
import logging

from config.settings import settings
from config.schema_patterns_configs import SCHEMA_PATTERNS
from config.file_name_pattrens_configs import file_name_patterns
logger = logging.getLogger(__name__)

class FileValidator:
    """File validation and schema detection for S3-based Excel files"""
    

    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """Validate file extension"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in settings.allowed_extensions_list

    @staticmethod
    def validate_filename_pattern(filename: str) -> Tuple[bool, str]:
        """
        Validate that filename contains one of the allowed patterns

        Args:
            filename: Name of the file to validate

        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        if not filename:
            return False, "Filename cannot be empty"

        # Check if filename contains any of the allowed patterns (case-insensitive)
        # Note: file_name_patterns is ordered from most specific to least specific
        filename_lower = filename.lower()
        matched_pattern = None

        for pattern in file_name_patterns:
            if pattern.lower() in filename_lower:
                matched_pattern = pattern
                logger.info(f"Filename pattern matched: '{pattern}' in '{filename}'")
                break

        if matched_pattern:
            logger.info(f"Filename pattern validation passed: '{filename}' matches pattern '{matched_pattern}'")
            return True, f"Filename matches pattern: {matched_pattern}"
        else:
            allowed_patterns = ', '.join(file_name_patterns)
            error_msg = f"Filename '{filename}' does not contain any allowed patterns. Allowed patterns: {allowed_patterns}"
            logger.warning(error_msg)
            return False, error_msg

    @staticmethod
    def detect_schema_type(df: pd.DataFrame) -> Optional[str]:
        """Detect which schema type the DataFrame matches"""

        columns = df.columns.tolist()
        logger.info(f"Detecting schema for columns: {columns[:10]}...")  # Log first 10 columns

        # Check for augmented columns first (more specific schema)
        augmented_indicators = [
            'weather_weather_condition', 'employee_experience_level',
            'site_site_risk_category', 'workload_workload_category'
        ]

        has_augmented_columns = any(col in columns for col in augmented_indicators)
        logger.info(f"Augmented columns detected: {has_augmented_columns}")

        # Define schema priority order (most specific first)
        schema_priority = ['ni_tct_augmented', 'ni_tct', 'ei_tech', 'srs']

        best_match = None
        best_score = 0

        # If augmented columns are detected, prioritize ni_tct_augmented
        if has_augmented_columns:
            logger.info("Augmented columns found, checking ni_tct_augmented schema first")
            schema_priority = ['ni_tct_augmented'] + [s for s in schema_priority if s != 'ni_tct_augmented']

        for schema_type in schema_priority:
            if schema_type not in SCHEMA_PATTERNS:
                continue

            expected_columns = SCHEMA_PATTERNS[schema_type]

            # Calculate match score
            matches = sum(1 for col in expected_columns if col in columns)
            score = matches / len(expected_columns)

            logger.info(f"Schema {schema_type}: {matches}/{len(expected_columns)} matches (score: {score:.2f})")

            # For augmented schema, require higher threshold and check for augmented columns
            if schema_type == 'ni_tct_augmented':
                if score > 0.8 and has_augmented_columns:  # Higher threshold for augmented
                    best_score = score
                    best_match = schema_type
                    logger.info(f"Augmented schema matched with score: {score:.2f}")
                    break  # Stop here if augmented schema matches
            else:
                # For regular schemas, use standard threshold but avoid if augmented columns present
                if score > 0.6 and not (has_augmented_columns and schema_type == 'ni_tct'):
                    if score > best_score:
                        best_score = score
                        best_match = schema_type

        if best_match:
            logger.info(f"Final detected schema type: {best_match} (score: {best_score:.2f})")
        else:
            logger.warning("No matching schema detected")

        return best_match
    
    @staticmethod
    def validate_required_columns(df: pd.DataFrame, schema_type: str) -> Tuple[bool, str]:
        """Validate that required columns are present"""

        if schema_type not in SCHEMA_PATTERNS:
            return False, f"Unknown schema type: {schema_type}"

        expected_columns = SCHEMA_PATTERNS[schema_type]
        df_columns = df.columns.tolist()

        # Calculate match percentage
        matches = sum(1 for col in expected_columns if col in df_columns)
        match_percentage = (matches / len(expected_columns)) * 100

        logger.info(f"Column validation for {schema_type}: {matches}/{len(expected_columns)} columns matched ({match_percentage:.1f}%)")

        # For augmented schema, require at least 80% match
        # For regular schemas, require at least 60% match
        required_threshold = 80 if schema_type == 'ni_tct_augmented' else 60

        if match_percentage < required_threshold:
            missing_columns = [col for col in expected_columns if col not in df_columns]
            return False, f"Insufficient column match for {schema_type}: {match_percentage:.1f}% (required: {required_threshold}%). Missing: {missing_columns[:10]}..."

        return True, f"Column validation passed: {match_percentage:.1f}% match"
