-- Need to run each statement separately in the Athena console (workgroup: aqp-workgroup).
-- Need to replace <BUCKET> with our data bucket name before running.

CREATE EXTERNAL TABLE IF NOT EXISTS aqp_db.air_quality (
  city string,
  latitude double,
  longitude double,
  observation_ts timestamp,
  pm2_5 double,
  pm10 double,
  carbon_monoxide double,
  nitrogen_dioxide double,
  sulphur_dioxide double,
  ozone double,
  us_aqi double,
  ingested_at timestamp,
  aqi_category string
)
PARTITIONED BY (dt string)
STORED AS PARQUET
LOCATION 's3://<BUCKET>/curated/air_quality/'
TBLPROPERTIES (
  'projection.enabled' = 'true',
  'projection.dt.type' = 'date',
  'projection.dt.range' = '2026-11-01,NOW',
  'projection.dt.format' = 'yyyy-MM-dd',
  'storage.location.template' = 's3://<BUCKET>/curated/air_quality/dt=${dt}/'
);

CREATE EXTERNAL TABLE IF NOT EXISTS aqp_db.weather (
  city string,
  latitude double,
  longitude double,
  observation_ts timestamp,
  temperature_2m double,
  relative_humidity_2m double,
  precipitation double,
  wind_speed_10m double,
  ingested_at timestamp
)
PARTITIONED BY (dt string)
STORED AS PARQUET
LOCATION 's3://<BUCKET>/curated/weather/'
TBLPROPERTIES (
  'projection.enabled' = 'true',
  'projection.dt.type' = 'date',
  'projection.dt.range' = '2026-11-01,NOW',
  'projection.dt.format' = 'yyyy-MM-dd',
  'storage.location.template' = 's3://<BUCKET>/curated/weather/dt=${dt}/'
);