from app.db.database import SessionLocal, engine, Base
from app.db.models import User
from app.core.security import get_password_hash
from app.core.config import settings

def create_admin_user():
    # EQUIVALENT ALEMBIC : On s'assure que les tables existent avant d'ajouter l'user
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # 1. On récupère les valeurs depuis le .env / Secrets
    username = settings.API_USERNAME
    password = settings.API_PASSWORD

    # DEBUG :
    print(f"DEBUG: Username lu = '{username}'")
    print(f"DEBUG: Password lu = '{password}' (Type: {type(password)})")

    print(f"Tentative de création de l'utilisateur : {username}")

    # Vérifie si l'admin existe déjà
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"L'utilisateur '{username}' existe déjà. Mise à jour du mot de passe...")
        existing_user.hashed_password = get_password_hash(password)
        db.commit()
        print(f"Mot de passe pour '{username}' mis à jour avec succès !")
        db.close()
        return

    # Création avec hachage
    hashed_pwd = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_pwd)

    db.add(new_user)
    db.commit()
    print(f"Utilisateur '{username}' créé avec succès !")
    db.close()

if __name__ == "__main__":
    create_admin_user()
