from datetime import datetime, timedelta
from jose import jwt, JWTError
from core.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
 
def create_token(id: int, email: str) -> str:
    """Create JWT token with user info and expiry."""
    payload = {
        "sub": email,           
        "user_id": id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
 
def decode_token(token: str) -> dict | None:
    """Verify and decode JWT token. Returns None if invalid."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
 