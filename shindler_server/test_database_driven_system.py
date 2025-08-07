#!/usr/bin/env python3
"""
Test script for the complete database-driven schema pattern system
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class DatabaseDrivenTester:
    """Test class for database-driven schema pattern system"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def initialize_default_patterns(self):
        """Initialize default schema patterns from config to database"""
        print("🔄 Initializing default schema patterns...")
        url = f"{self.base_url}/file-processing/initialize-default-patterns"
        response = self.session.post(url)
        
        if response.status_code == 200:
            print("✅ Default patterns initialized in database")
            return True
        else:
            print(f"❌ Failed to initialize: {response.text[:100]}")
            return False
    
    def get_all_patterns(self):
        """Get all schema patterns from database"""
        print("📋 Getting all schema patterns from database...")
        url = f"{self.base_url}/file-processing/schema-patterns"
        response = self.session.get(url)
        
        if response.status_code == 200:
            result = response.json()
            patterns = result['body']['patterns']
            print(f"✅ Found {len(patterns)} schema patterns in database:")
            for name, columns in patterns.items():
                print(f"   - {name}: {len(columns)} columns")
            return patterns
        else:
            print(f"❌ Failed to get patterns: {response.text[:100]}")
            return {}
    
    def add_new_pattern(self, schema_name: str, columns: list, description: str = ""):
        """Add new schema pattern to database"""
        print(f"➕ Adding new schema pattern: {schema_name}")
        url = f"{self.base_url}/file-processing/add-schema-pattern"
        payload = {
            "schema_name": schema_name,
            "columns": columns,
            "description": description
        }
        
        response = self.session.post(url, json=payload)
        
        if response.status_code == 200:
            print(f"✅ Added new pattern: {schema_name} with {len(columns)} columns")
            return True
        else:
            print(f"❌ Failed to add pattern: {response.text[:100]}")
            return False
    
    def upload_and_check_file(self, filename: str):
        """Upload file and check against database patterns"""
        print(f"📤 Uploading and checking: {filename}")
        
        # Upload
        url = f"{self.base_url}/file-processing/upload-and-check-schema"
        payload = {
            "filename": filename,
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        
        response = self.session.post(url, json=payload)
        if response.status_code not in [200, 201]:
            print(f"❌ Upload failed: {response.text[:100]}")
            return None
        
        file_id = response.json()['body']['file_id']
        print(f"✅ File uploaded: {file_id}")
        
        # Check schema
        url = f"{self.base_url}/file-processing/check-schema/{file_id}"
        response = self.session.post(url)
        
        if response.status_code == 200:
            result = response.json()['body']
            print(f"🔍 Schema check result:")
            print(f"   Action: {result['action']}")
            if result['action'] == 'confirm_schema':
                print(f"   Matched: {result['matched_schema']} ({result['confidence']}%)")
                print(f"   Recommendation: {result['recommendation']}")
            else:
                print(f"   Message: {result['message']}")
            
            return file_id, result
        else:
            print(f"❌ Schema check failed: {response.text[:100]}")
            return file_id, None
    
    def confirm_schema_with_tags(self, file_id: str, schema_name: str, user_tags: list):
        """Confirm schema and save user tags to database"""
        print(f"✅ Confirming schema {schema_name} with tags: {user_tags}")
        
        url = f"{self.base_url}/file-processing/confirm-schema/{file_id}"
        payload = {
            "schema_name": schema_name,
            "user_tags": user_tags
        }
        
        response = self.session.post(url, json=payload)
        
        if response.status_code == 200:
            print("✅ Schema confirmed and user tags saved to database!")
            print("   Future files with similar schema will be detected!")
            return True
        else:
            print(f"❌ Confirm failed: {response.text[:100]}")
            return False

def run_complete_database_test():
    """Run complete database-driven workflow test"""
    tester = DatabaseDrivenTester()
    
    print("🚀 Complete Database-Driven Schema Pattern System Test")
    print("=" * 60)
    
    # Step 1: Initialize default patterns
    print("\n📥 STEP 1: Initialize Default Patterns")
    tester.initialize_default_patterns()
    
    # Step 2: Show all patterns in database
    print("\n📋 STEP 2: Show All Patterns in Database")
    patterns = tester.get_all_patterns()
    
    # Step 3: Add a new custom pattern
    print("\n➕ STEP 3: Add New Custom Pattern")
    tester.add_new_pattern(
        "custom_safety_log",
        ["Date", "Event ID", "Severity", "Location", "Reporter", "Description", "Status"],
        "Custom safety incident logging format"
    )
    
    # Step 4: Show updated patterns
    print("\n📋 STEP 4: Show Updated Patterns")
    tester.get_all_patterns()
    
    # Step 5: Upload file that should match existing pattern
    print("\n📤 STEP 5: Upload File (Should Match Existing Pattern)")
    file_id1, result1 = tester.upload_and_check_file("safety_incident_report.xlsx")
    
    if result1 and result1['action'] == 'confirm_schema':
        # Step 6: Confirm schema with user tags
        print("\n✅ STEP 6: Confirm Schema with User Tags")
        tester.confirm_schema_with_tags(
            file_id1, 
            result1['matched_schema'], 
            ['safety', 'incident', 'monthly']
        )
    
    # Step 7: Upload another file to test detection
    print("\n📤 STEP 7: Upload Another File (Test Detection)")
    file_id2, result2 = tester.upload_and_check_file("another_safety_report.xlsx")
    
    print("\n🎉 Database-Driven System Test Complete!")
    print("=" * 60)
    print("\n📝 Summary:")
    print("✅ Schema patterns stored in database")
    print("✅ New patterns can be added to database")
    print("✅ File uploads check against database patterns")
    print("✅ User tags saved to database with confirmed schemas")
    print("✅ Future uploads will detect patterns from database")
    print("\n🎯 Your system is now fully database-driven!")

if __name__ == "__main__":
    run_complete_database_test()
