import requests


# ============================================================
# LOCATION
# ============================================================

PIN_CODE = "690518"

LOCATION = "Vallikunnam, Kerala, India"


# ============================================================
# STEP 1
# OPEN-METEO GEOCODING
# ============================================================

print("\n" + "=" * 60)
print("OPEN-METEO LOCATION LOOKUP")
print("=" * 60)

geocode_url = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

geocode_params = {

    "name": LOCATION,

    "count": 5,

    "language": "en",

    "format": "json"

}


try:

    response = requests.get(
        geocode_url,
        params=geocode_params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

except requests.RequestException as e:

    print("\nGeocoding request failed:")
    print(e)

    raise SystemExit


results = data.get("results", [])


if not results:

    print("\nNo location found.")

    raise SystemExit


location = results[0]


latitude = location["latitude"]

longitude = location["longitude"]


print("\nResolved Location")
print("-" * 60)

print("PIN        :", PIN_CODE)
print("Name       :", location.get("name"))
print("District   :", location.get("admin2"))
print("State      :", location.get("admin1"))
print("Country    :", location.get("country"))
print("Latitude   :", latitude)
print("Longitude  :", longitude)
print("Timezone   :", location.get("timezone"))


# ============================================================
# STEP 2
# OPEN-METEO WEATHER
# ============================================================

print("\n" + "=" * 60)
print("OPEN-METEO CURRENT WEATHER")
print("=" * 60)


weather_url = (
    "https://api.open-meteo.com/v1/forecast"
)


weather_params = {

    "latitude": latitude,

    "longitude": longitude,

    "current": (
        "temperature_2m,"
        "relative_humidity_2m,"
        "apparent_temperature,"
        "is_day,"
        "precipitation,"
        "rain,"
        "showers,"
        "weather_code,"
        "cloud_cover,"
        "surface_pressure,"
        "wind_speed_10m,"
        "wind_direction_10m,"
        "wind_gusts_10m"
    ),

    "timezone": "auto"

}


try:

    response = requests.get(
        weather_url,
        params=weather_params,
        timeout=15
    )

    response.raise_for_status()

    weather = response.json()

except requests.RequestException as e:

    print("\nWeather request failed:")
    print(e)

    raise SystemExit


# ============================================================
# STEP 3
# DISPLAY WEATHER
# ============================================================

current = weather["current"]


print("\nCurrent Conditions")
print("-" * 60)

print("Time             :", current["time"])

print(
    "Temperature      :",
    current["temperature_2m"],
    "°C"
)

print(
    "Feels Like       :",
    current["apparent_temperature"],
    "°C"
)

print(
    "Humidity         :",
    current["relative_humidity_2m"],
    "%"
)

print(
    "Precipitation    :",
    current["precipitation"],
    "mm"
)

print(
    "Rain             :",
    current["rain"],
    "mm"
)

print(
    "Showers          :",
    current["showers"],
    "mm"
)

print(
    "Cloud Cover      :",
    current["cloud_cover"],
    "%"
)

print(
    "Pressure         :",
    current["surface_pressure"],
    "hPa"
)

print(
    "Wind Speed       :",
    current["wind_speed_10m"],
    "km/h"
)

print(
    "Wind Direction   :",
    current["wind_direction_10m"],
    "°"
)

print(
    "Wind Gusts       :",
    current["wind_gusts_10m"],
    "km/h"
)

print(
    "Weather Code     :",
    current["weather_code"]
)

print(
    "Day/Night        :",
    "Day"
    if current["is_day"]
    else
    "Night"
)


print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)