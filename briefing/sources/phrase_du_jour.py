"""Mot sympa du jour, tiré au hasard dans phrases.txt."""

import random

from briefing.config import chemin_projet


def recuperer(config: dict) -> str:
    chemin = chemin_projet(config["phrases"]["fichier"])
    lignes = (ligne.strip() for ligne in chemin.read_text(encoding="utf-8").splitlines())
    phrases = [ligne for ligne in lignes if ligne and not ligne.startswith("#")]
    if not phrases:
        raise ValueError(f"aucune phrase dans {chemin.name}")
    return random.choice(phrases)
