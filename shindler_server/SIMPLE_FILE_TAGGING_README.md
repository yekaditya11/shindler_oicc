# Simple File Tagging System

A straightforward file processing system that matches uploaded files against existing schema patterns and allows users to add new patterns when needed.

## Core Use Case

1. **User uploads file** → System checks against existing schema patterns
2. **If match found** → Show recommendation and let user confirm
3. **If no match** → Ask user if they want to add new schema pattern
4. **Keep it simple** → No over-engineering, just basic pattern matching

## API Endpoints

### 1. Upload File
**POST** `/file-processing/upload-and-check-schema`

Upload a file and get ready for schema checking.

**Request:**
```json
{
    "filename": "safety_report.xlsx",
    "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}
```

**Response:**
```json
{
    "success": true,
    "body": {
        "file_id": "file_abc123",
        "upload_url": "https://s3.amazonaws.com/...",
        "next_step": "After uploading, call POST /file-processing/check-schema/file_abc123"
    }
}
```

### 2. Check Schema Pattern
**POST** `/file-processing/check-schema/{file_id}`

Check if the uploaded file matches any existing schema patterns.

**Response (Match Found):**
```json
{
    "success": true,
    "body": {
        "file_id": "file_abc123",
        "matched_schema": "ei_tech",
        "confidence": 85,
        "recommendation": "This file matches the 'ei_tech' schema pattern with 85% confidence.",
        "action": "confirm_schema",
        "next_step": "Call POST /file-processing/confirm-schema/file_abc123"
    }
}
```

**Response (No Match):**
```json
{
    "success": true,
    "body": {
        "file_id": "file_abc123",
        "message": "No existing schema pattern matches this file well.",
        "action": "add_new_schema",
        "next_step": "Call POST /file-processing/add-schema-pattern with new schema details"
    }
}
```

### 3. Confirm Schema Pattern
**POST** `/file-processing/confirm-schema/{file_id}`

Confirm the detected schema pattern and save the file with tags.

**Request:**
```json
{
    "schema_name": "ei_tech",
    "user_tags": ["safety", "monthly", "production"]
}
```

**Response:**
```json
{
    "success": true,
    "body": {
        "file_id": "file_abc123",
        "schema_name": "ei_tech",
        "user_tags": ["safety", "monthly", "production"],
        "status": "confirmed_and_saved"
    }
}
```

### 4. Add New Schema Pattern
**POST** `/file-processing/add-schema-pattern`

Add a new schema pattern to the system for future matching.

**Request:**
```json
{
    "schema_name": "maintenance_log",
    "columns": ["Date", "Equipment", "Maintenance Type", "Technician", "Status"],
    "description": "Equipment maintenance tracking log"
}
```

**Response:**
```json
{
    "success": true,
    "body": {
        "schema_name": "maintenance_log",
        "columns": ["Date", "Equipment", "Maintenance Type", "Technician", "Status"],
        "status": "added",
        "note": "Schema pattern added to system. Files can now be matched against this pattern."
    }
}
```

## Simple Workflow

```
1. User uploads file
   ↓
2. System reads file columns
   ↓
3. Matches against existing SCHEMA_PATTERNS
   ↓
4a. MATCH FOUND (>50% confidence)
    → Show recommendation
    → User confirms schema + adds tags
    → File saved with schema type
   
4b. NO MATCH FOUND (<50% confidence)
    → Ask user to add new schema pattern
    → User provides schema name + column list
    → New pattern added to system
```

## Key Features

✅ **Simple & Straightforward** - No over-engineering  
✅ **Schema Pattern Matching** - Uses your existing SCHEMA_PATTERNS config  
✅ **Case-Insensitive** - Handles column name variations  
✅ **Extensible** - Easy to add new schema patterns  
✅ **File ID Based** - Clean file management  

## Testing

Run the test script to see the system in action:

```bash
/Users/ajay/miniconda3/envs/schindler/bin/python test_simple_apis.py
```

## Configuration

Schema patterns are defined in `config/schema_patterns_configs.py`:

```python
SCHEMA_PATTERNS = {
    "ei_tech": ["Event ID", "Reporter Name", "Reported Date", ...],
    "srs": ["Event Id", "Reporter Name", "Reported Date", ...],
    "ni_tct": ["Reporting ID", "Status", "Location", ...]
}
```

## Database Tables

- `file_upload_sessions` - Tracks file uploads
- `tagged_files` - Stores confirmed files with schema types and tags

That's it! Simple, clean, and focused on your core use case. 🎯
