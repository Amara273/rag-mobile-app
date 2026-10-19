from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from schemas import Users
from crud import get_all_sessions, get_session_messages, delete_session

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("/")
def get_history(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    sessions = get_all_sessions(db, current_user.user_id)
    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "message": s.message,        # ← was "last_message", Flutter reads "message"
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in sessions
        ]
    }


@router.get("/{session_id}")
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    messages = get_session_messages(db, current_user.user_id, session_id)
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,        # "user" or "bot"
                "content": m.message,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
    }


@router.delete("/{session_id}")
def remove_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    delete_session(db, current_user.user_id, session_id)
    return {"message": f"Session {session_id} deleted."}