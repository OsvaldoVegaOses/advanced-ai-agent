"""
Conversation API Endpoints
Main interface for conversational AI interactions
"""

from typing import Dict, Any, List, Optional
import time
import uuid

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse

from core.database import get_db, get_session_mgr, SessionManager
from core.ai.model_manager import model_manager
from core.logging import conversation_logger, get_logger
from core.exceptions import AgentException

logger = get_logger(__name__)
router = APIRouter()


# Request/Response Models
class ConversationMessage(BaseModel):
    """Single conversation message"""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    timestamp: Optional[float] = Field(default=None, description="Message timestamp")


class ConversationRequest(BaseModel):
    """Request for conversation interaction"""
    message: str = Field(..., description="User message", min_length=1, max_length=4000)
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation continuity")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")
    stream: bool = Field(default=False, description="Enable streaming response")
    model_preference: Optional[str] = Field(default=None, description="Preferred model type")


class ConversationResponse(BaseModel):
    """Response from conversation interaction"""
    message: str = Field(..., description="AI assistant response")
    session_id: str = Field(..., description="Session ID")
    conversation_state: str = Field(..., description="Current conversation state")
    intent: Optional[str] = Field(default=None, description="Detected user intent")
    confidence: Optional[float] = Field(default=None, description="Intent confidence score")
    suggestions: List[str] = Field(default=[], description="Suggested follow-up actions")
    metadata: Dict[str, Any] = Field(default={}, description="Additional response metadata")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class SessionInfo(BaseModel):
    """Session information"""
    session_id: str
    created_at: float
    last_activity: float
    message_count: int
    conversation_state: str
    user_data: Dict[str, Any]


class MultimodalRequest(BaseModel):
    """Request for multimodal interaction"""
    text: Optional[str] = Field(default=None, description="Text input")
    image_data: Optional[str] = Field(default=None, description="Base64 encoded image")
    audio_data: Optional[str] = Field(default=None, description="Base64 encoded audio")
    document_data: Optional[str] = Field(default=None, description="Base64 encoded document")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")


@router.post("/chat", response_model=ConversationResponse)
async def chat_with_agent(
    request: ConversationRequest,
    background_tasks: BackgroundTasks,
    session_mgr: SessionManager = Depends(get_session_mgr)
):
    """
    Main chat endpoint for conversational AI interaction
    """
    start_time = time.time()
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get or create session
        session_data = await session_mgr.get_session(session_id)
        if not session_data:
            await session_mgr.create_session(session_id, {"user_id": request.user_id})
            session_data = await session_mgr.get_session(session_id)
        
        # Log user message
        conversation_logger.log_user_message(
            session_id=session_id,
            user_id=request.user_id or "anonymous",
            message=request.message,
            metadata=request.context
        )
        
        # Process the conversation
        from core.agents.conversation_processor import ConversationProcessor
        processor = ConversationProcessor(session_data, model_manager)
        
        result = await processor.process_message(
            user_message=request.message,
            context=request.context,
            stream=request.stream
        )
        
        # Update session with new data
        await session_mgr.update_session(session_id, {
            "conversation_state": result["state"],
            "messages": result["conversation_history"],
            "user_data": result["user_data"],
            "context": result["context"]
        })
        
        processing_time = (time.time() - start_time) * 1000
        
        # Log agent response
        conversation_logger.log_agent_response(
            session_id=session_id,
            agent_type=result.get("agent_type", "general"),
            response=result["response"],
            processing_time=processing_time / 1000,
            metadata={
                "intent": result.get("intent"),
                "confidence": result.get("confidence"),
                "model_used": result.get("model_used")
            }
        )
        
        # Schedule background tasks
        background_tasks.add_task(
            _process_conversation_analytics,
            session_id,
            request.message,
            result["response"],
            result.get("intent"),
            processing_time
        )
        
        return ConversationResponse(
            message=result["response"],
            session_id=session_id,
            conversation_state=result["state"],
            intent=result.get("intent"),
            confidence=result.get("confidence"),
            suggestions=result.get("suggestions", []),
            metadata=result.get("metadata", {}),
            processing_time_ms=processing_time
        )
        
    except AgentException as e:
        logger.error(f"Agent error in conversation: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
    except Exception as e:
        logger.error(f"Unexpected error in conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing your message"
        )


@router.post("/multimodal", response_model=ConversationResponse)
async def multimodal_interaction(
    request: MultimodalRequest,
    background_tasks: BackgroundTasks,
    session_mgr: SessionManager = Depends(get_session_mgr)
):
    """
    Multimodal interaction endpoint (text, images, audio, documents)
    """
    start_time = time.time()
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get or create session
        session_data = await session_mgr.get_session(session_id)
        if not session_data:
            await session_mgr.create_session(session_id)
            session_data = await session_mgr.get_session(session_id)
        
        # Process multimodal input
        from core.ai.multimodal_processor import MultimodalProcessor
        processor = MultimodalProcessor(model_manager)
        
        multimodal_result = await processor.process_multimodal_input({
            "text": request.text,
            "image": request.image_data,
            "audio": request.audio_data,
            "document": request.document_data,
            "context": request.context
        })
        
        # Use the synthesized understanding for conversation
        from core.agents.conversation_processor import ConversationProcessor
        conv_processor = ConversationProcessor(session_data, model_manager)
        
        # Create enriched message from multimodal analysis
        enriched_message = conv_processor.create_enriched_message(
            original_text=request.text or "Multimodal input provided",
            multimodal_analysis=multimodal_result
        )
        
        result = await conv_processor.process_message(
            user_message=enriched_message,
            context={**request.context, "multimodal": True}
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        # Update session
        await session_mgr.update_session(session_id, {
            "conversation_state": result["state"],
            "messages": result["conversation_history"],
            "user_data": result["user_data"]
        })
        
        return ConversationResponse(
            message=result["response"],
            session_id=session_id,
            conversation_state=result["state"],
            intent=result.get("intent"),
            confidence=result.get("confidence"),
            suggestions=result.get("suggestions", []),
            metadata={
                **result.get("metadata", {}),
                "multimodal_analysis": multimodal_result["synthesized_understanding"]
            },
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error in multimodal interaction: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error processing multimodal input"
        )


@router.get("/session/{session_id}", response_model=SessionInfo)
async def get_session_info(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_mgr)
):
    """Get information about a conversation session"""
    
    session_data = await session_mgr.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionInfo(
        session_id=session_id,
        created_at=session_data["created_at"],
        last_activity=session_data["last_activity"],
        message_count=len(session_data.get("messages", [])),
        conversation_state=session_data.get("conversation_state", "unknown"),
        user_data=session_data.get("user_data", {})
    )


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_mgr)
):
    """Delete a conversation session"""
    
    success = await session_mgr.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}


