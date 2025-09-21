import stripe
import os
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from app.database.database import get_database
from app.auth.models import User, Subscription, Payment, SubscriptionStatusEnum, PaymentStatusEnum
from app.auth.services import hash_password, create_access_token

# Charger les variables d'environnement
load_dotenv()

# Configuration Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "price_1OqXqXqXqXqXqXqXqXqXqXqX")

# Configuration du logging
logger = logging.getLogger(__name__)

class StripeService:
    @staticmethod
    def create_or_get_customer(email: str, first_name: str, last_name: str) -> str:
        try:
            customers = stripe.Customer.list(email=email, limit=1)
            
            if customers.data:
                customer = customers.data[0]
                if customer.name != f"{first_name} {last_name}":
                    stripe.Customer.modify(
                        customer.id,
                        name=f"{first_name} {last_name}"
                    )
                return customer.id
            else:
                customer = stripe.Customer.create(
                    email=email,
                    name=f"{first_name} {last_name}",
                    metadata={
                        "first_name": first_name,
                        "last_name": last_name
                    }
                )
                return customer.id
                
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors de la création/récupération du client: {e}")
            raise Exception(f"Erreur lors de la création du client Stripe: {str(e)}")
    
    @staticmethod
    def create_payment_intent(amount: int, currency: str = "eur", customer_id: str = None, 
                            metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            payment_intent_data = {
                "amount": amount,
                "currency": currency,
                "automatic_payment_methods": {
                    "enabled": True,
                },
                "metadata": metadata or {}
            }
            
            if customer_id:
                payment_intent_data["customer"] = customer_id
            
            payment_intent = stripe.PaymentIntent.create(**payment_intent_data)
            
            return {
                "id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "status": payment_intent.status
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors de la création du PaymentIntent: {e}")
            raise Exception(f"Erreur lors de la création du PaymentIntent: {str(e)}")

def create_payment_intent_service(db: Session, user_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        customer_id = StripeService.create_or_get_customer(
            email=user_data["email"],
            first_name=user_data["firstName"],
            last_name=user_data["lastName"]
        )
        
        payment_intent = StripeService.create_payment_intent(
            amount=999,
            currency="eur",
            customer_id=customer_id,
            metadata={
                "email": user_data["email"],
                "first_name": user_data["firstName"],
                "last_name": user_data["lastName"],
                "device_id": user_data["device_id"],
                "platform": user_data["platform"],
                "password": user_data.get("password", "")
            }
        )
        
        return {
            "client_secret": payment_intent["client_secret"],
            "payment_intent_id": payment_intent["id"],
            "customer_id": customer_id
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la création du PaymentIntent: {e}")
        raise e

def get_user_subscription(db: Session, user_id: str) -> Optional[Dict[str, Any]]:
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatusEnum.active
        ).first()
        
        if not subscription:
            return None
        
        return {
            "id": str(subscription.id),
            "status": subscription.status.value,
            "current_period_start": subscription.current_period_start.isoformat() if subscription.current_period_start else None,
            "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            "cancel_at_period_end": subscription.cancel_at_period_end
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'abonnement: {e}")
        raise e

def handle_stripe_webhook(payload: bytes, sig_header: str, db: Session) -> Dict[str, Any]:
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        
        logger.info(f"Événement webhook reçu: {event['type']}")
        
        if event['type'] == 'payment_intent.succeeded':
            handle_payment_intent_succeeded(event['data']['object'], db)
        elif event['type'] == 'invoice.payment_succeeded':
            handle_invoice_payment_succeeded(event['data']['object'], db)
        elif event['type'] == 'customer.subscription.updated':
            handle_subscription_updated(event['data']['object'], db)
        elif event['type'] == 'customer.subscription.deleted':
            handle_subscription_deleted(event['data']['object'], db)
        
        return {"status": "success", "event_type": event['type']}
        
    except ValueError as e:
        logger.error(f"Erreur lors du parsing du webhook: {e}")
        raise Exception("Erreur lors du parsing du webhook")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Erreur de signature du webhook: {e}")
        raise Exception("Erreur de signature du webhook")

def handle_payment_intent_succeeded(payment_intent: Dict[str, Any], db: Session):
    try:
        payment_intent_id = payment_intent['id']
        metadata = payment_intent.get('metadata', {})
        
        logger.info(f"Traitement PaymentIntent réussi: {payment_intent_id}")
        logger.info(f"Metadata reçues: {metadata}")
        
        existing_payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent_id
        ).first()
        
        if existing_payment:
            logger.info(f"Paiement {payment_intent_id} déjà traité")
            return
        
        email = metadata.get('email')
        first_name = metadata.get('first_name')
        last_name = metadata.get('last_name')
        device_id = metadata.get('device_id')
        platform = metadata.get('platform')
        password = metadata.get('password')
        
        if not all([email, first_name, last_name, device_id, platform]):
            logger.error(f"Metadata incomplètes pour PaymentIntent {payment_intent_id}: {metadata}")
            return
            
        if not password:
            logger.error(f"Mot de passe manquant dans metadata pour PaymentIntent {payment_intent_id}")
            return
        
        existing_user = db.query(User).filter(
            User.email == email,
            User.is_registered == True
        ).first()
        
        if existing_user:
            logger.warning(f"Utilisateur avec email {email} déjà inscrit")
            return
        
        user = db.query(User).filter(User.device_id == device_id).first()
        
        if user:
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.stripe_customer_id = payment_intent.get('customer')
            user.is_registered = True
            user.password_hash = hash_password(password)
        else:
            from app.auth.models import PlatformEnum
            platform_enum = PlatformEnum(platform) if isinstance(platform, str) else platform
            
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                device_id=device_id,
                platform=platform_enum,
                stripe_customer_id=payment_intent.get('customer'),
                is_registered=True,
                password_hash=hash_password(password)
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)
        
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id=None,
            stripe_price_id=STRIPE_PRICE_ID,
            status=SubscriptionStatusEnum.active,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30),
            cancel_at_period_end=False
        )
        db.add(subscription)
        
        payment = Payment(
            user_id=user.id,
            subscription_id=subscription.id,
            stripe_payment_intent_id=payment_intent_id,
            amount=payment_intent['amount'] / 100,
            currency=payment_intent['currency'],
            status=PaymentStatusEnum.completed,
            meta_data=f'{{"email": "{email}", "first_name": "{first_name}", "last_name": "{last_name}"}}'
        )
        db.add(payment)
        
        db.commit()
        
        logger.info(f"Utilisateur créé avec succès pour PaymentIntent {payment_intent_id}: {user.email}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors du traitement de payment_intent.succeeded: {e}")
        raise e

def handle_invoice_payment_succeeded(invoice: Dict[str, Any], db: Session):
    logger.info(f"Facture payée: {invoice['id']}")

def handle_subscription_updated(subscription: Dict[str, Any], db: Session):
    logger.info(f"Abonnement mis à jour: {subscription['id']}")

def handle_subscription_deleted(subscription: Dict[str, Any], db: Session):
    logger.info(f"Abonnement supprimé: {subscription['id']}")