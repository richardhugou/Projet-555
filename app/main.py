from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal # Pour forcer "Oui" ou "Non"
import joblib
import pandas as pd
import os # C'est bien d'y penser avant de faire le test, mais au moins maintenant je sais lire les erreurs dans le terminal

# Initialisation de l'application
app = FastAPI(
    title="API de scoring de crédit",
    description="API pour la prédiction de scoring de crédit",
    version="1.0.0" # Permet de gérer les versions de l'API
)

class EmployeeInput(BaseModel): # ge greater than or equal to, le less than or equal to, et ... ou ellipsis est interprété par pydantic comme un champ requis
    age: int = Field(..., ge=18, le=70, description="L'âge doit être entre 18 et 70 ans")

    revenu_mensuel: float = Field(..., ge=0, description="Revenu mensuel positif")

    distance_domicile_travail: float = Field(..., ge=0, description="Distance domicile-travail")

    satisfaction_environnement: int = Field(..., ge=1, le=4, description="Note entre 1 et 4")

    heures_supp: Literal["Oui", "Non"] = Field(..., description="Heures supplémentaires")

    annees_promo: int = Field(..., ge=0, description="Années depuis la dernière promotion")

    satisfaction_equilibre: int = Field(..., ge=1, le=4, description="Note entre 1 et 4")

    pee: int = Field(..., ge=0, description="Nombre de participations au PEE")

    poste_actuel: int = Field(..., ge=0, description="Poste actuel")

    anciennete: int = Field(..., ge=0, description="Ancienneté")

    exp_totale: float = Field(..., ge=0, description="Expérience totale")

# Chargement du modèle
# On enverra un message d'erreur si le modèle n'est pas trouvé, on est jamais à l'abri d'un plantage
# On retravaille cette partie, car ça fait planter les tests, on va utiliser un chemin absolu
# On utilise le chemin absolu pour que le modèle soit trouvé, peu importe où le script est exécuté
model_path = os.path.join(os.path.dirname(__file__), "../Data/model/model.joblib")
try:
    model = joblib.load(model_path)
except FileNotFoundError:
    model = None
    print("Modèle non trouvé")

# Route pour la prédiction
@app.post("/predict") # Le @ signifie que c'est une route
def predict_churn(data: EmployeeInput): # data est le paramètre qui va contenir les données, employeeInput est le type de données que l'on a défini plus haut, churn parce que ça fait plus marketing RH, c'est bien pour le côté corpo

    # Vérification que le modèle est bien là
    if model is None:
        raise HTTPException(status_code=500, detail="Le modèle n'est pas chargé.") # Le code 500 signifie qu'il y a eu une erreur, c'est normalisé

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
