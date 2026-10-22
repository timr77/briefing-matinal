"""Météo du jour via l'API Open-Meteo (gratuite, sans clé)."""

import requests

from briefing.modeles import Meteo

URL = "https://api.open-meteo.com/v1/forecast"

# Codes météo WMO -> description à insérer dans « on attend … ».
DESCRIPTIONS = {
    0: "un grand ciel bleu",
    1: "un ciel plutôt dégagé",
    2: "un ciel partiellement nuageux",
    3: "un ciel couvert",
    45: "du brouillard",
    48: "du brouillard givrant",
    51: "un peu de bruine",
    53: "de la bruine",
    55: "une bruine soutenue",
    56: "de la bruine verglaçante",
    57: "une bruine verglaçante soutenue",
    61: "une pluie faible",
    63: "de la pluie",
    65: "une pluie forte",
    66: "de la pluie verglaçante",
    67: "une forte pluie verglaçante",
    71: "quelques flocons de neige",
    73: "de la neige",
    75: "d'importantes chutes de neige",
    77: "des grains de neige",
    80: "quelques averses",
    81: "des averses",
    82: "de violentes averses",
    85: "des averses de neige",
    86: "de fortes averses de neige",
    95: "des orages",
    96: "des orages avec un peu de grêle",
    99: "des orages avec de la grêle",
}


def decrire(code: int) -> str:
    return DESCRIPTIONS.get(code, "un temps changeant")


def recuperer(config: dict) -> Meteo:
    ville = config["ville"]
    params = {
        "latitude": ville["latitude"],
        "longitude": ville["longitude"],
        "timezone": ville["fuseau"],
        "current": "temperature_2m",
        "daily": "weather_code,temperature_2m_min,temperature_2m_max,precipitation_probability_max",
        "forecast_days": 1,
    }
    reponse = requests.get(URL, params=params, timeout=config["reseau"]["timeout"])
    reponse.raise_for_status()
    donnees = reponse.json()
    actuel, jour = donnees["current"], donnees["daily"]

    return Meteo(
        ville=ville["nom"],
        temperature_actuelle=actuel["temperature_2m"],
        temperature_min=jour["temperature_2m_min"][0],
        temperature_max=jour["temperature_2m_max"][0],
        risque_pluie=jour["precipitation_probability_max"][0],
        # Code journalier : le phénomène le plus marquant de la journée.
        description=decrire(jour["weather_code"][0]),
    )
