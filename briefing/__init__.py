"""Générateur de briefing matinal.

Le pipeline tient en trois étapes indépendantes :
  1. collecte    : chaque module de `sources/` renvoie des données structurées ;
  2. rédaction   : `redaction/` transforme ces données en texte à lire ;
  3. publication : `publication/` diffuse le texte (fichier, plus tard flux RSS).
"""
