
import requests
import pandas as pd
import time
import datetime
import openmeteo_requests
import requests_cache
from retry_requests import retry

# ---------------------------------------------------------
# Étape 1 : Récupérer les infos de chaque pays (RestCountries)
# ---------------------------------------------------------
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
print(f"✅ {len(df_countries)} capitales trouvées au total")

# ---------------------------------------------------------
# Étape 1bis : Garder les 15 plus grandes capitales par continent
# ---------------------------------------------------------
continents = df_countries["region"].dropna().unique().tolist()
top_capitals = []

for continent in continents:
    subset = (
        df_countries[df_countries["region"] == continent]
        .sort_values(by="population", ascending=False)
        .head(15)
    )
    top_capitals.append(subset)

df_countries = pd.concat(top_capitals).reset_index(drop=True)
print(f"🌍 {len(df_countries)} capitales retenues (15 par continent max)")
print(df_countries[["region", "country", "capital", "population"]].head(15))

# ---------------------------------------------------------
# Étape 2 : Configuration client Open-Meteo (cache + retry)
# ---------------------------------------------------------
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=3, backoff_factor=0.3)
openmeteo = openmeteo_requests.Client(session=retry_session)

# ---------------------------------------------------------
# Étape 3 : Fonction pour récupérer les données météo d'une ville
# ---------------------------------------------------------
def get_weather_data(lat, lon):
    url_meteo = "https://historical-forecast-api.open-meteo.com/v1/forecast"
    
    # 📅 Définir la période : du 1er janvier 2024 à aujourd’hui
    start_date = "2024-01-01"
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

        daily_data = pd.DataFrame({
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
        return daily_data
    except Exception as e:
        print(f"⚠️ Erreur pour {lat}, {lon}: {e}")
        return None

# ---------------------------------------------------------
# Étape 4 : Boucle sur les capitales sélectionnées et combinaison
# ---------------------------------------------------------
meteo_records = []
for i, row in df_countries.iterrows():
    print(f"🌆 {i+1}/{len(df_countries)} → {row['capital']} ({row['country']}) ...")
    meteo_df = get_weather_data(row["latitude"], row["longitude"])
    if meteo_df is not None:
        meteo_df["country"] = row["country"]
        meteo_df["capital"] = row["capital"]
        meteo_df["latitude"] = row["latitude"]
        meteo_df["longitude"] = row["longitude"]
        meteo_df["region"] = row["region"]
        meteo_df["subregion"] = row["subregion"]
        meteo_records.append(meteo_df)

    # Pause pour ne pas saturer l’API
    time.sleep(0.3)

# ---------------------------------------------------------
# Étape 5 : Sauvegarde finale
# ---------------------------------------------------------
if meteo_records:
    df_final = pd.concat(meteo_records, ignore_index=True)
    df_final.to_csv("capitales_meteo_top15_par_continent_2024_aujourdhui.csv", index=False)
    print("✅ Fichier 'capitales_meteo_top15_par_continent_2024_aujourdhui.csv' créé avec succès !")
else:
    print("❌ Aucune donnée météo récupérée.")
