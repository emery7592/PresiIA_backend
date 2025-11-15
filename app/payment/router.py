from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
import logging
import os

from app.database.database import get_database
from app.payment.schemas import (
    IAPVerificationResponse,
    RevenueCatPurchaseRequest
)
from app.auth.dependencies import require_auth
from app.auth.models import User, Payment, Subscription, SubscriptionStatusEnum, PlatformEnum
from app.payment.revenuecat_service import revenuecat_service
from app.auth.services import hash_password, create_access_token
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payment", tags=["payment"])

@router.post("/verify-purchase", response_model=IAPVerificationResponse)
async def verify_revenuecat_purchase(
    request: RevenueCatPurchaseRequest,
    db: Session = Depends(get_database)
):
    """
    Vérifie l'achat RevenueCat et crée le compte utilisateur
    """
    try:
        # 1. Vérifier si email existe déjà
        existing_user = db.query(User).filter(
            User.email == request.email,
            User.is_registered == True
        ).first()

        if existing_user:
            return IAPVerificationResponse(
                success=False,
                message="Un compte existe déjà avec cet email",
                error="EMAIL_EXISTS"
            )

        # 2. Vérifier l'abonnement via RevenueCat
        # Utiliser l'email comme app_user_id (ou device_id selon ta config RevenueCat)
        subscription_info = await revenuecat_service.verify_purchase(request.email)

        if not subscription_info or not subscription_info.get("is_active"):
            return IAPVerificationResponse(
                success=False,
                message="Aucun abonnement actif trouvé",
                error="NO_ACTIVE_SUBSCRIPTION"
            )

        # 3. Créer l'utilisateur
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
        db.flush()  # Pour obtenir l'ID

        # 4. Créer l'abonnement dans la base
        subscription = Subscription(
            user_id=user.id,
            platform_source="revenuecat",
            status=SubscriptionStatusEnum.active,
            current_period_start=datetime.fromisoformat(
                subscription_info["original_purchase_date"].replace("Z", "+00:00")
            ),
            current_period_end=subscription_info["expires_date"]
        )
        db.add(subscription)
        db.commit()
        db.refresh(user)

        # 5. Générer le token JWT
        token = create_access_token({"sub": str(user.id)})

        return IAPVerificationResponse(
            success=True,
            message="Compte créé et abonnement activé",
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
        logger.error(f"Erreur vérification RevenueCat: {e}")
        db.rollback()
        return IAPVerificationResponse(
            success=False,
            message="Erreur lors de la vérification",
            error=str(e)
        )


@router.post("/webhook/revenuecat")
async def revenuecat_webhook(
    request: Request,
    db: Session = Depends(get_database)
):
    """Webhook pour les événements RevenueCat"""
    try:
        payload = await request.json()
        event_type = payload.get("type")

        logger.info(f"Webhook RevenueCat reçu: {event_type}")

        # Récupérer les informations de l'événement
        event_data = payload.get("event", {})
        app_user_id = event_data.get("app_user_id")
        product_id = event_data.get("product_id")

        if not app_user_id:
            logger.error("app_user_id manquant dans le webhook")
            return {"status": "error", "message": "app_user_id manquant"}

        # Récupérer l'utilisateur (app_user_id devrait être l'email)
        user = db.query(User).filter(User.email == app_user_id).first()

        if not user:
            logger.warning(f"Utilisateur non trouvé pour app_user_id: {app_user_id}")
            return {"status": "error", "message": "Utilisateur non trouvé"}

        # Récupérer l'abonnement actif
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == SubscriptionStatusEnum.active
        ).first()

        if event_type == "RENEWAL":
            # Mettre à jour current_period_end
            if subscription:
                expiration_date = event_data.get("expiration_at_ms")
                if expiration_date:
                    subscription.current_period_end = datetime.fromtimestamp(int(expiration_date) / 1000)
                    db.commit()
                    logger.info(f"Abonnement renouvelé pour {app_user_id}")

        elif event_type == "CANCELLATION":
            # Marquer cancel_at_period_end = True
            if subscription:
                subscription.cancel_at_period_end = True
                subscription.canceled_at = datetime.utcnow()
                db.commit()
                logger.info(f"Abonnement annulé pour {app_user_id}")

        elif event_type == "EXPIRATION":
            # Mettre status = inactive
            if subscription:
                subscription.status = SubscriptionStatusEnum.inactive
                db.commit()
                logger.info(f"Abonnement expiré pour {app_user_id}")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Erreur webhook RevenueCat: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
async def payment_health_check():
    """Vérification de santé du module de paiement"""
    return {
        "status": "healthy",
        "module": "payment",
        "revenuecat_configured": bool(os.getenv("REVENUECAT_API_KEY"))
    }


@router.get("/subscription/status")
async def get_subscription_status(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_database)
):
    """Récupère le statut de l'abonnement de l'utilisateur"""
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
