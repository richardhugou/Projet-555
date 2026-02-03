import pytest
import os
from fastapi.testclient import TestClient
from app.db.database import Base, get_db, engine, SessionLocal
from app.main import app
from app.core.config import settings
from app.core.security import get_password_hash
# On importe les modèles pour être sûr qu'ils sont enregistrés dans Base
from app.db import models

# La Fixture qui gère la BDD
@pytest.fixture(scope="function")
def db_session():
    # NETTOYAGE PRÉVENTIF : On supprime tout pour partir d'une feuille blanche
    # (Évite les erreurs si une exécution précédente a crashé sans nettoyer)
    Base.metadata.drop_all(bind=engine)
    
    # Crée les tables sur la vraie base
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    # --- CRÉATION DE L'UTILISATEUR DE TEST ---
    # On crée l'utilisateur que le test va utiliser pour s'authentifier
    hashed_pwd = get_password_hash(settings.API_PASSWORD)
    user = models.User(username=settings.API_USERNAME, hashed_password=hashed_pwd)
    session.add(user)
    session.commit()
    # -----------------------------------------

    try:
        yield session
    finally:
        session.close()
        # Supprime les tables après le test pour nettoyer
        Base.metadata.drop_all(bind=engine)

# La Fixture CLIENT
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

# Payload à la base pour faciliter le multi test
base_payload = {
    "age": 30,
    "revenu_mensuel": 3000,
    "distance_domicile_travail": 10,
    "satisfaction_environnement": 3,
    "heures_supp": "Non",
    "annees_promo": 2,
    "satisfaction_equilibre": 3,
    "pee": 1,
    "poste_actuel": 5,
    "anciennete": 5,
    "exp_totale": 8
}

# Définition des scénarios de test
# On ouvre une liste pour stocker les scénérios, et un dico pour mettre des infos spécifiques
scenarios = [
    # Le test oklm
    {
        "name": "nominal",
        "payload": base_payload,
        "expected_status": 200,
        # La liste des clés qui DOIVENT être présentes
        "required_keys": ["prediction", "probability", "message"]
    },
    # Le test avec des données invalides
    {
        "name": "invalid_data",
        "payload": {
            "age": 150,
            "revenu_mensuel": -1000,
            "distance_domicile_travail": 10,
            "satisfaction_environnement": 3,
            "heures_supp": "Non",
            "annees_promo": 2,
            "satisfaction_equilibre": 3,
            "pee": 1,
            "poste_actuel": 5,
            "anciennete": 5,
            "exp_totale": 8
        },
        "expected_status": 422,
        # La liste des clés qui DOIVENT être présentes
        "required_keys": ["detail"]
    },
    # Scénario 3 : Données manquantes
    {
        "name": "missing_data",
        "payload": {
            "age": 30,
            "revenu_mensuel": 3000,
            "exp_totale": 8
        },
        "expected_status": 422,
        # La liste des clés qui DOIVENT être présentes
        "required_keys": ["detail"]
    },
    # Scénario 4 : Mauvais format
    {
        "name": "bad_type",
        "payload": {**base_payload, "revenu_mensuel": "beaucoup"},
        "expected_status": 422,
        "required_keys": ["detail"]
    }
]


# --- Fonction de test générale ---
# Il faut ajouter un décorateur pour que pytest reconnaisse la fonction
@pytest.mark.parametrize("scenario", scenarios) # On dit à pytest de prendre tous les scénarios et de les envoyer à la fonction test_predict_general
def test_predict_general(client, scenario):
    # Print statement pour voir le scénario en cours
    print(f"\n--- Test: {scenario['name']} ---")
    print(f"Payload: {scenario['payload']}")
    print(f"Expected Status: {scenario['expected_status']}")

    # Récupération des identifiants
    username = os.getenv("API_USERNAME", "admin")
    password = os.getenv("API_PASSWORD", "secret")

    # Authentification
    response =client.post(
        "/predict",
        auth=(username, password), # On utilise le tuple (username, password) pour l'authentification httpbasic était un outil serveur pas adapté
        json=scenario["payload"]
    )

    # Adapte l'expected status en fonction du scénario
    assert response.status_code == scenario["expected_status"]

    # On vérifie qu'on reçoit bien une prédiction et un message
    data = response.json()
    # On ne vérifie que les clés qui sont dans le scénario
    for key in scenario["required_keys"]:
        assert key in data, f"Il manque la clé '{key}' dans la réponse !"
