-- SQL script to create demo file processing tables
-- Run this directly in your PostgreSQL database

-- Create file_upload_sessions table
CREATE TABLE IF NOT EXISTS file_upload_sessions (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(100) NOT NULL UNIQUE,
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(500) NOT NULL,
    presigned_url VARCHAR(1000),
    upload_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    file_size INTEGER,
    content_type VARCHAR(100),
    user_tags JSON,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create file_processing_logs table
CREATE TABLE IF NOT EXISTS file_processing_logs (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(100) NOT NULL UNIQUE,
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(500),
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

-- Create tagged_files table
CREATE TABLE IF NOT EXISTS tagged_files (
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

-- Create schema_templates table
CREATE TABLE IF NOT EXISTS schema_templates (
    id SERIAL PRIMARY KEY,
    template_name VARCHAR(100) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    schema_structure JSON NOT NULL,
    required_columns JSON,
    optional_columns JSON,
    confidence_threshold INTEGER DEFAULT 80,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(template_name, file_type)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_file_upload_sessions_file_id ON file_upload_sessions(file_id);
CREATE INDEX IF NOT EXISTS idx_file_processing_logs_file_id ON file_processing_logs(file_id);
CREATE INDEX IF NOT EXISTS idx_tagged_files_file_id ON tagged_files(file_id);
CREATE INDEX IF NOT EXISTS idx_tagged_files_schema_hash ON tagged_files(schema_hash);
CREATE INDEX IF NOT EXISTS idx_schema_templates_file_type ON schema_templates(file_type);

-- Display created tables
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('file_upload_sessions', 'file_processing_logs', 'tagged_files', 'schema_templates')
ORDER BY table_name, ordinal_position;
