#!/usr/bin/env python3
"""
Test script for Presigned URL File Upload Workflow
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/file-processing"

def test_presigned_url_workflow():
    """Test the complete presigned URL file upload workflow"""
    
    print("🚀 Testing Presigned URL File Upload Workflow")
    print("=" * 55)
    
    # Test data
    test_file_info = {
        "filename": "test_ei_tech_data.xlsx",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "bucket_name": None  # Use default bucket
    }
    
    try:
        # Step 1: Generate presigned URL
        print("\n1️⃣ Generating presigned URL...")
        presigned_response = requests.post(
            f"{API_BASE}/presigned-url",
            json=test_file_info,
            timeout=30
        )
        
        if presigned_response.status_code == 200:
            presigned_data = presigned_response.json()
            file_id = presigned_data['file_id']
            presigned_url = presigned_data['presigned_url']
            s3_key = presigned_data['s3_key']
            
            print(f"✅ Presigned URL generated successfully!")
            print(f"   File ID: {file_id}")
            print(f"   Filename: {presigned_data['filename']}")
            print(f"   S3 Key: {s3_key}")
            print(f"   Expires at: {presigned_data['expires_at']}")
            print(f"   Upload method: {presigned_data['upload_method']}")
        else:
            print(f"❌ Presigned URL generation failed: {presigned_response.text}")
            return None
        
        # Step 2: Check upload session
        print("\n2️⃣ Checking upload session...")
        session_response = requests.get(
            f"{API_BASE}/upload-session/{file_id}",
            timeout=10
        )
        
        if session_response.status_code == 200:
            session_data = session_response.json()
            print(f"✅ Upload session retrieved!")
            print(f"   Status: {session_data['upload_status']}")
            print(f"   Content type: {session_data['content_type']}")
            print(f"   File size: {session_data['file_size'] or 'Not uploaded yet'}")
        else:
            print(f"❌ Session check failed: {session_response.text}")
        
        # Step 3: Simulate file upload (in real scenario, client would upload to presigned URL)
        print("\n3️⃣ Simulating file upload...")
        print(f"   In a real scenario, the client would:")
        print(f"   - Use the presigned URL: {presigned_url[:50]}...")
        print(f"   - Upload the file using PUT method")
        print(f"   - Call /upload-complete/{file_id} after successful upload")
        
        # Step 4: Mark upload as complete
        print("\n4️⃣ Marking upload as complete...")
        complete_response = requests.post(
            f"{API_BASE}/upload-complete/{file_id}",
            timeout=10
        )
        
        if complete_response.status_code == 200:
            complete_data = complete_response.json()
            print(f"✅ Upload marked as complete!")
            print(f"   Status: {complete_data['body']['status']}")
            print(f"   Message: {complete_data['body']['message']}")
        else:
            print(f"❌ Upload completion failed: {complete_response.text}")
        
        # Step 5: Process the uploaded file
        print("\n5️⃣ Processing uploaded file...")
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
        
        # Step 6: Validate tags
        print("\n6️⃣ Validating tags...")
        validation_response = requests.post(
            f"{API_BASE}/validate-tags",
            json={
                "file_id": file_id,
                "proposed_tags": ["ei_tech", "safety", "test"]
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
        
        # Step 7: Save tagged file
        print("\n7️⃣ Saving tagged file...")
        save_response = requests.post(
            f"{API_BASE}/save-tagged-file",
            json={
                "file_id": file_id,
                "user_tags": ["ei_tech", "safety", "test"]
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
        
        # Step 8: Get final file info
        print("\n8️⃣ Getting final file information...")
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
            print(f"   S3 Key: {info_data['s3_key']}")
        else:
            print(f"❌ File info failed: {info_response.text}")
        
        print("\n🎉 Complete presigned URL workflow test successful!")
        return file_id
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    return None

def test_presigned_url_features():
    """Test additional presigned URL features"""
    
    print("\n🔧 Testing Presigned URL Features")
    print("=" * 40)
    
    # Test with different file types
    test_cases = [
        {
            "filename": "safety_report.xlsx",
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        },
        {
            "filename": "incident_data.xls",
            "content_type": "application/vnd.ms-excel"
        },
        {
            "filename": "test_data.csv",
            "content_type": "text/csv"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📁 Test case {i}: {test_case['filename']}")
        
        try:
            response = requests.post(
                f"{API_BASE}/presigned-url",
                json=test_case,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Generated for: {data['filename']}")
                print(f"   File ID: {data['file_id']}")
                print(f"   Content type: {data.get('content_type', 'auto-detected')}")
                print(f"   Expires in: 1 hour")
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_upload_session_management():
    """Test upload session management"""
    
    print("\n📊 Testing Upload Session Management")
    print("=" * 45)
    
    # Create a test upload session
    test_file = {
        "filename": "session_test.xlsx",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }
    
    try:
        # Generate presigned URL
        response = requests.post(
            f"{API_BASE}/presigned-url",
            json=test_file,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            file_id = data['file_id']
            
            print(f"✅ Created upload session: {file_id}")
            
            # Check session status
            session_response = requests.get(
                f"{API_BASE}/upload-session/{file_id}",
                timeout=10
            )
            
            if session_response.status_code == 200:
                session_data = session_response.json()
                print(f"   Status: {session_data['upload_status']}")
                print(f"   Created: {session_data['created_at']}")
                print(f"   Expires: {session_data['expires_at']}")
            
            # Mark as complete
            complete_response = requests.post(
                f"{API_BASE}/upload-complete/{file_id}",
                timeout=10
            )
            
            if complete_response.status_code == 200:
                print(f"   ✅ Marked as complete")
                
                # Check updated status
                updated_session = requests.get(
                    f"{API_BASE}/upload-session/{file_id}",
                    timeout=10
                )
                
                if updated_session.status_code == 200:
                    updated_data = updated_session.json()
                    print(f"   Updated status: {updated_data['upload_status']}")
            else:
                print(f"   ❌ Failed to mark complete: {complete_response.text}")
                
        else:
            print(f"❌ Failed to create session: {response.text}")
            
    except Exception as e:
        print(f"❌ Error in session management test: {e}")

def test_error_handling():
    """Test error handling for presigned URL workflow"""
    
    print("\n🚨 Testing Error Handling")
    print("=" * 25)
    
    # Test with invalid file ID
    try:
        response = requests.get(
            f"{API_BASE}/upload-session/invalid_file_id",
            timeout=10
        )
        
        if response.status_code == 404:
            print("✅ Error handling working correctly for invalid file ID")
        else:
            print(f"⚠️ Unexpected response for invalid file ID: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in error handling test: {e}")
    
    # Test with invalid upload completion
    try:
        response = requests.post(
            f"{API_BASE}/upload-complete/invalid_file_id",
            timeout=10
        )
        
        if response.status_code == 500:
            print("✅ Error handling working correctly for invalid upload completion")
        else:
            print(f"⚠️ Unexpected response for invalid upload completion: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in upload completion test: {e}")

def main():
    """Run all tests"""
    
    print("🚀 Starting Presigned URL File Upload Tests")
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
    file_id = test_presigned_url_workflow()
    test_presigned_url_features()
    test_upload_session_management()
    test_error_handling()
    
    print("\n🏁 All presigned URL tests completed!")
    print("\n📖 For more information, see FILE_PROCESSING_README.md")
    
    if file_id:
        print(f"\n💡 Test file ID for reference: {file_id}")

if __name__ == "__main__":
    main() 