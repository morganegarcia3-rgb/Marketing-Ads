Marketing Ads — Projet Final Algo & BDD
MSc2 Manager Data Marketing — INSEEC 2026

Problématique métier
Dans un contexte d'agence digitale, la gestion simultanée de plusieurs clients et plateformes publicitaires (Meta, LinkedIn, Google Ads) rend difficile la lecture transversale des performances.
Comment piloter et comparer la performance publicitaire de plusieurs clients et plateformes pour identifier les campagnes les plus efficaces et détecter les anomalies de dépense ?
Ce projet construit un pipeline complet : base de données relationnelle, script Python de scoring automatique, et dashboard interactif pour visualiser les résultats.

Structure du projet
algo-bdd-projet/
├── create_db.sql        # Création de la base et insertion des données
├── requete.sql          # Requêtes SQL (SELECT, CTE, procédure stockée)
├── .env                 # Variables d'environnement (non commité)
├── .gitignore
├── python/
│   ├── pipeline.py      # Connexion MySQL + Pandas + API + scoring
│   └── dashboard.py     # Dashboard Plotly/Dash interactif
└── README.md

Base de données
6 tables relationnelles modélisant un portefeuille clients multi-plateformes :
TableDescriptionclientsAnnonceurs géréscampagnesCampagnes par client et plateformeperformancesMétriques quotidiennes (impressions, clics, spend, conversions)audiencesSegments cibléscampagne_audiencesLiaison many-to-many campagnes ↔ audiencesscores_campagnesRésultats du scoring Python
Afficher l'image

Pipeline Python
Le script pipeline.py exécute les étapes suivantes :

Connexion à MySQL via mysql-connector-python
Chargement et agrégation des données avec pandas
Appel API externe — taux de change EUR/USD (open.er-api.com) pour normaliser les dépenses
Calcul du score de performance par campagne (algorithme CTR / CPC / ROAS / Volume)
Écriture des scores enrichis dans la table scores_campagnes

bashpython python/pipeline.py

Dashboard interactif
Le dashboard dashboard.py (Plotly/Dash) permet de visualiser les performances en temps réel avec des filtres dynamiques.
KPIs affichés

Budget total dépensé
Conversions totales
Score de performance moyen

Graphiques

Score de performance par client et plateforme
Répartition du budget par plateforme
Segmentation des campagnes (Top / Mid / Low)

bashpython python/dashboard.py
Ouvrir dans le navigateur : http://127.0.0.1:8050

Algorithme de scoring
Chaque campagne reçoit un score sur 100, calculé à partir de 4 métriques normalisées :
MétriqueDescriptionPoidsCTRTaux de clic (clics / impressions)30%CPCCoût par clic (inversé — plus bas = mieux)25%ROASRetour sur dépense publicitaire30%VolumeImpressions normalisées15%
Segmentation automatique

Top — score > 66
Mid — score entre 33 et 66
Low — score < 33


Technologies

Python 3.13 / Anaconda
MySQL 8.0
pandas, plotly, dash, mysql-connector-python, python-dotenv, requests