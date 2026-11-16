"""Transform Lambda: raw Open-Meteo JSON (S3 raw/) -> curated Parquet (S3 curated/)."""

import json
import logging
import os
import urllib.parse

import awswrangler as wr
import boto3
import pandas as pd

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

CURATED_PREFIX = os.environ.get("CURATED_PREFIX", "curated")

# US AQI category thresholds
AQI_BINS = [-0.001, 50, 100, 150, 200, 300, float("inf")]
AQI_LABELS = [
    "Good",
    "Moderate",
    "Unhealthy for Sensitive Groups",
    "Unhealthy",
    "Very Unhealthy",
    "Hazardous",
]


def build_dataframe(envelope):
    """Flatten one raw envelope into a tidy, typed DataFrame (one row per hour)."""
    response = envelope["response"]

    df = pd.DataFrame(response["hourly"]).rename(columns={"time": "observation_ts"})
    df["observation_ts"] = pd.to_datetime(df["observation_ts"])

    value_cols = [c for c in df.columns if c != "observation_ts"]
    df[value_cols] = df[value_cols].apply(pd.to_numeric, errors="coerce").astype("float64")

    # Drop forecast hours: keep only hours up to "now" in the city's local time.
    ingested_at = pd.Timestamp(envelope["ingested_at"]).tz_convert("UTC")
    offset = pd.Timedelta(seconds=response.get("utc_offset_seconds", 0))
    local_now = (ingested_at + offset).tz_localize(None)
    df = df[df["observation_ts"] <= local_now].copy()

    df.insert(0, "city", envelope["city"])
    df.insert(1, "latitude", float(response["latitude"]))
    df.insert(2, "longitude", float(response["longitude"]))
    df["ingested_at"] = ingested_at.tz_localize(None)

    if "us_aqi" in df.columns:
        df["aqi_category"] = pd.cut(df["us_aqi"], bins=AQI_BINS, labels=AQI_LABELS).astype(object)

    return df.reset_index(drop=True), ingested_at


def write_partitions(df, bucket, dataset, city, ingested_at):
    """Write one Parquet file per observation date; return the keys written."""
    stamp = ingested_at.strftime("%Y%m%dT%H")
    written = []
    for obs_date, part in df.groupby(df["observation_ts"].dt.strftime("%Y-%m-%d")):
        key = f"{CURATED_PREFIX}/{dataset}/dt={obs_date}/{city}_{stamp}.parquet"
        wr.s3.to_parquet(
            df=part.reset_index(drop=True),
            path=f"s3://{bucket}/{key}",
            index=False,
            pyarrow_additional_kwargs={
                "coerce_timestamps": "ms",
                "allow_truncated_timestamps": True,
            },
        )
        written.append(key)
    return written


def handler(event, context):
    results = []
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        # S3 event keys are URL-encoded ("=" arrives as "%3D"), so decode first.
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        if not key.startswith("raw/"):
            logger.info("Skipping non-raw key: %s", key)
            continue

        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
        envelope = json.loads(body)

        df, ingested_at = build_dataframe(envelope)
        if df.empty:
            logger.warning("No rows after filtering for %s", key)
            continue

        keys = write_partitions(df, bucket, envelope["dataset"], envelope["city"], ingested_at)
        logger.info("%s -> %d rows, %d file(s): %s", key, len(df), len(keys), keys)
        results.append({"source": key, "rows": len(df), "outputs": keys})

    return {"processed": len(results)}