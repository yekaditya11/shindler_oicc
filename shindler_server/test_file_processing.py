#!/usr/bin/env python3
"""
Test script for File Processing with Tag-based Schema Detection (ID-based)
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/file-processing"

def test_file_processing_workflow():
    """Test the complete file processing workflow using IDs"""
    
    print("🧪 Testing File Processing with ID-based System")
    print("=" * 55)
    
    # Test data
    test_file = {
        "s3_key": "uploads/test_ei_tech_data.xlsx",
        "filename": "test_ei_tech_data.xlsx",
        "user_tags": ["ei_tech", "safety", "test"],
        "bucket_name": None  # Use default bucket
    }
    
    try:
        # Step 1: Create file record
        print("\n1️⃣ Creating file record...")
        create_response = requests.post(
            f"{API_BASE}/create-file",
            json=test_file,
            timeout=30
        )
        
        if create_response.status_code == 201:
            create_data = create_response.json()
            file_id = create_data['body']['file_id']
            print(f"✅ File record created successfully!")
            print(f"   File ID: {file_id}")
            print(f"   Filename: {create_data['body']['filename']}")
        else:
            print(f"❌ File creation failed: {create_response.text}")
            return
        
        # Step 2: Process file by ID
        print("\n2️⃣ Processing file by ID...")
        process_response = requests.post(
            f"{API_BASE}/process-file",
            json={"file_id": file_id},
            timeout=30
        )
        
        if process_response.status_code == 200:
            process_data = process_response.json()
            print(f"✅ File processed successfully!")
            print(f"   Detected type: {process_data['file_type']}")
            print(f"   Confidence: {process_data['confidence_score']}%")
            print(f"   Suggested tags: {process_data['suggested_tags']}")
            
            if process_data['existing_matches']:
                print(f"   Found {len(process_data['existing_matches'])} similar files")
        else:
            print(f"❌ Processing failed: {process_response.text}")
            return
        
        # Step 3: Validate tags
        print("\n3️⃣ Validating tags...")
        validation_response = requests.post(
            f"{API_BASE}/validate-tags",
            json={
                "file_id": file_id,
                "proposed_tags": test_file["user_tags"]
            },
            timeout=30
        )
        
        if validation_response.status_code == 200:
            validation_data = validation_response.json()
            print(f"✅ Tag validation completed!")
            print(f"   Valid: {validation_data['is_valid']}")
            if validation_data['conflicting_files']:
                print(f"   Conflicts found: {len(validation_data['conflicting_files'])}")
            if validation_data['suggested_corrections']:
                print(f"   Suggestions: {validation_data['suggested_corrections']}")
        else:
            print(f"❌ Tag validation failed: {validation_response.text}")
        
        # Step 4: Save tagged file
        print("\n4️⃣ Saving tagged file...")
        save_response = requests.post(
            f"{API_BASE}/save-tagged-file",
            json={
                "file_id": file_id,
                "user_tags": test_file["user_tags"]
            },
            timeout=30
        )
        
        if save_response.status_code == 201:
            save_data = save_response.json()
            print(f"✅ Tagged file saved successfully!")
            print(f"   File ID: {save_data['body']['file_id']}")
            print(f"   Tags: {save_data['body']['user_tags']}")
        else:
            print(f"❌ Saving failed: {save_response.text}")
        
        # Step 5: Get file info
        print("\n5️⃣ Getting file information...")
        info_response = requests.get(
            f"{API_BASE}/file/{file_id}",
            timeout=10
        )
        
        if info_response.status_code == 200:
            info_data = info_response.json()
            print(f"✅ File info retrieved!")
            print(f"   Filename: {info_data['filename']}")
            print(f"   File type: {info_data['file_type']}")
            print(f"   Tags: {info_data['user_tags']}")
        else:
            print(f"❌ File info failed: {info_response.text}")
        
        # Step 6: Get processing status
        print("\n6️⃣ Checking processing status...")
        status_response = requests.get(
            f"{API_BASE}/processing-status/{file_id}",
            timeout=10
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"✅ Status retrieved!")
            print(f"   Status: {status_data['status']}")
            print(f"   File type: {status_data['file_type']}")
            print(f"   Confidence: {status_data['confidence_score']}%")
        else:
            print(f"❌ Status check failed: {status_response.text}")
        
        # Step 7: Get schema matches
        print("\n7️⃣ Finding schema matches...")
        matches_response = requests.get(
            f"{API_BASE}/schema-matches/{file_id}",
            timeout=30
        )
        
        if matches_response.status_code == 200:
            matches_data = matches_response.json()
            print(f"✅ Schema matches found!")
            print(f"   Message: {matches_data['message']}")
            if matches_data['body']['matches']:
                print(f"   Matches: {len(matches_data['body']['matches'])}")
        else:
            print(f"❌ Schema matches failed: {matches_response.text}")
        
        print("\n🎉 All tests completed successfully!")
        return file_id
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_schema_template_creation():
    """Test creating a custom schema template"""
    
    print("\n🔧 Testing Schema Template Creation")
    print("=" * 40)
    
    template_data = {
        "template_name": "test_custom_ei_tech",
        "file_type": "ei_tech",
        "schema_structure": {
            "columns": ["event_type", "event_date", "location", "description", "severity"],
            "types": {
                "event_type": "object",
                "event_date": "datetime64[ns]",
                "location": "object",
                "description": "object",
                "severity": "object"
            }
        },
        "required_columns": ["event_type", "event_date", "location"],
        "optional_columns": ["description", "severity"],
        "confidence_threshold": 85
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/schema-templates",
            json=template_data,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Schema template created successfully!")
            print(f"   Template: {data['body']['template_name']}")
            print(f"   File type: {data['body']['file_type']}")
        else:
            print(f"❌ Template creation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating template: {e}")

def test_files_listing():
    """Test listing files"""
    
    print("\n📋 Testing Files Listing")
    print("=" * 25)
    
    try:
        # Test with no filters
        response = requests.get(
            f"{API_BASE}/files",
            params={"limit": 10},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Files retrieved!")
            print(f"   Total count: {data['total_count']}")
            
            if data['files']:
                print(f"   Sample files:")
                for file in data['files'][:3]:
                    print(f"     - {file['filename']} ({file['file_type']}) - ID: {file['file_id']}")
            else:
                print("   No files found")
        else:
            print(f"❌ Failed to retrieve files: {response.text}")
            
    except Exception as e:
        print(f"❌ Error listing files: {e}")

def test_error_handling():
    """Test error handling scenarios"""
    
    print("\n🚨 Testing Error Handling")
    print("=" * 25)
    
    # Test with invalid file ID
    try:
        response = requests.post(
            f"{API_BASE}/process-file",
            json={"file_id": "invalid_file_id"},
            timeout=10
        )
        
        if response.status_code == 500:
            print("✅ Error handling working correctly for invalid file ID")
        else:
            print(f"⚠️ Unexpected response for invalid file ID: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in error handling test: {e}")

def test_file_operations_by_id(file_id: str):
    """Test file operations using a specific file ID"""
    
    print(f"\n🔍 Testing File Operations for ID: {file_id}")
    print("=" * 50)
    
    try:
        # Get file info
        print("\n📄 Getting file information...")
        info_response = requests.get(f"{API_BASE}/file/{file_id}", timeout=10)
        
        if info_response.status_code == 200:
            info_data = info_response.json()
            print(f"✅ File info:")
            print(f"   Filename: {info_data['filename']}")
            print(f"   File type: {info_data['file_type']}")
            print(f"   Tags: {info_data['user_tags']}")
            print(f"   S3 Key: {info_data['s3_key']}")
        else:
            print(f"❌ Failed to get file info: {info_response.text}")
        
        # Get processing status
        print("\n📊 Getting processing status...")
        status_response = requests.get(f"{API_BASE}/processing-status/{file_id}", timeout=10)
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"✅ Processing status:")
            print(f"   Status: {status_data['status']}")
            print(f"   Confidence: {status_data['confidence_score']}%")
            print(f"   Error: {status_data['error_message'] or 'None'}")
        else:
            print(f"❌ Failed to get processing status: {status_response.text}")
        
        # Get schema matches
        print("\n🔗 Getting schema matches...")
        matches_response = requests.get(f"{API_BASE}/schema-matches/{file_id}", timeout=30)
        
        if matches_response.status_code == 200:
            matches_data = matches_response.json()
            print(f"✅ Schema matches:")
            print(f"   Found {len(matches_data['body']['matches'])} similar files")
            for match in matches_data['body']['matches'][:3]:  # Show first 3
                print(f"     - {match['matched_filename']} (ID: {match['matched_file_id']})")
        else:
            print(f"❌ Failed to get schema matches: {matches_response.text}")
            
    except Exception as e:
        print(f"❌ Error in file operations test: {e}")

def main():
    """Run all tests"""
    
    print("🚀 Starting File Processing API Tests (ID-based)")
    print("=" * 60)
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running and healthy")
        else:
            print("❌ Server is not responding properly")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8001")
        return
    
    # Run tests
    file_id = test_file_processing_workflow()
    test_schema_template_creation()
    test_files_listing()
    test_error_handling()
    
    # Test operations on the created file
    if file_id:
        test_file_operations_by_id(file_id)
    
    print("\n🏁 All tests completed!")
    print("\n📖 For more information, see FILE_PROCESSING_README.md")

if __name__ == "__main__":
    main() 