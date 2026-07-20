"""Service trésorerie — soldes caisse/banque (approche NCECF simplifiée)."""

from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modeles.tresorerie import (
    CompteTresorerie,
    OperationTresorerie,
    TypeCompteTresorerie,
    TypeOperationTresorerie,
)
from app.pagination import LIMITE_MAX
from app.services.calculs import arrondir


def calculer_solde(session: Session, compte: CompteTresorerie) -> Decimal:
    """Solde = ouverture + entrées − sorties (registre de caisse canadien)."""
    from sqlalchemy import case, func

    solde = arrondir(compte.solde_ouverture or Decimal("0"))
    total = (
        session.query(
            func.coalesce(
                func.sum(
                    case(
                        (OperationTresorerie.est_entree.is_(True), OperationTresorerie.montant),
                        else_=-OperationTresorerie.montant,
                    )
                ),
                0,
            )
        )
        .filter(OperationTresorerie.compte_id == compte.id)
        .scalar()
    )
    return arrondir(solde + Decimal(str(total)))


def lister_comptes_avec_soldes(session: Session, utilisateur_id: int) -> list[dict]:
    comptes = (
        session.query(CompteTresorerie)
        .filter_by(actif=True, utilisateur_id=utilisateur_id)
        .order_by(CompteTresorerie.type_compte, CompteTresorerie.nom)
        .limit(LIMITE_MAX)
        .all()
    )
    resultats = []
    total = Decimal("0")
    for compte in comptes:
        solde = calculer_solde(session, compte)
        total = arrondir(total + solde)
        resultats.append(
            {
                "id": compte.id,
                "nom": compte.nom,
                "type_compte": compte.type_compte if isinstance(compte.type_compte, str) else compte.type_compte.value,
                "solde_ouverture": compte.solde_ouverture,
                "solde_actuel": solde,
                "actif": compte.actif,
            }
        )
    return resultats


def resume_tresorerie(session: Session, utilisateur_id: int) -> dict:
    comptes = lister_comptes_avec_soldes(session, utilisateur_id)
    caisse = arrondir(sum((c["solde_actuel"] for c in comptes if c["type_compte"] == "caisse"), Decimal("0")))
    banque = arrondir(sum((c["solde_actuel"] for c in comptes if c["type_compte"] == "banque"), Decimal("0")))
    return {
        "comptes": comptes,
        "total_caisse": caisse,
        "total_banque": banque,
        "total_tresorerie": arrondir(caisse + banque),
    }


def _exiger_compte(session: Session, compte_id: int, utilisateur_id: int) -> CompteTresorerie:
    compte = session.get(CompteTresorerie, compte_id)
    if not compte or not compte.actif or compte.utilisateur_id != utilisateur_id:
        raise HTTPException(status_code=404, detail="Compte de trésorerie introuvable")
    return compte


def _vers_reponse(op: OperationTresorerie) -> dict:
    return {
        "id": op.id,
        "date_operation": op.date_operation,
        "type_operation": op.type_operation if isinstance(op.type_operation, str) else op.type_operation.value,
        "compte_id": op.compte_id,
        "compte_nom": op.compte.nom if op.compte else "",
        "compte_contrepartie_id": op.compte_contrepartie_id,
        "compte_contrepartie_nom": op.compte_contrepartie.nom if op.compte_contrepartie else None,
        "montant": op.montant,
        "est_entree": op.est_entree,
        "libelle": op.libelle,
        "reference": op.reference,
        "notes": op.notes,
        "revenu_id": op.revenu_id,
    }


def lister_operations(
    session: Session,
    utilisateur_id: int,
    *,
    compte_id: int | None = None,
    date_debut: date | None = None,
    date_fin: date | None = None,
    decalage: int = 0,
    limite: int = 100,
) -> list[dict]:
    requete = (
        session.query(OperationTresorerie)
        .join(CompteTresorerie, OperationTresorerie.compte_id == CompteTresorerie.id)
        .filter(CompteTresorerie.utilisateur_id == utilisateur_id)
        .order_by(
            OperationTresorerie.date_operation.desc(),
            OperationTresorerie.id.desc(),
        )
    )
    if compte_id is not None:
        requete = requete.filter(OperationTresorerie.compte_id == compte_id)
    if date_debut is not None:
        requete = requete.filter(OperationTresorerie.date_operation >= date_debut)
    if date_fin is not None:
        requete = requete.filter(OperationTresorerie.date_operation <= date_fin)
    operations = requete.offset(decalage).limit(limite).all()
    return [_vers_reponse(op) for op in operations]


