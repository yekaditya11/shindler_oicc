# Deployment Guide for Shindler Safety Analytics

## Issue Resolution: Langfuse Dependencies

### Problem Description
Your application was failing in deployment because the chat agents depend on Langfuse for observability, but the Langfuse packages were not included in the `requirements.txt` file. This caused import errors when the application tried to use Langfuse features.

### What Was Fixed

1. **Added Missing Dependencies**: Updated `requirements.txt` to include:
   - `langfuse`
   - `langfuse-langchain`

2. **Created Langfuse Configuration**: Added `config/langfuse_config.py` to handle Langfuse initialization with fallback support.

3. **Updated Main Application**: Modified `app.py` to initialize Langfuse properly and handle cases where it's not available.

4. **Made Chat Agents Resilient**: Updated `convBI/conversationalBI.py` to handle Langfuse imports gracefully with fallback behavior.

5. **Updated AI Insights**: Modified `ai_insights/insights_generator.py` to work with or without Langfuse.

6. **Fixed API Endpoint Mismatch**: Updated conversation router to use `/api/v1` prefix to match frontend expectations.

7. **Added Required Parameters**: Updated frontend to include `file_id` parameter that backend expects.

### Deployment Steps

#### 1. Update Dependencies
Make sure your deployment environment has the updated `requirements.txt`:

```bash
pip install -r requirements.txt
```

#### 2. Environment Variables (Optional)
If you want to use Langfuse observability in production, set these environment variables:

```env
# Langfuse Configuration (Optional)
LANGFUSE_SECRET_KEY=your_secret_key_here
LANGFUSE_PUBLIC_KEY=your_public_key_here
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PROJECT_NAME=shindler-safety-analytics
LANGFUSE_ENABLED=true
```

If you don't set these variables, the application will work without Langfuse observability.

#### 3. Verify Installation
Check that all dependencies are installed:

```bash
python -c "import langfuse; print('Langfuse installed successfully')"
python -c "import langfuse.langchain; print('Langfuse LangChain integration available')"
```

#### 4. Test the Application
Start your application and test the chat functionality:

```bash
python app.py
```

Then test the health endpoint:
```bash
curl http://localhost:8001/health
```

You can also run the comprehensive test script:
```bash
python test_chat_fix.py
```

You should see:
```json
{
  "status": "healthy",
  "message": "Shindler Safety Analytics API Server health check",
  "azure_openai_configured": true,
  "database_connected": true,
  "langfuse_configured": true
}
```

### How It Works Now

#### With Langfuse Available
- Full observability and tracing of AI agents
- Langfuse tags and metadata for monitoring
- Complete functionality as designed

#### Without Langfuse (Fallback Mode)
- Application works normally without observability
- All chat agents function properly
- No errors or crashes
- Graceful degradation of features

### Troubleshooting

#### If Chat Agents Still Don't Work

1. **Check Dependencies**:
   ```bash
   pip list | grep langfuse
   ```

2. **Check Logs**:
   Look for any import errors in your application logs.

3. **Test Individual Components**:
   ```bash
   python -c "from convBI.conversationalBI import TextToSQLWorkflow; print('Chat workflow imported successfully')"
   ```

4. **Verify Environment Variables**:
   Make sure all required Azure OpenAI environment variables are set:
   ```env
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_API_KEY=your_key
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
   ```

#### Common Issues

1. **Import Errors**: Make sure all packages are installed
2. **Environment Variables**: Verify all required variables are set
3. **Database Connection**: Ensure PostgreSQL is accessible
4. **Azure OpenAI**: Confirm Azure OpenAI service is working

### Production Deployment

For production deployment, consider:

1. **Langfuse Cloud**: Set up a Langfuse cloud account for observability
2. **Environment Variables**: Use proper secret management
3. **Monitoring**: Set up application monitoring and alerting
4. **Logging**: Configure proper logging levels

### Support

If you continue to experience issues:

1. Check the application logs for specific error messages
2. Verify all environment variables are correctly set
3. Test the health endpoint to identify which components are failing
4. Ensure your deployment environment has all required system dependencies

The application is now designed to work in both development and production environments, with or without Langfuse observability.
