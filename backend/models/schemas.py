from pydantic import BaseModel, EmailStr


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