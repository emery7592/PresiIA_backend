from pydantic import BaseModel, EmailStr
from typing import Optional
from app.auth.models import PlatformEnum

# Schémas Pydantic pour l'authentification
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    firstName: str
    lastName: str
    device_id: str
    platform: PlatformEnum

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    device_id: str

class ChatRequest(BaseModel):
    message: str
    device_id: str
    platform: PlatformEnum

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ForgotPasswordResponse(BaseModel):
    success: bool
    message: str

class ResetPasswordResponse(BaseModel):
    success: bool
    message: str
