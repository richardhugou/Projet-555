from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from typing import Literal # Pour forcer "Oui" ou "Non"
import joblib
import pandas as pd
import os

# --- IMPORTS POUR LA BASE DE DONNÉES ---
from sqlalchemy.orm import Session  # Sert uniquement au "Typage" (pour que l'autocomplétion fonctionne sur l'objet db)
from app.db.database import get_db  # La fonction "Robinet" : C'est elle qui crée la session de connexion
from app.db.models import Historique, User # Le "Moule" : Historique et User
from app.core.security import verify_password

# Initialisation de l'application
app = FastAPI(
    title="API de prédiction de churn",
    description="API pour la prédiction de churn",
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

# sécurité
security = HTTPBasic()

# fonction de sécurité
def get_current_username(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)  # On injecte la dépendance DB
):
    # On cherche l'utilisateur dans la base de données
    user = db.query(User).filter(User.username == credentials.username).first()

    # Si l'utilisateur n'existe pas OU si le mot de passe ne matche pas le hash
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Chargement du modèle
model_path = os.path.join(os.path.dirname(__file__), "../Data/model/model.joblib")
try:
    model = joblib.load(model_path)
except FileNotFoundError:
    model = None
    print("Modèle non trouvé")

# Route pour la prédiction
@app.post("/predict") # Le @ signifie que c'est une route, post est la méthode HTTP utilisée, ici l'envoi de données
def predict_churn( # le post défini juste au dessus défini l'URL et la méthode HTTP, ici /predict et POST
    data: EmployeeInput, # On définit les données attendues avec pydantic
    db: Session = Depends(get_db), # On injecte la dépendance DB
    username: str = Depends(get_current_username) # On injecte la dépendance de sécurité
    ):  # on rajoute un paramètre pour se connecter à la base de données
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



    # On ajoute la prédiction et la probabilité dans la base de données
    historique = Historique(
        # Les champs sont les mêmes que dans le modèle
        age=data.age,
        revenu_mensuel=data.revenu_mensuel,
        distance_domicile_travail=data.distance_domicile_travail,
        satisfaction_environnement=data.satisfaction_environnement,
        heures_supp=data.heures_supp,
        annees_promo=data.annees_promo,
        satisfaction_equilibre=data.satisfaction_equilibre,
        pee=data.pee,
        poste_actuel=data.poste_actuel,
        anciennete=data.anciennete,
        exp_totale=data.exp_totale,
        # Les 2 champs restants sont les prédictions et la probabilité en sortie
        prediction=int(prediction),
        probability=float(probability)
    )
    db.add(historique)
    db.commit()

    # Réponse simple pour commencer
    return {
        "prediction": int(prediction), # 0 ou 1
        "probability": float(probability),
        "message": "Risque de départ élevé" if prediction == 1 else "Employé stable"
    }

@app.get("/history")
def get_history(db: Session = Depends(get_db), limit: int = 10): # Je voulais consulter les prédicitions faite dans la base de données
    return db.query(Historique).order_by(Historique.date_prediction.desc()).limit(limit).all()

# Page d'accueil avec choix de la documentation
from fastapi.responses import HTMLResponse

@app.get("/", include_in_schema=False)
def root():
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API Churn Prediction - Accueil</title>
        <style>
            :root {
                --primary: #6366f1;
                --secondary: #ec4899;
                --bg: #0f172a;
                --card-bg: #1e293b;
                --text: #f8fafc;
                --text-dim: #94a3b8;
            }
            body {
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
            }
            .container {
                text-align: center;
                background: var(--card-bg);
                padding: 3rem;
                border-radius: 1rem;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                max-width: 500px;
                width: 90%;
            }
            h1 {
                margin-bottom: 0.5rem;
                background: linear-gradient(to right, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 2.5rem;
            }
            p {
                color: var(--text-dim);
                margin-bottom: 2rem;
                line-height: 1.6;
            }
            .buttons {
                display: flex;
                gap: 1rem;
                justify-content: center;
                flex-wrap: wrap;
            }
            a {
                text-decoration: none;
                padding: 0.75rem 1.5rem;
                border-radius: 0.5rem;
                font-weight: 600;
                transition: transform 0.2s, opacity 0.2s;
            }
            a:hover {
                transform: translateY(-2px);
                opacity: 0.9;
            }
            .btn-swagger {
                background-color: var(--primary);
                color: white;
            }
            .btn-redoc {
                background-color: transparent;
                border: 2px solid var(--secondary);
                color: var(--secondary);
            }
            .footer {
                margin-top: 2rem;
                font-size: 0.875rem;
                color: var(--text-dim);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>API Churn Prediction</h1>
            <p>Bienvenue sur l'API de scoring de crédit et de prédiction de départ employé. Le modèle ML est prêt à servir.</p>
            
            <div class="buttons">
                <a href="/docs" class="btn-swagger">📚 Swagger UI (Interactif)</a>
                <a href="/redoc" class="btn-redoc">📖 ReDoc (Lecture)</a>
            </div>

            <div class="footer">
                Projet 5 - OpenClassrooms
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


