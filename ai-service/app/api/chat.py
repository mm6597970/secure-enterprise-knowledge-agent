from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.langgraph_agent import run_agentic_rag

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    user: Optional[dict] = None
    history: Optional[List[Dict[str, Any]]] = None

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        res = run_agentic_rag(request.question, request.user, request.history)
        return {
            "answer": res.get("answer", "Information not found."),
            "agent_chosen": res.get("agent_chosen", "RAG"),
            "sql_query": res.get("sql_query", ""),
            "rag_docs": res.get("rag_docs", []),
            "status": res.get("status", "Success")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
