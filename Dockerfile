FROM python:3.13-slim

# Variables d'environnement optimisées
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV PIP_NO_CACHE_DIR=1
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/transformers
ENV TOKENIZERS_PARALLELISM=false
ENV OMP_NUM_THREADS=1

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    libblas3 \
    liblapack3 \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Créer l'utilisateur AVANT de copier les fichiers
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p /app/logs /app/uploads /app/.cache/huggingface /app/.cache/transformers /home/appuser

# CORRECTION: Donner les bonnes permissions
RUN chmod -R 777 /app/.cache
RUN chown -R appuser:appuser /app /home/appuser
RUN chmod -R 755 /app
RUN chmod +x /app # S'assurer que le répertoire est exécutable

# Basculer vers l'utilisateur non-root
USER appuser

# Exposer le port (garder 7860 comme dans votre original)
EXPOSE 7860

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:7860/api/health || exit 1

# Commande de démarrage avec un seul worker pour économiser la RAM
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]