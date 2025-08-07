# File Processing with Tag-based Schema Detection (ID-based)

This module provides comprehensive file processing capabilities with intelligent schema detection and tag-based validation. It uses a simple ID system to manage files, making the API much cleaner and easier to use.

## Features

### 🔍 **Intelligent Schema Detection**
- Automatically detects file types (ei_tech, srs, ni_tct, unknown)
- Analyzes file content, column names, and filenames
- Provides confidence scores for detection accuracy
- Supports custom schema templates

### 🏷️ **Tag-based Validation**
- Validates proposed tags against existing tagged files
- Identifies conflicting tags and suggests corrections
- Prevents inconsistent tagging across similar schemas
- Provides intelligent tag suggestions

### 📊 **Schema Matching**
- Finds files with similar schemas
- Tracks schema hashes for quick matching
- Maintains historical tagging patterns
- Enables data consistency across uploads

### 🔄 **S3 Integration**
- Seamless integration with AWS S3
- Supports file upload, download, and processing
- Handles large files efficiently
- Maintains file metadata and processing logs

### 🆔 **ID-based Management**
- Simple file ID system for easy reference
- No need to remember complex S3 keys
- Clean API endpoints using file IDs
- Automatic ID generation and management

## API Endpoints

### 1. Create File Record
**POST** `/file-processing/create-file`

Creates a new file record and returns a unique file ID.

**Request Body:**
```json
{
  "s3_key": "uploads/ei_tech_data.xlsx",
  "filename": "ei_tech_data.xlsx",
  "user_tags": ["ei_tech", "safety"],
  "bucket_name": "my-bucket" // optional
}
```

**Response:**
```json
{
  "status_code": 201,
  "message": "File record created successfully",
  "body": {
    "file_id": "file_a1b2c3d4e5f6",
    "filename": "ei_tech_data.xlsx",
    "s3_key": "uploads/ei_tech_data.xlsx"
  }
}
```

### 2. Process File by ID
**POST** `/file-processing/process-file`

Processes a file by ID and detects its schema with tag suggestions.

**Request Body:**
```json
{
  "file_id": "file_a1b2c3d4e5f6"
}
```

**Response:**
```json
{
  "success": true,
  "file_id": "file_a1b2c3d4e5f6",
  "file_type": "ei_tech",
  "detected_schema": {
    "columns": ["event_type", "event_date", "location", "description"],
    "total_rows": 150,
    "total_columns": 8,
    "schema_hash": "abc123...",
    "detected_type": "ei_tech",
    "confidence_score": 85,
    "sample_data": {...}
  },
  "confidence_score": 85,
  "suggested_tags": ["ei_tech", "safety", "unsafe_event"],
  "existing_matches": [
    {
      "matched_file_id": "file_x1y2z3a4b5c6",
      "matched_filename": "ei_tech_2023.xlsx",
      "matched_tags": ["ei_tech", "safety"],
      "confidence_score": 95,
      "schema_similarity": 100.0,
      "conflicting_tags": [],
      "suggested_tags": ["ei_tech", "safety"]
    }
  ],
  "message": "File processed successfully. Detected as ei_tech type."
}
```

### 3. Validate Tags
**POST** `/file-processing/validate-tags`

Validates proposed tags against existing tagged files to ensure consistency.

**Request Body:**
```json
{
  "file_id": "file_a1b2c3d4e5f6",
  "proposed_tags": ["ei_tech", "safety"]
}
```

**Response:**
```json
{
  "success": true,
  "is_valid": true,
  "conflicting_files": [],
  "suggested_corrections": [],
  "message": "Tag validation completed successfully."
}
```

### 4. Save Tagged File
**POST** `/file-processing/save-tagged-file`

Saves a file with user-assigned tags to the database for future schema matching.

**Request Body:**
```json
{
  "file_id": "file_a1b2c3d4e5f6",
  "user_tags": ["ei_tech", "safety", "2024"]
}
```

**Response:**
```json
{
  "status_code": 201,
  "message": "Tagged file saved successfully",
  "body": {
    "file_id": "file_a1b2c3d4e5f6",
    "user_tags": ["ei_tech", "safety", "2024"]
  }
}
```

