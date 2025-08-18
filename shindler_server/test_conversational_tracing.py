#!/usr/bin/env python3
"""
Test script to verify conversational BI tracing
"""

import os
import sys
import json
from datetime import datetime

def test_conversational_bi_trace():
    """Test if conversational BI creates proper traces"""
    
    print("🧪 Testing Conversational BI Tracing")
    print("=" * 50)
    
    try:
        # Import the workflow
        from convBI.conversationalBI import TextToSQLWorkflow, LANGFUSE_AVAILABLE
        
        print(f"✅ Conversational BI imported successfully")
        print(f"✅ Langfuse available: {LANGFUSE_AVAILABLE}")
        
        if not LANGFUSE_AVAILABLE:
            print("❌ Langfuse not available - cannot test tracing")
            return False
        
        # Create workflow instance
        workflow = TextToSQLWorkflow()
        print("✅ TextToSQLWorkflow created successfully")
        
        # Test the custom trace creation
        test_state = {
            "question": "How many unsafe events were reported?",
            "history": [],
            "intent": "",
            "database_ddl": "",
            "total_database_semantics": {},
            "tablename": "",
            "rephrased_question": "",
            "semantic_info": "",
            "sql_query": "",
            "query_result": "",
            "query_error_message": "",
            "needs_clarification": False,
            "visualization_data": "",
            "final_answer": "",
            "error_message": ""
        }
        
        # Test custom trace creation
        trace = workflow._create_agent_trace("test_agent", test_state)
        
        if trace:
            print("✅ Custom trace created successfully")
            print(f"✅ Trace ID: {trace.id}")
            
            # End the trace
            trace.end()
            print("✅ Trace ended successfully")
            
            return True
        else:
            print("❌ Failed to create custom trace")
            return False
            
    except Exception as e:
        print(f"❌ Error testing conversational BI tracing: {e}")
        return False

def test_langfuse_manual_trace():
    """Test manual Langfuse trace creation"""
    
    print("\n🧪 Testing Manual Langfuse Trace Creation")
    print("=" * 50)
    
    try:
        import langfuse
        
        # Create a test trace
        langfuse_client = langfuse.Langfuse()
        
        trace = langfuse_client.trace(
            name="test_conversational_bi_manual",
            metadata={
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "source": "conversational_bi_test"
            }
        )
        
        print("✅ Manual trace created successfully")
        print(f"✅ Trace ID: {trace.id}")
        
        # Create a span
        span = trace.span(
            name="test_agent_span",
            metadata={"agent": "test_agent"}
        )
        
        print("✅ Span created successfully")
        
        # End the span and trace
        span.end()
        trace.end()
        
        print("✅ Manual trace ended successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating manual trace: {e}")
        return False

def test_environment_variables():
    """Test environment variables"""
    
    print("\n🧪 Testing Environment Variables")
    print("=" * 50)
    
    required_vars = [
        'LANGFUSE_SECRET_KEY',
        'LANGFUSE_PUBLIC_KEY',
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_API_KEY'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var:
                print(f"✅ {var}: {'*' * 10} (hidden)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    return all_set

def main():
    """Run all tests"""
    
    print("🚀 Conversational BI Tracing Test")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Run tests
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Manual Langfuse Trace", test_langfuse_manual_trace),
        ("Conversational BI Trace", test_conversational_bi_trace)
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
        print("\n🎉 All tests passed! Conversational BI tracing should work correctly.")
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
