from app.db.database import SessionLocal, SQLALCHEMY_DATABASE_URL
from app.db.models import User
from app.core.security import verify_password
from app.core.config import settings
import sys

def verify_login_simulation():
    print("--- TEST AUTHENTIFICATION ---")
    print(f"DB URL utilisée : {SQLALCHEMY_DATABASE_URL}")

    # 1. Lecture des identifiants théoriques (.env)
    env_username = settings.API_USERNAME
    env_password = settings.API_PASSWORD
    print(f"User attendu (.env) : '{env_username}'")
    print(f"Pass attendu (.env) : '{env_password}'")

    # 2. Récupération en BDD
    db = SessionLocal()
    user = db.query(User).filter(User.username == env_username).first()
    db.close()

    if not user:
        print(f"❌ ERREUR : L'utilisateur '{env_username}' n'est PAS trouvé dans la base !")
        sys.exit(1)

    print(f"✅ Utilisateur trouvé en base (ID: {user.id})")
    print(f"   Hash en base : {user.hashed_password[:20]}...")

    # 3. Test du mot de passe
    print("Test du match...")
    if verify_password(env_password, user.hashed_password):
        print("🚀 SUCCÈS : Le mot de passe du .env correspond bien au hash en base !")
        print(f"   -> Tu peux utiliser '{env_password}' dans Swagger.")
    else:
        print("❌ ÉCHEC : Le mot de passe du .env NE CORRESPOND PAS au hash en base.")
        print("   -> La mise à jour du mot de passe a échoué ou n'a pas été commuée.")
        print("   -> Solution : Relance 'uv run python create_user.py' avec le bon .env")

if __name__ == "__main__":
    verify_login_simulation()
