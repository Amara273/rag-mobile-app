from sqlalchemy.orm import Session
from schemas import Users, ChatHistory
from models import UserCreate
from auth import get_password_hash
import uuid

def get_user_by_email(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(Users).filter(Users.user_id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(Users).filter(Users.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_psw = get_password_hash(user.password)
    db_user = Users(
        username=user.username,
        email=user.email,
        password=hashed_psw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def save_message(db: Session, user_id: int, session_id: str, role: str, message: str, input_type: str = "text"):
    """Save one message to chat history."""
    db_message = ChatHistory(
        user_id=user_id,
        session_id=session_id,
        role=role,
        message=message,
        input_type=input_type
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_all_sessions(db: Session, user_id: int):
    from sqlalchemy import func
    subquery = db.query(
        ChatHistory.session_id,
        func.max(ChatHistory.created_at).label("last_time")
    ).filter(
        ChatHistory.user_id == user_id,
        # ← removed role == "user" filter, NULLs were being excluded
    ).group_by(ChatHistory.session_id).subquery()

    results = db.query(ChatHistory).join(
        subquery,
        (ChatHistory.session_id == subquery.c.session_id) &
        (ChatHistory.created_at == subquery.c.last_time)
    ).all()
    return results

def get_session_messages(db: Session, user_id: int, session_id: str):
    """Get all messages in one session ordered by time."""
    return db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id,
        ChatHistory.session_id == session_id
    ).order_by(ChatHistory.created_at.asc()).all()

def delete_session(db: Session, user_id: int, session_id: str):
    """Delete all messages in a session."""
    db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id,
        ChatHistory.session_id == session_id
    ).delete()
    db.commit()