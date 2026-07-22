from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import answer_question

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        answer = answer_question(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
