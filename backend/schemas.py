from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
# 
from database import Base

class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    active = Column(Boolean, nullable=False, server_default="true")

    chats = relationship("ChatHistory", back_populates="user")

class ChatHistory(Base):
    __tablename__ = "chat_history"
 
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True)  
    session_id = Column(String(255), nullable=False)
    role       = Column(String(10), nullable=False)        # 'user' or 'bot'
    message    = Column(Text, nullable=False)
    input_type = Column(String(10), server_default="text") # 'text' 'voice' 'image'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
 
    user = relationship("Users", back_populates="chats")