#!/usr/bin/env python3
"""
Test script for the simplified file processing APIs
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class SimpleAPITester:
    """Test class for simple file processing APIs"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_upload_and_check_schema(self, filename: str) -> dict:
        """Test the upload-and-check-schema endpoint"""
        logger.info(f"Testing upload and schema check: {filename}")
        
        url = f"{self.base_url}/file-processing/upload-and-check-schema"
        payload = {
            "filename": filename,
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
    
    def test_check_schema(self, file_id: str) -> dict:
        """Test the check-schema endpoint"""
        logger.info(f"Testing schema check for file: {file_id}")
        
        url = f"{self.base_url}/file-processing/check-schema/{file_id}"
        response = self.session.post(url)
        
        if response.status_code == 200:
            result = response.json()
            body = result['body']
            logger.info(f"✅ Schema check complete!")
            logger.info(f"   Action: {body['action']}")
            if body['action'] == 'confirm_schema':
                logger.info(f"   Matched Schema: {body['matched_schema']} ({body['confidence']}%)")
                logger.info(f"   Recommendation: {body['recommendation']}")
            else:
                logger.info(f"   Message: {body['message']}")
            return body
        else:
            logger.error(f"❌ Schema check failed: {response.status_code} - {response.text}")
            return {}
    
    def test_confirm_schema(self, file_id: str, schema_name: str, user_tags: list) -> bool:
        """Test the confirm-schema endpoint"""
        logger.info(f"Testing schema confirmation for file: {file_id}")
        
        url = f"{self.base_url}/file-processing/confirm-schema/{file_id}"
        payload = {
            "schema_name": schema_name,
            "user_tags": user_tags
        }
        
        response = self.session.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Schema confirmed and saved!")
            return True
        else:
            logger.error(f"❌ Schema confirmation failed: {response.status_code} - {response.text}")
            return False
    
    def test_add_schema_pattern(self, schema_name: str, columns: list, description: str = "") -> bool:
        """Test the add-schema-pattern endpoint"""
        logger.info(f"Testing add schema pattern: {schema_name}")
        
        url = f"{self.base_url}/file-processing/add-schema-pattern"
        payload = {
            "schema_name": schema_name,
            "columns": columns,
            "description": description
        }
        
        response = self.session.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Schema pattern added!")
            return True
        else:
            logger.error(f"❌ Add schema pattern failed: {response.status_code} - {response.text}")
            return False

def run_simple_demo():
    """Run a simple demo test scenario"""
    tester = SimpleAPITester()
    
    print("🚀 Starting Simple File Processing Demo")
    print("=" * 50)
    
    # Test 1: Upload file that should match existing schema
    print("\n📤 Test 1: Upload file that should match existing schema")
    upload1 = tester.test_upload_and_check_schema("safety_incident_report.xlsx")
    
    if not upload1:
        print("❌ Demo failed at upload step")
        return
    
    file_id_1 = upload1['file_id']
    print(f"   📋 File ID: {file_id_1}")
    
    # Test 2: Check schema (should find match)
    print("\n🔍 Test 2: Check schema pattern")
    schema_check1 = tester.test_check_schema(file_id_1)
    
    if schema_check1.get('action') == 'confirm_schema':
        # Test 3: Confirm the matched schema
        print("\n✅ Test 3: Confirm matched schema")
        tester.test_confirm_schema(
            file_id_1, 
            schema_check1['matched_schema'], 
            ['safety', 'incident', 'monthly']
        )
    
    # Test 4: Upload file that won't match existing schemas
    print("\n📤 Test 4: Upload file with new schema")
    upload2 = tester.test_upload_and_check_schema("custom_maintenance_log.xlsx")
    
    if upload2:
        file_id_2 = upload2['file_id']
        print(f"   📋 File ID: {file_id_2}")
        
        # Test 5: Check schema (should not find good match)
        print("\n🔍 Test 5: Check schema (expect no match)")
        schema_check2 = tester.test_check_schema(file_id_2)
        
        if schema_check2.get('action') == 'add_new_schema':
            # Test 6: Add new schema pattern
            print("\n➕ Test 6: Add new schema pattern")
            tester.test_add_schema_pattern(
                "maintenance_log",
                ["Date", "Equipment", "Maintenance Type", "Technician", "Status", "Notes"],
                "Equipment maintenance tracking log"
            )
    
    print("\n🎉 Simple demo completed!")
    print("=" * 50)
    print("\n📝 Summary of Simple APIs:")
    print("✅ POST /file-processing/upload-and-check-schema - Upload file")
    print("✅ POST /file-processing/check-schema/{file_id} - Check schema patterns")
    print("✅ POST /file-processing/confirm-schema/{file_id} - Confirm matched schema")
    print("✅ POST /file-processing/add-schema-pattern - Add new schema pattern")
    print("\n🎯 Simple workflow: Upload → Check → Confirm OR Add New Pattern")

if __name__ == "__main__":
    run_simple_demo()
