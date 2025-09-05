#!/usr/bin/env python3
"""
Script pour créer toutes les tables de base de données
"""

import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import create_tables, check_database_connection
from app.auth.models import Base
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def main():
    """Fonction principale pour créer les tables"""
    print("🔍 Vérification de la connexion à la base de données...")
    
    if not check_database_connection():
        print("❌ Impossible de se connecter à la base de données")
        return False
    
    print("✅ Connexion à la base de données réussie")
    print("🔨 Création des tables...")
    
    if create_tables():
        print("✅ Tables créées avec succès")
        print("\n📋 Tables créées :")
        print("  - users")
        print("  - subscriptions") 
        print("  - payments")
        return True
    else:
        print("❌ Erreur lors de la création des tables")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
