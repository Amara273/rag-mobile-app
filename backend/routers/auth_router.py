from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from database import get_db
from models import UserCreate, UserLogin, Token, UserResponse
from auth import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
import crud

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix= "/api/auth",
    tags = ["authentication"]
)

@router.post("/register", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        if len(user.password) > 72:
            raise HTTPException(status_code=400, detail="Password cannot be longer than 72 characters.")
        
        if len(user.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

        db_user = crud.get_user_by_email(db=db, email=user.email)
        if db_user:
            raise HTTPException(status_code=409, detail="User already exists")

        new_user = crud.create_user(db=db, user=user)
        return new_user
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post("/login", response_model=Token)
def login_user(
    user: UserLogin,             
    db: Session = Depends(get_db)
):
    try:
        db_user = crud.get_user_by_email(db=db, email=user.email)  

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )

        if not verify_password(user.password, db_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.email},
            expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# app.include_router(router)