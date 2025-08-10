# LangGraph Streaming with PostgresSaver
# Complete FastAPI application with persistent conversation memory

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Annotated, TypedDict, AsyncGenerator, Optional, List
import json
import asyncio
import uuid
from datetime import datetime
import os
import logging

# LangGraph and LangChain imports
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

# Database imports
import asyncpg
from psycopg2.pool import SimpleConnectionPool
import psycopg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app setup
app = FastAPI(title="LangGraph Streaming with PostgreSQL", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables (set these in your environment)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/langgraph_db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Pydantic models
class ChatRequest(BaseModel):
    question: str
    thread_id: Optional[str] = None  # For conversation continuity
    stream_mode: str = "updates"
    user_id: Optional[str] = None

class StreamResponse(BaseModel):
    type: str
    data: dict
    timestamp: str
    thread_id: Optional[str] = None
    node: Optional[str] = None

# Define the graph state with enhanced structure
class ConversationState(TypedDict):
    messages: Annotated[List, add_messages]
    user_id: str
    conversation_summary: str
    processing_step: str
    metadata: dict
    token_count: int

# Global variables for database and graph
checkpointer = None
conversation_graph = None

# Database setup functions
async def setup_database():
    """Initialize PostgreSQL database and tables for LangGraph checkpointing"""
    global checkpointer
    
    try:
        # Create the checkpointer
        checkpointer = AsyncPostgresSaver.from_conn_string(DATABASE_URL)
        
        # Setup the database tables
        await checkpointer.setup()
        
        logger.info("✅ PostgreSQL checkpointer initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

# Graph node definitions
async def context_loader_node(state: ConversationState, config: RunnableConfig) -> ConversationState:
    """Load conversation context and prepare for processing"""
    
    # Get thread_id from config for context loading
    thread_id = config.get("configurable", {}).get("thread_id")
    
    await asyncio.sleep(0.5)  # Simulate context loading
    
    return {
        "processing_step": "context_loaded",
        "metadata": {
            "node": "context_loader",
            "timestamp": datetime.now().isoformat(),
            "thread_id": thread_id,
            "action": "Loaded conversation context from PostgreSQL"
        },
        "token_count": state.get("token_count", 0) + 50
    }

async def llm_processor_node(state: ConversationState, config: RunnableConfig) -> ConversationState:
    """Main LLM processing with conversation awareness"""
    
    llm = ChatOpenAI(
        model="gpt-3.5-turbo", 
        streaming=True,
        api_key=OPENAI_API_KEY
    )
    
    # Create context-aware system message
    system_msg = SystemMessage(content=f"""You are a helpful AI assistant. 
    Previous conversation summary: {state.get('conversation_summary', 'No previous context')}
    Current user: {state.get('user_id', 'anonymous')}
    Continue the conversation naturally.""")
    
    # Get all messages for context
    messages = [system_msg] + state.get("messages", [])
    
    # Generate response
    response = await llm.ainvoke(messages)
    
    # Update conversation summary
    summary = f"User asked about: {messages[-1].content[:100]}... AI responded with information."
    
    return {
        "messages": [response],
        "processing_step": "llm_processed",
        "conversation_summary": summary,
        "metadata": {
            "node": "llm_processor", 
            "timestamp": datetime.now().isoformat(),
            "action": "Generated AI response with conversation context",
            "response_length": len(response.content)
        },
        "token_count": state.get("token_count", 0) + len(response.content.split())
    }

async def memory_saver_node(state: ConversationState, config: RunnableConfig) -> ConversationState:
    """Save conversation state to PostgreSQL"""
    
    await asyncio.sleep(0.3)  # Simulate database write
    
    return {
        "processing_step": "memory_saved",
        "metadata": {
            "node": "memory_saver",
            "timestamp": datetime.now().isoformat(),
            "action": "Conversation state saved to PostgreSQL",
            "total_tokens": state.get("token_count", 0)
        }
    }

# Create the conversation graph
def create_conversation_graph():
    """Create StateGraph with PostgreSQL checkpointing"""
    
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("context_loader", context_loader_node)
    workflow.add_node("llm_processor", llm_processor_node)
    workflow.add_node("memory_saver", memory_saver_node)
    
    # Add edges
    workflow.add_edge(START, "context_loader")
    workflow.add_edge("context_loader", "llm_processor")
    workflow.add_edge("llm_processor", "memory_saver")
    workflow.add_edge("memory_saver", END)
    
    # Compile with checkpointer
    return workflow.compile(checkpointer=checkpointer)

# Streaming functions
async def stream_updates_with_postgres(
    question: str, 
    thread_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """Stream node updates while saving to PostgreSQL"""
    
    if not thread_id:
        thread_id = str(uuid.uuid4())
    
    if not user_id:
        user_id = "anonymous"
    
    # Create initial state
    initial_state = {
        "messages": [HumanMessage(content=question)],
        "user_id": user_id,
        "conversation_summary": "",
        "processing_step": "initialized",
        "metadata": {},
        "token_count": 0
    }
    
    # Configuration for checkpointing
    config = RunnableConfig(
        configurable={
            "thread_id": thread_id,
            "user_id": user_id
        }
    )
    
    try:
        # Send start event
        start_response = StreamResponse(
            type="stream_start",
            data={
                "message": "Starting conversation processing...",
                "thread_id": thread_id,
                "user_id": user_id
            },
            timestamp=datetime.now().isoformat(),
            thread_id=thread_id
        )
        yield f"data: {start_response.model_dump_json()}\n\n"
        
        # Stream the graph execution with updates
        async for chunk in conversation_graph.astream(
            initial_state, 
            config=config,
            stream_mode="updates"
        ):
            for node_name, update in chunk.items():
                # Create update response
                update_response = StreamResponse(
                    type="node_update",
                    data={
                        "node": node_name,
                        "update": update,
                        "step": update.get("processing_step", "unknown"),
                        "metadata": update.get("metadata", {})
                    },
                    timestamp=datetime.now().isoformat(),
                    thread_id=thread_id,
                    node=node_name
                )
                yield f"data: {update_response.model_dump_json()}\n\n"
                
                # Add small delay for better UX
                await asyncio.sleep(0.1)
        
        # Get final state from checkpoint
        final_state = await conversation_graph.aget_state(config)
        
        # Send completion event
        completion_response = StreamResponse(
            type="stream_complete",
            data={
                "message": "Conversation processing complete",
                "final_state": {
                    "step": final_state.values.get("processing_step"),
                    "message_count": len(final_state.values.get("messages", [])),
                    "token_count": final_state.values.get("token_count", 0)
                },
                "checkpoint_saved": True,
                "thread_id": thread_id
            },
            timestamp=datetime.now().isoformat(),
            thread_id=thread_id
        )
        yield f"data: {completion_response.model_dump_json()}\n\n"
        
    except Exception as e:
        logger.error(f"Streaming error for thread {thread_id}: {e}")
        error_response = StreamResponse(
            type="error",
            data={
                "error": str(e),
                "thread_id": thread_id
            },
            timestamp=datetime.now().isoformat(),
            thread_id=thread_id
        )
        yield f"data: {error_response.model_dump_json()}\n\n"

async def stream_conversation_history(thread_id: str) -> AsyncGenerator[str, None]:
    """Stream conversation history from PostgreSQL"""
    
    try:
        config = RunnableConfig(configurable={"thread_id": thread_id})
        
        # Get conversation history from checkpointer
        history = []
        async for state in conversation_graph.aget_state_history(config):
            history.append({
                "checkpoint_id": state.config["configurable"]["checkpoint_id"],
                "step": state.values.get("processing_step", "unknown"),
                "messages": [msg.content for msg in state.values.get("messages", [])],
                "timestamp": state.values.get("metadata", {}).get("timestamp", "unknown")
            })
        
        # Stream history
        for i, checkpoint in enumerate(reversed(history)):  # Chronological order
            response = StreamResponse(
                type="history_checkpoint",
                data={
                    "checkpoint_number": i + 1,
                    "checkpoint": checkpoint
                },
                timestamp=datetime.now().isoformat(),
                thread_id=thread_id
            )
            yield f"data: {response.model_dump_json()}\n\n"
            await asyncio.sleep(0.1)
            
    except Exception as e:
        error_response = StreamResponse(
            type="error",
            data={"error": f"Failed to load history: {str(e)}"},
            timestamp=datetime.now().isoformat(),
            thread_id=thread_id
        )
        yield f"data: {error_response.model_dump_json()}\n\n"

# FastAPI endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize database and graph on startup"""
    global conversation_graph
    
    logger.info("🚀 Starting up LangGraph Streaming API...")
    
    # Setup database
    db_ready = await setup_database()
    if not db_ready:
        logger.error("💥 Failed to initialize database")
        raise Exception("Database initialization failed")
    
    # Create conversation graph
    conversation_graph = create_conversation_graph()
    logger.info("✅ LangGraph with PostgreSQL ready!")

@app.post("/stream/chat")
async def stream_chat_conversation(request: ChatRequest):
    """Stream conversation with PostgreSQL persistence"""
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if not conversation_graph:
        raise HTTPException(status_code=503, detail="Graph not initialized")
    
    # Generate thread_id if not provided
    thread_id = request.thread_id or str(uuid.uuid4())
    user_id = request.user_id or "anonymous"
    
    return StreamingResponse(
        stream_updates_with_postgres(request.question, thread_id, user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Thread-ID": thread_id,
            "X-User-ID": user_id
        }
    )

@app.get("/stream/history/{thread_id}")
async def stream_conversation_history_endpoint(thread_id: str):
    """Stream conversation history for a thread"""
    
    if not conversation_graph:
        raise HTTPException(status_code=503, detail="Graph not initialized")
    
    return StreamingResponse(
        stream_conversation_history(thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/api/threads/{user_id}")
async def get_user_threads(user_id: str):
    """Get all conversation threads for a user"""
    
    try:
        # Query checkpointer for user's threads
        # Note: This requires custom query as PostgresSaver doesn't have built-in user filtering
        async with asyncpg.connect(DATABASE_URL) as conn:
            query = """
                SELECT DISTINCT thread_id, created_at, updated_at
                FROM checkpoints 
                WHERE checkpoint->>'user_id' = $1
                ORDER BY updated_at DESC
                LIMIT 50
            """
            rows = await conn.fetch(query, user_id)
            
            threads = [
                {
                    "thread_id": row["thread_id"],
                    "created_at": row["created_at"].isoformat(),
                    "updated_at": row["updated_at"].isoformat()
                }
                for row in rows
            ]
            
        return {"user_id": user_id, "threads": threads}
        
    except Exception as e:
        logger.error(f"Failed to get threads for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve threads")

@app.get("/api/thread/{thread_id}/summary")
async def get_thread_summary(thread_id: str):
    """Get summary of a conversation thread"""
    
    try:
        config = RunnableConfig(configurable={"thread_id": thread_id})
        state = await conversation_graph.aget_state(config)
        
        if not state.values:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        return {
            "thread_id": thread_id,
            "message_count": len(state.values.get("messages", [])),
            "last_step": state.values.get("processing_step", "unknown"),
            "summary": state.values.get("conversation_summary", ""),
            "token_count": state.values.get("token_count", 0),
            "user_id": state.values.get("user_id", "unknown"),
            "last_updated": state.values.get("metadata", {}).get("timestamp", "unknown")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get thread summary {thread_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve thread summary")

@app.delete("/api/thread/{thread_id}")
async def delete_thread(thread_id: str):
    """Delete a conversation thread from PostgreSQL"""
    
    try:
        async with asyncpg.connect(DATABASE_URL) as conn:
            result = await conn.execute(
                "DELETE FROM checkpoints WHERE thread_id = $1", 
                thread_id
            )
            
        return {
            "thread_id": thread_id,
            "deleted": True,
            "rows_affected": int(result.split()[-1])
        }
        
    except Exception as e:
        logger.error(f"Failed to delete thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete thread")

@app.get("/admin/database/stats")
async def get_database_stats():
    """Get database statistics for monitoring"""
    
    try:
        async with asyncpg.connect(DATABASE_URL) as conn:
            # Get checkpoint statistics
            stats_query = """
                SELECT 
                    COUNT(*) as total_checkpoints,
                    COUNT(DISTINCT thread_id) as unique_threads,
                    COUNT(DISTINCT checkpoint->>'user_id') as unique_users,
                    MIN(created_at) as oldest_checkpoint,
                    MAX(created_at) as newest_checkpoint
                FROM checkpoints
            """
            stats = await conn.fetchrow(stats_query)
            
            # Get recent activity
            recent_query = """
                SELECT thread_id, created_at, checkpoint->>'processing_step' as step
                FROM checkpoints 
                ORDER BY created_at DESC 
                LIMIT 10
            """
            recent = await conn.fetch(recent_query)
            
        return {
            "stats": dict(stats),
            "recent_activity": [
                {
                    "thread_id": row["thread_id"],
                    "timestamp": row["created_at"].isoformat(),
                    "step": row["step"]
                }
                for row in recent
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve database stats")

