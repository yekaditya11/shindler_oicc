"""
Data cleaning and transformation utilities
"""

import pandas as pd
import numpy as np
import logging
import re
from config.column_mapping_configs import column_mappings
logger = logging.getLogger(__name__)

class DataCleaner:
    """Data cleaning and transformation utilities"""
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame, schema_type: str) -> pd.DataFrame:
        """Clean and transform DataFrame based on schema type"""
        
        logger.info(f"Cleaning DataFrame with {len(df)} rows for schema: {schema_type}")
        
        # Make a copy to avoid modifying original
        cleaned_df = df.copy()
        
        # Basic cleaning
        cleaned_df = DataCleaner._basic_cleaning(cleaned_df)
        
        # Schema-specific cleaning
        if schema_type == "ei_tech":
            cleaned_df = DataCleaner._clean_ei_tech(cleaned_df)
        elif schema_type == "srs":
            cleaned_df = DataCleaner._clean_srs(cleaned_df)
        elif schema_type == "ni_tct":
            cleaned_df = DataCleaner._clean_ni_tct(cleaned_df)
        
        logger.info(f"Cleaning completed. Final rows: {len(cleaned_df)}")
        return cleaned_df
    
    @staticmethod
    def _basic_cleaning(df: pd.DataFrame) -> pd.DataFrame:
        """Basic cleaning operations"""
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Strip whitespace from string columns
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            df[col] = df[col].astype(str).str.strip()
            # Replace 'nan' strings with actual NaN
            df[col] = df[col].replace(['nan', 'NaN', 'NULL', 'null', ''], np.nan)
        
        return df
    
    @staticmethod
    def _clean_dates(df: pd.DataFrame, date_columns: list) -> pd.DataFrame:
        """Clean date columns"""
        
        for col in date_columns:
            if col in df.columns:
                try:
                    # Try to parse dates
                    df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                except Exception as e:
                    logger.warning(f"Error parsing dates in column {col}: {e}")
        
        return df
    
    @staticmethod
    def _clean_numeric(df: pd.DataFrame, numeric_columns: list) -> pd.DataFrame:
        """Clean numeric columns"""
        
        for col in numeric_columns:
            if col in df.columns:
                try:
                    # Convert to numeric, coercing errors to NaN
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Error converting {col} to numeric: {e}")
        
        return df
    
    @staticmethod
    def _clean_ei_tech(df: pd.DataFrame) -> pd.DataFrame:
        """Clean EI Tech specific data"""
        
        # Date columns
        date_cols = ['Reported Date', 'Date Of Unsafe Event']
        df = DataCleaner._clean_dates(df, date_cols)
        
        # Numeric columns
        numeric_cols = ['Event ID', 'Reporter ID']
        df = DataCleaner._clean_numeric(df, numeric_cols)
        
        # Clean Yes/No columns
        yes_no_cols = ['Work Stopped', 'Event requires sanction']
        for col in yes_no_cols:
            if col in df.columns:
                df[col] = df[col].str.upper().replace({'YES': 'YES', 'NO': 'NO'})
        
        return df
    
    @staticmethod
    def _clean_srs(df: pd.DataFrame) -> pd.DataFrame:
        """Clean SRS specific data"""
        
        # Date columns
        date_cols = ['Reported Date', 'Date Of Unsafe Event']
        df = DataCleaner._clean_dates(df, date_cols)
        
        # Clean Yes/No columns
        yes_no_cols = ['Work Stopped', 'Stop Work NOGO Violation', 'Event requires sanction', 'Serious Near Miss']
        for col in yes_no_cols:
            if col in df.columns:
                df[col] = df[col].str.upper().replace({'YES': 'Yes', 'NO': 'No'})
        
        return df
    
    @staticmethod
    def _clean_ni_tct(df: pd.DataFrame) -> pd.DataFrame:
        """Clean NI TCT specific data"""
        
        # Date columns
        date_cols = ['Created On', 'Date and Time of Unsafe Event']
        df = DataCleaner._clean_dates(df, date_cols)
        
        # Numeric columns
        numeric_cols = ['Reporting ID', 'Location_Key', 'Branch_Key', 'No']
        df = DataCleaner._clean_numeric(df, numeric_cols)
        
        # Boolean columns
        if 'Has Attachment' in df.columns:
            df['Has Attachment'] = df['Has Attachment'].map({'True': True, 'False': False})

        return df

    @staticmethod
    def normalize_column_names(df: pd.DataFrame, schema_type: str) -> pd.DataFrame:
        """Normalize column names to match database schema"""


        # Get the mapping for this schema type
        column_mapping = column_mappings.get(schema_type, {})

        # If no specific mapping, use generic normalization
        if not column_mapping:
            for col in df.columns:
                normalized = re.sub(r'[^a-zA-Z0-9]', '_', col.lower())
                normalized = re.sub(r'_+', '_', normalized)
                normalized = normalized.strip('_')
                column_mapping[col] = normalized

        # Apply the mapping
        df = df.rename(columns=column_mapping)
        logger.info(f"Normalized {len(column_mapping)} columns for schema: {schema_type}")

        return df
