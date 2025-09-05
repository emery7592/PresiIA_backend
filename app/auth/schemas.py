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

# Schémas Pydantic pour les paiements
class PaymentIntentRequest(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str
    device_id: str
    platform: PlatformEnum

class PaymentConfirmRequest(BaseModel):
    payment_intent_id: str
    email: EmailStr
    password: str
    firstName: str
    lastName: str
    device_id: str
    platform: PlatformEnum

class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str

class SubscriptionResponse(BaseModel):
    id: str
    status: str
    current_period_start: Optional[str]
    current_period_end: Optional[str]
    cancel_at_period_end: bool
