from pydantic import BaseModel
from typing import Optional
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    question: str
