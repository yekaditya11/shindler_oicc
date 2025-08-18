from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, AsyncGenerator
import json
import asyncio
from datetime import datetime
from convBI.conversationalBI import TextToSQLWorkflow, ddl_extraction, semantics_extraction
from dotenv import load_dotenv
load_dotenv()
# Create router instance
router = APIRouter(prefix="/api/v1", tags=["conversation"])

# Pydantic models for request/response
class ConversationRequest(BaseModel):
    file_id: int
    question: str

class ConversationResponse(BaseModel):
    response: str
    sql_query: Optional[str] = None
    table_name: Optional[str] = None
    visualization_data: Optional[Dict[str, Any]] = None
    intent: Optional[str] = None

@router.post("/chat", response_model=ConversationResponse)
async def chat_endpoint(request: ConversationRequest):
    """Main chat endpoint for conversational BI"""
    try:
        # Extract DDL and semantics
        required_database_ddl = ddl_extraction(request.file_id)
        required_database_semantics = semantics_extraction(request.file_id)
        
        # Initialize workflow
        workflow = TextToSQLWorkflow()
        
        # Run workflow
        final_state = workflow.run_workflow(
            request.question, 
            required_database_ddl, 
            required_database_semantics
        )
        
        # Extract response data with proper error handling
        response_text = final_state.get("final_answer", "No response generated")
        sql_query = final_state.get("sql_query", None)
        table_name = final_state.get("tablename", None)
        visualization_data = final_state.get("visualization_data", None)
        intent = final_state.get("intent", None)
        
        # Handle empty or None responses
        if not response_text or response_text.strip() == "":
            response_text = "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
        
        return ConversationResponse(
            response=response_text,
            sql_query=sql_query,
            table_name=table_name,
            visualization_data=visualization_data,
            intent=intent
        )
        
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Error in chat endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/stream/chat")
async def stream_chat_endpoint(request: ConversationRequest):
    """Streaming chat endpoint for conversational BI using Server-Sent Events (SSE)."""
    try:
        # Extract DDL and semantics
        required_database_ddl = ddl_extraction(request.file_id)
        required_database_semantics = semantics_extraction(request.file_id)

        # Initialize workflow
        workflow = TextToSQLWorkflow()

        async def event_stream() -> AsyncGenerator[str, None]:
            for chunk in workflow.run_stream_workflow(
                request.question,
                required_database_ddl,
                required_database_semantics,
            ):
                yield chunk

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Error in stream chat endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")

        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )

@router.post("/test-trace")
async def test_trace_endpoint():
    """Test endpoint to manually create a Langfuse trace"""
    try:
        from convBI.conversationalBI import LANGFUSE_AVAILABLE
        import langfuse
        from datetime import datetime
        
        if not LANGFUSE_AVAILABLE:
            return {"success": False, "message": "Langfuse not available"}
        
        # Create a test trace
        langfuse_client = langfuse.Langfuse()
        
        trace = langfuse_client.trace(
            name="test_conversational_bi_trace",
            metadata={
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "source": "conversational_bi_test"
            }
        )
        
        # Create a span
        span = trace.span(
            name="test_agent_span",
            metadata={"agent": "test_agent"}
        )
        
        # Simulate some work
        import time
        time.sleep(0.1)
        
        # End the span and trace
        span.end()
        trace.end()
        
        return {
            "success": True,
            "message": "Test trace created successfully",
            "trace_id": trace.id,
            "langfuse_available": LANGFUSE_AVAILABLE
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error creating test trace: {str(e)}",
            "langfuse_available": LANGFUSE_AVAILABLE if 'LANGFUSE_AVAILABLE' in locals() else False
        }