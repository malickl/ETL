import pandas as pd

def run_transform(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Date propre (sans timezone)
    out["date"] = pd.to_datetime(out["date"]).dt.date.astype(str)

    # Petits nettoyages simples
    out = out.drop_duplicates(subset=["capital", "date"])
    out = out.sort_values(["capital", "date"]).reset_index(drop=True)

    return out