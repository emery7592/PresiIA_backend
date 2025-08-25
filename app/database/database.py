from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de la base de données PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://redpill_ia_user:An2025resultat&@localhost:5432/redpill_ia_db"
)

# Créer l'engine SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Vérifier la connexion avant utilisation
    pool_recycle=300,    # Recycler les connexions après 5min
    pool_size=10,        # Taille du pool de connexions
    max_overflow=20      # Connexions supplémentaires si besoin
)

# SessionLocal pour créer des sessions de base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles SQLAlchemy
Base = declarative_base()

# Fonction pour obtenir une session de base de données
def get_database():
    """
    Générateur qui fournit une session de base de données
    et s'assure qu'elle est fermée après utilisation
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction pour créer toutes les tables
def create_tables():
    """
    Crée toutes les tables définies dans les modèles
    À utiliser uniquement en développement
    """
    Base.metadata.create_all(bind=engine)

# Fonction pour vérifier la connexion à la base
def check_database_connection():
    """
    Vérifie que la connexion à la base de données fonctionne
    """
    try:
        # Essayer de créer une connexion
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return False
    