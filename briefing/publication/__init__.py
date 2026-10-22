"""Diffusion du briefing rédigé.

Chaque module expose `publier(texte, donnees, config) -> Path`.
  - fichier.py : écriture de briefing.txt
  - audio.py   : MP3 lu par une voix de synthèse, dans docs/audio/ (option --rss)
  - rss.py     : ajout au flux RSS/podcast docs/feed.xml (option --rss)
"""
