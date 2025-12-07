from fastapi import APIRouter, File, UploadFile, BackgroundTasks, Depends
from ..services.storage import upload_book_to_supabase
from ..core.auth import get_current_user
from ..core.ingest import ingest_books
from ..database.db_models import Book
from ..database.connection import get_db
from sqlalchemy.orm import Session
from pathlib import Path
import uuid
import os



router = APIRouter()


@router.post("/upload")
async def upload_book(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    VECTORSTORE_BASE = BASE_DIR / "vectorstores"
    
    user_id = user.id if hasattr(user, "id") else user.get("id")
    book_id = str(uuid.uuid4())
    
    storage_path = await upload_book_to_supabase(file, user_id, book_id)
    
    vectorstore_path = str(VECTORSTORE_BASE / user_id / book_id)
    
    new_book = Book(
        id=book_id,
        user_id=user_id,
        title=file.filename,
        file_name=file.filename,
        storage_path=storage_path,
        vectorstore_path=vectorstore_path,
        status="uploaded"
    )
    
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    # ingestion task
    background_tasks.add_task(
        ingest_books,
        book_id,
        storage_path,
        vectorstore_path
    )
    
    return {
        "message": "Book uploaded to Supabase. Ingestion started.",
        "book_id": book_id
    }
    
    
    
    
@router.post("/test-header")
async def check_header(
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return {"user": user}



@router.post("/test-upload")
async def upload_book(
    file: UploadFile = File(...)
):
    return {"message": "file uploaded successfully"}