@router.get("/sessions/cleanup")
async def cleanup_expired_sessions(
    session_mgr: SessionManager = Depends(get_session_mgr)
):
    """Cleanup expired conversation sessions"""
    
    cleaned_count = await session_mgr.cleanup_expired_sessions()
    return {"message": f"Cleaned up {cleaned_count} expired sessions"}


@router.post("/chat/stream")
async def stream_chat_response(
    request: ConversationRequest,
    session_mgr: SessionManager = Depends(get_session_mgr)
):
    """Stream chat response for real-time interaction"""
    
    if not request.stream:
        raise HTTPException(status_code=400, detail="Streaming not enabled in request")
    
    async def generate_stream():
        """Generate streaming response"""
        try:
            session_id = request.session_id or str(uuid.uuid4())
            
            # Get or create session
            session_data = await session_mgr.get_session(session_id)
            if not session_data:
                await session_mgr.create_session(session_id, {"user_id": request.user_id})
                session_data = await session_mgr.get_session(session_id)
            
            # Process with streaming
            from core.agents.conversation_processor import ConversationProcessor
            processor = ConversationProcessor(session_data, model_manager)
            
            async for chunk in processor.process_message_stream(
                user_message=request.message,
                context=request.context
            ):
                yield f"data: {chunk}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/stream"
    )


@router.get("/models/status")
async def get_models_status():
    """Get status of all AI models"""
    
    try:
        status = await model_manager.get_status()
        return {"models": status, "manager_initialized": model_manager.initialized}
    except Exception as e:
        logger.error(f"Error getting models status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving models status")


async def _process_conversation_analytics(
    session_id: str,
    user_message: str,
    agent_response: str,
    intent: Optional[str],
    processing_time: float
):
    """Background task to process conversation analytics"""
    try:
        from services.analytics.conversation_analytics import ConversationAnalytics
        
        analytics = ConversationAnalytics()
        await analytics.record_interaction(
            session_id=session_id,
            user_message=user_message,
            agent_response=agent_response,
            intent=intent,
            processing_time_ms=processing_time
        )
    except Exception as e:
        logger.error(f"Error processing conversation analytics: {e}")