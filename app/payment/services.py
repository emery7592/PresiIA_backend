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
    
    @staticmethod
    def confirm_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirme un PaymentIntent Stripe
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if payment_intent.status == "succeeded":
                return {
                    "id": payment_intent.id,
                    "status": payment_intent.status,
                    "amount": payment_intent.amount,
                    "currency": payment_intent.currency,
                    "customer_id": payment_intent.customer
                }
            else:
                raise Exception(f"PaymentIntent non réussi. Statut: {payment_intent.status}")
                
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors de la confirmation du PaymentIntent: {e}")
            raise Exception(f"Erreur lors de la confirmation du PaymentIntent: {str(e)}")
    
    @staticmethod
    def create_subscription(customer_id: str, price_id: str = None) -> Dict[str, Any]:
        """
        Crée un abonnement Stripe
        """
        try:
            price_id = price_id or STRIPE_PRICE_ID
            
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
            )
            
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors de la création de l'abonnement: {e}")
            raise Exception(f"Erreur lors de la création de l'abonnement: {str(e)}")

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
        
        # Vérifier si l'email existe déjà
        existing_user = db.query(User).filter(User.email == payment_data["email"]).first()
        if existing_user:
            raise ValueError("Un utilisateur avec cet email existe déjà")
        
        # Créer l'utilisateur
        user = User(
            email=payment_data["email"],
            password_hash=hash_password(payment_data["password"]),
            first_name=payment_data["firstName"],
            last_name=payment_data["lastName"],
            device_id=payment_data["device_id"],
            platform=payment_data["platform"],
            stripe_customer_id=payment_intent["customer_id"],
            is_registered=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Créer l'abonnement Stripe
        subscription_data = StripeService.create_subscription(payment_intent["customer_id"])
        
        # Créer l'abonnement en base
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id=subscription_data["id"],
            stripe_price_id=STRIPE_PRICE_ID,
            status=SubscriptionStatusEnum.active,
            current_period_start=subscription_data["current_period_start"],
            current_period_end=subscription_data["current_period_end"],
            cancel_at_period_end=subscription_data["cancel_at_period_end"]
        )
        db.add(subscription)
        
        # Créer le paiement en base
        payment = Payment(
            user_id=user.id,
            subscription_id=subscription.id,
            stripe_payment_intent_id=payment_intent["id"],
            amount=9.99,
            currency="eur",
            status=PaymentStatusEnum.completed,
            meta_data=f'{{"email": "{payment_data["email"]}", "first_name": "{payment_data["firstName"]}", "last_name": "{payment_data["lastName"]}"}}'
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

def handle_stripe_webhook(payload: bytes, sig_header: str) -> Dict[str, Any]:
    """
    Gère les webhooks Stripe
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        
        # Gérer les différents types d'événements
        if event['type'] == 'payment_intent.succeeded':
            handle_payment_intent_succeeded(event['data']['object'])
        elif event['type'] == 'invoice.payment_succeeded':
            handle_invoice_payment_succeeded(event['data']['object'])
        elif event['type'] == 'customer.subscription.updated':
            handle_subscription_updated(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            handle_subscription_deleted(event['data']['object'])
        
        return {"status": "success", "event_type": event['type']}
        
    except ValueError as e:
        logger.error(f"Erreur lors du parsing du webhook: {e}")
        raise Exception("Erreur lors du parsing du webhook")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Erreur de signature du webhook: {e}")
        raise Exception("Erreur de signature du webhook")

def handle_payment_intent_succeeded(payment_intent: Dict[str, Any]):
    """Gère l'événement payment_intent.succeeded"""
    logger.info(f"PaymentIntent réussi: {payment_intent['id']}")

def handle_invoice_payment_succeeded(invoice: Dict[str, Any]):
    """Gère l'événement invoice.payment_succeeded"""
    logger.info(f"Facture payée: {invoice['id']}")

def handle_subscription_updated(subscription: Dict[str, Any]):
    """Gère l'événement customer.subscription.updated"""
    logger.info(f"Abonnement mis à jour: {subscription['id']}")

def handle_subscription_deleted(subscription: Dict[str, Any]):
    """Gère l'événement customer.subscription.deleted"""
    logger.info(f"Abonnement supprimé: {subscription['id']}")