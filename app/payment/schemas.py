from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
import logging
import os

from app.database.database import get_database
from app.payment.schemas import (
    PaymentIntentRequest, 
    PaymentIntentResponse,
    AppleReceiptRequest,
    GooglePurchaseRequest,
    IAPVerificationResponse
)
from app.auth.dependencies import require_auth
from app.auth.models import User, Payment, Subscription, SubscriptionStatusEnum, PlatformEnum
from app.payment.services import (
    create_payment_intent_service,
    get_user_subscription,
    handle_stripe_webhook
)
from app.payment.iap_service import (
    create_or_update_subscription_from_apple,
    create_or_update_subscription_from_google
)
from app.auth.services import hash_password, create_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payment", tags=["payment"])

@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    request: PaymentIntentRequest,
    db: Session = Depends(get_database)
):
    try:
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user and existing_user.is_registered:
            return PaymentIntentResponse(
                success=False,
                error="Un utilisateur avec cet email existe déjà",
                message="Email déjà utilisé"
            )
        
        user_data = {
            "email": request.email,
            "firstName": request.firstName,
            "lastName": request.lastName,
            "device_id": request.device_id,
            "platform": request.platform,
            "password": request.password
        }
        
        result = create_payment_intent_service(db, user_data)
        
        return PaymentIntentResponse(
            success=True,
            client_secret=result["client_secret"],
            message="PaymentIntent créé avec succès"
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la création du PaymentIntent: {e}")
        return PaymentIntentResponse(
            success=False,
            error=str(e),
            message="Erreur lors de la création du paiement"
        )

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature")
):
    try:
        if not stripe_signature:
            logger.error("Signature Stripe manquante dans les headers")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signature Stripe manquante"
            )
        
        payload = await request.body()
        logger.info(f"Webhook reçu avec signature: {stripe_signature[:20]}...")
        
        db = next(get_database())
        try:
            result = handle_stripe_webhook(payload, stripe_signature, db)
            db.close()
        except Exception as e:
            db.close()
            raise e
        
        return {"status": "success", "event_type": result["event_type"]}
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement du webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du traitement du webhook: {str(e)}"
        )

@router.get("/health")
async def payment_health_check():
    return {
        "status": "healthy",
        "module": "payment",
        "stripe_configured": bool(os.getenv("STRIPE_SECRET_KEY"))
    }

@router.get("/status/{payment_intent_id}")
async def check_payment_status(
    payment_intent_id: str,
    db: Session = Depends(get_database)
):
    try:
        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent_id
        ).first()
        
        if payment:
            return {"success": True, "message": "Paiement confirmé"}
        else:
            return {"success": False, "message": "Paiement en attente"}
    except Exception as e:
        return {"success": False, "message": "Erreur vérification"}

@router.post("/verify/apple", response_model=IAPVerificationResponse)
async def verify_apple_purchase(
    request: AppleReceiptRequest,
    db: Session = Depends(get_database)
):
    try:
        # Récupérer l'utilisateur par device_id
        user = db.query(User).filter(User.device_id == request.device_id).first()
        
        if not user:
            # Vérifier si email existe déjà
            existing_email = db.query(User).filter(User.email == request.email).first()
            if existing_email:
                return IAPVerificationResponse(
                    success=False,
                    message="Email déjà utilisé",
                    error="EMAIL_EXISTS"
                )
            
            # Créer le nouvel utilisateur
            logger.info(f"Création nouvel utilisateur iOS: {request.email}")
            
            user = User(
                email=request.email,
                first_name=request.first_name,
                last_name=request.last_name,
                device_id=request.device_id,
                platform=PlatformEnum.ios,
                password_hash=hash_password(request.password),
                is_registered=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"Utilisateur créé avec succès: {user.id}")
        
        # Créer/mettre à jour l'abonnement
        subscription = create_or_update_subscription_from_apple(
            db, user, request.receipt_data
        )
        
        # Générer token JWT pour login automatique
        token = create_access_token({"sub": str(user.id)})
        
        return IAPVerificationResponse(
            success=True,
            message="Abonnement Apple vérifié et compte créé",
            token=token,
            user={
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_premium": True
            },
            subscription={
                "id": str(subscription.id),
                "status": subscription.status.value,
                "expires_at": subscription.current_period_end.isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur vérification Apple: {e}")
        db.rollback()
        return IAPVerificationResponse(
            success=False,
            message="Erreur lors de la vérification",
            error=str(e)
        )


@router.post("/verify/google", response_model=IAPVerificationResponse)
async def verify_google_purchase(
    request: GooglePurchaseRequest,
    db: Session = Depends(get_database)
):
    try:
        # Récupérer l'utilisateur par device_id
        user = db.query(User).filter(User.device_id == request.device_id).first()
        
        if not user:
            # Vérifier si email existe déjà
            existing_email = db.query(User).filter(User.email == request.email).first()
            if existing_email:
                return IAPVerificationResponse(
                    success=False,
                    message="Email déjà utilisé",
                    error="EMAIL_EXISTS"
                )
            
            # Créer le nouvel utilisateur
            logger.info(f"Création nouvel utilisateur Android: {request.email}")
            
            user = User(
                email=request.email,
                first_name=request.first_name,
                last_name=request.last_name,
                device_id=request.device_id,
                platform=PlatformEnum.android,
                password_hash=hash_password(request.password),
                is_registered=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"Utilisateur créé avec succès: {user.id}")
        
        # Créer/mettre à jour l'abonnement
        subscription = create_or_update_subscription_from_google(
            db, user, request.purchase_token, request.product_id
        )
        
        # Générer token JWT pour login automatique
        token = create_access_token({"sub": str(user.id)})
        
        return IAPVerificationResponse(
            success=True,
            message="Abonnement Google vérifié et compte créé",
            token=token,
            user={
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_premium": True
            },
            subscription={
                "id": str(subscription.id),
                "status": subscription.status.value,
                "expires_at": subscription.current_period_end.isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur vérification Google: {e}")
        db.rollback()
        return IAPVerificationResponse(
            success=False,
            message="Erreur lors de la vérification",
            error=str(e)
        )


@router.get("/subscription/status")
async def get_subscription_status(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_database)
):
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.status == SubscriptionStatusEnum.active
        ).first()
        
        if not subscription:
            return {
                "has_subscription": False,
                "message": "Aucun abonnement actif"
            }
        
        return {
            "has_subscription": True,
            "subscription": {
                "id": str(subscription.id),
                "platform": subscription.platform_source,
                "status": subscription.status.value,
                "current_period_end": subscription.current_period_end.isoformat(),
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération statut abonnement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur"
        )