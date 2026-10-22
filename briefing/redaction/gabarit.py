"""Rédacteur sans IA : assemble des phrases fixes, pensées pour l'oral."""

from briefing.dates import date_en_toutes_lettres
from briefing.modeles import DonneesBriefing, Meteo, Titre

ORDINAUX = ["Premier", "Deuxième", "Troisième", "Quatrième", "Cinquième",
            "Sixième", "Septième", "Huitième", "Neuvième", "Dixième"]


def _degres(temperature: float) -> str:
    n = round(temperature)
    unite = "degré" if abs(n) < 2 else "degrés"
    return f"moins {-n} {unite}" if n < 0 else f"{n} {unite}"


def _avec_point(phrase: str) -> str:
    return phrase if phrase.endswith((".", "!", "?", "…")) else phrase + "."


def _section_meteo(meteo: Meteo) -> str:
    phrases = [
        f"Côté météo, il fait en ce moment {_degres(meteo.temperature_actuelle)} à {meteo.ville}.",
        f"Pour la journée, on attend {meteo.description}.",
    ]
    if round(meteo.temperature_min) == round(meteo.temperature_max):
        phrases.append(f"Le thermomètre restera stable, autour de {_degres(meteo.temperature_max)}.")
    else:
        phrases.append(
            f"Minimale de {_degres(meteo.temperature_min)}, "
            f"maximale de {_degres(meteo.temperature_max)}."
        )
    if meteo.risque_pluie is not None:
        risque = meteo.risque_pluie
        if risque < 20:
            phrases.append(f"Le risque de pluie est faible : {risque} pour cent.")
        elif risque < 60:
            phrases.append(f"Le risque de pluie est de {risque} pour cent.")
        else:
            phrases.append(f"Le risque de pluie monte à {risque} pour cent, pense au parapluie.")
    return " ".join(phrases)


def _section_actualites(titres: list[Titre], avec_resume: bool) -> str:
    n = len(titres)
    lignes = [f"Côté actualité, voici {'le titre' if n == 1 else f'les {n} titres'} à retenir ce matin."]
    for i, titre in enumerate(titres):
        prefixe = f"{ORDINAUX[i]} titre" if i < len(ORDINAUX) else f"Titre {i + 1}"
        ligne = f"{prefixe} : {_avec_point(titre.titre)}"
        if avec_resume and titre.resume:
            ligne += f" {_avec_point(titre.resume)}"
        lignes.append(ligne)
    return "\n".join(lignes)


def rediger(donnees: DonneesBriefing, config: dict) -> str:
    sections = [
        f"Bonjour ! Nous sommes {date_en_toutes_lettres(donnees.date)}. "
        "Voici ton briefing du matin."
    ]
    if donnees.phrase:
        sections.append(f"Pour bien démarrer, le mot du jour : {_avec_point(donnees.phrase)}")
    if donnees.meteo:
        sections.append(_section_meteo(donnees.meteo))
    conf = config["actualites"]
    # Le gabarit ne sait pas juger si une nouvelle est positive : dans ce mode, il s'abstient.
    if donnees.titres and not conf["nouvelles_positives_uniquement"]:
        titres = donnees.titres[: conf["nombre_titres"]]
        sections.append(_section_actualites(titres, conf["avec_resume"]))
    sections.append("C'est tout pour ce matin. Belle journée !")
    return "\n\n".join(sections) + "\n"
