from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routers import chat_router, auth_router, books_router
from pathlib import Path

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(books_router.router, prefix="/books", tags=["books"])
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(chat_router.router, prefix="/chat", tags=["chat"])

@app.get("/health")
async def check_health():
    return {"status": "ok"}