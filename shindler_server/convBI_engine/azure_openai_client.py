"""
Azure OpenAI Client with improved rate limit handling
"""

import os
import json
import time
import random
import sys
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Handle file locking based on platform
if sys.platform != 'win32':
    import fcntl
    
    def lock_file(file_handle):
        fcntl.flock(file_handle, fcntl.LOCK_EX)
        
    def unlock_file(file_handle):
        fcntl.flock(file_handle, fcntl.LOCK_UN)
else:
    import msvcrt
    
    def lock_file(file_handle):
        # Windows file locking
        file_handle.seek(0)
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_LOCK, 1)
        
    def unlock_file(file_handle):
        # Windows file unlocking
        file_handle.seek(0)
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)

class AzureOpenAIClient:
    """
    A client for Azure OpenAI that handles rate limits by:
    1. Using a round-robin approach across multiple endpoints
    2. Adding retry logic with exponential backoff
    3. Implementing proper file locking to prevent race conditions
    """
    
    def __init__(self):
        self.endpoints_count = 3  # Number of available endpoints
        
    def _get_next_endpoint_idx(self):
        """Get the next endpoint index using file locking to prevent race conditions"""
        with open("convBI_engine/round_robin.json", "r+") as f:
            lock_file(f)  # Exclusive lock
            try:
                data = json.load(f)
                current = data["count"]
                next_count = (current + 1) % self.endpoints_count
                
                # Reset file pointer and update the file
                f.seek(0)
                json.dump({"count": next_count}, f)
                f.truncate()
                
                return current
            finally:
                unlock_file(f)  # Release lock
    
    def get_llm(self):
        """
        Get a new LLM instance using the next endpoint in the rotation.
        This should be called for EACH API call to ensure proper rotation.
        """
        endpoint_idx = self._get_next_endpoint_idx()
        
        # Try to create the LLM with the selected endpoint
        try:
            return AzureChatOpenAI(
                azure_endpoint=os.environ[f"AZURE_OPENAI_ENDPOINT_{endpoint_idx}"],
                azure_deployment=os.environ[f"AZURE_OPENAI_DEPLOYMENT_NAME_{endpoint_idx}"],
                openai_api_version=os.environ[f"AZURE_OPENAI_API_VERSION_{endpoint_idx}"],
                api_key=os.environ[f"AZURE_OPENAI_API_KEY_{endpoint_idx}"]
            )
        except Exception as e:
            print(f"Error creating LLM with endpoint {endpoint_idx}: {e}")
            # If there's an error, try the next endpoint
            next_idx = (endpoint_idx + 1) % self.endpoints_count
            return AzureChatOpenAI(
                azure_endpoint=os.environ[f"AZURE_OPENAI_ENDPOINT_{next_idx}"],
                azure_deployment=os.environ[f"AZURE_OPENAI_DEPLOYMENT_NAME_{next_idx}"],
                openai_api_version=os.environ[f"AZURE_OPENAI_API_VERSION_{next_idx}"],
                api_key=os.environ[f"AZURE_OPENAI_API_KEY_{next_idx}"]
            )
    
    def invoke_with_retry(self, prompt, inputs, max_retries=3):
        """
        Invoke the LLM with retry logic and exponential backoff
        """
        retries = 0
        while retries < max_retries:
            try:
                # Get a fresh LLM instance for each attempt
                llm = self.get_llm()
                chain = prompt | llm
                return chain.invoke(inputs)
            except Exception as e:
                if "429" in str(e) and retries < max_retries - 1:
                    # Calculate backoff time with jitter
                    backoff_time = (2 ** retries) + random.uniform(0, 1)
                    print(f"Rate limited. Retrying in {backoff_time:.2f} seconds...")
                    time.sleep(backoff_time)
                    retries += 1
                else:
                    raise