"""Ingest Lambda: pulls air quality and weather data for each city
from Open-Meteo and writes the raw JSON to S3."""

import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import boto3

from common.config import (
    AIR_QUALITY_URL,
    AIR_QUALITY_VARS,
    CITIES,
    WEATHER_URL,
    WEATHER_VARS,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

BUCKET = os.environ["BUCKET_NAME"]
RAW_PREFIX = os.environ.get("RAW_PREFIX", "raw")
TIMEZONE = os.environ.get("TIMEZONE", "Asia/Kolkata")
MAX_ATTEMPTS = 3

DATASETS = [
    ("air_quality", AIR_QUALITY_URL, AIR_QUALITY_VARS),
    ("weather", WEATHER_URL, WEATHER_VARS),
]


def fetch_json(url, params):
    """GET a URL with query params, retrying transient failures."""
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(full_url, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            logger.warning("Attempt %d/%d failed: %s", attempt, MAX_ATTEMPTS, exc)
            if attempt < MAX_ATTEMPTS:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"All {MAX_ATTEMPTS} attempts failed: {last_error}")


def build_params(lat, lon, variables, past_days=1):
    return {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(variables),
        "timezone": TIMEZONE,
        "past_days": past_days,
        "forecast_days": 1,
    }


def handler(event, context):
    now = datetime.now(timezone.utc)
    dt = now.strftime("%Y-%m-%d")
    hr = now.strftime("%H")
    ingested_at = now.isoformat()
    past_days = 1
    if isinstance(event, dict):
        past_days = max(1, min(int(event.get("past_days", 1)), 92))

    written = 0
    failures = []

    for city, (lat, lon) in CITIES.items():
        for dataset, url, variables in DATASETS:
            params = build_params(lat, lon, variables, past_days)
            try:
                payload = fetch_json(url, params)
                envelope = {
                    "source": "openmeteo",
                    "dataset": dataset,
                    "city": city,
                    "ingested_at": ingested_at,
                    "request_params": params,
                    "response": payload,
                }
                key = (
                    f"{RAW_PREFIX}/source=openmeteo/dataset={dataset}/"
                    f"dt={dt}/hr={hr}/city={city}.json"
                )
                s3.put_object(
                    Bucket=BUCKET,
                    Key=key,
                    Body=json.dumps(envelope).encode("utf-8"),
                    ContentType="application/json",
                )
                written += 1
                logger.info("Wrote s3://%s/%s", BUCKET, key)
            except Exception as exc:  # keep going; report at the end
                logger.error("Failed %s/%s: %s", city, dataset, exc)
                failures.append(f"{city}/{dataset}")

    total = len(CITIES) * len(DATASETS)
    logger.info("Done: %d/%d files written", written, total)

    if failures:
        raise RuntimeError(f"{len(failures)}/{total} fetches failed: {failures}")

    return {"written": written, "total": total}