"""
AgriSmart AI - Chat Schemas
Chatbot follow-up conversation request and response models.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    role: str = Field(..., description="'user' or 'model'")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., description="The farmer's follow-up question")
    disease_name: str = Field(..., description="The diagnosed disease name from the CV model")
    crop: str = Field(..., description="The crop type")
    conversation_history: List[ConversationTurn] = Field(
        default=[], description="Previous turns in the conversation"
    )
    language: Optional[str] = Field("en", description="Preferred language (en, hi, mr, etc.)")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="AgriBot's response")
    conversation_history: List[ConversationTurn] = Field(
        ..., description="Updated conversation history including this turn"
    )
