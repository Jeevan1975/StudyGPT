from fastapi import APIRouter, File, UploadFile, BackgroundTasks, Depends, Header, HTTPException
from ..services.storage import upload_book_to_supabase, delete_book_from_supabase
from ..core.auth import get_current_user
from ..core.ingest import ingest_books
from ..database.db_models import Book
from ..database.connection import get_db
from ..models.schemas import BookResponse
from sqlalchemy.orm import Session
from pathlib import Path
import uuid
import os
import shutil


router = APIRouter()


@router.get("/", response_model=list[BookResponse])
async def list_books(db: Session = Depends(get_db), user = Depends(get_current_user)): 
    user_id = user["id"]
    books = db.query(Book).filter(Book.user_id == user_id).order_by(Book.uploaded_at.desc()).all()
    print(books)
    return books




@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    book_id = book_id
    user_id = user["id"]
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed to view this book")

    return book




@router.delete("/{book_id}")
async def delete_book(book_id: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    book_id = book_id
    user_id = user["id"]
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this book")
    
    await delete_book_from_supabase(storage_path=book.storage_path)

    # Delete from vectorstore
    try:
        shutil.rmtree(book.vectorstore_path, ignore_errors=True)
    except Exception as e:
        print("Vectorstore deletion error: ", e)

    # Delete from database
    db.delete(book)
    db.commit()
    
    return {"message": "Book deleted successfully", "book_id": book_id}




@router.post("/upload")
async def upload_book(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    VECTORSTORE_BASE = BASE_DIR / "vectorstores"
    
    user_id = user["id"]
    book_id = str(uuid.uuid4())
    
    user_access_token = user["access_token"]
    
    storage_path = await upload_book_to_supabase(file, user_id, book_id, user_access_token)
    
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