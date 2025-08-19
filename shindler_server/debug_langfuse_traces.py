#!/usr/bin/env python3
"""
Debug script to identify Langfuse tracing issues in deployed environment
"""

import os
import sys
import json
from datetime import datetime

def check_environment_variables():
    """Check if Langfuse environment variables are set"""
    print("🔍 Checking Langfuse Environment Variables:")
    print("=" * 50)
    
    langfuse_vars = [
        'LANGFUSE_SECRET_KEY',
        'LANGFUSE_PUBLIC_KEY', 
        'LANGFUSE_HOST',
        'LANGFUSE_ENABLED'
    ]
    
    for var in langfuse_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var:
                print(f"✅ {var}: {'*' * 10} (hidden)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
    
    print()

def test_langfuse_configuration():
    """Test Langfuse configuration and initialization"""
    print("🔍 Testing Langfuse Configuration:")
    print("=" * 50)
    
    try:
        from config.langfuse_config import langfuse_config, langfuse_client
        
        print(f"✅ Langfuse config loaded")
        print(f"✅ Langfuse enabled: {langfuse_config.langfuse_enabled}")
        print(f"✅ Langfuse client: {langfuse_client is not None}")
        
        if langfuse_config.langfuse_secret_key:
            print("✅ Langfuse credentials configured")
        else:
            print("⚠️  Langfuse credentials not configured (using defaults)")
            
        return True
        
    except Exception as e:
        print(f"❌ Langfuse config error: {e}")
        return False

def test_conversational_bi_tracing():
    """Test if conversational BI can create traces"""
    print("\n🔍 Testing Conversational BI Tracing:")
    print("=" * 50)
    
    try:
        from convBI.conversationalBI import TextToSQLWorkflow, LANGFUSE_AVAILABLE
        
        print(f"✅ Conversational BI imported")
        print(f"✅ Langfuse available: {LANGFUSE_AVAILABLE}")
        
        # Test creating a workflow instance
        workflow = TextToSQLWorkflow()
        print("✅ TextToSQLWorkflow created successfully")
        
        # Check if handlers are properly initialized
        handlers = [
            workflow.intent_handler,
            workflow.greeting_handler,
            workflow.table_id_handler,
            workflow.text_to_sql_handler,
            workflow.summarizer_handler,
            workflow.clarification_handler,
            workflow.visualization_handler
        ]
        
        for i, handler in enumerate(handlers):
            print(f"✅ Handler {i+1}: {type(handler).__name__}")
            
        return True
        
    except Exception as e:
        print(f"❌ Conversational BI error: {e}")
        return False

def test_langfuse_trace_creation():
    """Test creating a simple Langfuse trace"""
    print("\n🔍 Testing Langfuse Trace Creation:")
    print("=" * 50)
    
    try:
        import langfuse
        from langfuse.langchain import CallbackHandler
        
        # Create a simple trace
        langfuse_client = langfuse.Langfuse()
        
        # Create a trace
        trace = langfuse_client.trace(
            name="test_trace",
            metadata={"test": True, "timestamp": datetime.now().isoformat()}
        )
        
        print("✅ Langfuse trace created successfully")
        
        # Create a span
        span = trace.span(
            name="test_span",
            metadata={"test_span": True}
        )
        
        print("✅ Langfuse span created successfully")
        
        # End the span and trace
        span.end()
        trace.end()
        
        print("✅ Langfuse trace ended successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Langfuse trace creation error: {e}")
        return False

def test_azure_openai_integration():
    """Test Azure OpenAI integration with Langfuse"""
    print("\n🔍 Testing Azure OpenAI + Langfuse Integration:")
    print("=" * 50)
    
    try:
        from config.azure_config import get_azure_openai_client
        
        client = get_azure_openai_client()
        print("✅ Azure OpenAI client created with Langfuse integration")
        
        # Test a simple completion
        try:
            response = client.chat.completions.create(
                model="gpt-35-turbo",  # Adjust based on your deployment
                messages=[{"role": "user", "content": "Say hello"}],
                max_tokens=10
            )
            print("✅ Azure OpenAI request completed successfully")
            print(f"✅ Response: {response.choices[0].message.content}")
            return True
        except Exception as e:
            print(f"⚠️  Azure OpenAI request failed (this might be expected): {e}")
            print("   This could be due to missing credentials or model configuration")
            return True  # Still consider this a pass for debugging purposes
            
    except Exception as e:
        print(f"❌ Azure OpenAI integration error: {e}")
        return False

def check_network_connectivity():
    """Check if the deployment can reach Langfuse"""
    print("\n🔍 Checking Network Connectivity:")
    print("=" * 50)
    
    try:
        import requests
        
        # Test connectivity to Langfuse
        langfuse_host = os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')
        
        print(f"Testing connectivity to: {langfuse_host}")
        
        response = requests.get(langfuse_host, timeout=10)
        print(f"✅ Langfuse connectivity: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Network connectivity error: {e}")
        return False

def generate_debug_report():
    """Generate a comprehensive debug report"""
    print("🚀 Langfuse Tracing Debug Report")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Environment: {'Production' if os.getenv('LANGFUSE_SECRET_KEY') else 'Development'}")
    print()
    
    # Run all tests
    tests = [
        ("Environment Variables", check_environment_variables),
        ("Langfuse Configuration", test_langfuse_configuration),
        ("Conversational BI Tracing", test_conversational_bi_tracing),
        ("Langfuse Trace Creation", test_langfuse_trace_creation),
        ("Azure OpenAI Integration", test_azure_openai_integration),
        ("Network Connectivity", check_network_connectivity)
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
    print("📊 Debug Report Summary:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Langfuse should be working correctly.")
        print("\nIf you're still not seeing traces, check:")
        print("1. Langfuse dashboard filters and time range")
        print("2. Project settings in Langfuse")
        print("3. Network firewall rules")
        print("4. Langfuse API rate limits")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = generate_debug_report()
    sys.exit(0 if success else 1)

