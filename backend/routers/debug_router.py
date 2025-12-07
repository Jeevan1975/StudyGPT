from fastapi import APIRouter, Request


router = APIRouter()

@router.get("/headers")
async def debug_headers(request: Request):
    return dict(request.headers)