def creer_operation(
    session: Session,
    utilisateur_id: int,
    *,
    date_operation: date,
    type_operation: str,
    compte_id: int,
    montant: Decimal,
    libelle: str,
    compte_contrepartie_id: int | None = None,
    est_entree: bool | None = None,
    reference: str | None = None,
    notes: str | None = None,
    revenu_id: int | None = None,
) -> list[dict]:
    """Crée 1 ou 2 écritures selon le type (dépôt/retrait/transfert = partie double)."""
    montant = arrondir(montant)
    if montant <= 0:
        raise HTTPException(status_code=400, detail="Le montant doit être positif")

    try:
        type_op = TypeOperationTresorerie(type_operation)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Type d'opération invalide") from exc

    compte = _exiger_compte(session, compte_id, utilisateur_id)
    creees: list[OperationTresorerie] = []

    if type_op == TypeOperationTresorerie.ENCAISSEMENT:
        creees.append(
            OperationTresorerie(
                date_operation=date_operation,
                type_operation=type_op.value,
                compte_id=compte.id,
                montant=montant,
                est_entree=True,
                libelle=libelle,
                reference=reference,
                notes=notes,
                revenu_id=revenu_id,
            )
        )
    elif type_op == TypeOperationTresorerie.PAIEMENT:
        creees.append(
            OperationTresorerie(
                date_operation=date_operation,
                type_operation=type_op.value,
                compte_id=compte.id,
                montant=montant,
                est_entree=False,
                libelle=libelle,
                reference=reference,
                notes=notes,
            )
        )
    elif type_op == TypeOperationTresorerie.AJUSTEMENT:
        if est_entree is None:
            raise HTTPException(status_code=400, detail="Précisez si l'ajustement est une entrée ou une sortie")
        creees.append(
            OperationTresorerie(
                date_operation=date_operation,
                type_operation=type_op.value,
                compte_id=compte.id,
                montant=montant,
                est_entree=est_entree,
                libelle=libelle,
                reference=reference,
                notes=notes,
            )
        )
    elif type_op in {
        TypeOperationTresorerie.DEPOT,
        TypeOperationTresorerie.RETRAIT,
        TypeOperationTresorerie.TRANSFERT,
    }:
        if not compte_contrepartie_id:
            raise HTTPException(status_code=400, detail="Compte de contrepartie requis")
        contrepartie = _exiger_compte(session, compte_contrepartie_id, utilisateur_id)
        if contrepartie.id == compte.id:
            raise HTTPException(status_code=400, detail="Les deux comptes doivent être distincts")

        if type_op == TypeOperationTresorerie.DEPOT:
            # Caisse (sortie) → Banque (entrée)
            if compte.type_compte != TypeCompteTresorerie.CAISSE:
                raise HTTPException(status_code=400, detail="Un dépôt part de la caisse")
            if contrepartie.type_compte != TypeCompteTresorerie.BANQUE:
                raise HTTPException(status_code=400, detail="Un dépôt arrive en banque")
            source, destination = compte, contrepartie
        elif type_op == TypeOperationTresorerie.RETRAIT:
            if compte.type_compte != TypeCompteTresorerie.BANQUE:
                raise HTTPException(status_code=400, detail="Un retrait part de la banque")
            if contrepartie.type_compte != TypeCompteTresorerie.CAISSE:
                raise HTTPException(status_code=400, detail="Un retrait arrive en caisse")
            source, destination = compte, contrepartie
        else:
            source, destination = compte, contrepartie

        creees.append(
            OperationTresorerie(
                date_operation=date_operation,
                type_operation=type_op.value,
                compte_id=source.id,
                compte_contrepartie_id=destination.id,
                montant=montant,
                est_entree=False,
                libelle=libelle,
                reference=reference,
                notes=notes,
            )
        )
        creees.append(
            OperationTresorerie(
                date_operation=date_operation,
                type_operation=type_op.value,
                compte_id=destination.id,
                compte_contrepartie_id=source.id,
                montant=montant,
                est_entree=True,
                libelle=libelle,
                reference=reference,
                notes=notes,
            )
        )
    else:
        raise HTTPException(status_code=400, detail="Type d'opération non géré")

    for op in creees:
        session.add(op)
    session.commit()
    for op in creees:
        session.refresh(op)
    return [_vers_reponse(op) for op in creees]


def supprimer_operation(session: Session, operation_id: int, utilisateur_id: int) -> None:
    operation = session.get(OperationTresorerie, operation_id)
    if not operation or not operation.compte or operation.compte.utilisateur_id != utilisateur_id:
        raise HTTPException(status_code=404, detail="Opération introuvable")

    # Supprimer la paire liée (même date, type, montant, libelle, comptes croisés)
    if operation.compte_contrepartie_id and operation.type_operation in {
        TypeOperationTresorerie.DEPOT,
        TypeOperationTresorerie.RETRAIT,
        TypeOperationTresorerie.TRANSFERT,
    }:
        jumelle = (
            session.query(OperationTresorerie)
            .filter(
                OperationTresorerie.id != operation.id,
                OperationTresorerie.date_operation == operation.date_operation,
                OperationTresorerie.type_operation == operation.type_operation,
                OperationTresorerie.montant == operation.montant,
                OperationTresorerie.libelle == operation.libelle,
                OperationTresorerie.compte_id == operation.compte_contrepartie_id,
                OperationTresorerie.compte_contrepartie_id == operation.compte_id,
            )
            .first()
        )
        if jumelle:
            session.delete(jumelle)

    session.delete(operation)
    session.commit()


def assurer_comptes_par_defaut(session: Session, utilisateur_id: int) -> None:
    if session.query(CompteTresorerie).filter_by(utilisateur_id=utilisateur_id).limit(1).first():
        return
    session.add(
        CompteTresorerie(
            utilisateur_id=utilisateur_id,
            nom="Caisse",
            type_compte=TypeCompteTresorerie.CAISSE,
            solde_ouverture=Decimal("0"),
        )
    )
    session.add(
        CompteTresorerie(
            utilisateur_id=utilisateur_id,
            nom="Banque principale",
            type_compte=TypeCompteTresorerie.BANQUE,
            solde_ouverture=Decimal("0"),
        )
    )
    session.commit()
