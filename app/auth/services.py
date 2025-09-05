from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.auth.models import User
from app.auth.schemas import UserRegister, UserLogin
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Récupérer la clé depuis le fichier .env
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY manquante dans le fichier .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

def get_device_id_from_headers(request):
    """Extraire le device_id des headers ou du body"""
    # À implémenter selon comment vous voulez passer le device_id
    return None

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
    # Vérifier si l'email existe déjà
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise ValueError("Email already exists")
    
    # Créer ou récupérer l'utilisateur par device_id
    user = db.query(User).filter(User.device_id == user_data.device_id).first()
    if not user:
        user = User(device_id=user_data.device_id, platform=user_data.platform)
        db.add(user)
    
    # Mettre à jour avec les infos d'inscription
    user.email = user_data.email
    user.password_hash = hash_password(user_data.password)
    user.first_name = user_data.firstName  # Correspond à votre frontend
    user.last_name = user_data.lastName    # Correspond à votre frontend
    user.is_registered = True
    
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, login_data: UserLogin) -> User:
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        return None
    
    # Mettre à jour le device_id si nécessaire
    if user.device_id != login_data.device_id:
        user.device_id = login_data.device_id
        db.commit()
    
    return user

def can_ask_question(user: User) -> bool:
    if user.is_registered:
        return True  # Utilisateur inscrit = accès illimité
    return user.free_questions_used < 2

def increment_free_questions(db: Session, device_id: str) -> User:
    user = db.query(User).filter(User.device_id == device_id).first()
    if user and not user.is_registered:
        user.free_questions_used += 1
        db.commit()
        db.refresh(user)
    return user