import json
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from src.extract.extract_data import run_extract
from src.transform.transform_data import run_transform
from src.load.load_data import run_load
from src.utils.logger import log

def main():
    config_path = os.path.join(base_dir, "config", "settings.json")

    if not os.path.exists(config_path):
        log(f"❌ Erreur : Fichier config introuvable à {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        cfg = json.load(f)

    # 1. Extraction
    df_raw = run_extract(
        top_n_per_region=cfg["top_n_capitals_per_region"],
        start_date=cfg["start_date"]
    )
    log("✅ Extraction OK")

    # 2. Transformation
    df_clean = run_transform(df_raw)
    log("✅ Transformation OK")

    # 3. Chargement (Load)

    if os.getenv('K_SERVICE'):
        log("☁️ Environnement GCP détecté : Utilisation de l'identité du Job")
        gcs_key_path = cfg["gcs_key"] 
    else:
        gcs_key_path = cfg.get("gcs_key")

    run_load(
        df=df_clean,
        output_path=cfg["output_path"],
        bucket_name=cfg["bucket_name"],
        gcs_key=gcs_key_path
    )
    log(f"✅ Load OK → gs://{cfg['bucket_name']}/{cfg['gcs_key']}")


if __name__ == "__main__":
    main()