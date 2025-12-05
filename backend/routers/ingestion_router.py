from fastapi import APIRouter, UploadFile, File
from ..core.ingest import ingest_documents
from pathlib import Path
import shutil


router = APIRouter

DOCUMENTS_DIR = Path(__file__).resolve().parent.parent / "data" / "documents"
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = DOCUMENTS_DIR / file.filename
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ingest_documents()
    
    return("message:", "File uploaded and ingested successfully")