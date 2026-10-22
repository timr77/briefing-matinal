"""Structures de données échangées entre collecte, rédaction et publication.

Les sources ne produisent jamais de texte final : elles remplissent ces
structures, que le rédacteur (gabarit aujourd'hui, Claude demain) met en forme.
"""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Meteo:
    ville: str
    temperature_actuelle: float
    temperature_min: float
    temperature_max: float
    risque_pluie: int | None  # en %, None si non fourni
    description: str  # ex. « de la bruine légère »


@dataclass
class Titre:
    titre: str
    resume: str
    lien: str


@dataclass
class DonneesBriefing:
    date: date
    phrase: str | None = None
    meteo: Meteo | None = None
    titres: list[Titre] | None = None
    erreurs: list[str] = field(default_factory=list)
