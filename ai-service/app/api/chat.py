from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import answer_question

router = APIRouter()

from typing import Optional

class ChatRequest(BaseModel):
    question: str
    user: Optional[dict] = None

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        answer = answer_question(request.question, request.user)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
