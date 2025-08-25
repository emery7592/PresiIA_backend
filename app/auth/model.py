from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
import uuid
import enum

class PlatformEnum(str, enum.Enum):
    ios = "ios"
    android = "android"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    device_id = Column(String(255), unique=True, nullable=False)
    free_questions_used = Column(Integer, default=0)
    platform = Column(Enum(PlatformEnum), nullable=False)
    is_registered = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic schemas
from pydantic import BaseModel, EmailStr, validator

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    device_id: str
    platform: PlatformEnum
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        if not any(c.isupper() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in v):
            raise ValueError('Le mot de passe doit contenir au moins un caractère spécial')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    device_id: str

class ChatRequest(BaseModel):
    message: str
    device_id: str