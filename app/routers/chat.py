"""
AgriSmart AI - Chat Router
Provides Gemini 2.5 Flash powered multi-turn chatbot for plant disease follow-up questions.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.chat import ChatRequest, ChatResponse, ConversationTurn
from app.services.gemini_service import gemini_advisor

router = APIRouter(prefix="/api/v1/chat", tags=["AgriBot: Plant Disease Chatbot"])


@router.post(
    "/message",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask AgriBot a follow-up question about your plant diagnosis",
    description=(
        "Sends a farmer's follow-up question to Gemini 2.5 Flash with full disease context. "
        "Supports multi-turn conversation history. The bot is pre-primed with the diagnosed disease "
        "and crop name for context-aware answers."
    )
)
def send_chat_message(payload: ChatRequest):
    try:
        history_dicts = [{"role": t.role, "content": t.content} for t in payload.conversation_history]
        result = gemini_advisor.chat_followup(
            message=payload.message,
            disease_name=payload.disease_name,
            crop=payload.crop,
            conversation_history=history_dicts,
            language=payload.language or "en"
        )
        updated_history = [
            ConversationTurn(role=t["role"], content=t["content"])
            for t in result["conversation_history"]
        ]
        return ChatResponse(reply=result["reply"], conversation_history=updated_history)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )
