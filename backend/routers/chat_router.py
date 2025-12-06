from fastapi import APIRouter
from ..models.schemas import ChatRequest, ChatResponse
from ..core.rag_pipeline import run_rag


router = APIRouter()

@router.get("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main RAG chat endpoint
    Accepts a question from the user and returns a context-aware answer
    """
    answer = await run_rag(request.question)
    return ChatResponse(answer=answer)