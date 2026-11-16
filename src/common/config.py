"""Shared configuration for the air quality pipeline."""

# City name -> (latitude, longitude)
CITIES = {
    "delhi": (28.61, 77.21),
    "mumbai": (19.08, 72.88),
    "bengaluru": (12.97, 77.59),
    "hyderabad": (17.38, 78.49),
    "chennai": (13.08, 80.27),
    "kolkata": (22.57, 88.36),
    "pune": (18.52, 73.86),
    "ahmedabad": (23.02, 72.57),
}

AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

AIR_QUALITY_VARS = [
    "pm2_5",
    "pm10",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "us_aqi",
]

WEATHER_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
]