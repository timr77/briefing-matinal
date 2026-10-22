"""Rédacteur IA : l'API Claude (payante) met en forme les données collectées.

La clé est lue dans la variable d'environnement ANTHROPIC_API_KEY.
"""

import anthropic

from briefing.modeles import DonneesBriefing
from briefing.redaction.consignes import CONSIGNES, message_utilisateur


def rediger(donnees: DonneesBriefing, config: dict) -> str:
    conf = config["redaction"]["claude"]
    client = anthropic.Anthropic()
    reponse = client.beta.messages.create(
        model=conf["modele"],
        max_tokens=16000,
        system=CONSIGNES,
        output_config={"effort": conf["effort"]},
        # Si les filtres de sécurité refusent la requête, l'API la rejoue
        # automatiquement sur un modèle de repli.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": message_utilisateur(donnees)}],
    )
    if reponse.stop_reason != "end_turn":
        raise RuntimeError(f"réponse inutilisable (stop_reason={reponse.stop_reason})")
    texte = "".join(bloc.text for bloc in reponse.content if bloc.type == "text").strip()
    if not texte:
        raise RuntimeError("réponse vide")
    return texte + "\n"
