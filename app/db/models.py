from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.database import Base # Note l'import : app.db.database

class Historique(Base):
    __tablename__ = "historique_predictions"
    id = Column(Integer, primary_key=True, index=True)
    date_prediction = Column(DateTime(timezone=True), server_default=func.now()) # On ajoute la date de la prédiction, server_default=func.now() permet de mettre la date actuelle

    # Inputs, data qu'on utilise pour prédire
    age = Column(Integer)
    revenu_mensuel = Column(Float)
    distance_domicile_travail = Column(Integer)
    satisfaction_environnement = Column(Integer)
    heures_supp = Column(String)
    annees_promo = Column(Integer)
    satisfaction_equilibre = Column(Integer)
    pee = Column(Integer)
    poste_actuel = Column(Integer)
    anciennete = Column(Integer)
    exp_totale = Column(Integer)

    # Output, prédiction
    prediction = Column(Integer)
    probability = Column(Float)
