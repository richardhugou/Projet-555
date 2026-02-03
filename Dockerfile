# 1. On part d'une image Python 3.13 légère
FROM python:3.13-slim

# 2. On installe 'uv'
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. On définit le dossier de travail, c'est ici que le code sera copié
WORKDIR /app

# 4. On copie les fichiers de config pour installer les libs EN PREMIER (mise en cache Docker)
COPY pyproject.toml uv.lock ./

# 5. On installe les dépendances (--no-dev car on est en prod)
# --frozen signifie "n'essaie pas de mettre à jour le lockfile"
RUN uv sync --frozen --no-dev

# 6. On copie tout le reste du code
COPY . .

# 7. La commande de démarrage
# Séquence : 1. Migration BDD (Création tables) -> 2. Création Admin -> 3. Lancement Serveur
CMD ["sh", "-c", "uv run python create_user.py && uv run uvicorn app.main:app --host 0.0.0.0 --port 7860"]
