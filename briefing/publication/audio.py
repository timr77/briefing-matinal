"""Lecture du briefing à voix haute : produit un MP3 pour le flux podcast.

Le MP3 du jour est aussi copié sous un nom fixe (dernier-briefing.mp3, à la
racine du site), pour les automatisations du téléphone qui ont besoin d'une
adresse qui ne change pas.

Utilise les voix neuronales de Microsoft Edge via la bibliothèque edge-tts
(gratuite, sans clé, mais non officielle : le service peut changer).
"""

import asyncio
import shutil
from datetime import date
from pathlib import Path

import edge_tts

from briefing.config import chemin_projet
from briefing.modeles import DonneesBriefing

NOM_DERNIER = "dernier-briefing.mp3"


def chemin_audio(jour: date, config: dict) -> Path:
    return chemin_projet(config["rss"]["dossier"]) / "audio" / f"briefing-{jour.isoformat()}.mp3"


def publier(texte: str, donnees: DonneesBriefing, config: dict) -> Path:
    conf = config["audio"]
    chemin = chemin_audio(donnees.date, config)
    chemin.parent.mkdir(parents=True, exist_ok=True)

    voix = edge_tts.Communicate(texte, conf["voix"], rate=conf["vitesse"])
    try:
        asyncio.run(voix.save(str(chemin)))
    except Exception:
        chemin.unlink(missing_ok=True)  # pas de fichier tronqué dans le flux
        raise
    shutil.copyfile(chemin, chemin_projet(config["rss"]["dossier"]) / NOM_DERNIER)

    # Ne garder que les fichiers les plus récents, pour ne pas alourdir le dépôt.
    anciens = sorted(chemin.parent.glob("briefing-*.mp3"), reverse=True)[conf["nombre_fichiers"]:]
    for fichier in anciens:
        fichier.unlink()
    return chemin
