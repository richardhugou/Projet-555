import pytest # ça marche mieux avec
from fastapi.testclient import TestClient
from app.main import app # On importe l'API depuis main.py

# On créé un premier test, on doit pour ça faire un "client" qui va envoyer des requêtes à ton API
client = TestClient(app)

# --- Fonction de test générale ---
def test_predict_nominal():
    # On définit un employé "normal" (valide), on va envoyer que des données valides (cf schéma dans main.py)
    payload = {
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
    
    # Le robot envoie la requête POST
    response = client.post("/predict", json=payload)
    
    # ASSERT = "Je parie que..." on veut une réponse 200, c'est un fonction qui permet de vérifier que la réponse est bien 200
    assert response.status_code == 200
    
    # On vérifie qu'on reçoit bien une prédiction et un message
    data = response.json()
    assert "prediction" in data
    assert "probability" in data
    assert "message" in data
    # On vérifie que la probabilité est bien entre 0 et 1
    assert 0 <= data["probability"] <= 1