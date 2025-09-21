from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
import logging
import os

from app.database.database import get_database
from app.payment.schemas import (
    PaymentIntentRequest, 
    PaymentIntentResponse
)
from app.auth.dependencies import require_auth
from app.auth.models import User, Payment
from app.payment.services import (
    create_payment_intent_service,
    get_user_subscription,
    handle_stripe_webhook
)

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