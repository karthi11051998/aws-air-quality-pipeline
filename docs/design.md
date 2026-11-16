# Design Document: AWS Air Quality and Weather Batch Pipeline

**Status:** Approved (Phase 1)
**Region:** ap-south-2 (Hyderabad)
**Last updated:** 2026-11-13

## 1. Problem statement

Data analysts and business owners in logistics, outdoor retail, events and healthcare clinics need to know when air pollution and weather will hurt deliveries, footfall or demand. Today this data is scattered across APIs and not analysis-ready.

This project builds a serverless batch pipeline on AWS that pulls air quality and weather data for major Indian cities every 3 hours, stores it in a partitioned data lake, and exposes it through SQL so analysts can answer:

1. Which cities had unhealthy AQI levels most often this week?
2. Which hours of the day are riskiest for outdoor deliveries?
3. How do rain and temperature relate to AQI?

## 2. Out of scope

- Real-time or streaming ingestion
- Machine learning or AQI forecasting
- Cities beyond the 8 listed below
- Multi-region deployment

## 3. Data source

- **Open-Meteo Air Quality API:** https://open-meteo.com/en/docs/air-quality-api
- **Open-Meteo Weather Forecast API:** https://open-meteo.com/en/docs
- No API key required. Free for non-commercial use, which fits this portfolio project. Data is attributed to Open-Meteo.

## 4. Design decisions

| # | Decision | Choice | Rationale |
|---|---|---|---|
| 1 | Cities | Delhi, Mumbai, Bengaluru, Hyderabad, Chennai, Kolkata, Pune, Ahmedabad | Mix of heavily polluted and cleaner metros; well below API limits |
| 2 | Air quality fields | PM2.5, PM10, CO, NO2, SO2, O3, US AQI | Standard pollutant set analysts expect |
| 3 | Weather fields | Temperature, relative humidity, precipitation, wind speed | Supports the rain and temperature vs AQI question |
| 4 | Granularity | Hourly, timezone Asia/Kolkata | Needed to find the riskiest hours |
| 5 | Schedule | Every 3 hours (8 runs per day) | Meets the "every few hours" requirement at near-zero cost |
| 6 | Pull window | Each run fetches the last 24 hours | Deliberate overlap recovers from failed runs and catches revised values |
| 7 | Idempotency | Transform deduplicates on city + observation hour, keeping the latest ingestion | Reruns never create duplicate rows |
| 8 | Raw zone | Original JSON, never modified, partitioned by ingestion date and hour | Enables replay and debugging |
| 9 | Curated zone | Parquet, partitioned by observation date only | Data is small; partitioning by city would over-partition |
| 10 | Derived field | AQI category (Good, Moderate, Unhealthy, and so on) added during transform | Business users think in categories, not raw numbers |
| 11 | Runtime | Python 3.12, x86_64, AWS SDK for pandas managed Lambda layer | Layer availability verified in ap-south-2 |
| 12 | Naming | All resources prefixed `aqp-` | Easy to find, tag and clean up |

## 5. Architecture

```
EventBridge Scheduler (every 3 hrs)
        |
        v
Lambda: ingest  -->  S3 raw/  (JSON, partitioned by ingestion date and hour)
                        | (S3 event trigger)
                        v
Lambda: transform -->  S3 curated/ (Parquet, partitioned by observation date)
                        |
                        v
        Glue Data Catalog --> Athena (SQL views)
                                  |
                                  v
                  Dashboard (QuickSight not available in ap-south-2;
                  fallback: Athena result screenshots)
```

Supporting components: CloudWatch logs and alarms, SNS email alerts on failure, and a dead-letter queue.

## 6. Repository principle

GitHub is the source of truth and AWS is where the code is deployed. Every Lambda, SQL query and infrastructure definition lives in this repo as a file and is deployed with AWS SAM. Nothing is authored only in the AWS console.

## 7. Cost and safety

- Everything fits in the AWS free tier at this volume.
- An AWS Budget alert is configured.
- IAM roles are least-privilege and scoped to this project's bucket.
- No secrets or account IDs are committed; configuration is passed through environment variables.
