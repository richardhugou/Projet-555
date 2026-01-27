import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# On ajoute les variables d'environnement
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/scoring_db")

# On crée l'engine et la session
engine = create_engine(SQLALCHEMY_DATABASE_URL) # On crée l'engine, sert à la connexion à la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # On crée la session, sert à la connexion à la base de données
Base = declarative_base() # On crée la base de données

# Fonction pour obtenir une session, c'est une brique de code standard
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

