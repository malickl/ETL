# Projet ETL – Données Météo (Cloud)

## 🎯 Objectif
Ce projet a pour objectif de mettre en place un pipeline **ETL (Extract, Transform, Load)** en Python, déployé sur le cloud, permettant de collecter des données météorologiques depuis des APIs publiques, de les transformer, puis de les stocker dans un service de stockage cloud.

---

## 📊 Sources de données
Les données utilisées proviennent de sources Open Data :
- **RestCountries API** : récupération des pays, capitales, régions et populations
- **Open-Meteo API** : récupération des données météo journalières (température, précipitations, UV, vent, etc.)

---

## ⚙️ Architecture du pipeline
Le pipeline suit les étapes suivantes :

1. **Extraction**
   - Récupération des capitales des pays via RestCountries
   - Sélection des N capitales les plus peuplées par région
   - Appels à l’API Open-Meteo pour chaque capitale

2. **Transformation**
   - Nettoyage des données
   - Normalisation des dates
   - Suppression des doublons
   - Structuration sous forme tabulaire

3. **Load**
   - Export des données transformées en CSV
   - Chargement du fichier dans un bucket **Google Cloud Storage**

L’orchestration est assurée par un script principal (`main.py`) qui exécute successivement les étapes Extract → Transform → Load.

---

## 🗂️ Structure du projet
```
ETL_Project/
├── config/
│   └── settings.json
├── src/
│   ├── main.py
│   ├── extract/
│   │   └── extract_data.py
│   ├── transform/
│   │   └── transform_data.py
│   ├── load/
│   │   └── load_data.py
│   └── utils/
│       └── logger.py
├── docs/
│   └── data_dictionary.csv
├── tests/
├── requirements.txt
└── README.md
```

---

## ☁️ Stockage Cloud
Les données finales sont stockées dans un bucket **Google Cloud Storage** :

```
gs://etl-meteo-malick/raw/capitales_meteo.csv
```

À chaque exécution du pipeline, le fichier est **écrasé**, ce qui correspond à une première version simple du pipeline.  
Une historisation des données est identifiée comme une perspective d’amélioration.

---

## ▶️ Exécution du projet

### Pré-requis
- Python 3.10+
- Un compte Google Cloud avec Cloud Storage activé
- Une clé de compte de service GCP configurée via la variable d’environnement :

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/chemin/vers/la-cle.json"
```

### Installation des dépendances
```bash
pip install -r requirements.txt
```

### Lancer le pipeline
```bash
python -m src.main
```

---

## 🚀 Perspectives d’amélioration
- Historisation des données (partition par date)
- Ajout de tests unitaires
- Orchestration automatisée (cron, Cloud Scheduler)
- Stockage analytique (BigQuery)

---

## 👤 Auteur
Projet réalisé dans le cadre d’un projet académique de **Data Engineering / Architecture ETL**.
