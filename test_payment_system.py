#!/usr/bin/env python3
"""
Script de test pour le système de paiement Stripe
"""

import sys
import os
import asyncio
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test que tous les imports fonctionnent"""
    print("🔍 Test des imports...")
    
    try:
        from app.database.database import get_database, create_tables
        print("✅ Import database OK")
        
        from app.auth.models import User, Subscription, Payment, PlatformEnum, SubscriptionStatusEnum, PaymentStatusEnum
        print("✅ Import models OK")
        
        from app.auth.schemas import UserRegister, PaymentIntentRequest, PaymentConfirmRequest
        print("✅ Import schemas OK")
        
        from app.auth.services import hash_password, create_access_token
        print("✅ Import auth services OK")
        
        from app.payment.services import StripeService, create_payment_intent_service
        print("✅ Import payment services OK")
        
        from app.payment.router import router as payment_router
        print("✅ Import payment router OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_database_connection():
    """Test la connexion à la base de données"""
    print("\n🔍 Test de la connexion à la base de données...")
    
    try:
        from app.database.database import check_database_connection
        
        if check_database_connection():
            print("✅ Connexion à la base de données OK")
            return True
        else:
            print("❌ Échec de la connexion à la base de données")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_stripe_configuration():
    """Test la configuration Stripe"""
    print("\n🔍 Test de la configuration Stripe...")
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    stripe_secret = os.getenv("STRIPE_SECRET_KEY")
    stripe_public = os.getenv("STRIPE_PUBLIC_KEY")
    stripe_webhook = os.getenv("STRIPE_WEBHOOK_SECRET")
    stripe_price = os.getenv("STRIPE_PRICE_ID")
    
    if stripe_secret:
        print("✅ STRIPE_SECRET_KEY configuré")
    else:
        print("⚠️  STRIPE_SECRET_KEY manquant")
    
    if stripe_public:
        print("✅ STRIPE_PUBLIC_KEY configuré")
    else:
        print("⚠️  STRIPE_PUBLIC_KEY manquant")
    
    if stripe_webhook:
        print("✅ STRIPE_WEBHOOK_SECRET configuré")
    else:
        print("⚠️  STRIPE_WEBHOOK_SECRET manquant")
    
    if stripe_price:
        print("✅ STRIPE_PRICE_ID configuré")
    else:
        print("⚠️  STRIPE_PRICE_ID manquant")
    
    return bool(stripe_secret and stripe_public)

def test_models():
    """Test la création des modèles"""
    print("\n🔍 Test des modèles...")
    
    try:
        from app.auth.models import User, Subscription, Payment, PlatformEnum, SubscriptionStatusEnum, PaymentStatusEnum
        
        # Test création d'un utilisateur
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            device_id="test_device_123",
            platform=PlatformEnum.ios,
            is_registered=True
        )
        print("✅ Création User OK")
        
        # Test création d'un abonnement
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id="sub_test_123",
            stripe_price_id="price_test_123",
            status=SubscriptionStatusEnum.active
        )
        print("✅ Création Subscription OK")
        
        # Test création d'un paiement
        payment = Payment(
            user_id=user.id,
            subscription_id=subscription.id,
            stripe_payment_intent_id="pi_test_123",
            amount=9.99,
            currency="eur",
            status=PaymentStatusEnum.completed
        )
        print("✅ Création Payment OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création modèles: {e}")
        return False

def test_schemas():
    """Test la validation des schémas"""
    print("\n🔍 Test des schémas Pydantic...")
    
    try:
        from app.auth.schemas import UserRegister, PaymentIntentRequest, PaymentConfirmRequest
        from app.auth.models import PlatformEnum
        
        # Test UserRegister
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "firstName": "Test",
            "lastName": "User",
            "device_id": "test_device_123",
            "platform": PlatformEnum.ios
        }
        user_register = UserRegister(**user_data)
        print("✅ Validation UserRegister OK")
        
        # Test PaymentIntentRequest
        payment_data = {
            "email": "test@example.com",
            "firstName": "Test",
            "lastName": "User",
            "device_id": "test_device_123",
            "platform": PlatformEnum.ios
        }
        payment_request = PaymentIntentRequest(**payment_data)
        print("✅ Validation PaymentIntentRequest OK")
        
        # Test PaymentConfirmRequest
        confirm_data = {
            "payment_intent_id": "pi_test_123",
            "email": "test@example.com",
            "password": "password123",
            "firstName": "Test",
            "lastName": "User",
            "device_id": "test_device_123",
            "platform": PlatformEnum.ios
        }
        confirm_request = PaymentConfirmRequest(**confirm_data)
        print("✅ Validation PaymentConfirmRequest OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur validation schémas: {e}")
        return False

def test_services():
    """Test les services"""
    print("\n🔍 Test des services...")
    
    try:
        from app.auth.services import hash_password, verify_password
        
        # Test hashage de mot de passe
        password = "test_password"
        hashed = hash_password(password)
        print("✅ Hashage mot de passe OK")
        
        # Test vérification de mot de passe
        if verify_password(password, hashed):
            print("✅ Vérification mot de passe OK")
        else:
            print("❌ Vérification mot de passe échouée")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur services: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Test du système de paiement Stripe")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Connexion base de données", test_database_connection),
        ("Configuration Stripe", test_stripe_configuration),
        ("Modèles", test_models),
        ("Schémas", test_schemas),
        ("Services", test_services)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur lors du test {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Résultats des tests:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Score: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! Le système est prêt.")
        return True
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
