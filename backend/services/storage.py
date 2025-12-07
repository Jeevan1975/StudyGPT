from ..database.supabase_client import supabase
import uuid


async def upload_book_to_supabase(file, user_id: str, book_id: str):
    """
    Uploads books to supabase storage bucket
    """
    storage_path = f"{user_id}/{book_id}/{file.filename}"
    
    file_bytes = await file.read()
    try:
        supabase.storage.from_("books").upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": "application/pdf", "upsert":True}
        )
        
        return storage_path

    except Exception as e:
        print("Upload error -> ", e)
        raise e