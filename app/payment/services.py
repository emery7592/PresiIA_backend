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
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "price_1OqXqXqXqXqXqXqXqXqXqXqX")  # Votre price ID Stripe

# Configuration du logging
logger = logging.getLogger(__name__)

class StripeService:
    """Service pour gérer les interactions avec Stripe"""
    
    @staticmethod
    def create_or_get_customer(email: str, first_name: str, last_name: str) -> str:
        """
        Crée ou récupère un client Stripe
        """
        try:
            # Vérifier si le client existe déjà
            customers = stripe.Customer.list(email=email, limit=1)
            
            if customers.data:
                customer = customers.data[0]
                # Mettre à jour les informations si nécessaire
                if customer.name != f"{first_name} {last_name}":
                    stripe.Customer.modify(
                        customer.id,
                        name=f"{first_name} {last_name}"
                    )
                return customer.id
            else:
                # Créer un nouveau client
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
        """
        Crée un PaymentIntent Stripe
        """
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
    """
    Service principal pour créer un PaymentIntent
    """
    try:
        # Créer ou récupérer le client Stripe
        customer_id = StripeService.create_or_get_customer(
            email=user_data["email"],
            first_name=user_data["firstName"],
            last_name=user_data["lastName"]
        )
        
        # Créer le PaymentIntent (999 = 9.99€ en centimes)
        payment_intent = StripeService.create_payment_intent(
            amount=999,
            currency="eur",
            customer_id=customer_id,
            metadata={
                "email": user_data["email"],
                "first_name": user_data["firstName"],
                "last_name": user_data["lastName"],
                "device_id": user_data["device_id"],
                "platform": user_data["platform"]
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

def validate_and_create_user(db: Session, payment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valide le paiement et crée l'utilisateur avec son abonnement
    """
    try:
        # Confirmer le PaymentIntent
        payment_intent = StripeService.confirm_payment_intent(payment_data["payment_intent_id"])
        
        # Vérifier si l'email existe déjà sur un utilisateur INSCRIT
        existing_user = db.query(User).filter(
            User.email == payment_data["email"]
        ).filter(
            User.is_registered == True
        ).first()
        
        if existing_user:
            raise ValueError("Un utilisateur avec cet email est déjà inscrit")
        
        # Essayer de récupérer l'utilisateur par device_id
        user = db.query(User).filter(User.device_id == payment_data["device_id"]).first()
        
        if user:
            # MISE À JOUR de l'utilisateur existant
            user.email = payment_data["email"]
            user.password_hash = hash_password(payment_data["password"])
            user.first_name = payment_data["firstName"]
            user.last_name = payment_data["lastName"]
            user.stripe_customer_id = payment_intent["customer_id"]
            user.is_registered = True
        else:
            # CRÉATION d'un nouvel utilisateur
            from app.auth.models import PlatformEnum
            platform_value = payment_data["platform"]
            if isinstance(platform_value, str):
                platform_value = PlatformEnum(platform_value)
            
            user = User(
                email=payment_data["email"],
                password_hash=hash_password(payment_data["password"]),
                first_name=payment_data["firstName"],
                last_name=payment_data["lastName"],
                device_id=payment_data["device_id"],
                platform=platform_value,
                stripe_customer_id=payment_intent["customer_id"],
                is_registered=True
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)
        
        # Créer l'abonnement en base
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
        
        # Enregistrer le paiement
        payment = Payment(
            user_id=user.id,
            subscription_id=subscription.id,
            stripe_payment_intent_id=payment_intent["id"],
            amount=9.99,
            currency="eur",
            status=PaymentStatusEnum.completed,
            meta_data='{"processed": true}'
        )
        db.add(payment)
        
        db.commit()
        
        # Créer le token d'accès
        token = create_access_token({"sub": str(user.id)})
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": str(user.id),
            "subscription_id": str(subscription.id),
            "payment_intent_id": payment_intent["id"]
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la validation et création de l'utilisateur: {e}")
        raise e

def get_user_subscription(db: Session, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère l'abonnement actif d'un utilisateur
    """
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
    """
    Gère les webhooks Stripe
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        
        logger.info(f"Événement webhook reçu: {event['type']}")
        
        # Gérer les différents types d'événements
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
    """
    Gère l'événement payment_intent.succeeded - CRÉE LE COMPTE UTILISATEUR
    """
    try:
        payment_intent_id = payment_intent['id']
        metadata = payment_intent.get('metadata', {})
        
        logger.info(f"Traitement PaymentIntent réussi: {payment_intent_id}")
        logger.info(f"Metadata reçues: {metadata}")
        
        # Vérifier si le paiement existe déjà en base
        existing_payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent_id
        ).first()
        
        if existing_payment:
            logger.info(f"Paiement {payment_intent_id} déjà traité")
            return
        
        # Extraire les données des metadata
        email = metadata.get('email')
        first_name = metadata.get('first_name')
        last_name = metadata.get('last_name')
        device_id = metadata.get('device_id')
        platform = metadata.get('platform')
        
        if not all([email, first_name, last_name, device_id, platform]):
            logger.error(f"Metadata incomplètes pour PaymentIntent {payment_intent_id}: {metadata}")
            return
        
        # Vérifier si l'utilisateur existe déjà avec cet email et est inscrit
        existing_user = db.query(User).filter(
            User.email == email,
            User.is_registered == True
        ).first()
        
        if existing_user:
            logger.warning(f"Utilisateur avec email {email} déjà inscrit")
            return
        
        # Récupérer ou créer l'utilisateur par device_id
        user = db.query(User).filter(User.device_id == device_id).first()
        
        if user:
            # Mettre à jour l'utilisateur existant
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.stripe_customer_id = payment_intent.get('customer')
            user.is_registered = True
        else:
            # Créer un nouvel utilisateur
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
                password_hash=None  # Sera défini lors du premier login
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)
        
        # Créer l'abonnement (1 mois)
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
        
        # Enregistrer le paiement
        payment = Payment(
            user_id=user.id,
            subscription_id=subscription.id,
            stripe_payment_intent_id=payment_intent_id,
            amount=payment_intent['amount'] / 100,  # Convertir centimes en euros
            currency=payment_intent['currency'],
            status=PaymentStatusEnum.completed,
            metadata=f'{{"email": "{email}", "first_name": "{first_name}", "last_name": "{last_name}"}}'
        )
        db.add(payment)
        
        db.commit()
        
        logger.info(f"Utilisateur créé avec succès pour PaymentIntent {payment_intent_id}: {user.email}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors du traitement de payment_intent.succeeded: {e}")
        raise e

def handle_invoice_payment_succeeded(invoice: Dict[str, Any], db: Session):
    """Gère l'événement invoice.payment_succeeded"""
    logger.info(f"Facture payée: {invoice['id']}")

def handle_subscription_updated(subscription: Dict[str, Any], db: Session):
    """Gère l'événement customer.subscription.updated"""
    logger.info(f"Abonnement mis à jour: {subscription['id']}")

def handle_subscription_deleted(subscription: Dict[str, Any], db: Session):
    """Gère l'événement customer.subscription.deleted"""
    logger.info(f"Abonnement supprimé: {subscription['id']}")