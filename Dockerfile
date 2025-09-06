FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV PIP_NO_CACHE_DIR=1
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/transformers

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

# Copier et installer les dépendances Python EN TANT QUE ROOT
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application EN TANT QUE ROOT
COPY . .

# Créer l'utilisateur APRÈS avoir copié les fichiers
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Créer les répertoires nécessaires et DONNER TOUTES LES PERMISSIONS À LA FIN
RUN mkdir -p /app/logs /app/uploads /app/.cache/huggingface /app/.cache/transformers /home/appuser
RUN chown -R appuser:appuser /app /home/appuser
RUN chmod -R 755 /app

# Basculer vers l'utilisateur non-root SEULEMENT À LA FIN
USER appuser

# Exposer le port
EXPOSE 7860

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:7860/api/health || exit 1

# Commande de démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]