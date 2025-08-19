#!/usr/bin/env python3
"""
Test script to verify Langfuse initialization fix
"""

import sys

def test_langfuse_initialization():
    """Test Langfuse initialization without credentials"""
    
    print("Testing Langfuse initialization...")
    
    try:
        # Test the Langfuse config import
        from config.langfuse_config import langfuse_client, langfuse_config
        
        print(f"✅ Langfuse config loaded successfully")
        print(f"✅ Langfuse enabled: {langfuse_config.langfuse_enabled}")
        
        # Test basic Langfuse import
        import langfuse
        print("✅ Langfuse package imported successfully")
        
        # Test Langfuse LangChain integration
        from langfuse.langchain import CallbackHandler
        print("✅ Langfuse LangChain integration imported successfully")
        
        # Test creating a Langfuse instance
        try:
            langfuse_instance = langfuse.Langfuse()
            print("✅ Langfuse instance created successfully without credentials")
        except Exception as e:
            print(f"❌ Failed to create Langfuse instance: {e}")
            return False
        
        # Test with credentials (if available)
        if langfuse_config.langfuse_secret_key:
            try:
                langfuse_with_creds = langfuse.Langfuse(
                    secret_key=langfuse_config.langfuse_secret_key,
                    public_key=langfuse_config.langfuse_public_key,
                    host=langfuse_config.langfuse_host
                )
                print("✅ Langfuse instance created successfully with credentials")
            except Exception as e:
                print(f"❌ Failed to create Langfuse instance with credentials: {e}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure to run: pip install langfuse langfuse-langchain")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_conversational_bi_import():
    """Test that the conversational BI module can be imported"""
    
    print("\nTesting conversational BI import...")
    
    try:
        from convBI.conversationalBI import TextToSQLWorkflow, LANGFUSE_AVAILABLE
        print(f"✅ Conversational BI imported successfully")
        print(f"✅ Langfuse available: {LANGFUSE_AVAILABLE}")
        return True
    except Exception as e:
        print(f"❌ Failed to import conversational BI: {e}")
        return False

def main():
    """Run all tests"""
    
    print("🧪 Testing Langfuse Initialization Fix")
    print("=" * 50)
    
    # Test 1: Langfuse initialization
    langfuse_ok = test_langfuse_initialization()
    
    # Test 2: Conversational BI import
    convbi_ok = test_conversational_bi_import()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Langfuse Initialization: {'✅ PASS' if langfuse_ok else '❌ FAIL'}")
    print(f"Conversational BI Import: {'✅ PASS' if convbi_ok else '❌ FAIL'}")
    
    if all([langfuse_ok, convbi_ok]):
        print("\n🎉 All tests passed! Langfuse initialization is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

