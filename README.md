# Briefing matinal

Génère chaque matin un court texte en français, à écouter à voix haute (~2 min) :
un mot sympa du jour, la météo à Stockholm (Open-Meteo) et les principaux titres
de franceinfo (RSS). Le texte est rédigé par une IA (Gemini, offre gratuite) et
publié dans un flux RSS par GitHub Actions.

Flux : https://timr77.github.io/briefing-matinal/feed.xml

## Lancer en local

Python 3.11 ou plus récent.

```powershell
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS : source .venv/bin/activate
pip install -r requirements.txt
$env:GEMINI_API_KEY = "..."     # facultatif, voir ci-dessous
python main.py
```

Le texte s'affiche dans le terminal et est enregistré dans `briefing.txt`.
`python main.py --rss` met aussi à jour le flux dans `docs/` (c'est ce que fait
GitHub Actions ; inutile en local).

**Robustesse :**
- Si une source échoue (réseau, flux indisponible…), le briefing est produit
  sans cette section.
- Sans clé API, ou si l'appel à l'IA échoue (quota gratuit épuisé…), le texte
  est rédigé par le gabarit sans IA. Un avertissement s'affiche dans les deux cas.

## Personnaliser

- `config.toml` : ville, flux RSS, nombre de titres, rédacteur (`gemini`,
  `claude` ou `gabarit`) et modèle, etc.
- `phrases.txt` : une phrase par ligne (lignes vides ou commençant par `#` ignorées).
- `briefing/redaction/consignes.py` : les instructions de rédaction données à l'IA.

## Mise en ligne (GitHub Actions + GitHub Pages)

Déjà en place pour ce dépôt. Pour le refaire ailleurs :

1. Pousser ce dossier dans un dépôt GitHub public.
2. Dans `config.toml`, mettre `url_site` à `https://<pseudo>.github.io/<dépôt>/`.
3. Ajouter le secret `GEMINI_API_KEY` (clé gratuite sur https://aistudio.google.com) :
   `gh secret set GEMINI_API_KEY`.
4. Lancer le workflow une première fois (onglet *Actions*, *Run workflow*) ;
   il crée `docs/`.
5. *Settings > Pages* : source « Deploy from a branch », branche `main`,
   dossier `/docs`.

Le workflow tourne ensuite chaque jour à 04:00 UTC, soit 5 h à Stockholm en
hiver et 6 h en été. Il committe `docs/feed.xml` et `docs/briefings.json`
(historique des 30 derniers briefings).

## Architecture

```
main.py                     collecte -> rédaction -> publication
config.toml, phrases.txt
briefing/
  config.py, modeles.py, dates.py
  sources/                  recuperer(config) -> données
    phrase_du_jour.py, meteo.py, actualites.py
  redaction/                rediger(donnees, config) -> texte
    consignes.py            instructions communes aux IA
    gemini.py               API Gemini (gratuite)
    claude.py               API Claude (payante)
    gabarit.py              phrases fixes, sans IA (repli)
  publication/              publier(texte, donnees, config)
    fichier.py              briefing.txt
    rss.py                  docs/feed.xml + docs/briefings.json
.github/workflows/briefing.yml
```

Pour ajouter une source, un rédacteur ou un canal de publication, il suffit
d'écrire un module avec la même fonction et de l'enregistrer dans `main.py`.
