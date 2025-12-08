from fastapi.responses import StreamingResponse
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..database.db_models import Book
from ..core.auth import get_current_user
from ..models.schemas import ChatRequest
from ..core.rag_pipeline import run_rag_stream


router = APIRouter()

@router.post("/stream")
async def chat_stream(request: ChatRequest, user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Main RAG chat endpoint
    Accepts a question from the user and returns a context-aware answer
    """

    book = db.query(Book).filter(Book.id == request.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    user_id = user["id"]
    if book.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed to access this book")
    
    if book.status != "ready":
        raise HTTPException(status_code=400, detail="Book is still ingesting")

    async def event_generator():
        async for chunk in run_rag_stream(request.question, book.vectorstore_path):
            yield chunk
    return StreamingResponse(event_generator(), media_type="text/plain")