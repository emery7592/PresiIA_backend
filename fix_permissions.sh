#!/bin/bash

# Script de correction des permissions Docker
# À placer dans /opt/varain-backend/fix_permissions.sh

echo "🔧 Correction des permissions Docker..."

# Arrêter les conteneurs si ils tournent
echo "Arrêt des conteneurs..."
docker-compose down

# Correction des permissions sur l'hôte
echo "Correction des permissions du répertoire app..."
sudo chown -R $(id -u):$(id -g) ./app
sudo chmod -R 755 ./app

# Vérifier que les fichiers sont lisibles
echo "Vérification des permissions du fichier models.py..."
ls -la ./app/auth/models.py

# Nettoyer l'ancienne image
echo "Nettoyage de l'ancienne image..."
docker-compose build --no-cache app

# Redémarrer avec les bonnes permissions
echo "🚀 Redémarrage des conteneurs..."
docker-compose up -d

# Attendre que les services démarrent
echo "⏳ Attente du démarrage (30s)..."
sleep 30

# Vérifier le statut
echo "📊 Vérification du statut:"
docker-compose ps

echo "📋 Logs de l'application (dernières 20 lignes):"
docker-compose logs app --tail=20

# Test de connectivité
echo "🧪 Test des endpoints:"
echo "Test /api/health:"
curl -i http://localhost:7860/api/health
echo ""
echo "Test /api/payment/health:"
curl -i http://localhost:7860/api/payment/health

echo "✅ Script terminé!"