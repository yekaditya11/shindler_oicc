"""
File Upload API Routes
FastAPI routes for handling Excel file uploads and determining dashboard types
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import Optional, Dict, Any
import pandas as pd
import io
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/files", tags=["File Upload"])

def analyze_file_content(df: pd.DataFrame, filename: str = "") -> str:
    """
    Analyze uploaded Excel file content and filename to determine dashboard type
    Returns: 'ei_tech', 'srs', 'ni_tct', or 'unknown'
    """
    # Convert filename to lowercase for case-insensitive comparison
    filename_lower = filename.lower().strip() if filename else ""
    
    # Convert column names to lowercase for case-insensitive comparison
    columns = [col.lower().strip() for col in df.columns]
    
    # Filename-based indicators (higher priority)
    filename_ei_tech_indicators = [
        'ei tech app', 'ei_tech', 'eitech', 'unsafe event - ei tech',
        'unsafe event ei tech', 'ei tech', 'electrical incident'
    ]
    
    filename_srs_indicators = [
        'unsafe event dump - srs', 'srs', 'safety reporting system',
        'unsafe event dump', 'dump - srs', 'srs app'
    ]
    
    filename_ni_tct_indicators = [
        'unsafe event- ni tct app', 'ni tct app', 'ni_tct', 'nitct',
        'unsafe event ni tct', 'ni tct', 'non-intrusive testing'
    ]
    
    # Check filename first (higher weight)
    filename_ei_tech_score = 0
    filename_srs_score = 0
    filename_ni_tct_score = 0
    
    for indicator in filename_ei_tech_indicators:
        if indicator in filename_lower:
            filename_ei_tech_score += 2  # Higher weight for filename matches
    
    for indicator in filename_srs_indicators:
        if indicator in filename_lower:
            filename_srs_score += 2
    
    for indicator in filename_ni_tct_indicators:
        if indicator in filename_lower:
            filename_ni_tct_score += 2
    
    # EI Tech specific indicators (for column analysis)
    ei_tech_indicators = [
        'ei tech', 'eitech', 'unsafe event', 'unsafe_event',
        'event type', 'event_type', 'electrical incident',
        'technology incident', 'ei_tech', 'electrical', 'power',
        'equipment failure', 'machinery incident'
    ]
    
    # SRS specific indicators
    srs_indicators = [
        'srs', 'safety reporting system', 'safety_reporting',
        'safety report', 'safety_report', 'incident report',
        'incident_report', 'safety event', 'accident',
        'near miss', 'hazard', 'risk assessment'
    ]
    
    # NI TCT specific indicators
    ni_tct_indicators = [
        'ni tct', 'nitct', 'non-intrusive', 'non_intrusive',
        'testing', 'tct', 'ni_tct', 'inspection',
        'non intrusive testing', 'test result', 'compliance',
        'audit', 'certification', 'validation'
    ]
    
    # Check for EI Tech indicators (column names)
    ei_tech_score = 0
    for indicator in ei_tech_indicators:
        for col in columns:
            if indicator in col:
                ei_tech_score += 1
    
    # Check for SRS indicators (column names)
    srs_score = 0
    for indicator in srs_indicators:
        for col in columns:
            if indicator in col:
                srs_score += 1
    
    # Check for NI TCT indicators (column names)
    ni_tct_score = 0
    for indicator in ni_tct_indicators:
        for col in columns:
            if indicator in col:
                ni_tct_score += 1
    
    # Also check content in the first few rows for additional context
    if len(df) > 0:
        # Get sample of text content from first 5 rows
        sample_content = ""
        for col in df.columns:
            if df[col].dtype == 'object':  # Text columns
                sample_values = df[col].head(5).astype(str).str.lower()
                sample_content += " " + " ".join(sample_values.tolist())
        
        # Check content indicators
        for indicator in ei_tech_indicators:
            if indicator in sample_content:
                ei_tech_score += 0.5  # Lower weight for content vs column names
        
        for indicator in srs_indicators:
            if indicator in sample_content:
                srs_score += 0.5
        
        for indicator in ni_tct_indicators:
            if indicator in sample_content:
                ni_tct_score += 0.5
    
    # Combine filename scores with column/content scores
    total_ei_tech_score = filename_ei_tech_score + ei_tech_score
    total_srs_score = filename_srs_score + srs_score
    total_ni_tct_score = filename_ni_tct_score + ni_tct_score
    
    # Determine the most likely type
    scores = {
        'ei_tech': total_ei_tech_score,
        'srs': total_srs_score,
        'ni_tct': total_ni_tct_score
    }
    
    max_score = max(scores.values())
    if max_score == 0:
        return 'unknown'
    
    # Log detection details for debugging
    logger.info(f"File detection for '{filename}': EI_Tech={total_ei_tech_score}, SRS={total_srs_score}, NI_TCT={total_ni_tct_score}")
    
    # Return the type with highest score
    for file_type, score in scores.items():
        if score == max_score:
            logger.info(f"Detected file type: {file_type} (score: {score})")
            return file_type
    
    logger.info("Could not determine file type - returning 'unknown'")
    return 'unknown'

@router.post("/upload-analyze")
async def upload_and_analyze_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload Excel file and analyze its content to determine dashboard type
    
    Returns:
    - file_type: Type of dashboard (ei_tech, srs, ni_tct, unknown)
    - available_dashboards: List of available dashboard options
    - filename: Original filename
    - file_info: Basic file information
    """
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400, 
                detail="Only Excel files (.xlsx, .xls) are supported"
            )
        
        # Read file content
        contents = await file.read()
        
        # Try to read as Excel file
        try:
            df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to read Excel file: {str(e)}"
            )
        
        # Analyze file content and filename
        file_type = analyze_file_content(df, file.filename)
        
        # Determine available dashboards based on file type
        available_dashboards = ['custom-dashboard']  # Always available
        
        if file_type == 'ei_tech':
            available_dashboards.insert(0, 'ei-tech-dashboard')
        elif file_type == 'srs':
            available_dashboards.insert(0, 'srs-dashboard')
        elif file_type == 'ni_tct':
            available_dashboards.insert(0, 'ni-tct-dashboard')
        else:
            # If unknown, show all options
            available_dashboards = [
                'ei-tech-dashboard',
                'srs-dashboard', 
                'ni-tct-dashboard',
                'custom-dashboard'
            ]
        
        # Basic file info
        file_info = {
            'filename': file.filename,
            'size': len(contents),
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'upload_time': datetime.now().isoformat()
        }
        
        # Reset file position
        await file.seek(0)
        
        return {
            'success': True,
            'file_type': file_type,
            'available_dashboards': available_dashboards,
            'filename': file.filename,
            'file_info': file_info,
            'message': f'File analyzed successfully. Detected as {file_type.upper().replace("_", " ")} type.' if file_type != 'unknown' else 'File uploaded successfully. Could not determine specific type.'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 