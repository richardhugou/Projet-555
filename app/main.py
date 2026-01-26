from fastapi import FastAPI # Nécessaire pour le projet
from pydantic import BaseModel
import joblib
from fastapi import HTTPException
import pandas as pd

# Initialisation de l'application
app = FastAPI(
    title="API de scoring de crédit",
    description="API pour la prédiction de scoring de crédit",
    version="1.0.0" # Permet de gérer les versions de l'API
)

# Définition des inputs, on va devoir y revenir pour éviter les erreurs de saisie
class EmployeeInput(BaseModel):
    age: int
    revenu_mensuel: float
    distance_domicile_travail: float
    satisfaction_environnement: int
    heures_supp: str  # "Oui" ou "Non"
    annees_promo: int
    satisfaction_equilibre: int
    pee: int
    poste_actuel: int
    anciennete: int
    exp_totale: float

# Chargement du modèle
# On enverra un message d'erreur si le modèle n'est pas trouvé, on est jamais à l'abri d'un plantage
try:
    model = joblib.load("../model/model.joblib")
except FileNotFoundError:
    model = None
    print("Modèle non trouvé")

# Route pour la prédiction
@app.post("/predict") # Le @ signifie que c'est une route
def predict_churn(data: EmployeeInput): # data est le paramètre qui va contenir les données, employeeInput est le type de données que l'on a défini plus haut

    # Vérification que le modèle est bien là
    if model is None:
        raise HTTPException(status_code=500, detail="Le modèle n'est pas chargé.") # Le code 500 signifie qu'il y a eu une erreur, c'est normalisé

    # On accède aux valeurs avec data.age, data.revenu_mensuel, etc.
    # Vérification des valeurs, on va changer ça après avec la méthode pydantic, c'est juste pour tester
    if data.age < 18:
        raise HTTPException(status_code=400, detail="L'âge doit être supérieur à 18 ans.") # Le code 400 correspond à une erreur de requête
    if data.revenu_mensuel < 0:
        raise HTTPException(status_code=400, detail="Le revenu mensuel doit être positif.")
    if data.distance_domicile_travail < 0:
        raise HTTPException(status_code=400, detail="La distance domicile-travail doit être positive.")
    if data.satisfaction_environnement < 0 or data.satisfaction_environnement > 5:
        raise HTTPException(status_code=400, detail="La satisfaction environnement doit être entre 0 et 5.")
    if data.annees_promo < 0:
        raise HTTPException(status_code=400, detail="Les années depuis la dernière promotion doivent être positives.")
    if data.satisfaction_equilibre < 0 or data.satisfaction_equilibre > 5:
        raise HTTPException(status_code=400, detail="La satisfaction équilibre-pro-perso doit être entre 0 et 5.")
    if data.pee < 0:
        raise HTTPException(status_code=400, detail="Le nombre de participations au PEE doit être positif.")
    if data.poste_actuel < 0:
        raise HTTPException(status_code=400, detail="Le poste actuel doit être positif.")
    if data.anciennete < 0:
        raise HTTPException(status_code=400, detail="L'ancienneté doit être positive.")
    if data.exp_totale < 0:
        raise HTTPException(status_code=400, detail="L'expérience totale doit être positive.")


    # Feature Engineering
    hp_sup = 1 if data.heures_supp == "Oui" else 0 # 1 si Oui, 0 si Non pour rappel

    # Attention aux divisions par zéro
    anciennete = data.anciennete if data.anciennete > 0 else 1 # On évite les divisions par zéro
    ratio_stagnation = data.poste_actuel / anciennete

    exp_totale = data.exp_totale if data.exp_totale > 0 else 1 # On évite les divisions par zéro
    revenu_par_exp = data.revenu_mensuel / exp_totale

    # Création du DataFrame pour le modèle, on respecte les noms des colonnes attendus par le modèle
    input_df = pd.DataFrame([{
        'revenu_mensuel': data.revenu_mensuel,
        'age': data.age,
        'distance_domicile_travail': data.distance_domicile_travail,
        'satisfaction_employee_environnement': data.satisfaction_environnement,
        'heure_supplementaires': hp_sup,
        'annees_depuis_la_derniere_promotion': data.annees_promo,
        'satisfaction_employee_equilibre_pro_perso': data.satisfaction_equilibre,
        'nombre_participation_pee': data.pee,
        'ratio_stagnation': ratio_stagnation,
        'revenu_par_annee_exp': revenu_par_exp
    }])

    # Prédiction
    prediction = model.predict(input_df)[0] # 0, peu de risque de départ, 1, risque élevé
    probability = 0.0
    if hasattr(model, "predict_proba"): # Au cas où j'essaye un autre modèle plus tard, ce que je ne ferai sans doute pas
        probability = model.predict_proba(input_df)[0][1] # On regarde le premier résultat de la liste, il y en a qu'un de toute façon, et on récupère la probabilité, qui est la deuxième valeur [1]

    # Réponse simple pour commencer
    # Une API renvoie généralement du JSON (un dictionnaire Python) jamais utilisé avant mais on va le faire
    return {
        "prediction": int(prediction), # 0 ou 1
        "probability": float(probability),
        "message": "Risque de départ élevé" if prediction == 1 else "Employé stable"
    }
