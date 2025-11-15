import os
import httpx
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RevenueCatService:
    """Service pour vérifier les achats via RevenueCat REST API"""

    BASE_URL = "https://api.revenuecat.com/v1"

    def __init__(self):
        self.api_key = os.getenv("REVENUECAT_API_KEY")
        if not self.api_key:
            raise ValueError("REVENUECAT_API_KEY manquante dans .env")

    async def verify_purchase(self, app_user_id: str) -> Optional[Dict[str, Any]]:
        """
        Vérifie l'abonnement d'un utilisateur via RevenueCat

        Args:
            app_user_id: L'identifiant unique de l'utilisateur (peut être email ou device_id)

        Returns:
            Dict contenant les infos d'abonnement ou None si pas d'abonnement actif
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            url = f"{self.BASE_URL}/subscribers/{app_user_id}"

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)

                if response.status_code != 200:
                    logger.error(f"Erreur RevenueCat API: {response.status_code} - {response.text}")
                    return None

                data = response.json()
                subscriber = data.get("subscriber", {})

                # Vérifier si l'utilisateur a un entitlement actif
                entitlements = subscriber.get("entitlements", {})
                premium = entitlements.get("premium", {})  # "premium" = identifier de ton entitlement

                if not premium or premium.get("expires_date") is None:
                    logger.info(f"Pas d'abonnement actif pour {app_user_id}")
                    return None

                # Vérifier si l'abonnement est toujours valide
                expires_date = datetime.fromisoformat(premium["expires_date"].replace("Z", "+00:00"))
                if expires_date < datetime.now(expires_date.tzinfo):
                    logger.info(f"Abonnement expiré pour {app_user_id}")
                    return None

                # Récupérer les détails du purchase
                subscriptions = subscriber.get("subscriptions", {})

                return {
                    "is_active": True,
                    "expires_date": expires_date,
                    "product_id": premium.get("product_identifier"),
                    "store": subscriber.get("management_url"),  # "play_store" ou "app_store"
                    "original_purchase_date": premium.get("original_purchase_date"),
                    "subscriptions": subscriptions
                }

        except Exception as e:
            logger.error(f"Erreur lors de la vérification RevenueCat: {e}")
            return None

revenuecat_service = RevenueCatService()
