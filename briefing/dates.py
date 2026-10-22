"""Formatage des dates en français, sans dépendre de la locale du système."""

from datetime import date

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def date_en_toutes_lettres(jour: date) -> str:
    """Ex. « jeudi 22 octobre », « lundi 1er décembre »."""
    numero = "1er" if jour.day == 1 else str(jour.day)
    return f"{JOURS[jour.weekday()]} {numero} {MOIS[jour.month - 1]}"
