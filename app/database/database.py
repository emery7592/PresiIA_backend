from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de la base de données PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://redpill_ia_user:An2025resultat&@postgres:5432/redpill_ia_db"
)

# Créer l'engine SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Vérifier la connexion avant utilisation
    pool_recycle=300,    # Recycler les connexions après 5min
    pool_size=10,        # Taille du pool de connexions
    max_overflow=20,     # Connexions supplémentaires si besoin
    echo=False           # Mettre True pour voir les requêtes SQL en debug
)

# SessionLocal pour créer des sessions de base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles SQLAlchemy
Base = declarative_base()

# Fonction pour obtenir une session de base de données (pour FastAPI)
def get_db():
    """
    Générateur qui fournit une session de base de données
    et s'assure qu'elle est fermée après utilisation
    À utiliser comme dépendance FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction legacy (pour compatibilité avec votre code existant)
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
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables créées avec succès")
        return True
    except Exception as e:
        print(f"Erreur lors de la création des tables : {e}")
        return False

# Fonction pour vérifier la connexion à la base
def check_database_connection():
    """
    Vérifie que la connexion à la base de données fonctionne
    """
    try:
        # Essayer de créer une connexion
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("Connexion à la base de données réussie")
                return True
            else:
                print("Connexion établie mais réponse inattendue")
                return False
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return False

# Fonction pour obtenir des informations sur la base
def get_database_info():
    """
    Récupère des informations sur la base de données
    """
    try:
        with engine.connect() as connection:
            # Version de PostgreSQL
            version_result = connection.execute(text("SELECT version()"))
            version = version_result.fetchone()[0]
            
            # Nom de la base de données actuelle
            db_name_result = connection.execute(text("SELECT current_database()"))
            db_name = db_name_result.fetchone()[0]
            
            # Utilisateur actuel
            user_result = connection.execute(text("SELECT current_user"))
            user = user_result.fetchone()[0]
            
            return {
                "version": version,
                "database": db_name,
                "user": user,
                "status": "connected"
            }
    except Exception as e:
        return {
            "error": str(e),
            "status": "disconnected"
        }

# Test automatique de la connexion au démarrage du module
if __name__ == "__main__":
    print("Test de connexion à la base de données...")
    if check_database_connection():
        info = get_database_info()
        print(f"Base de données : {info.get('database')}")
        print(f"Utilisateur : {info.get('user')}")
    else:
        print("Échec de la connexion à la base de données")