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
from controllers.file_upload_controller import insert_file_data,get_all_files,add_tab,update_file_id,delete_tab

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/files", tags=["File Upload"])

def analyze_file_content(df: pd.DataFrame, filename: str = "") -> str:
        for key_name in ["srs_raw","srs_agumented","srs_enriched"]:
            if key_name in filename.strip().lower():
                return key_name 
        return "unknown"
        
@router.post("/upload-analyze")
async def upload_and_analyze_file(tab_id:str,file: UploadFile = File(...)) -> Dict[str, Any]:
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
        
        file_id=1
        if file_type=="srs_enriched":
            file_id=2
        if file_type=="srs_agumented":
            file_id=3

        # insert_file_data(upload_file_name,file_id)
        update_file_id(tab_id,file_id,file_type)
        # Reset file position
        await file.seek(0)
        
        return {
            'success': True,
            "tab_id":tab_id,
            'file_id':file_id,
            'file_type': file_type,
            'filename': file.filename,
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
    

@router.get("/get-all-files")
def get_all_files_router():
    result=get_all_files()
    return result


@router.post("/add-tab") 
def add_tab_router(tab_name:str):
    result=add_tab(tab_name)
    return result


@router.post("/delete-tab")
def delete_tab_router(tab_id:int):
    result=delete_tab(tab_id)
    return result