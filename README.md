Cyclist Performance Analytics API
Une API complète pour gérer et analyser les performances des cyclistes, avec une interface utilisateur Streamlit intégrée.
📋 Vue d'ensemble
Ce projet fournit une solution complète pour suivre et analyser les performances cyclistes. Il comprend :

Une API FastAPI pour la gestion des données et l'authentification
Une interface utilisateur Streamlit pour la visualisation et l'interaction
Un système d'authentification sécurisé basé sur JWT
Des fonctionnalités avancées d'analyse statistique

🚀 Fonctionnalités
API Backend

Authentification des utilisateurs

Inscription et connexion sécurisées
Système de jetons JWT pour l'authentification


Gestion des athlètes

Création et modification des profils d'athlètes
Stockage des métriques physiques (âge, poids, taille, etc.)


Suivi des performances

Enregistrement des performances cyclistes
Métriques telles que puissance, VO2max, fréquence cardiaque, etc.


Statistiques avancées

Identification de l'athlète le plus puissant
Analyse du VO2max
Calcul du rapport puissance/poids optimal



Interface Streamlit

Tableau de bord interactif
Visualisation graphique des performances
Comparaison entre athlètes
Gestion pratique des données

🔧 Installation

Clonez le dépôt :
Copiergit clone https://github.com/MichAdebayo/sql_fast-api.git

Créez et activez un environnement virtuel :
Copierpython -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate

Installez les dépendances :
Copierpip install -r requirements.txt

Créez un fichier .env à la racine du projet avec les variables suivantes :
CopierSECRET_KEY=votre_clé_secrète_ici
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=cyclist_database.db


🏃‍♂️ Utilisation
Lancer l'API
Copiercd api_cyclist
uvicorn app.main:app --reload
L'API sera accessible à l'adresse http://127.0.0.1:8000
Documentation interactive de l'API disponible à http://127.0.0.1:8000/docs
Lancer l'interface Streamlit
Copiercd app_cyclist
streamlit run app.py
L'interface utilisateur sera accessible à l'adresse http://localhost:8501
📁 Structure du Projet
Copiercyclist-analytics/
├── app.py                  # Application Streamlit principale
├── config.toml             # Configuration Streamlit
├── components/             # Composants réutilisables de l'interface
│   └── sidebar.py          # Barre latérale de navigation
├── utils/                  # Utilitaires
│   ├── api.py              # Fonctions de communication avec l'API
│   ├── auth.py             # Gestion de l'authentification
│   └── session.py          # Gestion des états de session
├── views/                  # Pages de l'interface utilisateur
│   ├── dashboard.py        # Tableau de bord principal
│   ├── profile.py          # Profil utilisateur
│   ├── athlete_creation.py # Création d'athlètes
│   └── ...                 # Autres pages
└── app/                    # API FastAPI
    ├── main.py             # Point d'entrée de l'API
    ├── config.py           # Configuration de l'API
    ├── database.py         # Connexion à la base de données
    ├── models/             # Modèles de données Pydantic
    ├── endpoints/          # Points d'accès API
    └── utils/              # Utilitaires pour l'API
🔐 Authentification
Le système utilise l'authentification JWT (JSON Web Tokens). Pour accéder aux endpoints protégés :

Créez un utilisateur via /users/register
Obtenez un token via /token
Incluez le token dans l'en-tête Authorization des requêtes : Bearer {votre_token}