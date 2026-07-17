"""Pagination simple pour les listes API (évite l'épuisement mémoire)."""

from fastapi import Query

LIMITE_DEFAUT = 100
LIMITE_MAX = 200


def params_pagination(
    decalage: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limite: int = Query(LIMITE_DEFAUT, ge=1, le=LIMITE_MAX, description="Taille de page"),
) -> tuple[int, int]:
    return decalage, limite


def appliquer_pagination(elements: list, decalage: int, limite: int) -> list:
    return elements[decalage : decalage + limite]
