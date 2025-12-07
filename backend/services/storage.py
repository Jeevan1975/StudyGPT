from supabase import create_client
from ..config import settings
import uuid
import httpx


custom_httpx = httpx.Client(
    timeout=httpx.Timeout(write=60.0, connect=30.0, read=30.0, pool=30.0),
    http2=False
)


def get_user_supabase_client(user_access_token: str):
    supabase = create_client(settings.SUPABASE_URL, user_access_token)
    
    supabase.storage._client = custom_httpx

    return supabase



async def upload_book_to_supabase(file, user_id: str, book_id: str, user_access_token: str):
    """
    Uploads books to supabase storage bucket
    """
    supabase = get_user_supabase_client(user_access_token)
    
    storage_path = f"{user_id}/{book_id}/{file.filename}"
    
    file_bytes = await file.read()
    try:
        supabase.storage.from_("books").upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": "application/pdf"}
        )
        
        return storage_path

    except Exception as e:
        print("Upload error -> ", e)
        raise e