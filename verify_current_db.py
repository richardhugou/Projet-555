from app.db.database import SessionLocal, engine
from app.db.models import User, Historique
from app.core.config import settings
from sqlalchemy import text

def check_db_health():
    print("--- DIAGNOSTIC BASE DE DONNÉES ---")
    print(f"URL configurée : {settings.DATABASE_URL}")

    try:
        # 1. Test de connexion brute
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("Connexion Engine : OK")
    except Exception as e:
        print(f"Connexion Engine : ÉCHEC ({e})")
        return

    db = SessionLocal()
    try:
        # 2. Vérification des utilisateurs
        users = db.query(User).all()
        print(f"\nUtilisateurs ({len(users)}) :")
        for u in users:
            print(f"   - ID: {u.id} | User: '{u.username}'")

        if not users:
            print("AUCUN UTILISATEUR TROUVÉ ! L'authentification ne marchera pas.")

        # 3. Vérification de l'historique
        history_count = db.query(Historique).count()
        print(f"\nHistorique Prédictions : {history_count} entrées")

    except Exception as e:
        print(f"Erreur lors de la lecture des tables : {e}")
        print("Les tables n'existent peut-être pas ou sont corrompues.")
    finally:
        db.close()
    print("\n----------------------------------")

if __name__ == "__main__":
    check_db_health()
