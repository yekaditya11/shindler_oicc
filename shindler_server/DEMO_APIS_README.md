# Demo File Processing APIs (Cleaned Up)

This document describes the streamlined demo-focused file processing APIs that work with file IDs and user-provided tags for schema conflict detection.

## Overview

The demo APIs are designed to:
1. Allow users to upload files with tags directly
2. Detect schema conflicts with previously tagged files
3. Warn users when similar schemas have different tags
4. Work entirely with file IDs for easy integration
5. Provide a simple file listing interface

**✅ Cleaned Up**: Removed all unnecessary file processing endpoints, keeping only the essential ones for the demo workflow.

## API Endpoints (Final List)

### 1. Generate Presigned URL
**POST** `/file-processing/presigned-url`

Generate a presigned URL for direct S3 upload (standard endpoint).

**Request Body:**
```json
{
    "filename": "safety_report_jan.xlsx",
    "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}
```

### 2. Mark Upload Complete
**POST** `/file-processing/upload-complete/{file_id}`

Mark file upload as complete after uploading to S3.

### 3. Upload File with Tags (Demo Endpoint)
**POST** `/file-processing/upload-with-tags`

Upload a file to S3 with user-provided tags.

**Request Body:**
```json
{
    "filename": "safety_report_jan.xlsx",
    "user_tags": ["safety", "monthly", "production"],
    "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Upload URL generated with tags",
    "body": {
        "file_id": "file_abc123",
        "upload_url": "https://s3.amazonaws.com/...",
        "s3_key": "files/file_abc123_safety_report_jan.xlsx",
        "user_tags": ["safety", "monthly", "production"],
        "expires_at": "2024-01-01T12:00:00Z"
    }
}
```

### 4. Process File with Schema Check (Demo Endpoint)
**POST** `/file-processing/process-with-schema-check/{file_id}`

Process uploaded file and check for schema conflicts with existing tagged files.

**Response:**
```json
{
    "success": true,
    "message": "File processed with schema analysis",
    "body": {
        "file_id": "file_abc123",
        "detected_schema": {
            "columns": ["Date", "Event", "Severity"],
            "schema_hash": "abc123def456"
        },
        "file_type": "safety_report",
        "confidence_score": 95,
        "user_tags": ["safety", "monthly", "production"],
        "schema_conflicts": [
            {
                "file_id": "file_xyz789",
                "filename": "previous_safety.xlsx",
                "existing_tags": ["safety", "weekly", "testing"],
                "your_tags": ["safety", "monthly", "production"],
                "schema_similarity": 98.5
            }
        ],
        "proceed_warning": "Found 1 file(s) with similar schema but different tags. Would you like to proceed?",
        "has_conflicts": true,
        "suggested_tags": ["safety", "weekly", "testing"]
    }
}
```

### 5. Confirm File Tags (Demo Endpoint)
**POST** `/file-processing/confirm-tags/{file_id}`

Confirm and save file with user tags after reviewing schema conflicts.

**Request Body:**
```json
{
    "confirmed_tags": ["safety", "monthly", "production"],
    "proceed_despite_conflicts": true
}
```

**Response:**
```json
{
    "success": true,
    "message": "File tags confirmed and saved successfully",
    "body": {
        "file_id": "file_abc123",
        "confirmed_tags": ["safety", "monthly", "production"],
        "proceed_despite_conflicts": true,
        "status": "tagged_and_saved"
    }
}
```

### 6. Get File List (Demo Endpoint)
**GET** `/file-processing/files/list`

Get list of all file IDs with optional details.

**Query Parameters:**
- `limit`: Maximum number of results (default: 100)
- `offset`: Number of results to skip (default: 0)
- `include_details`: Include file details like tags and schema info (default: false)

**Response (with details):**
```json
{
    "success": true,
    "message": "Retrieved 2 file(s)",
    "body": {
        "files": [
            {
                "file_id": "file_abc123",
                "filename": "safety_report_jan.xlsx",
                "user_tags": ["safety", "monthly", "production"],
                "file_type": "safety_report",
                "upload_status": "uploaded",
                "created_at": "2024-01-01T10:00:00Z"
            },
            {
                "file_id": "file_xyz789",
                "filename": "safety_report_feb.xlsx",
                "user_tags": ["safety", "weekly", "testing"],
                "file_type": "safety_report",
                "upload_status": "uploaded",
                "created_at": "2024-01-02T10:00:00Z"
            }
        ],
        "total_count": 2,
        "limit": 100,
        "offset": 0,
        "include_details": true
    }
}
```

## Demo Workflow

1. **Upload File with Tags**: User uploads a file and specifies the tags they want to associate with it
2. **Upload to S3**: Client uses the presigned URL to upload the file directly to S3
3. **Mark Upload Complete**: Call `/upload-complete/{file_id}` to mark the upload as finished
4. **Process with Schema Check**: System analyzes the file schema and checks for conflicts with existing files
5. **Review Conflicts**: If conflicts exist, user reviews the warning and decides whether to proceed
6. **Confirm Tags**: User confirms their tags, and the file is saved to the database for future schema matching
7. **List Files**: User can retrieve all file IDs and their associated information

## Database Changes

The system now includes a `user_tags` JSON column in the `file_upload_sessions` table to store user-provided tags during the upload process.

## Running the Demo

1. **Run Migration**: Execute the migration script to add the user_tags column:
   ```bash
   python migrate_add_user_tags.py
   ```

2. **Start Server**: Start your FastAPI server

3. **Run Demo Test**: Execute the demo test script:
   ```bash
   python test_demo_apis.py
   ```

## Removed Endpoints

The following endpoints were removed to keep only the essential demo APIs:
- ❌ `/get-upload-session/{file_id}` - Not needed for demo
- ❌ `/create-file` - Replaced by upload-with-tags
- ❌ `/process-file` - Replaced by process-with-schema-check
- ❌ `/validate-tags` - Integrated into process-with-schema-check
- ❌ `/save-tagged-file` - Replaced by confirm-tags
- ❌ `/file/{file_id}` - Use files/list instead
- ❌ `/processing-status/{file_id}` - Not needed for demo
- ❌ `/schema-matches/{file_id}` - Integrated into process-with-schema-check
- ❌ `/schema-templates` - Not needed for demo

## Key Features for Demo

- **File ID-based Operations**: All operations work with file IDs, making integration simple
- **Tag-based Schema Conflict Detection**: Automatically detects when similar schemas have different tags
- **User-friendly Warnings**: Clear messages about potential conflicts
- **No Real-time Database Ingestion**: Files are processed and tagged but not ingested into production tables
- **Simple File Management**: Easy listing and retrieval of all processed files
- **Streamlined API**: Only 7 endpoints total, focused on demo workflow
