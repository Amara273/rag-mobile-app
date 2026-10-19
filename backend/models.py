from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ── User models ────────────────────────────────────────────────────────────────
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    user_id: int
    created_at: Optional[datetime]
    active: bool
    class Config:
        from_attributes = True

# ── JWT models ─────────────────────────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# ── Chat models ────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    top_k: int = 5

class ChatResponse(BaseModel):
    response: str
    sources: list
    session_id: Optional[str]
    saved: bool

class MessageResponse(BaseModel):
    role: str
    message: str
    input_type: str
    created_at: Optional[datetime]
    class Config:
        from_attributes = True

class SessionResponse(BaseModel):
    session_id: str
    last_message: str
    created_at: Optional[datetime]

class LoginRequest(BaseModel):
    email: str
    password: str

