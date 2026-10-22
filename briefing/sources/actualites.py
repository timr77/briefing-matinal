"""Titres d'actualité depuis un ou plusieurs flux RSS (franceinfo par défaut).

Les titres de tous les flux sont regroupés en une liste de candidats ; c'est le
rédacteur qui choisit lesquels lire (par exemple les seules nouvelles positives).
"""

import html
import logging
import re
import xml.etree.ElementTree as ET

import requests

from briefing.modeles import Titre

USER_AGENT = "briefing-matinal/0.1 (usage personnel)"

log = logging.getLogger("briefing")


def _nettoyer(texte: str | None) -> str:
    """Retire balises HTML, entités et espaces superflus."""
    if not texte:
        return ""
    texte = re.sub(r"<[^>]+>", " ", html.unescape(texte))
    return " ".join(texte.split())  # gère aussi les espaces insécables


def _lire_flux(url: str, nombre: int, timeout: int) -> list[Titre]:
    reponse = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    reponse.raise_for_status()
    racine = ET.fromstring(reponse.content)

    titres = []
    for item in racine.iter("item"):
        titre = _nettoyer(item.findtext("title"))
        if not titre:
            continue
        titres.append(
            Titre(
                titre=titre,
                resume=_nettoyer(item.findtext("description")),
                lien=(item.findtext("link") or "").strip(),
            )
        )
        if len(titres) >= nombre:
            break
    return titres


def recuperer(config: dict) -> list[Titre]:
    conf = config["actualites"]
    candidats, deja_vus = [], set()
    for url in conf["flux_rss"]:
        try:
            titres = _lire_flux(url, conf["titres_par_flux"], config["reseau"]["timeout"])
        except Exception as erreur:  # un flux en panne n'empêche pas de lire les autres
            log.warning("flux %s ignoré : %s", url, erreur)
            continue
        for titre in titres:
            if titre.titre not in deja_vus:  # un même article peut figurer dans plusieurs rubriques
                deja_vus.add(titre.titre)
                candidats.append(titre)

    if not candidats:
        raise ValueError("aucun titre dans les flux RSS")
    return candidats
