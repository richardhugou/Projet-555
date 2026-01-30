import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool # maintenir la connection, pour éviter le test failure
from app.db.database import Base, get_db
from app.main import app
# On importe les modèles pour être sûr qu'ils sont enregistrés dans Base

# Configuration de la BDD de test qui fonctionnera dans la mémoire et sera détruite à la fin des tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}, # Permet à plusieurs threads de se connecter à la base de données
    poolclass=StaticPool # On garde la même connexion tout le temps, dans les tests précédents on avait un problème de connexion
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# La Fixture qui gère la BDD
@pytest.fixture(scope="function")
def db_session():
    # Crée les tables sur la connexion unique (StaticPool)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
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
