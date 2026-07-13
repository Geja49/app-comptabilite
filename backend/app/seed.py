from app.database import SessionLocale
from app.modeles import CategorieDepense

CATEGORIES_SYSTEME = [
    "Essence/Énergie",
    "Assurance commerciale",
    "Entretien véhicule",
    "Téléphone",
    "Permis et licences",
    "Autre",
]


def executer_seed():
    session = SessionLocale()
    try:
        for nom in CATEGORIES_SYSTEME:
            existe = session.query(CategorieDepense).filter_by(nom=nom).first()
            if not existe:
                session.add(CategorieDepense(nom=nom, est_systeme=True))
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    executer_seed()
