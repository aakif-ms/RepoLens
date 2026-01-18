from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

class ChatSession(BaseModel):
    session_id: str
    repo_id: str
    created_at: datetime
    messages: List[dict] = []
    
class ChatMessage(BaseModel):
    session_id: str
    message: str
    
class CreateSessionRequest(BaseModel):
    repo_id: str
    
class StreamResponse(BaseModel):
    content: str
    done: bool = False