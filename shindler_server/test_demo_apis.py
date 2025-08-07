#!/usr/bin/env python3
"""
Test script for the new demo file processing APIs
"""

import asyncio
import json
import logging
import requests
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class DemoAPITester:
    """Test class for demo file processing APIs"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_upload_with_tags(self, filename: str, user_tags: list) -> Dict[str, Any]:
        """Test the upload-with-tags endpoint"""
        logger.info(f"Testing upload with tags: {filename} -> {user_tags}")
        
        url = f"{self.base_url}/file-processing/upload-with-tags"
        payload = {
            "filename": filename,
            "user_tags": user_tags,
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        
        response = self.session.post(url, json=payload)

        if response.status_code in [200, 201]:
            result = response.json()
            logger.info(f"✅ Upload successful! File ID: {result['body']['file_id']}")
            return result['body']
        else:
            logger.error(f"❌ Upload failed: {response.status_code} - {response.text}")
            return {}
    
    def test_process_with_schema_check(self, file_id: str) -> Dict[str, Any]:
        """Test the process-with-schema-check endpoint"""
        logger.info(f"Testing schema check for file: {file_id}")
        
        url = f"{self.base_url}/file-processing/process-with-schema-check/{file_id}"
        response = self.session.post(url)
        
        if response.status_code == 200:
            result = response.json()
            body = result['body']
            logger.info(f"✅ Schema check complete!")
            logger.info(f"   File type: {body['file_type']}")
            logger.info(f"   User tags: {body['user_tags']}")
            logger.info(f"   Has conflicts: {body['has_conflicts']}")
            if body['has_conflicts']:
                logger.info(f"   Conflicts: {len(body['schema_conflicts'])}")
                logger.info(f"   Warning: {body['proceed_warning']}")
            return body
        else:
            logger.error(f"❌ Schema check failed: {response.status_code} - {response.text}")
            return {}
    
    def test_confirm_tags(self, file_id: str, confirmed_tags: list, proceed_despite_conflicts: bool = True) -> bool:
        """Test the confirm-tags endpoint"""
        logger.info(f"Testing tag confirmation for file: {file_id}")
        
        url = f"{self.base_url}/file-processing/confirm-tags/{file_id}"
        payload = {
            "confirmed_tags": confirmed_tags,
            "proceed_despite_conflicts": proceed_despite_conflicts
        }
        
        response = self.session.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Tags confirmed and saved!")
            return True
        else:
            logger.error(f"❌ Tag confirmation failed: {response.status_code} - {response.text}")
            return False
    
    def test_get_file_list(self, include_details: bool = False) -> Dict[str, Any]:
        """Test the file list endpoint"""
        logger.info(f"Testing file list (include_details={include_details})")
        
        url = f"{self.base_url}/file-processing/files/list"
        params = {"include_details": include_details, "limit": 10}
        
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            result = response.json()
            files = result['body']['files']
            logger.info(f"✅ Retrieved {len(files)} files")
            for file in files[:3]:  # Show first 3 files
                logger.info(f"   - {file['file_id']}: {file['filename']}")
            return result['body']
        else:
            logger.error(f"❌ File list failed: {response.status_code} - {response.text}")
            return {}

def run_demo_test():
    """Run a complete demo test scenario"""
    tester = DemoAPITester()

    print("🚀 Starting Demo API Test Scenario")
    print("=" * 50)
    print("Note: This test requires the server to be running and database to be set up")
    print("Make sure to run: python migrate_add_user_tags.py first")

    # Test 1: Upload first file with tags
    print("\n📤 Test 1: Upload file with tags")
    upload1 = tester.test_upload_with_tags(
        filename="safety_report_jan.xlsx",
        user_tags=["safety", "monthly", "production"]
    )

    if not upload1:
        print("❌ Demo failed at upload step")
        return

    file_id_1 = upload1['file_id']
    print(f"   📋 File ID: {file_id_1}")

    # Note: In real usage, client would upload file to S3 using the presigned URL
    # For demo, we'll simulate marking upload complete
    print("\n📤 Test 1b: Mark upload complete")
    complete_url = f"{BASE_URL}/file-processing/upload-complete/{file_id_1}"
    response = tester.session.post(complete_url)
    if response.status_code == 200:
        print("✅ Upload marked as complete")
    else:
        print(f"❌ Failed to mark upload complete: {response.status_code}")

    # Test 2: Process file with schema check
    print("\n🔍 Test 2: Process file with schema check")
    schema_check1 = tester.test_process_with_schema_check(file_id_1)

    # Test 3: Confirm tags
    print("\n✅ Test 3: Confirm file tags")
    tester.test_confirm_tags(file_id_1, ["safety", "monthly", "production"])

    # Test 4: Upload second file with different tags but similar schema
    print("\n📤 Test 4: Upload second file (potential conflict)")
    upload2 = tester.test_upload_with_tags(
        filename="safety_report_feb.xlsx",
        user_tags=["safety", "weekly", "testing"]  # Different tags
    )

    if upload2:
        file_id_2 = upload2['file_id']
        print(f"   📋 File ID: {file_id_2}")

        # Mark second upload complete
        complete_url = f"{BASE_URL}/file-processing/upload-complete/{file_id_2}"
        tester.session.post(complete_url)

        # Test 5: Process second file (should show conflicts)
        print("\n🔍 Test 5: Process second file (expect conflicts)")
        schema_check2 = tester.test_process_with_schema_check(file_id_2)

        # Test 6: Confirm tags despite conflicts
        print("\n✅ Test 6: Confirm tags despite conflicts")
        tester.test_confirm_tags(file_id_2, ["safety", "weekly", "testing"], proceed_despite_conflicts=True)

    # Test 7: Get file list
    print("\n📋 Test 7: Get file list")
    tester.test_get_file_list(include_details=True)

    print("\n🎉 Demo test scenario completed!")
    print("=" * 50)
    print("\n📝 Summary of cleaned up APIs:")
    print("✅ POST /file-processing/presigned-url - Generate upload URL")
    print("✅ POST /file-processing/upload-complete/{file_id} - Mark upload done")
    print("✅ POST /file-processing/upload-with-tags - Upload with user tags")
    print("✅ POST /file-processing/process-with-schema-check/{file_id} - Check conflicts")
    print("✅ POST /file-processing/confirm-tags/{file_id} - Confirm final tags")
    print("✅ GET /file-processing/files/list - List all file IDs")
    print("✅ GET /file-processing/files - List tagged files (filtered)")
    print("\n🗑️  Removed all other file processing endpoints as requested")

if __name__ == "__main__":
    run_demo_test()
