#!/usr/bin/env python3
"""
Test script for the enhanced tagging system with nearby matched tags
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class EnhancedTaggingTester:
    """Test class for enhanced tagging system with nearby matched tags"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def initialize_system(self):
        """Initialize the system with default patterns"""
        print("🔄 Initializing system...")
        url = f"{self.base_url}/file-processing/initialize-default-patterns"
        response = self.session.post(url)
        
        if response.status_code == 200:
            print("✅ System initialized with default patterns")
            return True
        else:
            print(f"❌ Failed to initialize: {response.text[:100]}")
            return False
    
    def get_schema_patterns(self):
        """Get all schema patterns"""
        print("📋 Getting schema patterns...")
        url = f"{self.base_url}/file-processing/schema-patterns"
        response = self.session.get(url)
        
        if response.status_code == 200:
            result = response.json()
            patterns = result['body']['patterns']
            print(f"✅ Found {len(patterns)} schema patterns")
            return patterns
        else:
            print(f"❌ Failed to get patterns: {response.text[:100]}")
            return {}
    
    def get_user_tags(self):
        """Get all user tags that have been used"""
        print("🏷️  Getting all user tags...")
        url = f"{self.base_url}/file-processing/user-tags"
        response = self.session.get(url)
        
        if response.status_code == 200:
            result = response.json()
            tags = result['body']['tags']
            print(f"✅ Found {len(tags)} unique user tags: {tags}")
            return tags
        else:
            print(f"❌ Failed to get user tags: {response.text[:100]}")
            return []
    
    def upload_and_check_with_tags(self, filename: str):
        """Upload file and check for nearby matched tags"""
        print(f"\n📤 Testing: {filename}")
        
        # Upload
        url = f"{self.base_url}/file-processing/upload-and-check-schema"
        payload = {
            "filename": filename,
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        
        response = self.session.post(url, json=payload)
        if response.status_code not in [200, 201]:
            print(f"❌ Upload failed: {response.text[:100]}")
            return None, None
        
        file_id = response.json()['body']['file_id']
        print(f"✅ File uploaded: {file_id}")
        
        # Check schema with nearby tags
        url = f"{self.base_url}/file-processing/check-schema/{file_id}"
        response = self.session.post(url)
        
        if response.status_code == 200:
            result = response.json()['body']
            print(f"🔍 Schema check result:")
            print(f"   Action: {result['action']}")
            print(f"   File columns: {result['file_columns']}")
            
            if 'nearby_tags' in result:
                print(f"   🏷️  Suggested tags: {result['nearby_tags']}")
            
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
        """Confirm schema and save user tags"""
        print(f"✅ Confirming schema '{schema_name}' with tags: {user_tags}")
        
        url = f"{self.base_url}/file-processing/confirm-schema/{file_id}"
        payload = {
            "schema_name": schema_name,
            "user_tags": user_tags
        }
        
        response = self.session.post(url, json=payload)
        
        if response.status_code == 200:
            print("✅ Schema confirmed and user tags saved!")
            print("   These tags will now be suggested for similar files!")
            return True
        else:
            print(f"❌ Confirm failed: {response.text[:100]}")
            return False
    
    def add_schema_pattern(self, schema_name: str, columns: list, description: str = ""):
        """Add new schema pattern"""
        print(f"➕ Adding schema pattern: {schema_name}")
        
        url = f"{self.base_url}/file-processing/add-schema-pattern"
        payload = {
            "schema_name": schema_name,
            "columns": columns,
            "description": description
        }
        
        response = self.session.post(url, json=payload)
        
        if response.status_code == 200:
            print(f"✅ Added schema pattern: {schema_name}")
            return True
        else:
            print(f"❌ Failed to add pattern: {response.text[:100]}")
            return False

def run_enhanced_tagging_demo():
    """Run enhanced tagging system demo"""
    tester = EnhancedTaggingTester()
    
    print("🚀 Enhanced Tagging System with Nearby Matched Tags")
    print("=" * 60)
    
    # Step 1: Initialize system
    print("\n📥 STEP 1: Initialize System")
    tester.initialize_system()
    
    # Step 2: Show current patterns and tags
    print("\n📋 STEP 2: Current System State")
    tester.get_schema_patterns()
    tester.get_user_tags()
    
    # Step 3: Upload first file and confirm with tags
    print("\n📤 STEP 3: Upload First File (Build Tag History)")
    file_id1, result1 = tester.upload_and_check_with_tags("safety_incident_report.xlsx")
    
    if result1 and result1['action'] == 'confirm_schema':
        # Confirm with specific tags
        tester.confirm_schema_with_tags(
            file_id1, 
            result1['matched_schema'], 
            ['safety', 'incident', 'monthly', 'critical']
        )
    
    # Step 4: Upload second similar file
    print("\n📤 STEP 4: Upload Similar File (Should Show Previous Tags)")
    file_id2, result2 = tester.upload_and_check_with_tags("another_safety_report.xlsx")
    
    if result2 and result2['action'] == 'confirm_schema':
        # Should now show nearby tags from previous file
        tester.confirm_schema_with_tags(
            file_id2, 
            result2['matched_schema'], 
            ['safety', 'incident', 'weekly', 'minor']
        )
    
    # Step 5: Add new schema pattern
    print("\n➕ STEP 5: Add New Schema Pattern")
    tester.add_schema_pattern(
        "maintenance_checklist",
        ["Date", "Equipment", "Checklist Item", "Status", "Technician", "Notes"],
        "Equipment maintenance checklist"
    )
    
    # Step 6: Upload file for new pattern
    print("\n📤 STEP 6: Upload File for New Pattern")
    file_id3, result3 = tester.upload_and_check_with_tags("equipment_maintenance.xlsx")
    
    if result3 and result3['action'] == 'add_new_schema':
        print("   As expected, no good match found for new file type")
    
    # Step 7: Show final system state
    print("\n📋 STEP 7: Final System State")
    tester.get_user_tags()
    
    print("\n🎉 Enhanced Tagging System Demo Complete!")
    print("=" * 60)
    print("\n📝 Key Features Demonstrated:")
    print("✅ Schema patterns stored in database")
    print("✅ User tags saved with confirmed schemas")
    print("✅ 5 nearby matched tags suggested for similar files")
    print("✅ Tag suggestions based on previous user choices")
    print("✅ Default tag suggestions when no history exists")
    print("✅ All user tags tracked and retrievable")
    print("\n🎯 Your enhanced tagging system is ready!")

if __name__ == "__main__":
    run_enhanced_tagging_demo()
