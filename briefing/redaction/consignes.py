"""Consignes et données communes aux rédacteurs IA (Gemini, Claude…)."""

import json
from dataclasses import asdict

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


def message_utilisateur(donnees: DonneesBriefing) -> str:
    contenu = asdict(donnees)
    del contenu["erreurs"]  # diagnostic interne, inutile pour la rédaction
    contenu["date"] = date_en_toutes_lettres(donnees.date)
    return "Données du jour :\n\n" + json.dumps(contenu, ensure_ascii=False, indent=2)
