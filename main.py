"""Point d'entrée : collecte -> rédaction -> publication."""

import argparse
import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from briefing.config import RACINE, charger_config
from briefing.modeles import DonneesBriefing
from briefing.publication import fichier, rss
from briefing.redaction import claude, gabarit
from briefing.sources import actualites, meteo, phrase_du_jour

# Champ de DonneesBriefing -> fonction de collecte.
SOURCES = {
    "phrase": phrase_du_jour.recuperer,
    "meteo": meteo.recuperer,
    "titres": actualites.recuperer,
}

REDACTEURS = {
    "gabarit": gabarit.rediger,
    "claude": claude.rediger,
}

log = logging.getLogger("briefing")


def collecter(config: dict) -> DonneesBriefing:
    aujourdhui = datetime.now(ZoneInfo(config["ville"]["fuseau"])).date()
    donnees = DonneesBriefing(date=aujourdhui)
    for champ, recuperer in SOURCES.items():
        try:
            setattr(donnees, champ, recuperer(config))
        except Exception as erreur:  # une source en échec ne bloque pas le briefing
            message = f"section « {champ} » ignorée : {erreur}"
            log.warning(message)
            donnees.erreurs.append(message)
    return donnees


def rediger(donnees: DonneesBriefing, config: dict) -> str:
    moteur = config["redaction"]["moteur"]
    if moteur != "gabarit":
        try:
            return REDACTEURS[moteur](donnees, config)
        except Exception as erreur:  # sans IA, le gabarit produit toujours un briefing
            log.warning("rédaction « %s » en échec, repli sur le gabarit : %s", moteur, erreur)
    return gabarit.rediger(donnees, config)


def main() -> None:
    parser = argparse.ArgumentParser(description="Génère le briefing matinal.")
    parser.add_argument("--rss", action="store_true",
                        help="ajoute aussi le briefing au flux RSS (utilisé par GitHub Actions)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    sys.stdout.reconfigure(encoding="utf-8")

    config = charger_config()
    donnees = collecter(config)
    texte = rediger(donnees, config)
    print(texte)

    publications = [fichier] + ([rss] if args.rss else [])
    for module in publications:
        chemin = module.publier(texte, donnees, config)
        log.info("Publié : %s", chemin.relative_to(RACINE).as_posix())


if __name__ == "__main__":
    main()
