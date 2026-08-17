# Tableau de bord — Diagnostic acces a l'eau potable au Togo

Application Streamlit realisee pour le Ministere de l'Efficacite du Service Public et de la
Transformation Numerique, a partir de l'analyse exploratoire des donnees TdE, COSO et de l'indice
de risque d'inondation (FRI).

## Contenu du dossier

```
app.py                 Point d'entree de l'application
theme.py                Couleurs et styles CSS partages
components.py           Composants d'interface reutilisables (en-tete, cartes KPI, etc.)
filters.py              Filtres globaux (barre laterale)
data_loader.py          Chargement/mise en cache des donnees precalculees
views/                  Une page par module (accueil, carte, pression, inondation, coso,
                         priorisation, territoires, methodologie)
app_data/               Donnees precalculees (CSV + GeoJSON leger), logo du ministere
precompute.py           Script (a usage ponctuel, hors application) qui reproduit la
                         methodologie du notebook et regenere le contenu de app_data/
requirements.txt        Dependances Python de l'application
.streamlit/config.toml  Theme visuel de l'application
```

L'application ne depend, a l'execution, que de `streamlit`, `pandas` et `plotly` : les traitements
plus lourds (jointures spatiales avec `geopandas`, modelisation avec `scikit-learn`) ont ete
executes une fois pour produire les fichiers du dossier `app_data/`, ce qui rend le deploiement
plus rapide et plus leger.

## Lancer l'application en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

L'application s'ouvre automatiquement dans le navigateur (par defaut sur
`http://localhost:8501`).

## Deployer l'application

### Option 1 — Streamlit Community Cloud (gratuit, recommande pour une premiere mise en ligne)

1. Deposer ce dossier dans un depot Git (GitHub, GitLab...).
2. Se rendre sur https://share.streamlit.io, connecter le depot.
3. Indiquer `app.py` comme fichier principal.
4. Streamlit Cloud installe automatiquement les dependances listees dans `requirements.txt`.

### Option 2 — Serveur interne / conteneur Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t eau-togo-dashboard .
docker run -p 8501:8501 eau-togo-dashboard
```

### Option 3 — Toute plateforme PaaS compatible Python (Render, Railway, Azure App Service, etc.)

Point d'entree : `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Regenerer les donnees (optionnel)

Si les fichiers sources (TdE, COSO, FRI cantons) sont mis a jour, relancer :

```bash
pip install geopandas shapely pyogrio scikit-learn pandas
python precompute.py
```

Ce script relit les fichiers sources originaux (chemins configures en tete du script) et
regenere l'integralite du dossier `app_data/`. Il reproduit fidelement la methodologie du
notebook d'analyse exploratoire, y compris un correctif applique a la comparaison de libelles
accentues (statuts COSO, type d'ouvrage TdE) qui faussait initialement certains comptages.

## A lire avant toute decision operationnelle

La page "Methodologie et limites" de l'application documente en detail les sources de donnees,
les hypotheses de calcul et les limites identifiees (couverture partielle des bases d'ouvrages,
absence de champ d'etat de fonctionnement, donnee demographique mono-annuelle, etc.). Le rapport
d'analyse joint (`Rapport_Diagnostic_Eau_Potable_Togo.docx`) reprend cette meme exigence de
transparence de maniere redactionnelle.
