from fastapi.testclient import TestClient
from app.main import app # On importe l'API depuis main.py
import pytest # ça marche mieux avec

# On créé un premier test, on doit pour ça faire un "client" qui va envoyer des requêtes à ton API
client = TestClient(app)

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
    }
]


# --- Fonction de test générale ---
# Il faut ajouter un décorateur pour que pytest reconnaisse la fonction
@pytest.mark.parametrize("scenario", scenarios) # On dit à pytest de prendre tous les scénarios et de les envoyer à la fonction test_predict_general
def test_predict_general(scenario):
    # Print statement pour voir le scénario en cours
    print(f"\n--- Test: {scenario['name']} ---")    
    print(f"Payload: {scenario['payload']}")
    print(f"Expected Status: {scenario['expected_status']}")
    # On envoie la requête POST
    response = client.post("/predict", json=scenario["payload"])

    # ASSERT = "Je parie que..." on veut une réponse 200, c'est un fonction qui permet de vérifier que la réponse est bien 200
    assert response.status_code == scenario["expected_status"]

    # On vérifie qu'on reçoit bien une prédiction et un message
    data = response.json()
    assert "prediction" in data
    assert "probability" in data
    assert "message" in data
    # On vérifie que la probabilité est bien entre 0 et 1
    assert 0 <= data["probability"] <= 1