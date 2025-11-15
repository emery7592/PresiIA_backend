# 🐍 Guide : Utilisation de l'environnement virtuel (venv)

## Qu'est-ce qu'un environnement virtuel ?

Un **environnement virtuel (venv)** est un espace isolé pour votre projet Python qui contient ses propres dépendances, indépendamment des autres projets. Cela évite les conflits entre versions de packages.

---

## ✅ Installation des dépendances dans le venv

### 1️⃣ Activer l'environnement virtuel

**Sur Linux/Mac :**
```bash
cd /home/user/PresiIA_backend
source venv/bin/activate
```

**Sur Windows :**
```bash
cd C:\Users\...\PresiIA_backend
venv\Scripts\activate
```

Vous verrez `(venv)` apparaître avant votre ligne de commande :
```bash
(venv) user@machine:~/PresiIA_backend$
```

---

### 2️⃣ Installer les dépendances

**Option 1 : Installation minimale (recommandé)**
```bash
pip install -r requirements-minimal.txt
```

Cette option installe **seulement les dépendances essentielles** pour RevenueCat :
- FastAPI, SQLAlchemy, PostgreSQL
- Authentication (JWT, passlib)
- httpx pour RevenueCat API
- **SANS** les librairies ML lourdes (torch, transformers, etc.)

**Option 2 : Installation complète**
```bash
pip install -r requirements.txt
```

⚠️ **Attention** : Cette option peut prendre beaucoup de temps et d'espace disque (plusieurs Go) car elle installe torch, transformers, etc.

---

### 3️⃣ Vérifier que tout fonctionne

```bash
python -c "from app.payment.revenuecat_service import revenuecat_service; print('✅ OK')"
```

---

## 🔧 Utilisation quotidienne

### ▶️ Démarrer le serveur FastAPI

```bash
# 1. Activer le venv
source venv/bin/activate

# 2. Lancer le serveur
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le serveur sera accessible sur : `http://localhost:8000`

---

### 🛑 Désactiver l'environnement virtuel

Quand vous avez fini de travailler :

```bash
deactivate
```

---

## 📝 Configuration du fichier .env

Le fichier `.env` contient vos variables d'environnement. **Important** :

1. **Ne jamais commit** le fichier `.env` (il est déjà dans .gitignore)
2. Modifier `.env` avec vos vraies valeurs :

```bash
# Ouvrir le fichier .env
nano .env
```

Remplacer ces valeurs :
```env
# RevenueCat - OBLIGATOIRE pour la migration
REVENUECAT_API_KEY=sk_xxxxxxxxxxxxxxxxxx  # ← À récupérer depuis RevenueCat Dashboard

# JWT - Générer une vraie clé secrète
SECRET_KEY=votre-vraie-cle-secrete-longue-et-aleatoire

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

---

## 🔑 Obtenir votre clé RevenueCat

1. Aller sur [RevenueCat Dashboard](https://app.revenuecat.com)
2. Sélectionner votre projet
3. **Settings** → **API Keys**
4. Copier la **Public App-Specific API Key** (commence par `sk_`)
5. Coller dans `.env` :
   ```env
   REVENUECAT_API_KEY=sk_votre_cle_ici
   ```

---

## 🚨 Dépannage

### Problème : "Module not found"

**Solution** : Vérifier que le venv est activé
```bash
which python
# Devrait afficher : /home/user/PresiIA_backend/venv/bin/python
```

Si ce n'est pas le cas :
```bash
source venv/bin/activate
```

---

### Problème : "SECRET_KEY manquante"

**Solution** : Créer le fichier `.env` avec les variables nécessaires (voir section Configuration ci-dessus)

---

### Problème : "REVENUECAT_API_KEY manquante"

**Solution** : Ajouter votre clé RevenueCat dans `.env`

---

## 📦 Structure du projet

```
PresiIA_backend/
├── venv/                        # ← Environnement virtuel (ne pas commit)
├── app/
│   ├── payment/
│   │   ├── revenuecat_service.py  # Service RevenueCat
│   │   ├── router.py              # Endpoints de paiement
│   │   └── schemas.py             # Schémas Pydantic
│   └── ...
├── .env                         # ← Variables d'environnement (ne pas commit)
├── .env.example                 # ← Template pour .env
├── requirements.txt             # ← Toutes les dépendances
├── requirements-minimal.txt     # ← Dépendances essentielles
└── GUIDE_VENV.md               # ← Ce fichier
```

---

## 🎯 Checklist de démarrage

- [ ] Activer le venv : `source venv/bin/activate`
- [ ] Installer les dépendances : `pip install -r requirements-minimal.txt`
- [ ] Créer le fichier `.env` avec les vraies valeurs
- [ ] Ajouter la clé RevenueCat dans `.env`
- [ ] Tester les imports : `python -c "from app.payment import router"`
- [ ] Lancer le serveur : `uvicorn app.main:app --reload`

---

## 💡 Conseil

Gardez **toujours le venv activé** quand vous travaillez sur ce projet. Cela garantit que vous utilisez les bonnes versions des dépendances.

---

**Besoin d'aide ?** Consultez la documentation FastAPI : https://fastapi.tiangolo.com/
