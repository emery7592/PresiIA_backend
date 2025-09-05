# Système de Paiement Stripe - Backend FastAPI

## Vue d'ensemble

Ce système permet de gérer les paiements Stripe pour un chatbot avec un modèle freemium :
- 2 questions gratuites pour les utilisateurs anonymes
- Abonnement de 9.99€/mois pour un accès illimité

## Structure du projet

```
app/
├── auth/
│   ├── model.py          # Modèles User, Subscription, Payment
│   ├── services.py       # Services d'authentification
│   ├── router.py         # Routes d'authentification
│   └── dependencies.py   # Schémas Pydantic et dépendances
├── payment/
│   ├── services.py       # Services Stripe
│   └── router.py         # Routes de paiement
├── database/
│   └── database.py       # Configuration base de données
└── main.py               # Application FastAPI principale
```

## Configuration requise

### Variables d'environnement (.env)

```env
# Base de données
DATABASE_URL=postgresql://user:password@host:port/database

# JWT
SECRET_KEY=your-secret-key

# Stripe
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...
```

### Dépendances Python

```bash
pip install stripe fastapi sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart
```

## API Endpoints

### 1. Créer un PaymentIntent
```http
POST /api/payment/create-intent
Content-Type: application/json

{
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "device_id": "device123",
  "platform": "ios"
}
```

**Réponse :**
```json
{
  "client_secret": "pi_xxx_secret_xxx",
  "payment_intent_id": "pi_xxx"
}
```

### 2. Confirmer le paiement
```http
POST /api/payment/confirm
Content-Type: application/json

{
  "payment_intent_id": "pi_xxx",
  "email": "user@example.com",
  "password": "password123",
  "firstName": "John",
  "lastName": "Doe",
  "device_id": "device123",
  "platform": "ios"
}
```

**Réponse :**
```json
{
  "message": "Paiement confirmé et compte créé avec succès",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": "uuid",
  "subscription_id": "uuid"
}
```

### 3. Récupérer l'abonnement
```http
GET /api/payment/subscription
Authorization: Bearer <token>
```

**Réponse :**
```json
{
  "id": "uuid",
  "status": "active",
  "current_period_start": "2024-01-01T00:00:00",
  "current_period_end": "2024-02-01T00:00:00",
  "cancel_at_period_end": false
}
```

### 4. Webhook Stripe
```http
POST /api/payment/webhook
Stripe-Signature: t=xxx,v1=xxx
```

## Modèles de données

### User
```python
class User(Base):
    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    device_id = Column(String, unique=True)
    free_questions_used = Column(Integer, default=0)
    platform = Column(Enum(PlatformEnum))
    is_registered = Column(Boolean, default=False)
    stripe_customer_id = Column(String)  # Nouveau
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

### Subscription
```python
class Subscription(Base):
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    stripe_subscription_id = Column(String, unique=True)
    stripe_price_id = Column(String)
    status = Column(Enum(SubscriptionStatusEnum))
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

### Payment
```python
class Payment(Base):
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    subscription_id = Column(UUID, ForeignKey("subscriptions.id"))
    stripe_payment_intent_id = Column(String, unique=True)
    stripe_invoice_id = Column(String)
    amount = Column(Numeric(10, 2))
    currency = Column(String, default="eur")
    status = Column(Enum(PaymentStatusEnum))
    payment_method_id = Column(String)
    failure_reason = Column(String)
    metadata = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

## Flow de paiement

1. **Frontend** → `POST /api/payment/create-intent`
   - Envoie les données utilisateur
   - Reçoit le `client_secret` Stripe

2. **Frontend** → Stripe Elements
   - Utilise le `client_secret` pour afficher le formulaire de paiement
   - L'utilisateur saisit ses informations de carte

3. **Frontend** → `POST /api/payment/confirm`
   - Envoie le `payment_intent_id` et les données utilisateur
   - Le backend valide le paiement avec Stripe
   - Crée l'utilisateur et l'abonnement en base
   - Retourne le token d'authentification

4. **Utilisateur connecté** → Accès illimité au chatbot

## Webhooks Stripe

Le système gère automatiquement les événements Stripe :
- `payment_intent.succeeded` : Paiement réussi
- `invoice.payment_succeeded` : Facture payée
- `customer.subscription.updated` : Abonnement mis à jour
- `customer.subscription.deleted` : Abonnement supprimé

## Sécurité

- Validation des signatures Stripe pour les webhooks
- Hachage des mots de passe avec bcrypt
- Tokens JWT pour l'authentification
- Validation des données avec Pydantic
- Gestion des erreurs robuste

## Déploiement

1. **Créer les tables :**
```bash
python app/create_tables.py
```

2. **Configurer Stripe :**
   - Créer un compte Stripe
   - Créer un produit et un prix récurrent
   - Configurer les webhooks
   - Mettre à jour les variables d'environnement

3. **Lancer l'application :**
```bash
python app/main.py
```

## Tests

Pour tester le système :

1. **Mode test Stripe :**
   - Utilisez les cartes de test Stripe
   - Carte réussie : `4242424242424242`
   - Carte échouée : `4000000000000002`

2. **Webhooks locaux :**
   - Utilisez Stripe CLI pour rediriger les webhooks vers localhost
   ```bash
   stripe listen --forward-to localhost:7860/api/payment/webhook
   ```

## Support

Pour toute question ou problème, consultez :
- [Documentation Stripe](https://stripe.com/docs)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation SQLAlchemy](https://docs.sqlalchemy.org/)
