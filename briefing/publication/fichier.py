"""Enregistre le briefing dans un fichier texte."""

from pathlib import Path

from briefing.config import chemin_projet
from briefing.modeles import DonneesBriefing


def publier(texte: str, donnees: DonneesBriefing, config: dict) -> Path:
    chemin = chemin_projet(config["sortie"]["fichier"])
    chemin.write_text(texte, encoding="utf-8")
    return chemin
