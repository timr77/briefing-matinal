"""Rédacteur IA : l'API Gemini de Google (offre gratuite) met en forme les données.

La clé est lue dans la variable d'environnement GEMINI_API_KEY.
"""

import logging
import os
import time

import requests

from briefing.modeles import DonneesBriefing
from briefing.redaction.consignes import CONSIGNES, message_utilisateur

URL = "https://generativelanguage.googleapis.com/v1beta/models/{modele}:generateContent"
ERREURS_TEMPORAIRES = {429, 500, 503}  # quota par minute, surcharge du service
TENTATIVES = 3
PAUSE = 20  # secondes, multipliée à chaque nouvelle tentative

log = logging.getLogger("briefing")


def _appeler(modele: str, cle: str, donnees: DonneesBriefing) -> requests.Response:
    """Appelle un modèle, en réessayant si le service est momentanément indisponible."""
    for tentative in range(1, TENTATIVES + 1):
        reponse = requests.post(
            URL.format(modele=modele),
            headers={"x-goog-api-key": cle},  # en en-tête : la clé n'apparaît pas dans les logs
            json={
                "systemInstruction": {"parts": [{"text": CONSIGNES}]},
                "contents": [{"role": "user", "parts": [{"text": message_utilisateur(donnees)}]}],
            },
            timeout=60,  # une réponse normale prend moins de 20 s
        )
        if reponse.status_code not in ERREURS_TEMPORAIRES or tentative == TENTATIVES:
            return reponse
        log.info("%s indisponible (HTTP %d), nouvel essai dans %d s",
                 modele, reponse.status_code, PAUSE * tentative)
        time.sleep(PAUSE * tentative)
    raise AssertionError("inatteignable")


def _extraire_texte(reponse: requests.Response) -> str:
    if not reponse.ok:
        try:
            detail = reponse.json()["error"]["message"]
        except (ValueError, KeyError):
            detail = reponse.text[:300]
        raise RuntimeError(f"HTTP {reponse.status_code} : {detail}")

    resultat = reponse.json()
    candidats = resultat.get("candidates") or []
    if not candidats:
        raise RuntimeError(f"aucune réponse (blocage : {resultat.get('promptFeedback')})")
    candidat = candidats[0]
    if candidat.get("finishReason") != "STOP":
        raise RuntimeError(f"réponse inutilisable (finishReason={candidat.get('finishReason')})")
    parties = candidat.get("content", {}).get("parts", [])
    texte = "".join(p.get("text", "") for p in parties if not p.get("thought")).strip()
    if not texte:
        raise RuntimeError("réponse vide")
    return texte + "\n"


def rediger(donnees: DonneesBriefing, config: dict) -> str:
    cle = os.environ.get("GEMINI_API_KEY")
    if not cle:
        raise RuntimeError("variable d'environnement GEMINI_API_KEY absente")

    # Les modèles sont essayés dans l'ordre : le suivant sert de secours.
    erreurs = []
    for modele in config["redaction"]["gemini"]["modeles"]:
        try:
            texte = _extraire_texte(_appeler(modele, cle, donnees))
            log.info("Briefing rédigé par %s", modele)
            return texte
        except (RuntimeError, requests.RequestException) as erreur:
            log.warning("%s en échec : %s", modele, erreur)
            erreurs.append(f"{modele} : {erreur}")
    raise RuntimeError("aucun modèle Gemini n'a répondu (" + " ; ".join(erreurs) + ")")
