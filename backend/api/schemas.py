from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    message: str
    session_id: str
    agent: str = "cisa"
    aws_profile: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = []

class HealthResponse(BaseModel):
    status: str
    version: str
