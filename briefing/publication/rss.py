"""Ajoute le briefing du jour à un flux RSS statique (servi par GitHub Pages).

Le dossier de publication contient :
  - briefings.json : l'historique des derniers briefings (source de vérité) ;
  - audio/         : les MP3 récents, produits par publication/audio.py ;
  - feed.xml       : le flux RSS 2.0, régénéré entièrement à chaque exécution.
Un briefing dont le MP3 existe devient un épisode de podcast (<enclosure>).
"""

import json
from datetime import date, datetime
from email.utils import format_datetime
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo

from briefing.config import chemin_projet
from briefing.dates import date_en_toutes_lettres
from briefing.modeles import DonneesBriefing
from briefing.publication.audio import chemin_audio


def _charger_archive(chemin: Path) -> list[dict]:
    if not chemin.exists():
        return []
    return json.loads(chemin.read_text(encoding="utf-8"))


def _en_html(texte: str) -> str:
    lignes = (ligne.strip() for ligne in texte.splitlines())
    return "".join(f"<p>{escape(ligne, quote=False)}</p>" for ligne in lignes if ligne)


def _construire_flux(archive: list[dict], config: dict) -> ET.ElementTree:
    conf = config["rss"]
    rss = ET.Element("rss", version="2.0")
    canal = ET.SubElement(rss, "channel")
    ET.SubElement(canal, "title").text = conf["titre"]
    ET.SubElement(canal, "link").text = conf["url_site"]
    ET.SubElement(canal, "description").text = conf["description"]
    ET.SubElement(canal, "language").text = "fr"
    if archive:
        ET.SubElement(canal, "lastBuildDate").text = format_datetime(
            datetime.fromisoformat(archive[0]["publie_le"])
        )

    for entree in archive:
        item = ET.SubElement(canal, "item")
        jour = date.fromisoformat(entree["date"])
        ET.SubElement(item, "title").text = f"Briefing du {date_en_toutes_lettres(jour)}"
        ET.SubElement(item, "link").text = conf["url_site"]
        ET.SubElement(item, "guid", isPermaLink="false").text = f"briefing-{entree['date']}"
        ET.SubElement(item, "pubDate").text = format_datetime(
            datetime.fromisoformat(entree["publie_le"])
        )
        ET.SubElement(item, "description").text = _en_html(entree["texte"])
        audio = chemin_audio(jour, config)
        if audio.exists():
            ET.SubElement(item, "enclosure", url=f"{conf['url_site']}audio/{audio.name}",
                          length=str(audio.stat().st_size), type="audio/mpeg")

    ET.indent(rss)
    return ET.ElementTree(rss)


def publier(texte: str, donnees: DonneesBriefing, config: dict) -> Path:
    conf = config["rss"]
    dossier = chemin_projet(conf["dossier"])
    dossier.mkdir(parents=True, exist_ok=True)
    chemin_archive = dossier / "briefings.json"

    # Une seule entrée par jour : une relance le même jour remplace la précédente.
    jour = donnees.date.isoformat()
    archive = [e for e in _charger_archive(chemin_archive) if e["date"] != jour]
    maintenant = datetime.now(ZoneInfo(config["ville"]["fuseau"]))
    archive.append({"date": jour, "publie_le": maintenant.isoformat(timespec="seconds"), "texte": texte})
    archive.sort(key=lambda e: e["date"], reverse=True)
    archive = archive[: conf["nombre_briefings"]]

    chemin_archive.write_text(json.dumps(archive, ensure_ascii=False, indent=2), encoding="utf-8")
    chemin_flux = dossier / "feed.xml"
    _construire_flux(archive, config).write(chemin_flux, encoding="utf-8", xml_declaration=True)
    return chemin_flux
