# Briefing matinal

Génère chaque matin un court texte en français, à écouter à voix haute (~2 min) :
un mot sympa du jour, la météo à Stockholm (Open-Meteo) et les principaux titres
de franceinfo (RSS). Le texte est rédigé par Claude et publié dans un flux RSS
par GitHub Actions.

## Lancer en local

Python 3.11 ou plus récent.

```powershell
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS : source .venv/bin/activate
pip install -r requirements.txt
$env:ANTHROPIC_API_KEY = "sk-ant-..."   # facultatif, voir ci-dessous
python main.py
```

Le texte s'affiche dans le terminal et est enregistré dans `briefing.txt`.
`python main.py --rss` met aussi à jour le flux dans `docs/` (c'est ce que fait
GitHub Actions ; inutile en local).

**Robustesse :**
- Si une source échoue (réseau, flux indisponible…), le briefing est produit
  sans cette section.
- Sans clé API, ou si l'appel à Claude échoue, le texte est rédigé par le
  gabarit sans IA. Un avertissement s'affiche dans les deux cas.

## Personnaliser

- `config.toml` : ville, flux RSS, nombre de titres, rédacteur (`claude` ou
  `gabarit`), modèle, URL du site pour le flux, etc.
- `phrases.txt` : une phrase par ligne (lignes vides ou commençant par `#` ignorées).

## Mise en ligne (GitHub Actions + GitHub Pages)

1. Créer un dépôt GitHub et y pousser ce dossier.
2. Dans `config.toml`, remplacer `url_site` par
   `https://<pseudo>.github.io/<nom-du-depot>/`.
3. *Settings > Secrets and variables > Actions* : ajouter le secret
   `ANTHROPIC_API_KEY`.
4. *Actions* : lancer une première fois le workflow « Briefing matinal »
   (*Run workflow*) ; il crée `docs/`.
5. *Settings > Pages* : source « Deploy from a branch », branche `main`,
   dossier `/docs`.

Le flux est alors disponible sur `https://<pseudo>.github.io/<nom-du-depot>/feed.xml`.
Le workflow tourne ensuite chaque jour à 04:00 UTC, soit 5 h à Stockholm en
hiver et 6 h en été. Il committe `docs/feed.xml` et `docs/briefings.json`
(historique des 30 derniers briefings).

Coût de l'API : un appel par jour, de l'ordre de quelques centimes.

## Architecture

```
main.py                     collecte -> rédaction -> publication
config.toml, phrases.txt
briefing/
  config.py, modeles.py, dates.py
  sources/                  recuperer(config) -> données
    phrase_du_jour.py, meteo.py, actualites.py
  redaction/                rediger(donnees, config) -> texte
    claude.py               API Claude (consignes dans CONSIGNES)
    gabarit.py              phrases fixes, sans IA (repli)
  publication/              publier(texte, donnees, config)
    fichier.py              briefing.txt
    rss.py                  docs/feed.xml + docs/briefings.json
.github/workflows/briefing.yml
```

Pour ajouter une source, un rédacteur ou un canal de publication, il suffit
d'écrire un module avec la même fonction et de l'enregistrer dans `main.py`.
Piste suivante possible : synthèse vocale, pour transformer le flux en podcast
(fichier audio en `<enclosure>`).
