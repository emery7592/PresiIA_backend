import requests
import jwt
import time
import os
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from google.auth.transport import requests as google_requests
from google.oauth2 import service_account

from app.auth.models import User, Subscription, Payment, SubscriptionStatusEnum, PaymentStatusEnum

logger = logging.getLogger(__name__)

# Configuration
APPLE_BUNDLE_ID = os.getenv("APPLE_BUNDLE_ID", "app.redpill-ia")
GOOGLE_PACKAGE_NAME = os.getenv("GOOGLE_PACKAGE_NAME", "app.redpill-ia")
APPLE_SHARED_SECRET = os.getenv("APPLE_SHARED_SECRET")

# Product IDs
MONTHLY_PRODUCT_IOS = "app.redpill_ia.monthly"
MONTHLY_PRODUCT_ANDROID = "monthly_subscription"

class AppleIAPService:
    PRODUCTION_URL = "https://buy.itunes.apple.com/verifyReceipt"
    SANDBOX_URL = "https://sandbox.itunes.apple.com/verifyReceipt"
    
    @staticmethod
    def verify_receipt(receipt_data: str, use_sandbox: bool = False) -> Dict[str, Any]:
        url = AppleIAPService.SANDBOX_URL if use_sandbox else AppleIAPService.PRODUCTION_URL
        
        payload = {
            "receipt-data": receipt_data,
            "password": APPLE_SHARED_SECRET,
            "exclude-old-transactions": True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            
            # Si erreur 21007 (sandbox receipt en prod), retry en sandbox
            if result.get("status") == 21007 and not use_sandbox:
                return AppleIAPService.verify_receipt(receipt_data, use_sandbox=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur vérification Apple receipt: {e}")
            raise Exception(f"Erreur vérification Apple: {str(e)}")
    
    @staticmethod
    def parse_receipt(receipt_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if receipt_response.get("status") != 0:
            logger.error(f"Apple receipt invalide: {receipt_response.get('status')}")
            return None
        
        latest_receipt_info = receipt_response.get("latest_receipt_info", [])
        if not latest_receipt_info:
            return None
        
        # Prendre la dernière transaction
        latest = latest_receipt_info[-1]
        
        expires_date_ms = int(latest.get("expires_date_ms", 0))
        purchase_date_ms = int(latest.get("purchase_date_ms", 0))
        
        return {
            "transaction_id": latest.get("transaction_id"),
            "original_transaction_id": latest.get("original_transaction_id"),
            "product_id": latest.get("product_id"),
            "purchase_date": datetime.fromtimestamp(purchase_date_ms / 1000),
            "expires_date": datetime.fromtimestamp(expires_date_ms / 1000),
            "is_trial": latest.get("is_trial_period") == "true",
            "cancellation_date": latest.get("cancellation_date_ms")
        }


class GoogleIAPService:
    @staticmethod
    def get_credentials():
        credentials_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not credentials_path or not os.path.exists(credentials_path):
            raise Exception("Google Service Account JSON non trouvé")
        
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/androidpublisher']
        )
        return credentials
    
    @staticmethod
    def verify_purchase(purchase_token: str, product_id: str) -> Dict[str, Any]:
        try:
            credentials = GoogleIAPService.get_credentials()
            credentials.refresh(google_requests.Request())
            
            url = (
                f"https://androidpublisher.googleapis.com/androidpublisher/v3/"
                f"applications/{GOOGLE_PACKAGE_NAME}/purchases/subscriptions/"
                f"{product_id}/tokens/{purchase_token}"
            )
            
            headers = {
                "Authorization": f"Bearer {credentials.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Erreur Google API: {response.text}")
                raise Exception(f"Erreur vérification Google: {response.status_code}")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Erreur vérification Google purchase: {e}")
            raise e
    
    @staticmethod
    def parse_purchase(purchase_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            start_time_ms = int(purchase_data.get("startTimeMillis", 0))
            expiry_time_ms = int(purchase_data.get("expiryTimeMillis", 0))
            
            return {
                "order_id": purchase_data.get("orderId"),
                "purchase_token": purchase_data.get("purchaseToken"),
                "purchase_state": purchase_data.get("purchaseState"),
                "start_date": datetime.fromtimestamp(start_time_ms / 1000),
                "expires_date": datetime.fromtimestamp(expiry_time_ms / 1000),
                "auto_renewing": purchase_data.get("autoRenewing", False),
                "payment_state": purchase_data.get("paymentState")
            }
        except Exception as e:
            logger.error(f"Erreur parsing Google purchase: {e}")
            return None


def create_or_update_subscription_from_apple(
    db: Session,
    user: User,
    receipt_data: str
) -> Subscription:
    # Vérifier le receipt
    receipt_response = AppleIAPService.verify_receipt(receipt_data)
    parsed = AppleIAPService.parse_receipt(receipt_response)
    
    if not parsed:
        raise Exception("Receipt Apple invalide")
    
    # Vérifier si abonnement existe déjà
    existing = db.query(Subscription).filter(
        Subscription.apple_original_transaction_id == parsed["original_transaction_id"]
    ).first()
    
    if existing:
        # Mettre à jour
        existing.current_period_end = parsed["expires_date"]
        existing.status = SubscriptionStatusEnum.active
        db.commit()
        db.refresh(existing)
        return existing
    
    # Créer nouveau
    subscription = Subscription(
        user_id=user.id,
        apple_transaction_id=parsed["transaction_id"],
        apple_original_transaction_id=parsed["original_transaction_id"],
        apple_product_id=parsed["product_id"],
        platform_source="apple",
        status=SubscriptionStatusEnum.active,
        current_period_start=parsed["purchase_date"],
        current_period_end=parsed["expires_date"]
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    return subscription


def create_or_update_subscription_from_google(
    db: Session,
    user: User,
    purchase_token: str,
    product_id: str
) -> Subscription:
    # Vérifier le purchase
    purchase_data = GoogleIAPService.verify_purchase(purchase_token, product_id)
    parsed = GoogleIAPService.parse_purchase(purchase_data)
    
    if not parsed or parsed["purchase_state"] != 0:
        raise Exception("Purchase Google invalide")
    
    # Vérifier si abonnement existe déjà
    existing = db.query(Subscription).filter(
        Subscription.google_purchase_token == purchase_token
    ).first()
    
    if existing:
        # Mettre à jour
        existing.current_period_end = parsed["expires_date"]
        existing.status = SubscriptionStatusEnum.active
        db.commit()
        db.refresh(existing)
        return existing
    
    # Créer nouveau
    subscription = Subscription(
        user_id=user.id,
        google_purchase_token=purchase_token,
        google_order_id=parsed["order_id"],
        google_product_id=product_id,
        platform_source="google",
        status=SubscriptionStatusEnum.active,
        current_period_start=parsed["start_date"],
        current_period_end=parsed["expires_date"]
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    return subscription