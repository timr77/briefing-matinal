"""Rédacteur IA : l'API Claude met en forme les données collectées.

La clé est lue dans la variable d'environnement ANTHROPIC_API_KEY.
"""

import json
from dataclasses import asdict

import anthropic

from briefing.dates import date_en_toutes_lettres
from briefing.modeles import DonneesBriefing

CONSIGNES = """\
Tu rédiges le briefing matinal d'une personne qui vit à Stockholm. Elle l'écoutera \
à voix haute en se préparant le matin. Tu reçois en JSON les données du jour : la \
date, un mot du jour, la météo et des titres d'actualité de franceinfo avec leur résumé.

Écris en français un texte destiné à l'oral, d'environ 300 mots (deux minutes de \
lecture). Tutoie l'auditeur, avec un ton chaleureux et naturel, sans emphase ni mièvrerie.

Structure : une salutation avec la date, le mot du jour cité tel quel, la météo, \
l'actualité, puis une courte conclusion.

Contraintes :
- Texte brut uniquement : pas de titres, de puces, de markdown, d'emojis ni de liens. \
Paragraphes séparés par une ligne vide.
- Écris pour l'oreille : phrases courtes, transitions naturelles entre les sujets, \
nombres faciles à prononcer (« 12 degrés », « 25 pour cent », « moins 3 degrés »).
- Actualité : reste strictement fidèle aux titres et résumés fournis. Reformule pour \
l'oral, mais n'ajoute aucun fait, chiffre, nom ou contexte qui n'y figure pas, et ne \
donne pas d'opinion. Évoque chacun des titres fournis.
- Météo : appuie-toi sur la description, les températures et le risque de pluie \
fournis ; un conseil pratique (parapluie, écharpe…) est bienvenu s'il découle des données.
- Si une section vaut null, omets-la sans le signaler.
- Réponds uniquement avec le texte du briefing."""


def _donnees_en_json(donnees: DonneesBriefing) -> str:
    contenu = asdict(donnees)
    del contenu["erreurs"]  # diagnostic interne, inutile pour la rédaction
    contenu["date"] = date_en_toutes_lettres(donnees.date)
    return json.dumps(contenu, ensure_ascii=False, indent=2)


def rediger(donnees: DonneesBriefing, config: dict) -> str:
    conf = config["redaction"]
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
        messages=[{"role": "user", "content": f"Données du jour :\n\n{_donnees_en_json(donnees)}"}],
    )
    if reponse.stop_reason != "end_turn":
        raise RuntimeError(f"réponse inutilisable (stop_reason={reponse.stop_reason})")
    texte = "".join(bloc.text for bloc in reponse.content if bloc.type == "text").strip()
    if not texte:
        raise RuntimeError("réponse vide")
    return texte + "\n"
