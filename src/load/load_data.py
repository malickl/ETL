import pandas as pd
from google.cloud import storage

def run_load(df: pd.DataFrame, output_path: str, bucket_name: str, gcs_key: str) -> None:
    df.to_csv(output_path, index=False)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_key)

    blob.upload_from_filename(output_path)