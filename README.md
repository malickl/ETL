🌦️ Projet ETL -- Données Météo (Cloud Native)
=============================================

🎯 Objectif
-----------

Mise en place d'un pipeline **ETL (Extract, Transform, Load)** automatisé et conteneurisé sur **Google Cloud Platform (GCP)**. Le système collecte des données météo mondiales, les traite et les stocke quotidiennement de manière autonome.

* * * * *

📊 Sources de données
---------------------

-   **RestCountries API** : Liste des capitales et populations par région.

-   **Open-Meteo API** : Données météo historiques et temps réel.

* * * * *

⚙️ Architecture du pipeline (Cloud Native)
------------------------------------------

Le pipeline est désormais entièrement **Serverless** :

1.  **Conteneurisation** : L'application est packagée avec **Docker** et stockée sur **Artifact Registry**.

2.  **Exécution (Compute)** : Le code tourne sur **Cloud Run Jobs**, s'activant uniquement lors des tâches ETL.

3.  **Orchestration** : **Cloud Scheduler** déclenche le job chaque matin à 9h00 via une requête HTTP sécurisée.

4.  **Stockage** : Les données transformées sont envoyées vers **Google Cloud Storage**.

* * * * *

🗂️ Structure du projet
-----------------------

Plaintext

```
ETL_Project/
├── config/
│   └── settings.json       # Configuration (bucket, dates, filtres)
├── src/
│   ├── main.py             # Point d'entrée (Orchestrateur)
│   ├── extract/            # Logique d'extraction API
│   ├── transform/          # Nettoyage et structuration Pandas
│   ├── load/               # Upload vers GCS (Auto-auth)
│   └── utils/              # Logs et outils
├── Dockerfile              # Instructions pour l'image Cloud
├── requirements.txt        # Dépendances Python
└── README.md

```

* * * * *

☁️ Infrastructure GCP
---------------------

-   **Bucket final** : `gs://etl-meteo-malick/raw/capitales_meteo.csv`

-   **Sécurité** : Utilisation d'un **Service Account** (`etl-runner`) avec le rôle `Storage Object Admin`.

-   **Automatisation** : Planifié tous les jours à **09:00 (UTC/Paris)**.

* * * * *

▶️ Déploiement et Maintenance
-----------------------------

### Mettre à jour le code sur le Cloud

Si tu modifies le code Python localement, utilise ces commandes pour mettre à jour la version qui tourne à 9h :

Bash

```
# 1. Build de la nouvelle image
gcloud builds submit --tag gcr.io/gcp-hetic-pipeline/etl-image

# 2. Mise à jour du job Cloud Run
gcloud run jobs update etl-job --image gcr.io/gcp-hetic-pipeline/etl-image --region europe-west1

# 3. Test manuel immédiat
gcloud run jobs execute etl-job --region europe-west1

```

### Vérifier les logs

Les logs d'exécution (succès ou erreurs) sont consultables directement dans la console GCP : `Cloud Run > Jobs > etl-job > Exécutions`

* * * * *

🚀 Perspectives d'amélioration (V3)
-----------------------------------

-   **Historisation** : Ajouter un timestamp au nom du fichier (ex: `capitales_meteo_2026-01-07.csv`).

-   **Data Warehouse** : Charger les données directement dans **BigQuery** pour analyse SQL.

-   **Alerting** : Configurer des notifications Cloud Monitoring en cas d'échec du job.

* * * * *

👤 Auteur
---------

**Malick** -- Projet Data Engineering / Cloud Architecture.



lien dashboard : https://lookerstudio.google.com/reporting/76b662f5-5fff-4e76-beb6-c3a90d43c188