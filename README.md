# Algo & BDD — Projet Final MSc2 Data Marketing

## Problématique métier
Algo & BDD — Projet Final MSc2 Data Marketing
Problématique métier
Comment piloter et comparer la performance publicitaire de plusieurs clients et plateformes (Meta, LinkedIn, Google Ads) pour identifier les campagnes les plus efficaces et détecter les anomalies de dépense ?
Structure du projet
algo-bdd-projet/
├── create_db.sql       # Création de la base et insertion des données
├── requete.sql         # Requêtes SQL (SELECT, CTE, procédure stockée)
├── .env                # Variables d'environnement (non commité)
├── .gitignore
├── python/
│   ├── pipeline.py     # Connexion MySQL + Pandas + API + scoring
│   └── dashboard.py    # Dashboard Plotly/Dash interactif
└── README.md
Base de données
5 tables relationnelles :

clients — annonceurs gérés
campagnes — campagnes par client et plateforme
performances — métriques quotidiennes (impressions, clics, spend, conversions)
audiences — segments ciblés
campagne_audiences — liaison many-to-many campagnes ↔ audiences
scores_campagnes — résultats du scoring Python

Afficher l'image
Pipeline Python

Connexion à MySQL via mysql-connector-python
Chargement des données avec pandas
Appel API externe : taux de change EUR/USD (open.er-api.com)
Algorithme de scoring de performance (CTR, CPC, ROAS, Volume)
Écriture des scores dans la table scores_campagnes

Lancer le pipeline
bashpython python/pipeline.py
Dashboard interactif

3 KPIs : budget dépensé, conversions totales, score moyen
Graphique 1 : score de performance par client
Graphique 2 : répartition du budget par plateforme
Graphique 3 : segmentation Top / Mid / Low

Lancer le dashboard
bashpython python/dashboard.py
Puis ouvrir : http://127.0.0.1:8050
Technologies

Python 3.13 / Anaconda
MySQL 8.0
pandas, plotly, dash, mysql-connector-python, python-dotenv, requests

Algorithme de scoring
Score pondéré sur 100 points :
MétriquePoidsCTR30%CPC25%ROAS30%Volume15%
Segmentation : Top (>66) / Mid (33-66) / Low (<33)