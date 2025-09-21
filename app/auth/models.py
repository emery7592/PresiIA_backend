# Imports nécessaires
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, Numeric, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import uuid
import enum

# Enums existants
class PlatformEnum(str, enum.Enum):
    ios = "ios"
    android = "android"

# Enums pour les paiements
class SubscriptionStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    canceled = "canceled"
    past_due = "past_due"

class PaymentStatusEnum(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"

# Classe User modifiée
class User(Base):
    __tablename__ = "users"
    
    # Colonnes existantes
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    device_id = Column(String(255), unique=True, nullable=False)
    free_questions_used = Column(Integer, default=0)
    platform = Column(Enum(PlatformEnum), nullable=False)
    is_registered = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Nouvelle colonne pour Stripe
    stripe_customer_id = Column(String(255), nullable=True)
    
    # Relations
    subscriptions = relationship("Subscription", back_populates="user")
    payments = relationship("Payment", back_populates="user")

# Classe Subscription
class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    stripe_price_id = Column(String(255), nullable=False)
    status = Column(Enum(SubscriptionStatusEnum), default=SubscriptionStatusEnum.active)
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")

# Classe Payment corrigée
class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    stripe_payment_intent_id = Column(String(255), unique=True, nullable=False)
    stripe_invoice_id = Column(String(255), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="eur")
    status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.pending)
    payment_method_id = Column(String(255), nullable=True)
    failure_reason = Column(String(500), nullable=True)
    metadata = Column(JSON, nullable=True)  # CORRIGÉ: metadata -> meta_data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")