### 5. Get File Information
**GET** `/file-processing/file/{file_id}`

Retrieves complete file information by ID.

**Response:**
```json
{
  "file_id": "file_a1b2c3d4e5f6",
  "filename": "ei_tech_data.xlsx",
  "s3_key": "uploads/ei_tech_data.xlsx",
  "file_type": "ei_tech",
  "user_tags": ["ei_tech", "safety"],
  "file_size": 1024000,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:05Z"
}
```

### 6. Get Processing Status
**GET** `/file-processing/processing-status/{file_id}`

Retrieves the processing status for a specific file ID.

**Response:**
```json
{
  "file_id": "file_a1b2c3d4e5f6",
  "filename": "ei_tech_data.xlsx",
  "status": "completed",
  "file_type": "ei_tech",
  "confidence_score": 85,
  "assigned_tags": ["ei_tech", "safety"],
  "error_message": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:05Z"
}
```

### 7. Get Schema Matches
**GET** `/file-processing/schema-matches/{file_id}`

Finds files with similar schemas for a given file ID.

**Response:**
```json
{
  "status_code": 200,
  "message": "Found 3 files with similar schemas",
  "body": {
    "file_id": "file_a1b2c3d4e5f6",
    "detected_schema": {...},
    "matches": [
      {
        "matched_file_id": "file_x1y2z3a4b5c6",
        "matched_filename": "ei_tech_2023.xlsx",
        "matched_tags": ["ei_tech", "safety"],
        "confidence_score": 95,
        "schema_similarity": 100.0,
        "conflicting_tags": [],
        "suggested_tags": ["ei_tech", "safety"]
      }
    ]
  }
}
```

### 8. Create Schema Template
**POST** `/file-processing/schema-templates`

Creates a custom schema template for better file type detection.

**Request Body:**
```json
{
  "template_name": "custom_ei_tech",
  "file_type": "ei_tech",
  "schema_structure": {
    "columns": ["event_type", "event_date", "location", "description"],
    "types": {"event_type": "object", "event_date": "datetime64[ns]"}
  },
  "required_columns": ["event_type", "event_date"],
  "optional_columns": ["severity", "equipment"],
  "confidence_threshold": 80
}
```

### 9. Get Files List
**GET** `/file-processing/files`

Retrieves a list of tagged files with optional filtering.

**Query Parameters:**
- `file_type`: Filter by file type (ei_tech, srs, ni_tct)
- `tag`: Filter by specific tag
- `limit`: Maximum number of results (default: 50)
- `offset`: Number of results to skip (default: 0)

**Response:**
```json
{
  "files": [
    {
      "file_id": "file_a1b2c3d4e5f6",
      "filename": "ei_tech_data.xlsx",
      "s3_key": "uploads/ei_tech_data.xlsx",
      "file_type": "ei_tech",
      "user_tags": ["ei_tech", "safety"],
      "file_size": 1024000,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:05Z"
    }
  ],
  "total_count": 25,
  "limit": 50,
  "offset": 0
}
```

## Database Schema

### FileProcessingLog
Tracks file processing and tag assignments.

