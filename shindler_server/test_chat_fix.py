#!/usr/bin/env python3
"""
Test script to verify chat functionality after Langfuse fixes
"""

import requests
import json
import sys

def test_chat_endpoint():
    """Test the chat endpoint to ensure it's working"""
    
    # Test configuration
    base_url = "http://localhost:8001"  # Adjust if your server runs on different port
    endpoint = "/api/v1/chat"
    
    # Test payload
    payload = {
        "question": "How many unsafe events were reported?",
        "file_id": 1
    }
    
    print(f"Testing chat endpoint: {base_url}{endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Make the request
        response = requests.post(
            f"{base_url}{endpoint}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat endpoint is working!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Chat endpoint failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running.")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The server might be overloaded.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    
    base_url = "http://localhost:8001"
    endpoint = "/health"
    
    print(f"\nTesting health endpoint: {base_url}{endpoint}")
    
    try:
        response = requests.get(f"{base_url}{endpoint}", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health endpoint is working!")
            print(f"Health Status: {json.dumps(result, indent=2)}")
            
            # Check if Langfuse is configured
            if result.get("langfuse_configured"):
                print("✅ Langfuse is properly configured")
            else:
                print("⚠️  Langfuse is not configured (this is okay for basic functionality)")
            
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint error: {str(e)}")
        return False

def test_langfuse_import():
    """Test if Langfuse can be imported"""
    
    print("\nTesting Langfuse imports...")
    
    try:
        # Test basic Langfuse import
        import langfuse
        print("✅ Langfuse package imported successfully")
        
        # Test Langfuse LangChain integration
        from langfuse.langchain import CallbackHandler
        print("✅ Langfuse LangChain integration imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Langfuse import failed: {str(e)}")
        print("Make sure to run: pip install langfuse langfuse-langchain")
        return False

def main():
    """Run all tests"""
    
    print("🧪 Testing Shindler Safety Analytics Chat Fix")
    print("=" * 50)
    
    # Test 1: Langfuse imports
    langfuse_ok = test_langfuse_import()
    
    # Test 2: Health endpoint
    health_ok = test_health_endpoint()
    
    # Test 3: Chat endpoint
    chat_ok = test_chat_endpoint()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Langfuse Imports: {'✅ PASS' if langfuse_ok else '❌ FAIL'}")
    print(f"Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Chat Endpoint: {'✅ PASS' if chat_ok else '❌ FAIL'}")
    
    if all([langfuse_ok, health_ok, chat_ok]):
        print("\n🎉 All tests passed! Chat functionality should be working.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

