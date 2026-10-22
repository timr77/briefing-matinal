"""Chargement de la configuration (config.toml)."""

import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def charger_config(chemin: Path = RACINE / "config.toml") -> dict:
    with open(chemin, "rb") as f:
        return tomllib.load(f)


def chemin_projet(relatif: str) -> Path:
    """Résout un chemin de la config par rapport au dossier du projet."""
    return RACINE / relatif
