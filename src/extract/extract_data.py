import requests
import pandas as pd
import time
import datetime
import openmeteo_requests
import requests_cache
from retry_requests import retry

from src.utils.logger import log


def run_extract(top_n_per_region: int, start_date: str) -> pd.DataFrame:
    # --- 1) Pays / capitales (RestCountries)
    url_countries = "https://restcountries.com/v3.1/all"
    params_countries = {"fields": "name,capital,latlng,region,subregion,population"}
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url_countries, headers=headers, params=params_countries)
    response.raise_for_status()
    data_countries = response.json()

    countries = []
    for country in data_countries:
        name = country.get("name", {}).get("common")
        capital_list = country.get("capital", [])
        capital = capital_list[0] if capital_list else None
        latlng = country.get("latlng", [None, None])
        region = country.get("region")
        subregion = country.get("subregion")
        population = country.get("population", 0)

        if capital and latlng[0] and latlng[1]:
            countries.append({
                "country": name,
                "capital": capital,
                "latitude": latlng[0],
                "longitude": latlng[1],
                "region": region,
                "subregion": subregion,
                "population": population
            })

    df_countries = pd.DataFrame(countries)
    log(f"✅ {len(df_countries)} capitales trouvées au total")

    # --- 1bis) Top N par région
    regions = df_countries["region"].dropna().unique().tolist()
    top_capitals = []
    for region in regions:
        subset = (
            df_countries[df_countries["region"] == region]
            .sort_values(by="population", ascending=False)
            .head(top_n_per_region)
        )
        top_capitals.append(subset)

    df_countries = pd.concat(top_capitals).reset_index(drop=True)
    log(f"🌍 {len(df_countries)} capitales retenues ({top_n_per_region} par région max)")

    # --- 2) Client Open-Meteo
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=3, backoff_factor=0.3)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # --- 3) Fonction météo
    def get_weather_data(lat, lon):
        url_meteo = "https://historical-forecast-api.open-meteo.com/v1/forecast"
        end_date = datetime.date.today().strftime("%Y-%m-%d")

        params_meteo = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "daylight_duration",
                "uv_index_max",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max"
            ]
        }

        try:
            responses = openmeteo.weather_api(url_meteo, params=params_meteo)
            response = responses[0]
            daily = response.Daily()

            return pd.DataFrame({
                "date": pd.date_range(
                    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=daily.Interval()),
                    inclusive="left"
                ),
                "temperature_2m_max": daily.Variables(0).ValuesAsNumpy(),
                "temperature_2m_min": daily.Variables(1).ValuesAsNumpy(),
                "daylight_duration": daily.Variables(2).ValuesAsNumpy(),
                "uv_index_max": daily.Variables(3).ValuesAsNumpy(),
                "precipitation_sum": daily.Variables(4).ValuesAsNumpy(),
                "precipitation_probability_max": daily.Variables(5).ValuesAsNumpy(),
                "wind_speed_10m_max": daily.Variables(6).ValuesAsNumpy(),
            })
        except Exception as e:
            log(f"⚠️ Erreur météo ({lat}, {lon}) : {e}")
            return None

    # --- 4) Boucle
    meteo_records = []
    for i, row in df_countries.iterrows():
        log(f"🌆 {i+1}/{len(df_countries)} → {row['capital']} ({row['country']})")
        meteo_df = get_weather_data(row["latitude"], row["longitude"])

        if meteo_df is not None:
            meteo_df["country"] = row["country"]
            meteo_df["capital"] = row["capital"]
            meteo_df["latitude"] = row["latitude"]
            meteo_df["longitude"] = row["longitude"]
            meteo_df["region"] = row["region"]
            meteo_df["subregion"] = row["subregion"]
            meteo_records.append(meteo_df)

        time.sleep(0.3)

    if not meteo_records:
        raise RuntimeError("Aucune donnée météo récupérée.")

    return pd.concat(meteo_records, ignore_index=True)