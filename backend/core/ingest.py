from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from ..database.db_models import Book
from ..database.supabase_client import supabase
from ..database.connection import SessionLocal
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from pathlib import Path
from uuid import uuid4
import tempfile
import os
from datetime import datetime
import unicodedata
import re


load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


def clean_text(text: str) -> str:
    # Remove surrogate characters
    text = text.encode("utf-8", "ignore").decode("utf-8", "ignore")

    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)

    # Optional: remove non-BMP characters (math fonts, emoji)
    text = re.sub(r"[\U00010000-\U0010FFFF]", "", text)

    return text


def download_book_from_supabase(storage_path: str):
    response = supabase.storage.from_("books").download(storage_path)
    return response


def ingest_books(book_id: str, storage_path: str, vectorstore_path: str):
    """
    Ingest the uploaded book into its own vectorstore.
    """
    print(f"\n[INGEST] Starting ingestion for book {book_id}")
    
    db = SessionLocal()
    
    # Update DB -> status = ingesting
    book = db.query(Book).filter(Book.id==book_id).first()
    if book:
        book.status = "ingesting"
        db.commit()
        
    # Download PDF from supabase storage
    pdf_bytes = download_book_from_supabase(storage_path)
    
    # Create a temporary file to load the pdf
    tmp_pdf_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            tmp_pdf_path = tmp_pdf.name
        
        # Load pdf
        loader = PyPDFLoader(tmp_pdf_path)
        docs = loader.load()
        
        # Clean text in all documents before splitting
        for doc in docs:
            doc.page_content = clean_text(doc.page_content)
        
        # Splitting
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=100
        )
        chunks = splitter.split_documents(docs)
        
        # Create vector directory
        Path(vectorstore_path).mkdir(parents=True, exist_ok=True)
        
        vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory=vectorstore_path
        )
        
        ids = [f"{book_id}_{uuid4()}" for _ in range(len(chunks))]
        vector_store.add_documents(documents=chunks, ids=ids)
        
        if book:
            book.status = "ready"
            book.ingested_at = datetime.now()
            db.commit()
            
        print(f"[INGEST] Completed ingestion for {book_id}")
    
    except Exception as e:
        book.status = "failed"
        db.commit()
        print("[INGEST ERROR]", e)
        raise e
    
    finally:
        # Deleting temporary file
        if tmp_pdf_path and os.path.exists(tmp_pdf_path):
            os.remove(tmp_pdf_path)
            print(f"[INGEST] Deleted temporary file {tmp_pdf_path}")
