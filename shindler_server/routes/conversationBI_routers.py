from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Try to import dependencies, handle gracefully if missing
try:
    from convBI_engine.convBI import TextToSQLWorkflow
    CONVBI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ConvBI engine not available: {e}")
    CONVBI_AVAILABLE = False
    TextToSQLWorkflow = None

from schemas.chat_schemas import ChatRequest

conv_bi_router = APIRouter(prefix="/api/v1", tags=["Conversational BI"])


@conv_bi_router.post("/chat")
def chat_question(request: ChatRequest):
    """
    Process natural language questions and convert them to SQL queries for safety data analysis
    
    Parameters:
    - question: Natural language question about safety data
    
    Returns:
    - JSON response with query results and analysis
    """
    # Check if conversational BI engine is available
    if not CONVBI_AVAILABLE:
        content = {
            "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
            "message": "Conversational BI engine not available",
            "body": {"detail": "Install dependencies with: pip install -r convBI_engine/requirements.txt"}
        }
        return JSONResponse(
            content=content,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    question = request.question
    
    # Validate question
    if not question or not question.strip():
        content = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "message": "Bad Request",
            "body": {"detail": "Question cannot be empty"}
        }
        return JSONResponse(
            content=content,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    workflow = TextToSQLWorkflow()

    try:
        response = workflow.run_workflow(question)
        content = {
            "status_code": status.HTTP_200_OK,
            "message": "Success",
            "body": response
        }
    
        return JSONResponse(
            content=content,
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        logger.error(f"Error: {e}")
        content = {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal Server Error",
            "body": {"detail": str(e)}
        }
        return JSONResponse(
            content=content,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
