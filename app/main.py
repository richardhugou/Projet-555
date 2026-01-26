from fastapi import FastAPI # Nécessaire pour le projet
from pydantic import BaseModel
import joblib

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
    model = joblib.load("model/model.pkl")
except FileNotFoundError:
    model = None
    print("Modèle non trouvé")


