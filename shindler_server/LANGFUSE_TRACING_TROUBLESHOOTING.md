# Langfuse Tracing Troubleshooting Guide

## Issue: No Traces from Conversational BI in Deployed Environment

### Problem Description
- ✅ Chat agents are working (no crashes)
- ✅ Insights are generating traces
- ✅ Local environment shows traces
- ❌ Deployed environment shows no traces from conversational BI

## Step-by-Step Debugging

### 1. Run the Debug Script
First, run the comprehensive debug script to identify the issue:

```bash
python debug_langfuse_traces.py
```

This will check:
- Environment variables
- Langfuse configuration
- Conversational BI tracing setup
- Langfuse trace creation
- Azure OpenAI integration
- Network connectivity

### 2. Test Manual Trace Creation
Test if Langfuse can create traces manually:

```bash
curl -X POST http://your-deployed-url:8001/api/v1/test-trace
```

Expected response:
```json
{
  "success": true,
  "message": "Test trace created successfully",
  "trace_id": "some-trace-id",
  "langfuse_available": true
}
```

### 3. Check Environment Variables
Verify these environment variables are set in your deployment:

```bash
# Required for production tracing
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENABLED=true

# Azure OpenAI (required for chat functionality)
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
```

### 4. Check Langfuse Dashboard Settings

#### 4.1 Verify Project Configuration
- Log into your Langfuse dashboard
- Check that you're looking at the correct project
- Verify the project has the correct API keys

#### 4.2 Check Filters and Time Range
- Ensure you're not filtering out traces
- Check the time range covers when you're testing
- Look for traces with tags: `["intent_classification_agent", "text_to_sql_workflow"]`

#### 4.3 Check Trace Names
Look for traces with these names:
- `intent_classification_agent`
- `greeting_agent`
- `table_identification_agent`
- `text_to_sql_agent`
- `summarizer_agent`
- `clarification_agent`
- `visualization_agent`

### 5. Network and Firewall Issues

#### 5.1 Check Outbound Connectivity
Ensure your deployment can reach Langfuse:

```bash
# Test from your deployment server
curl -I https://cloud.langfuse.com
```

#### 5.2 Check Firewall Rules
- Ensure outbound HTTPS (443) is allowed
- Check if your deployment environment blocks external API calls

### 6. Langfuse Configuration Issues

#### 6.1 Check Langfuse Client Initialization
Add this to your application startup to verify Langfuse is initialized:

```python
from config.langfuse_config import langfuse_client, langfuse_config
print(f"Langfuse enabled: {langfuse_config.langfuse_enabled}")
print(f"Langfuse client: {langfuse_client is not None}")
```

#### 6.2 Verify Callback Handler Setup
Check that the CallbackHandler is properly configured:

```python
from convBI.conversationalBI import TextToSQLWorkflow
workflow = TextToSQLWorkflow()
print(f"Intent handler: {type(workflow.intent_handler)}")
```

### 7. Common Issues and Solutions

#### Issue 1: Langfuse Not Initialized
**Symptoms**: No traces at all, even from insights
**Solution**: Check environment variables and Langfuse configuration

#### Issue 2: Network Connectivity
**Symptoms**: Traces from insights but not from chat
**Solution**: Check firewall rules and network connectivity

#### Issue 3: Wrong Project/Environment
**Symptoms**: Traces appear in wrong project
**Solution**: Verify Langfuse project settings and API keys

#### Issue 4: Callback Handler Not Working
**Symptoms**: Chat works but no traces
**Solution**: Check if CallbackHandler is properly initialized

#### Issue 5: Rate Limiting
**Symptoms**: Intermittent tracing
**Solution**: Check Langfuse API rate limits

### 8. Enhanced Logging

To get more detailed information, add these environment variables:

```bash
# Enable debug logging
LANGFUSE_DEBUG=true
PYTHONPATH=/path/to/your/app
```

### 9. Testing Checklist

- [ ] Debug script passes all tests
- [ ] Manual trace creation works
- [ ] Environment variables are set correctly
- [ ] Network connectivity to Langfuse works
- [ ] Langfuse dashboard shows the correct project
- [ ] No filters are hiding traces
- [ ] Time range covers test period
- [ ] CallbackHandler is properly initialized
- [ ] Chat functionality works (even without traces)

### 10. Alternative Debugging Methods

#### 10.1 Add Trace Logging
Add this to your conversational BI to log trace creation:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In your agent methods
logger.debug(f"Creating trace for {agent_name}")
```

#### 10.2 Check Langfuse SDK Version
Ensure you're using a compatible version:

```bash
pip show langfuse
pip show langfuse-langchain
```

#### 10.3 Test with Different Langfuse Host
If using self-hosted Langfuse:

```bash
LANGFUSE_HOST=http://your-langfuse-server:3000
```

### 11. Production Deployment Considerations

#### 11.1 Environment Variables
Use proper secret management:
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Environment variables in deployment platform

#### 11.2 Monitoring
Set up monitoring for:
- Langfuse API calls
- Network connectivity
- Application logs

#### 11.3 Fallback Strategy
Ensure the application works without Langfuse:
- Graceful degradation
- Error handling
- Logging alternatives

### 12. Getting Help

If the issue persists:

1. Run the debug script and share the output
2. Check application logs for errors
3. Verify Langfuse dashboard settings
4. Test network connectivity
5. Contact Langfuse support if needed

### 13. Quick Fixes to Try

1. **Restart the application** after setting environment variables
2. **Clear browser cache** for Langfuse dashboard
3. **Check timezone settings** in Langfuse dashboard
4. **Verify API key permissions** in Langfuse
5. **Test with a simple trace** first before complex workflows

Remember: The chat functionality should work regardless of tracing status. Focus on getting traces working after confirming chat works.