```sql
CREATE TABLE file_processing_logs (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(100) NOT NULL UNIQUE,
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(500),  -- nullable for processing
    file_size INTEGER NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    detected_schema JSON,
    assigned_tags JSON,
    confidence_score INTEGER,
    processing_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### TaggedFile
Stores files with their tags for schema matching.

```sql
CREATE TABLE tagged_files (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(100) NOT NULL UNIQUE,
    s3_key VARCHAR(500) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    user_tags JSON NOT NULL,
    schema_hash VARCHAR(64),
    schema_structure JSON,
    sample_data JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### SchemaTemplate
Stores schema templates for different file types.

```sql
CREATE TABLE schema_templates (
    id SERIAL PRIMARY KEY,
    template_name VARCHAR(100) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    schema_structure JSON NOT NULL,
    required_columns JSON,
    optional_columns JSON,
    confidence_threshold INTEGER DEFAULT 80,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## Usage Examples

### 1. Upload and Process a File

```python
import requests

# Step 1: Upload file to S3 (using existing S3 upload endpoint)
upload_response = requests.post("/s3/generate-presigned-url")
# ... upload file to S3 using presigned URL

# Step 2: Create file record
create_response = requests.post("/file-processing/create-file", json={
    "s3_key": "uploads/ei_tech_data.xlsx",
    "filename": "ei_tech_data.xlsx",
    "user_tags": ["ei_tech", "safety"]
})

file_id = create_response.json()['body']['file_id']

# Step 3: Process the file
process_response = requests.post("/file-processing/process-file", json={
    "file_id": file_id
})

# Step 4: Validate tags
validation_response = requests.post("/file-processing/validate-tags", json={
    "file_id": file_id,
    "proposed_tags": ["ei_tech", "safety"]
})

# Step 5: Save tagged file
save_response = requests.post("/file-processing/save-tagged-file", json={
    "file_id": file_id,
    "user_tags": ["ei_tech", "safety"]
})
```

### 2. Check for Schema Conflicts

```python
# Get schema matches to see if similar files exist
matches_response = requests.get(f"/file-processing/schema-matches/{file_id}")

# If conflicts exist, validate tags before saving
if matches_response.json()["body"]["matches"]:
    validation = requests.post("/file-processing/validate-tags", json={
        "file_id": file_id,
        "proposed_tags": ["ei_tech", "safety"]
    })
    
    if not validation.json()["is_valid"]:
        print("Conflicting tags detected!")
        print("Suggested corrections:", validation.json()["suggested_corrections"])
```

### 3. Monitor Processing Status

```python
# Check processing status
status_response = requests.get(f"/file-processing/processing-status/{file_id}")
status = status_response.json()

if status["status"] == "completed":
    print(f"File processed successfully as {status['file_type']}")
    print(f"Confidence score: {status['confidence_score']}%")
elif status["status"] == "failed":
    print(f"Processing failed: {status['error_message']}")
```

### 4. Get File Information

```python
# Get complete file information
info_response = requests.get(f"/file-processing/file/{file_id}")
file_info = info_response.json()

print(f"Filename: {file_info['filename']}")
print(f"File type: {file_info['file_type']}")
print(f"Tags: {file_info['user_tags']}")
print(f"S3 Key: {file_info['s3_key']}")
```

## Configuration

### Environment Variables

Ensure these environment variables are set in your `.env` file:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=shindler_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

### Schema Templates

The system comes with predefined schema templates for common file types:

- **ei_tech**: Electrical incident and technology files
- **srs**: Safety reporting system files  
- **ni_tct**: Non-intrusive testing files

You can create custom templates using the `/file-processing/schema-templates` endpoint.

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: File or processing record not found
- **409 Conflict**: Schema template already exists
- **500 Internal Server Error**: Processing or database errors

All errors include detailed error messages and suggestions for resolution.

## Performance Considerations

- Schema detection uses efficient hashing for quick matching
- Database queries are optimized with proper indexing
- S3 operations are asynchronous and handle large files
- Processing logs are maintained for debugging and monitoring
- File IDs are generated using UUID for uniqueness

## Security Features

- S3 access is validated before processing
- File content is analyzed securely without storing sensitive data
- Database queries use parameterized statements
- Error messages don't expose internal system details
- File IDs are randomly generated and not predictable

## Monitoring and Logging

The system provides comprehensive logging:

- File processing events and results
- Schema detection confidence scores
- Tag validation conflicts and resolutions
- Error tracking and debugging information

All logs are structured and can be integrated with monitoring systems.

## Benefits of ID-based System

### 🎯 **Simplicity**
- No need to remember complex S3 keys
- Simple file ID format: `file_a1b2c3d4e5f6`
- Clean API endpoints

### 🔒 **Security**
- File IDs are randomly generated
- No exposure of internal S3 paths
- Better access control

### 📊 **Management**
- Easy file tracking and monitoring
- Simple file operations by ID
- Better user experience

### 🔄 **Flexibility**
- Can change S3 keys without affecting API
- Easy file migration and backup
- Better system architecture 