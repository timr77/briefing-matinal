"""Rédaction du texte à partir des données collectées.

Chaque rédacteur expose `rediger(donnees, config) -> str`.
  - gabarit.py   : phrases fixes, sans IA (sert aussi de repli)
  - gemini.py    : API Gemini de Google (offre gratuite)
  - claude.py    : API Claude (payante)
  - consignes.py : consignes de rédaction communes aux rédacteurs IA
"""
