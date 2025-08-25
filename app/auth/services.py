from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from models import User, UserRegister, UserLogin
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_or_create_anonymous_user(db: Session, device_id: str, platform: str) -> User:
    user = db.query(User).filter(User.device_id == device_id).first()
    if not user:
        user = User(device_id=device_id, platform=platform)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def register_user(db: Session, user_data: UserRegister) -> User:
    # Récupérer l'utilisateur anonyme existant
    user = db.query(User).filter(User.device_id == user_data.device_id).first()
    if not user:
        raise ValueError("Device non trouvé")
    
    # Vérifier que l'email n'existe pas déjà
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise ValueError("Email déjà utilisé")
    
    # Mettre à jour avec les infos d'inscription
    user.email = user_data.email
    user.password_hash = hash_password(user_data.password)
    user.is_registered = True
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, login_data: UserLogin) -> User:
    user = db.query(User).filter(
        User.email == login_data.email,
        User.device_id == login_data.device_id
    ).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        return None
    return user

def can_ask_question(user: User) -> bool:
    if user.is_registered:
        return True  # Utilisateur payant peut poser des questions
    return user.free_questions_used < 2