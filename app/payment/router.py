from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
import logging
import os

from app.database.database import get_database
from app.payment.schemas import (
    PaymentIntentRequest, 
    PaymentConfirmationRequest, 
    PaymentIntentResponse, 
    SubscriptionResponse
)
from app.auth.dependencies import require_auth
from app.auth.models import User
from app.payment.services import (
    create_payment_intent_service,
    validate_and_create_user,
    get_user_subscription,
    handle_stripe_webhook
)

# Configuration du logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payment", tags=["payment"])

@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    request: PaymentIntentRequest,
    db: Session = Depends(get_database)
):
    """
    Crée un PaymentIntent Stripe pour l'inscription avec paiement
    """
    try:
        # Vérifier si l'email existe déjà
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user and existing_user.is_registered:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec cet email existe déjà"
            )
        
        # Créer le PaymentIntent
        user_data = {
            "email": request.email,
            "firstName": request.firstName,
            "lastName": request.lastName,
            "device_id": request.device_id,
            "platform": request.platform
        }
        
        result = create_payment_intent_service(db, user_data)
        
        return PaymentIntentResponse(
            client_secret=result["client_secret"],
            payment_intent_id=result["payment_intent_id"]
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la création du PaymentIntent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du paiement: {str(e)}"
        )

@router.post("/confirm")
async def confirm_payment(
    request: PaymentConfirmRequest,
    db: Session = Depends(get_database)
):
    """
    Confirme le paiement et crée l'utilisateur avec son abonnement
    """
    try:
        # Valider le paiement et créer l'utilisateur
        payment_data = {
            "payment_intent_id": request.payment_intent_id,
            "email": request.email,
            "password": request.password,
            "firstName": request.firstName,
            "lastName": request.lastName,
            "device_id": request.device_id,
            "platform": request.platform
        }
        
        result = validate_and_create_user(db, payment_data)
        
        return {
            "message": "Paiement confirmé et compte créé avec succès",
            "access_token": result["access_token"],
            "token_type": result["token_type"],
            "user_id": result["user_id"],
            "subscription_id": result["subscription_id"]
        }
        
    except ValueError as e:
        logger.error(f"Erreur de validation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la confirmation du paiement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la confirmation du paiement: {str(e)}"
        )

@router.get("/subscription", response_model=Optional[SubscriptionResponse])
async def get_subscription(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_database)
):
    """
    Récupère l'abonnement actif de l'utilisateur connecté
    """
    try:
        subscription = get_user_subscription(db, str(current_user.id))
        
        if not subscription:
            return None
        
        return SubscriptionResponse(
            id=subscription["id"],
            status=subscription["status"],
            current_period_start=subscription["current_period_start"],
            current_period_end=subscription["current_period_end"],
            cancel_at_period_end=subscription["cancel_at_period_end"]
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'abonnement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'abonnement: {str(e)}"
        )

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None)
):
    """
    Webhook Stripe pour synchroniser les événements de paiement
    """
    try:
        if not stripe_signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signature Stripe manquante"
            )
        
        # Lire le body de la requête
        payload = await request.body()
        
        # Traiter le webhook
        result = handle_stripe_webhook(payload, stripe_signature)
        
        return {"status": "success", "event_type": result["event_type"]}
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement du webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du traitement du webhook: {str(e)}"
        )

@router.get("/health")
async def payment_health_check():
    """
    Vérification de la santé du module de paiement
    """
    return {
        "status": "healthy",
        "module": "payment",
        "stripe_configured": bool(os.getenv("STRIPE_SECRET_KEY"))
    }