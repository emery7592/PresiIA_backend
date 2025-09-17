from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from decimal import Decimal
import re

class UserRegister(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    device_id: str
    platform: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:  # Adapté à ton frontend (6 caractères minimum)
            raise ValueError('Password must be at least 6 characters')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    device_id: str

class PaymentIntentRequest(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    device_id: str
    platform: str
    amount: Decimal = Decimal('9.99')
    currency: str = 'eur'

class PaymentIntentResponse(BaseModel):
    success: bool
    client_secret: Optional[str] = None
    error: Optional[str] = None
    message: str

class PaymentConfirmRequest(BaseModel):
    payment_intent_id: str
    email: EmailStr
    password: str
    firstName: str
    lastName: str
    device_id: str
    platform: str

class PaymentConfirmationResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    user: Optional[dict] = None
    error: Optional[str] = None

class SubscriptionResponse(BaseModel):
    id: str
    status: str
    current_period_start: str
    current_period_end: str
    cancel_at_period_end: bool

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class RegisterResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict
    message: str

class ChatRequest(BaseModel):
    message: str
    history: list = []
    language: str = "en"
    device_id: str

