# Projet 5 : Scoring de Crédit et Prédiction de Churn

| Branche | Statut CI |
| :--- | :--- |
| **Main** | ![CI - Main](https://github.com/richardhugou/Projet-555/actions/workflows/_01_integration.yaml/badge.svg?branch=main) |
| **Develop** | ![CI - Develop](https://github.com/richardhugou/Projet-555/actions/workflows/_01_integration.yaml/badge.svg?branch=develop) |

Ce dépôt contient le pipeline complet pour un modèle de machine learning : de l'entraînement à la mise en production via une API. On se concentre ici sur le "churn" RH, c'est-à-dire prédire le risque de départ d'un employé.

## Présentation
L'idée est de sortir un score basé sur les données socio-pros (salaire, distance, satisfaction, etc.) pour empêche... Pour améliorer la satisfaction des collaborateurs, et créer un environnement de travail épanouissant.

### Choix techniques
*   **FastAPI** : Pour la rapidité et parce que Pydantic gère tout seul la validation des entrées (on évite les erreurs de saisie). On fera quand même des tests pour s'en assurer.
*   **uv** : Pour la gestion des dépendances. C'est beaucoup plus rapide que pip et ça garantit qu'on a tous le même environnement.
*   **CI/CD** : Un workflow GitHub Actions qui lance Ruff pour le linting et Pytest pour les tests à chaque push. Le linting permet de garder un code propre et les tests permettent de s'assurer que le code fonctionne. On a aussi mis en place un système de déploiement sur Hugging Face.
*   **GitFlow** : On garde un historique propre en passant par des branches feature/ avant de merge.
*   **SQLAlchemy** : Pour la gestion de la base de données.
*   **Alembic** : Pour la gestion des migrations de la base de données. En itérant sur ce projet précédemment, j'ai constaté que l'ajout d'une colonne nécessitait la destruction de la base de données. Alembic permet d'éviter cela.


---

## Installation

### Prérequis
*   Python 3.13+
*   L'outil `uv` installé sur la machine.

### Setup
```powershell
# On récupère le dossier
git clone https://github.com/richardhugou/Projet-555.git
cd "Projet 555"

# Installation propre des dépendances
uv sync --all-extras
```

### Base de données
Le projet utilise Alembic pour gérer le schéma :
```powershell
# Appliquer les migrations
uv run alembic upgrade head
```

---

## Utilisation

### Lancer l'API en local
```powershell
uv run uvicorn app.main:app --reload
```
L'API tourne par défaut sur : `http://127.0.0.1:8000`

### Tester les endpoints
FastAPI génère automatiquement la doc interactive, c'est super pratique :
*   **Swagger UI** : `http://127.0.0.1:8000/docs`
*   **ReDoc** : `http://127.0.0.1:8000/redoc`

* Pour rappel :
    - **Swagger UI** (/docs) : C'est un outil de test. Il est interactif et permet d'envoyer des requêtes à l'API directement depuis le navigateur. Idéal pour les développeurs en phase de construction et de debug.
    - **ReDoc** (/redoc) : C'est une documentation de référence. Elle est statique, visuelle et optimisée pour la lecture. Idéale pour présenter proprement l'API à des clients ou des utilisateurs externes.

---

## Tests et Qualité

### Lancer la suite de tests
On utilise des **tests paramétrés** pour couvrir plusieurs scénarios (nominal, données invalides, types erronés) en une seule fonction :
```powershell
uv run pytest tests/ -v --cov=app
```

### Vérifier le style (Linting)
On utilise Ruff pour garder un code propre :
```powershell
uvx ruff check .
```

---

## Structure du Projet
```text
├── .github/workflows/   # Pipeline CI/CD
├── Data/
│   ├── model/           # Modèle entraîné (joblib)
│   └── database/        # Dossier pour la base SQLite
├── app/
│   └── main.py          # L'API où tout se passe
├── migrations/          # Scripts de migration Alembic
├── tests/               # La partie tests unitaires paramétrés
├── pyproject.toml       # Config et dépendances
└── README.md
```

### Pourquoi ces fichiers `__init__.py` partout ?
On les a mis dans `app/` et `tests/` pour que Python comprenne que ce sont des packages. C'est ce qui nous permet de faire des `from app.main import app` proprement dans les tests. Sans ça, les dossiers ne se "voient" pas entre eux.

---

## API : POST /predict
C'est le point d'entrée pour la prédiction. 

**Exemple de JSON à envoyer :**
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
*Projet 5 3éme itération.*
