# Azure OpenAI Rate Limit Fix

## Problem Identified

The current implementation in `convBI.py` has a critical flaw that causes rate limit errors:

1. The LLM is initialized only once when the `TextToSQLWorkflow` class is instantiated (in `__init__`).
2. This same LLM instance is reused for all API calls throughout the workflow.
3. Even though the round-robin count is updated in the JSON file, it doesn't affect subsequent API calls within the same workflow execution.

This means that all API calls within a single workflow execution go to the same endpoint, quickly hitting rate limits.

## Solution

Create a new `AzureOpenAIClient` class that properly rotates endpoints for each API call:

```python
"""
Azure OpenAI Client with improved rate limit handling
"""

import os
import json
import fcntl
import time
import random
from langchain_openai import AzureChatOpenAI

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
        with open("src/convBI_engine/round_robin.json", "r+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)  # Exclusive lock
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
                fcntl.flock(f, fcntl.LOCK_UN)  # Release lock
    
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
```

## Implementation Changes

Modify the `TextToSQLWorkflow` class in `convBI.py` to use this new client:

```python
class TextToSQLWorkflow:
    def __init__(self):
        # Remove the LLM initialization from here
        # Instead, create an instance of our new client
        self.openai_client = AzureOpenAIClient()
    
    def _intent_classification_agent(self, state: WorkflowState) -> WorkflowState:
        prompt = ChatPromptTemplate.from_messages(intent_prompt)
        
        # Use the client's invoke_with_retry method instead of direct LLM usage
        result = self.openai_client.invoke_with_retry(prompt, {
            "question": state["question"],
            "history": state["history"]
        })
        
        self._update_history(state, result)
        state["intent"] = result.content.strip().lower()
        
        return state
    
    # Similarly update all other agent methods to use self.openai_client.invoke_with_retry
    # instead of creating a chain with self.llm
```

## Benefits of This Approach

1. **True Round-Robin**: Each API call gets a fresh LLM instance with the next endpoint in rotation.
2. **Race Condition Prevention**: File locking prevents multiple processes from reading/writing the counter simultaneously.
3. **Automatic Retry**: Built-in retry logic with exponential backoff for rate limit errors.
4. **Fault Tolerance**: If one endpoint fails, it automatically tries the next one.

## Implementation Steps

1. Create the new `azure_openai_client.py` file with the `AzureOpenAIClient` class.
2. Modify `convBI.py` to use this new client instead of directly initializing the LLM.
3. Update all agent methods to use the client's `invoke_with_retry` method.
4. Test the implementation to ensure it properly rotates endpoints and handles rate limits.