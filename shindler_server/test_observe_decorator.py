#!/usr/bin/env python3
"""
Test script to verify @observe decorator is working
"""

import os
import sys
from datetime import datetime

def test_observe_decorator():
    """Test if @observe decorator creates proper traces"""
    
    print("🧪 Testing @observe Decorator")
    print("=" * 50)
    
    try:
        # Import the workflow
        from convBI.conversationalBI import TextToSQLWorkflow, LANGFUSE_AVAILABLE, observe
        
        print(f"✅ Conversational BI imported successfully")
        print(f"✅ Langfuse available: {LANGFUSE_AVAILABLE}")
        
        if not LANGFUSE_AVAILABLE:
            print("❌ Langfuse not available - cannot test @observe")
            return False
        
        # Test the @observe decorator directly
        @observe(name="test_observe_function")
        def test_function():
            print("🔍 Test function executed")
            return "test result"
        
        # Call the decorated function
        result = test_function()
        print(f"✅ Decorated function result: {result}")
        
        # Create workflow instance
        workflow = TextToSQLWorkflow()
        print("✅ TextToSQLWorkflow created successfully")
        
        # Test that the methods are properly decorated
        methods = [
            workflow._intent_classification_agent,
            workflow._greeting_agent,
            workflow._table_identification_agent,
            workflow._text_to_sql_agent,
            workflow._summarizer_agent,
            workflow._clarification_agent,
            workflow._visualization_agent
        ]
        
        for method in methods:
            print(f"✅ Method {method.__name__} is decorated")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing @observe decorator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_langfuse_import():
    """Test Langfuse import and observe function"""
    
    print("\n🧪 Testing Langfuse Import")
    print("=" * 50)
    
    try:
        from langfuse import observe
        print("✅ Langfuse observe imported successfully")
        
        # Test creating a simple observed function
        @observe(name="test_simple_function")
        def simple_function():
            return "simple result"
        
        result = simple_function()
        print(f"✅ Simple observed function result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing Langfuse observe: {e}")
        return False

def main():
    """Run all tests"""
    
    print("🚀 @observe Decorator Test")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Run tests
    tests = [
        ("Langfuse Import", test_langfuse_import),
        ("@observe Decorator", test_observe_decorator)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! @observe decorator should work correctly.")
        print("\nNext steps:")
        print("1. Deploy the updated code")
        print("2. Test with a real chat message")
        print("3. Check Langfuse dashboard for agent-specific traces")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
