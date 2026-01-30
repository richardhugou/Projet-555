# Projet 5 : Scoring de Crédit et Prédiction de Churn

| Branche | Statut CI |
| :--- | :--- |
| **Main** | ![CI - Main](https://github.com/richardhugou/Projet-555/actions/workflows/_01_integration.yaml/badge.svg?branch=main) |
| **Develop** | ![CI - Develop](https://github.com/richardhugou/Projet-555/actions/workflows/_01_integration.yaml/badge.svg?branch=develop) |

Ce dépôt contient le pipeline complet **MLOps** pour un modèle de machine learning : de l'entraînement à la mise en production via une API sécurisée. Le modèle prédit le risque de départ d'un employé ("churn") en fonction de données socio-professionnelles.

## Fonctionnalités Clés
*   **API REST** : Développée avec **FastAPI**, rapide, typée et auto-documentée.
*   **Sécurité** : Authentification via **Bcrypt** (hachage) et stockage en base de données PostgreSQL.
*   **Persistance** : Historisation des prédictions et des probabilités via **SQLAlchemy**.
*   **DevOps** :
    *   Gestion des dépendances moderne avec **uv**.
    *   Pipeline CI/CD complet avec **GitHub Actions** (Linting, Tests, Migrations).
    *   Conteneurisation via Docker (à venir).

---

## Architecture Technique

### Stack
*   **Langage** : Python 3.13+
*   **API** : FastAPI, Pydantic
*   **Base de Données** : PostgreSQL 15, SQLAlchemy (ORM), Alembic (Migrations)
*   **Sécurité** : Passlib (Bcrypt), Python-Jose (si JWT ajouté), Pydantic-Settings
*   **Tests** : Pytest, Pytest-Cov, TestClient
*   **Qualité** : Ruff (Linter/Formatter), GitFlow

### Structure du Projet
```text
├── .github/workflows/   # Pipeline CI/CD automatisé
├── alembic/             # Gestionnaires de migration BDD
├── Data/
│   └── model/           # Modèle ML entraîné (.joblib)
├── app/
│   ├── core/            # Configuration et Sécurité (security.py, config.py)
│   ├── db/              # Modèles SQLAlchemy (models.py) et Connexion (database.py)
│   └── main.py          # Point d'entrée de l'API
├── tests/               # Tests unitaires et d'intégration
├── create_user.py       # Script d'initialisation admin
└── pyproject.toml       # Gestionnaire de dépendances
```

---

## Installation et Démarrage

### 1. Prérequis
*   Un serveur **PostgreSQL** qui tourne en local ou via Docker.
*   L'outil **[uv](https://github.com/astral-sh/uv)** installé.

### 2. Duplication du dépôt
```powershell
git clone https://github.com/richardhugou/Projet-555.git
cd "Projet 555"
```

### 3. Installation des dépendances
```powershell
uv sync --all-extras
```

### 4. Configuration (.env)
Créez un fichier `.env` à la racine :
```ini
# Connexion Base de données (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/scoring_db

# Identifiants API (pour l'initialisation admin)
API_USERNAME=admin
API_PASSWORD=monSuperPasswordSecurise
```

### 5. Initialisation de la Base de Données
On utilise Alembic pour créer les tables (Users, Historique) :
```powershell
uv run alembic upgrade head
```

### 6. Création de l'Administrateur
Lancez le script dédié pour créer votre premier utilisateur hashé en base :
```powershell
uv run python create_user.py
```
*(Vous verrez le message : `Utilisateur 'admin' créé avec succès !`)*

---

## 🖥️ Utilisation

### Lancer l'API
```powershell
uv run uvicorn app.main:app --reload
```
L'API est accessible sur `http://127.0.0.1:8000`.

### Documentation Interactive
FastAPI génère automatiquement la documentation :
*   **Swagger UI** : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
    *   *Cliquez sur le cadenas 🔒 et entrez vos identifiants admin pour utiliser `/predict`.*
*   **ReDoc** : [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Exemple de Requête (/predict)
**POST** `/predict` (Authentifié Basic Auth)
```json
{
  "age": 35,
  "revenu_mensuel": 5000,
  "distance_domicile_travail": 10,
  "satisfaction_environnement": 3,
  "heures_supp": "Oui",
  "annees_promo": 2,
  "satisfaction_equilibre": 4,
  "pee": 1,
  "poste_actuel": 5,
  "anciennete": 8,
  "exp_totale": 12
}
```

---

## Tests et Qualité

### Lancer les Tests
La suite de tests est configurée pour :
1.  Créer une table temporaire pour chaque test.
2.  Créer un utilisateur de test à la volée.
3.  Vérifier les scénarios nominaux et d'erreur.

```powershell
uv run pytest tests/ -v --cov=app
```
*(Résultat attendu : 100% de réussite)*

### Linting
```powershell
uvx ruff check .
```

---

## 📦 CI/CD Pipeline
Le fichier `_01_integration.yaml` gère l'intégration continue :
1.  **Checkout** du code.
2.  Setup de **Python** et **uv**.
3.  Démarrage d'un **Service PostgreSQL** temporaire.
4.  Application des **Migrations** en base.
5.  Exécution des **Tests**.
6.  Analyse de **Couverture**.

---
*Projet réalisé dans le cadre de la certification MLOps.*
