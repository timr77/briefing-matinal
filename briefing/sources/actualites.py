"""Principaux titres de l'actualité depuis un flux RSS (franceinfo par défaut)."""

import html
import re
import xml.etree.ElementTree as ET

import requests

from briefing.modeles import Titre

USER_AGENT = "briefing-matinal/0.1 (usage personnel)"


def _nettoyer(texte: str | None) -> str:
    """Retire balises HTML, entités et espaces superflus."""
    if not texte:
        return ""
    texte = re.sub(r"<[^>]+>", " ", html.unescape(texte))
    return " ".join(texte.split())  # gère aussi les espaces insécables


def recuperer(config: dict) -> list[Titre]:
    conf = config["actualites"]
    reponse = requests.get(
        conf["flux_rss"],
        headers={"User-Agent": USER_AGENT},
        timeout=config["reseau"]["timeout"],
    )
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
        if len(titres) >= conf["nombre_titres"]:
            break

    if not titres:
        raise ValueError("le flux RSS ne contient aucun titre")
    return titres
