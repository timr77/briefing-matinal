"""Rédacteur IA : l'API Gemini de Google (offre gratuite) met en forme les données.

La clé est lue dans la variable d'environnement GEMINI_API_KEY.
"""

import os

import requests

from briefing.modeles import DonneesBriefing
from briefing.redaction.consignes import CONSIGNES, message_utilisateur

URL = "https://generativelanguage.googleapis.com/v1beta/models/{modele}:generateContent"


def rediger(donnees: DonneesBriefing, config: dict) -> str:
    cle = os.environ.get("GEMINI_API_KEY")
    if not cle:
        raise RuntimeError("variable d'environnement GEMINI_API_KEY absente")

    reponse = requests.post(
        URL.format(modele=config["redaction"]["gemini"]["modele"]),
        headers={"x-goog-api-key": cle},  # en en-tête : la clé n'apparaît pas dans les logs
        json={
            "systemInstruction": {"parts": [{"text": CONSIGNES}]},
            "contents": [{"role": "user", "parts": [{"text": message_utilisateur(donnees)}]}],
        },
        timeout=120,
    )
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
