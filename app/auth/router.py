from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.auth.schemas import UserRegister, UserLogin, ChatRequest
from app.auth.services import *
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_database)):
    try:
        user = register_user(db, user_data)
        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer", "user_id": str(user.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_database)):
    user = authenticate_user(db, login_data)
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user_id": str(user.id)}

@router.post("/logout")
def logout():
    return {"message": "Déconnexion réussie"}