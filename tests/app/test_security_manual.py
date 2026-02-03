from app.core.security import verify_password

# Hash de "pomme23" généré dynamiquement pour ce fichier
# Hash = $2b$12$FmEEkwV/3sC0ixAhW45pcuNCteF9XccsD.HL8MRfRZ4FBWlaMAIRe
KNOWN_HASH_POMME23 = "$2b$12$FmEEkwV/3sC0ixAhW45pcuNCteF9XccsD.HL8MRfRZ4FBWlaMAIRe"

def test_hashing_brick_manual():
    print(f"\nTest avec hash : {KNOWN_HASH_POMME23}")

    # 1. Le bon mot de passe doit passer
    assert verify_password("pomme23", KNOWN_HASH_POMME23) is True, "pomme23 rejeté !"

    # 2. Un mauvais mot de passe doit échouer
    assert verify_password("banane19", KNOWN_HASH_POMME23) is False, "banane19 accepté !"

    # 3. Une variante doit échouer
    assert verify_password("pomme24", KNOWN_HASH_POMME23) is False, "pomme24 acceptée !"
