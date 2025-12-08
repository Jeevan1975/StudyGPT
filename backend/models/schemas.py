from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    question: str
    

class ChatResponse(BaseModel):
    answer: str
    

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    
    
class BookResponse(BaseModel):
    id: UUID
    title: str
    status: str
    file_name: str
    storage_path: str
    uploaded_at: datetime
    ingested_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)