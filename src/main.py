import json

from src.extract.extract_data import run_extract
from src.transform.transform_data import run_transform
from src.load.load_data import run_load
from src.utils.logger import log


def main():
    with open("config/settings.json", "r") as f:
        cfg = json.load(f)

    df_raw = run_extract(
        top_n_per_region=cfg["top_n_capitals_per_region"],
        start_date=cfg["start_date"]
    )
    log("✅ Extraction OK")

    df_clean = run_transform(df_raw)
    log("✅ Transformation OK")

    run_load(
        df=df_clean,
        output_path=cfg["output_path"],
        bucket_name=cfg["bucket_name"],
        gcs_key=cfg["gcs_key"]
    )
    log(f"✅ Load OK → gs://{cfg['bucket_name']}/{cfg['gcs_key']}")


if __name__ == "__main__":
    main()