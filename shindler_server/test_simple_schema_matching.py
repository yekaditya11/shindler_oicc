#!/usr/bin/env python3
"""
Test script for simple schema matching system
- Shows top 5 nearby schemas based on match threshold
- Schema names become tags when finalized
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class SimpleSchemaMatchingTester:
    """Test class for simple schema matching system"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def initialize_system(self):
        """Initialize the system with default patterns"""
        print("🔄 Initializing system...")
        url = f"{self.base_url}/file-processing/initialize-default-patterns"
        response = self.session.post(url)
        
        if response.status_code == 200:
            print("✅ System initialized")
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
            print(f"✅ Found {len(patterns)} schema patterns:")
            for name, columns in patterns.items():
                print(f"   - {name}: {len(columns)} columns")
            return patterns
        else:
            print(f"❌ Failed to get patterns: {response.text[:100]}")
            return {}
    
    def upload_and_check_schemas(self, filename: str):
        """Upload file and get top 5 nearby schema matches"""
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
        
        # Check schema matches
        url = f"{self.base_url}/file-processing/check-schema/{file_id}"
        response = self.session.post(url)
        
        if response.status_code == 200:
            result = response.json()['body']
            print(f"🔍 Schema matching result:")
            print(f"   Action: {result['action']}")
            print(f"   File columns: {result['file_columns']}")
            
            if 'top_5_schemas' in result:
                print(f"   📊 Top 5 nearby schemas:")
                for i, schema in enumerate(result['top_5_schemas'], 1):
                    print(f"      {i}. {schema['schema_name']}: {schema['confidence']}%")
            
            if result['action'] == 'confirm_schema':
                print(f"   ✅ Best match: {result['best_match']} ({result['confidence']}%)")
            else:
                print(f"   💡 {result['message']}")
            
            return file_id, result
        else:
            print(f"❌ Schema check failed: {response.text[:100]}")
            return file_id, None
    
    def confirm_schema_as_tag(self, file_id: str, schema_name: str, additional_tags: list = None):
        """Confirm schema - schema name becomes primary tag"""
        print(f"✅ Confirming schema '{schema_name}' as primary tag")
        if additional_tags:
            print(f"   Additional tags: {additional_tags}")
        
        url = f"{self.base_url}/file-processing/confirm-schema/{file_id}"
        payload = {
            "schema_name": schema_name,
            "additional_tags": additional_tags or []
        }
        
        response = self.session.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()['body']
            print(f"✅ Schema confirmed! All tags: {result.get('all_tags', [schema_name])}")
            return True
        else:
            print(f"❌ Confirm failed: {response.text[:100]}")
            return False
    
    def add_new_schema(self, schema_name: str, columns: list, description: str = ""):
        """Add new schema pattern"""
        print(f"➕ Adding new schema: {schema_name}")
        
        url = f"{self.base_url}/file-processing/add-schema-pattern"
        payload = {
            "schema_name": schema_name,
            "columns": columns,
            "description": description
        }
        
        response = self.session.post(url, json=payload)
        
        if response.status_code == 200:
            print(f"✅ Added schema: {schema_name}")
            return True
        else:
            print(f"❌ Failed to add: {response.text[:100]}")
            return False

def run_simple_schema_demo():
    """Run simple schema matching demo"""
    tester = SimpleSchemaMatchingTester()
    
    print("🚀 Simple Schema Matching System")
    print("Schema names become tags when finalized")
    print("=" * 50)
    
    # Step 1: Initialize
    print("\n📥 STEP 1: Initialize System")
    tester.initialize_system()
    tester.get_schema_patterns()
    
    # Step 2: Upload safety file
    print("\n📤 STEP 2: Upload Safety File")
    file_id1, result1 = tester.upload_and_check_schemas("safety_incident_report.xlsx")
    
    if result1:
        if result1['action'] == 'confirm_schema':
            # Pick the best match
            tester.confirm_schema_as_tag(
                file_id1, 
                result1['best_match'], 
                ['monthly', 'critical']
            )
        elif 'top_5_schemas' in result1:
            # Pick from top 5
            top_schema = result1['top_5_schemas'][0]
            print(f"   Picking top schema: {top_schema['schema_name']}")
            tester.confirm_schema_as_tag(
                file_id1, 
                top_schema['schema_name'], 
                ['monthly']
            )
    
    # Step 3: Upload maintenance file
    print("\n📤 STEP 3: Upload Maintenance File")
    file_id2, result2 = tester.upload_and_check_schemas("equipment_maintenance.xlsx")
    
    if result2 and 'top_5_schemas' in result2:
        # Show user can pick any from top 5
        print("   User can pick any from top 5 schemas")
        second_choice = result2['top_5_schemas'][1] if len(result2['top_5_schemas']) > 1 else result2['top_5_schemas'][0]
        tester.confirm_schema_as_tag(
            file_id2, 
            second_choice['schema_name'], 
            ['weekly']
        )
    
    # Step 4: Add completely new schema
    print("\n➕ STEP 4: Add New Schema")
    tester.add_new_schema(
        "quality_inspection",
        ["Date", "Inspector", "Product", "Quality Score", "Pass/Fail", "Notes"],
        "Quality inspection checklist"
    )
    
    print("\n🎉 Simple Schema Matching Demo Complete!")
    print("=" * 50)
    print("\n📝 Key Points:")
    print("✅ Top 5 nearby schemas shown based on match threshold")
    print("✅ User can pick any schema from the top 5")
    print("✅ Schema name becomes the primary tag")
    print("✅ Additional tags are optional")
    print("✅ New schemas can be added anytime")
    print("\n🎯 Simple and straightforward!")

if __name__ == "__main__":
    run_simple_schema_demo()
