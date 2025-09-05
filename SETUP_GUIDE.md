# Guide de Configuration - Système de Paiement Stripe

## 🚀 Installation et Configuration

### 1. Prérequis

- Python 3.8+
- PostgreSQL
- Compte Stripe (test ou production)

### 2. Installation des dépendances

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration de l'environnement

1. **Copier le fichier d'exemple :**
```bash
cp env.example .env
```

2. **Configurer les variables dans `.env` :**

```env
# Base de données
DATABASE_URL=postgresql://user:password@host:port/database

# JWT (générer une clé secrète)
SECRET_KEY=your-super-secret-key-here

# Stripe (récupérer depuis le dashboard Stripe)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...
```

### 4. Configuration Stripe

#### A. Créer un compte Stripe
1. Aller sur [stripe.com](https://stripe.com)
2. Créer un compte
3. Passer en mode test

#### B. Créer un produit et un prix
1. Dashboard Stripe → Produits
2. Créer un nouveau produit : "Accès Premium Chatbot"
3. Ajouter un prix récurrent : 9.99€/mois
4. Copier le `price_id` (commence par `price_`)

#### C. Configurer les webhooks
1. Dashboard Stripe → Développeurs → Webhooks
2. Ajouter un endpoint : `https://votre-domaine.com/api/payment/webhook`
3. Sélectionner les événements :
   - `payment_intent.succeeded`
   - `invoice.payment_succeeded`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copier le `webhook_secret` (commence par `whsec_`)

### 5. Création des tables

```bash
# Créer toutes les tables
python3 app/create_tables.py
```

### 6. Test du système

```bash
# Lancer les tests
python3 test_payment_system.py
```

### 7. Démarrage de l'application

```bash
# Lancer l'application
python3 app/main.py
```

L'application sera disponible sur :
- API : http://localhost:7860
- Documentation : http://localhost:7860/docs
- Interface Gradio : http://localhost:7860/gradio

## 🔧 Utilisation

### Flow de paiement complet

1. **Frontend envoie les données d'inscription :**
```javascript
const response = await fetch('/api/payment/create-intent', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    firstName: 'John',
    lastName: 'Doe',
    device_id: 'device123',
    platform: 'ios'
  })
});

const { client_secret, payment_intent_id } = await response.json();
```

2. **Frontend utilise Stripe Elements :**
```javascript
const { error } = await stripe.confirmCardPayment(client_secret, {
  payment_method: {
    card: cardElement,
    billing_details: {
      name: 'John Doe',
      email: 'user@example.com'
    }
  }
});

if (error) {
  console.error('Erreur de paiement:', error);
} else {
  // Paiement réussi, confirmer avec le backend
  await confirmPayment(payment_intent_id);
}
```

3. **Frontend confirme le paiement :**
```javascript
const confirmResponse = await fetch('/api/payment/confirm', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    payment_intent_id: payment_intent_id,
    email: 'user@example.com',
    password: 'password123',
    firstName: 'John',
    lastName: 'Doe',
    device_id: 'device123',
    platform: 'ios'
  })
});

const { access_token, user_id } = await confirmResponse.json();
// Utilisateur créé et connecté !
```

### API Endpoints

#### POST /api/payment/create-intent
Crée un PaymentIntent Stripe pour l'inscription.

**Body :**
```json
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

#### POST /api/payment/confirm
Confirme le paiement et crée l'utilisateur.

**Body :**
```json
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

#### GET /api/payment/subscription
Récupère l'abonnement de l'utilisateur connecté.

**Headers :**
```
Authorization: Bearer <access_token>
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

## 🧪 Tests

### Cartes de test Stripe

- **Carte réussie :** `4242424242424242`
- **Carte échouée :** `4000000000000002`
- **Carte nécessitant authentification :** `4000002500003155`

### Test des webhooks en local

```bash
# Installer Stripe CLI
brew install stripe/stripe-cli/stripe

# Se connecter
stripe login

# Écouter les webhooks
stripe listen --forward-to localhost:7860/api/payment/webhook
```

## 🔒 Sécurité

### Variables d'environnement sensibles

- `STRIPE_SECRET_KEY` : Ne jamais exposer publiquement
- `STRIPE_WEBHOOK_SECRET` : Garder secret
- `SECRET_KEY` : Utiliser une clé forte et unique

### Validation des webhooks

Le système valide automatiquement les signatures Stripe pour s'assurer que les webhooks proviennent bien de Stripe.

### Hachage des mots de passe

Les mots de passe sont hachés avec bcrypt avant d'être stockés en base de données.

## 🐛 Dépannage

### Erreurs courantes

1. **"STRIPE_SECRET_KEY manquant"**
   - Vérifier que le fichier `.env` existe
   - Vérifier que la variable est correctement définie

2. **"Connexion à la base de données échouée"**
   - Vérifier l'URL de connexion PostgreSQL
   - Vérifier que la base de données est accessible

3. **"Signature webhook invalide"**
   - Vérifier le `STRIPE_WEBHOOK_SECRET`
   - Vérifier que l'URL du webhook est correcte

4. **"Price ID invalide"**
   - Vérifier le `STRIPE_PRICE_ID` dans le dashboard Stripe
   - S'assurer que le prix est récurrent

### Logs

Les logs sont disponibles dans la console. Pour plus de détails :

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

Pour toute question ou problème :

1. Vérifier les logs de l'application
2. Tester avec le script `test_payment_system.py`
3. Consulter la documentation Stripe
4. Vérifier la configuration dans le dashboard Stripe
