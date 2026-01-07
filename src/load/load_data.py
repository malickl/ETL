import pandas as pd
from google.cloud import storage
import os

def run_load(df: pd.DataFrame, output_path: str, bucket_name: str, gcs_key: str) -> None:
    # 1. Sauvegarde locale temporaire dans le conteneur
    df.to_csv(output_path, index=False)

    # 2. Initialisation du client (Auto-authentifié sur GCP)
    client = storage.Client()
    
    # 3. Accès au bucket
    bucket = client.bucket(bucket_name)
    
    blob = bucket.blob(gcs_key)

    # 4. Upload
    blob.upload_from_filename(output_path)
    
    if os.path.exists(output_path):
        os.remove(output_path)