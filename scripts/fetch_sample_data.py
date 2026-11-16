"""Download one sample response from each Open-Meteo API (Delhi) into sample_data/.

Run from the repo root:
    python scripts/fetch_sample_data.py

Uses only the Python standard library, so nothing needs to be installed.
"""

import json
import urllib.parse
import urllib.request
from pathlib import Path

SAMPLE_DIR = Path(__file__).resolve().parents[1] / "sample_data"

DELHI = {"latitude": 28.61, "longitude": 77.21}

REQUESTS = {
    "airquality_delhi.json": {
        "url": "https://air-quality-api.open-meteo.com/v1/air-quality",
        "hourly": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi",
    },
    "weather_delhi.json": {
        "url": "https://api.open-meteo.com/v1/forecast",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
    },
}


def fetch(url: str, hourly: str) -> dict:
    params = {
        **DELHI,
        "hourly": hourly,
        "timezone": "Asia/Kolkata",
        "past_days": 1,
    }
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    print(f"GET {full_url}")
    with urllib.request.urlopen(full_url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    SAMPLE_DIR.mkdir(exist_ok=True)
    for filename, cfg in REQUESTS.items():
        data = fetch(cfg["url"], cfg["hourly"])
        out_path = SAMPLE_DIR / filename
        out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        hourly = data.get("hourly", {})
        print(f"Saved {out_path} ({len(hourly.get('time', []))} hourly rows)")


if __name__ == "__main__":
    main()
